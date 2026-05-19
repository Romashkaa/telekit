import logging
import sys
from pathlib import Path
from typing import Union, Callable

try:
    from rich.logging import RichHandler as _RichHandler
    _RICH = True
except ImportError:
    _RICH = False

# ------------------------------
# Formatter
# ------------------------------
formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)s | %(filename)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
formatter_lineno = logging.Formatter(
    fmt="%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
formatter_nofile = logging.Formatter(
    fmt="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def _make_handler(formatter: logging.Formatter) -> logging.Handler:
    if _RICH:
        handler = _RichHandler(rich_tracebacks=True, show_path=False) # pyright: ignore[reportPossiblyUnboundVariable]
    else:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    return handler


# ------------------------------
# Main Library Logger
# ------------------------------
library_logger: logging.Logger = logging.getLogger("library")
library_logger.setLevel(logging.DEBUG)
library_logger.addHandler(_make_handler(formatter))

# ------------------------------
# User Logging
# ------------------------------
_enabled_users: set[Union[int, str]] = set()

user_logger: logging.Logger = logging.getLogger("users")
user_logger.setLevel(logging.DEBUG)
user_logger.addHandler(_make_handler(formatter_lineno))


def enable_user_logging(*user_ids: Union[int, str]) -> None:
    _enabled_users.update(user_ids)


class _UserLogger:
    """Thin wrapper that prefixes every log line with the user ID."""
    __slots__ = ("_user_id",)

    def __init__(self, user_id: int | str | None) -> None:
        self._user_id = user_id

    def _log(self, level: int, msg: str, *args, **kwargs) -> None:
        if self._user_id in _enabled_users:
            user_logger.log(level, f"[{self._user_id}] {msg}", *args, stacklevel=3, **kwargs)

    def debug(self, msg: str, *args, **kwargs) -> None:
        self._log(logging.DEBUG, msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        self._log(logging.INFO, msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        self._log(logging.WARNING, msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        self._log(logging.ERROR, msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs) -> None:
        self._log(logging.CRITICAL, msg, *args, **kwargs)


# ------------------------------
# Server Logging
# ------------------------------
server_logger: logging.Logger = logging.getLogger("server")
server_logger.setLevel(logging.DEBUG)

# ------------------------------
# Enable file logging
# ------------------------------
def enable_file_logging(log_folder: Union[str, Path] = "logs") -> None:
    LOG_FOLDER = Path(log_folder)
    LOG_FOLDER.mkdir(exist_ok=True)

    for log, name, fmt in (
        (library_logger, "library.log", formatter),
        (user_logger,    "users.log",   formatter_lineno),
        (server_logger,  "server.log",  formatter_nofile),
    ):
        fh = logging.FileHandler(LOG_FOLDER / name, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)
        log.addHandler(fh)


# ------------------------------
# Typed convenience wrapper
# ------------------------------
class LoggerWrapper:
    library: logging.Logger = library_logger
    server: logging.Logger = server_logger
    enable_user_logging: Callable[..., None] = enable_user_logging
    enable_file_logging: Callable[..., None] = enable_file_logging

    def users(self, user_id: int | str | None) -> _UserLogger:
        return _UserLogger(user_id)


logger: LoggerWrapper = LoggerWrapper()
__all__ = ["logger", "enable_user_logging", "enable_file_logging"]