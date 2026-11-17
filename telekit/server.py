# 
# Copyright (C) 2026 Romashka
# 
# This file is part of Telekit.
# 
# Telekit is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version.
# 
# Telekit is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty 
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See 
# the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License 
# along with Telekit. If not, see <https://www.gnu.org/licenses/>.
# 

import random
import re
import socket
import ssl
import sys
import time
import traceback
import warnings
from enum import Enum
from typing import Callable, Literal, Optional
from urllib.parse import urlparse

import requests
import telebot
import urllib3
from telebot import apihelper
from telebot.apihelper import ApiTelegramException

from . import _init, _state

from ._logger import server_logger

# ------------------------------------------
# Network helpers
# ------------------------------------------

_TOKEN_RE = re.compile(r"bot\d+:[A-Za-z0-9_-]+")

_NETWORK_ERRORS = (
    requests.exceptions.ConnectionError,
    requests.exceptions.Timeout,
    requests.exceptions.ChunkedEncodingError,
    urllib3.exceptions.HTTPError,
    socket.gaierror,
    socket.timeout,
    ssl.SSLError,
    ConnectionError,
    TimeoutError,
)

# Transient Bot API answers: rate limit and server-side failures.
_RETRYABLE_API_CODES = frozenset({429, 500, 502, 503, 504})


def _mask(obj: object) -> str:
    """Hide bot tokens (``bot<id>:<secret>``) that leak via request URLs."""
    return _TOKEN_RE.sub("bot<hidden>", str(obj))


def is_network_error(exc: Optional[BaseException]) -> bool:
    """
    Check whether an exception was caused by a transient network problem.

    Walks the ``__cause__`` / ``__context__`` chain. A Bot API error counts
    as a network error only if its code is in :data:`_RETRYABLE_API_CODES`
    (so ``401`` or ``409`` do **not**).

    :param exc: Exception to inspect.
    :type exc: :obj:`BaseException` | :obj:`None`
    :return: ``True`` if the failure is transient and network related.
    :rtype: :obj:`bool`
    """
    seen: set[int] = set()
    while exc is not None and id(exc) not in seen:
        seen.add(id(exc))
        if isinstance(exc, ApiTelegramException):
            return exc.error_code in _RETRYABLE_API_CODES
        if isinstance(exc, _NETWORK_ERRORS):
            return True
        exc = exc.__cause__ or exc.__context__
    return False


def _retry_after(exc: BaseException) -> float:
    """Return ``parameters.retry_after`` from a Bot API error, or ``0.0``."""
    result_json = getattr(exc, "result_json", None)
    if isinstance(result_json, dict):
        params = result_json.get("parameters")
        if isinstance(params, dict):
            try:
                return float(params.get("retry_after") or 0)
            except (TypeError, ValueError):
                pass
    return 0.0


class _Backoff:
    """Exponential backoff with jitter."""

    def __init__(self, base: float, cap: float):
        self.base, self.cap, self.attempt = base, cap, 0

    def reset(self) -> None:
        self.attempt = 0

    def next(self) -> float:
        delay = min(self.cap, self.base * 2 ** min(self.attempt, 10))
        self.attempt += 1
        return delay * random.uniform(0.8, 1.2)


_DEFAULT_API_URL = "https://api.telegram.org/bot{0}/{1}"


def _api_endpoint() -> Optional[tuple[str, int]]:
    """
    Resolve ``(host, port)`` of the Bot API from :mod:`telebot.apihelper`.

    Falls back to the official ``api.telegram.org`` if
    :data:`telebot.apihelper.API_URL` is not set (``None``), which is the
    case in some telebot versions.

    Returns ``None`` when a proxy is configured, because a direct TCP probe
    would be meaningless in that case.
    """
    if getattr(apihelper, "proxy", None):
        return None

    api_url = getattr(apihelper, "API_URL", None) or _DEFAULT_API_URL
    try:
        parsed = urlparse(str(api_url).format("", ""))
    except (IndexError, KeyError, ValueError):
        parsed = urlparse(_DEFAULT_API_URL.format("", ""))

    if not parsed.hostname:
        return None
    return parsed.hostname, parsed.port or (443 if parsed.scheme == "https" else 80)


def wait_for_network(
    *,
    check_timeout: float = 5.0,
    max_wait: Optional[float] = None,
) -> bool:
    """
    Block until a TCP connection to the Bot API host succeeds.

    Covers both DNS (``Temporary failure in name resolution``) and routing
    (``Network is unreachable``) problems. Returns immediately if the
    endpoint cannot be probed (proxy in use).

    :param check_timeout: Timeout of a single connection attempt, seconds.
    :type check_timeout: :obj:`float`
    :param max_wait: Give up after this many seconds. ``None`` waits forever.
    :type max_wait: :obj:`float` | :obj:`None`
    :return: ``True`` if the network is available, ``False`` if ``max_wait`` expired.
    :rtype: :obj:`bool`
    """
    endpoint = _api_endpoint()
    if endpoint is None:
        return True

    backoff = _Backoff(2.0, 30.0)
    started = time.monotonic()
    tries = 0
    while True:
        try:
            socket.create_connection(endpoint, timeout=check_timeout).close()
            if tries:
                server_logger.info(f"Network is back after {time.monotonic() - started:.0f}s")
            return True
        except OSError as e:
            if tries % 10 == 0:
                server_logger.warning(
                    f"No connection to {endpoint[0]}:{endpoint[1]} ({e}); waiting (attempt {tries + 1})"
                )
            tries += 1
            if max_wait is not None and time.monotonic() - started > max_wait:
                return False
            time.sleep(backoff.next())

# ------------------------------------------
# Server
# ------------------------------------------

__all__ = ["Server", "RestartMode", "RestartLiteral"]


RestartLiteral = Literal["never", "network", "always"]
"""String forms accepted by the ``restart`` parameter."""


class RestartMode(str, Enum):
    """Defines which polling failures :class:`Server` survives."""

    NEVER = "never"
    """Any error stops the server and is re-raised."""

    NETWORK = "network"
    """Only transient network / Bot API errors (5xx, 429) are survived.
    Everything else (bad token, conflicts, bugs) is re-raised."""

    ALWAYS = "always"
    """Any exception is logged and polling is restarted."""


class _Unset:
    def __repr__(self) -> str:
        return "<unset>"

_UNSET = _Unset()


class Server:
    RESTART_DELAY_MIN: float = 5.0
    "Initial pause between restarts, seconds."

    RESTART_DELAY_MAX: float = 60.0
    "Maximum pause between restarts, seconds."

    STABLE_AFTER: float = 120.0
    "If one polling cycle lived at least this long, the backoff is reset."

    def __init__(
        self,
        bot: telebot.TeleBot | str,
        *,
        auto_restart: "bool | _Unset" = _UNSET,
        restart: "RestartMode | RestartLiteral | None" = None,
    ):
        """
        :param bot: Bot instance or bot token.
        :type bot: :obj:`telebot.TeleBot` | :obj:`str`

        :param auto_restart: Deprecated. ``True`` is equivalent to
            ``restart="always"``, ``False`` to ``restart="never"``.
            Cannot be combined with ``restart``.
        :type auto_restart: :obj:`bool`

        :param restart: Failure policy, see :class:`RestartMode`.
            Defaults to :attr:`RestartMode.ALWAYS`.
        :type restart: :class:`RestartMode` | ``"never"`` | ``"network"`` | ``"always"`` | :obj:`None`

        :raises TypeError: If both ``auto_restart`` and ``restart`` are given.
        :raises ValueError: If ``restart`` is not a valid :class:`RestartMode`.

        .. deprecated:: X.Y.Z
            ``auto_restart`` is replaced by ``restart``.

        .. note::

            Unless ``restart`` is :attr:`RestartMode.NEVER`, the constructor
            blocks until the Bot API is reachable, because it needs ``getMe``.
        """
        if auto_restart is not _UNSET:
            if restart is not None:
                raise TypeError("'auto_restart' and 'restart' are mutually exclusive")
            warnings.warn(
                "'auto_restart' is deprecated, use restart='always' | 'network' | 'never' instead",
                DeprecationWarning,
                stacklevel=2,
            )
            server_logger.warning(
                "'auto_restart' is deprecated, use restart='always' | 'network' | 'never' instead"
            )
            mode = RestartMode.ALWAYS if auto_restart else RestartMode.NEVER
        else:
            mode = RestartMode(restart) if restart is not None else RestartMode.ALWAYS

        self._restart = mode
        self._auto_restart = mode is not RestartMode.NEVER  # kept for backward compatibility

        if mode is not RestartMode.NEVER:
            wait_for_network()

        if isinstance(bot, str):
            bot = telebot.TeleBot(bot)

        self._bot = bot
        _init.init(bot)

    def infinity_polling(
            self, 
            *, 
            timeout: Optional[int]=20, 
            skip_pending: Optional[bool]=False, 
            long_polling_timeout: Optional[int]=20, 
            allowed_updates: Optional[list[str]]=None,
            restart_on_change: Optional[bool]=False, 
            path_to_watch: Optional[str]=None, 
            **kwargs
        ):
        """
        Wrap polling with infinite loop and exception handling to avoid bot stops polling.

        .. note::

            Install watchdog and psutil before using restart_on_change option.

        .. note::

            The ``restart`` policy is not applied here: restarts are handled
            by :meth:`telebot.TeleBot.infinity_polling` itself.

        :param timeout: Request connection timeout.
        :type timeout: :obj:`int`

        :param long_polling_timeout: Timeout in seconds for long polling (see API docs)
        :type long_polling_timeout: :obj:`int`

        :param skip_pending: skip old updates
        :type skip_pending: :obj:`bool`

        :param logger_level: Custom (different from logger itself) logging level for infinity_polling logging.
            Use logger levels from logging as a value. None/NOTSET = no error logging
        :type logger_level: :obj:`int`.

        :param allowed_updates: A list of the update types you want your bot to receive.
            For example, specify [“message”, “edited_channel_post”, “callback_query”] to only receive updates of these types.
            See util.update_types for a complete list of available update types.
            Specify an empty list to receive all update types except chat_member (default).
            If not specified, the previous setting will be used.
            Please note that this parameter doesn't affect updates created before the call to the get_updates,
            so unwanted updates may be received for a short period of time.
        :type allowed_updates: :obj:`list` of :obj:`str`

        :param restart_on_change: Restart a file on file(s) change. Defaults to False
        :type restart_on_change: :obj:`bool`

        :param path_to_watch: Path to watch for changes. Defaults to current directory
        :type path_to_watch: :obj:`str`

        :return:
        """
        server_logger.info("Telekit server is infinity polling...")
        self._bot.infinity_polling(
            timeout = timeout,
            skip_pending = skip_pending,
            long_polling_timeout = long_polling_timeout,
            allowed_updates = allowed_updates,
            restart_on_change = restart_on_change,
            path_to_watch = path_to_watch,
            **kwargs
        )

    def polling(self):
        """
        Standard ``bot.polling(none_stop=True)`` polling, protected
        according to the ``restart`` policy.

        Returns normally if polling was stopped via
        :meth:`telebot.TeleBot.stop_polling`; the server is **not** restarted.

        :raises Exception: The original error, if the policy does not allow a restart.
        """
        self._run(lambda: self._bot.polling(none_stop=True), "polling")

    def long_polling(self, *, timeout: int = 60):
        """
        Long ``bot.polling(none_stop=True, timeout=timeout)`` polling with a
        custom timeout, protected according to the ``restart`` policy.

        Returns normally if polling was stopped via
        :meth:`telebot.TeleBot.stop_polling`; the server is **not** restarted.

        :param timeout: Long polling timeout in seconds.
        :type timeout: :obj:`int`
        :raises Exception: The original error, if the policy does not allow a restart.
        """
        self._run(lambda: self._bot.polling(none_stop=True, timeout=timeout), "long polling")

    def _run(self, target: Callable[[], None], label: str) -> None:
        mode = self._restart
        backoff = _Backoff(self.RESTART_DELAY_MIN, self.RESTART_DELAY_MAX)

        while True:
            server_logger.info(f"Telekit server is {label}... [restart={mode.value}]")
            started = time.monotonic()

            try:
                target()
            except Exception as exception:
                network = is_network_error(exception)

                if mode is RestartMode.NEVER or (mode is RestartMode.NETWORK and not network):
                    server_logger.fatal(
                        f"[server dead] Polling cycle error [restart={mode.value}] : {_mask(exception)}"
                    )
                    raise

                if time.monotonic() - started >= self.STABLE_AFTER:
                    backoff.reset()

                delay = max(backoff.next(), _retry_after(exception))

                if network:
                    server_logger.warning(
                        f"Network error ({type(exception).__name__}): {_mask(exception)} "
                        f"- restarting in {delay:.0f}s (attempt {backoff.attempt})"
                    )
                else:
                    server_logger.error(
                        f"Unexpected error ({type(exception).__name__}): {_mask(exception)} "
                        f"- restarting in {delay:.0f}s\n{_mask(traceback.format_exc())}"
                    )

                time.sleep(delay)
                if network:
                    wait_for_network()
                self._refresh_state()
            else:
                # bot.polling() returned without an error: stop_polling() was called
                server_logger.info(f"Telekit server stopped {label} normally")
                return

    @staticmethod
    def _refresh_state() -> None:
        """Refresh cached bot info; a failure here must never kill the server."""
        try:
            _state.TelekitState._update()
        except Exception as e:
            server_logger.warning(f"TelekitState update skipped ({type(e).__name__}): {_mask(e)}")


# Example

def example(token: str):
    import telekit.example as example

    example.example_server.run_example(token)