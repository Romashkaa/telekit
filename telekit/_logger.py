import logging
import os
import sys
from pathlib import Path
from typing import Callable, Union

try:
    from rich.console import Console
    from rich.logging import RichHandler
    _RICH = True
except ImportError:
    _RICH = False

_USE_RICH: bool = _RICH and not os.environ.get("TELEKIT_NO_RICH")

__all__ = [
    "server_logger",
    "library_logger",
    "user_logger",
    "get_user_logger",
    "UserLogger",
    "enable_user_logging",
    "disable_user_logging",
    "enable_file_logging",
    "set_level",
    "logger",
]

# ------------------------------
# Formatting
# ------------------------------

_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s",
    datefmt=_DATE_FORMAT,
)
"Used by the plain console handler and by every file handler."


def _make_console_handler() -> logging.Handler:
    handler: logging.Handler
    if _USE_RICH:
        handler = RichHandler(  # pyright: ignore[reportPossiblyUnboundVariable]
            # soft_wrap: do not hard-wrap lines to 80 columns when stdout is not a TTY
            console=Console(soft_wrap=True),  # pyright: ignore[reportPossiblyUnboundVariable]
            rich_tracebacks=True,
            show_path=True,
            enable_link_path=False,
            # messages contain things like "[server dead]" or "[123]", not rich markup
            markup=False,
            omit_repeated_times=False,
            log_time_format=f"[{_DATE_FORMAT}]",
        )
    else:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(_formatter)
    return handler

# ------------------------------
# Loggers
# ------------------------------

_root: logging.Logger = logging.getLogger("telekit")
_root.setLevel(logging.DEBUG)
_root.propagate = False  # otherwise every line is printed twice if the app configured the root logger
if not _root.handlers:  # guard against reloads
    _root.addHandler(_make_console_handler())

library_logger: logging.Logger = logging.getLogger("telekit.library")
"Internal events of the library."

server_logger: logging.Logger = logging.getLogger("telekit.server")
"Polling, restarts and network state."

user_logger: logging.Logger = logging.getLogger("telekit.users")
"Per-user events, see :func:`get_user_logger`."


def set_level(level: Union[int, str]) -> None:
    """
    Set the level of all Telekit loggers.

    :param level: Level number or name, e.g. ``"INFO"``.
    :type level: :obj:`int` | :obj:`str`
    """
    _root.setLevel(level)

# ------------------------------
# User logging
# ------------------------------

_enabled_users: set[Union[int, str]] = set()


def enable_user_logging(*user_ids: Union[int, str]) -> None:
    """Start logging events of the given users (nothing is logged by default)."""
    _enabled_users.update(user_ids)


def disable_user_logging(*user_ids: Union[int, str]) -> None:
    """Stop logging events of the given users."""
    _enabled_users.difference_update(user_ids)


class UserLogger:
    """Thin wrapper that prefixes every line with the user ID and
    drops it unless the user was enabled via :func:`enable_user_logging`."""

    __slots__ = ("_user_id",)

    def __init__(self, user_id: Union[int, str, None]) -> None:
        self._user_id = user_id

    def _log(self, level: int, msg: str, *args, **kwargs) -> None:
        if self._user_id in _enabled_users:
            # stacklevel=3: point at the caller of debug()/info()/..., not at this module
            kwargs.setdefault("stacklevel", 3)
            user_logger.log(level, f"[{self._user_id}] {msg}", *args, **kwargs)

    def debug(self, msg: str, *args, **kwargs) -> None:
        self._log(logging.DEBUG, msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        self._log(logging.INFO, msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        self._log(logging.WARNING, msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        self._log(logging.ERROR, msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs) -> None:
        kwargs.setdefault("exc_info", True)
        self._log(logging.ERROR, msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs) -> None:
        self._log(logging.CRITICAL, msg, *args, **kwargs)


def get_user_logger(user_id: Union[int, str, None]) -> UserLogger:
    """
    Get a logger bound to a user.

    :param user_id: Telegram user ID.
    :type user_id: :obj:`int` | :obj:`str` | :obj:`None`
    :rtype: :class:`UserLogger`
    """
    return UserLogger(user_id)

# ------------------------------
# File logging
# ------------------------------

_file_logging_enabled: bool = False


def enable_file_logging(log_folder: Union[str, Path] = "logs") -> None:
    """
    Duplicate logs into ``library.log``, ``users.log`` and ``server.log``.

    Calling it more than once has no effect.

    :param log_folder: Folder for the log files, created if missing.
    :type log_folder: :obj:`str` | :obj:`pathlib.Path`
    """
    global _file_logging_enabled
    if _file_logging_enabled:
        return

    folder = Path(log_folder)
    folder.mkdir(parents=True, exist_ok=True)

    for log, name in (
        (library_logger, "library.log"),
        (user_logger, "users.log"),
        (server_logger, "server.log"),
    ):
        handler = logging.FileHandler(folder / name, encoding="utf-8")
        handler.setFormatter(_formatter)
        log.addHandler(handler)

    _file_logging_enabled = True

# ------------------------------
# Backward compatibility
# ------------------------------

class _LoggerNamespace:
    "Kept so that ``logger.server`` / ``logger.users(id)`` keep working."

    library: logging.Logger = library_logger
    server: logging.Logger = server_logger
    enable_user_logging: Callable[..., None] = staticmethod(enable_user_logging)
    enable_file_logging: Callable[..., None] = staticmethod(enable_file_logging)

    @staticmethod
    def users(user_id: Union[int, str, None]) -> UserLogger:
        return get_user_logger(user_id)


logger: _LoggerNamespace = _LoggerNamespace()

_library = library_logger
_server = server_logger