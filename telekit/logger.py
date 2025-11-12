import logging
import sys
from pathlib import Path
from typing import Union, Callable, Protocol

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

# ------------------------------
# Main Library Logger
# ------------------------------
library_logger: logging.Logger = logging.getLogger("library")
library_logger.setLevel(logging.DEBUG)

# Console handler (always on)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
library_logger.addHandler(ch)

# ------------------------------
# User Logging
# ------------------------------
_enabled_users: set[Union[int, str]] = set()
user_logger: logging.Logger = logging.getLogger("users")
user_logger.setLevel(logging.DEBUG)

# Console handler (always on)
uch = logging.StreamHandler(sys.stdout)
uch.setLevel(logging.DEBUG)
uch.setFormatter(formatter_lineno)
user_logger.addHandler(uch)

def enable_user_logging(*user_ids: Union[int, str]) -> None:
    _enabled_users.update(user_ids)

class UserLoggerProtocol(Protocol):
    def info(self, msg: str, *args, **kwargs) -> None: ...
    def warning(self, msg: str, *args, **kwargs) -> None: ...
    def debug(self, msg: str, *args, **kwargs) -> None: ...
    def error(self, msg: str, *args, **kwargs) -> None: ...
    def critical(self, msg: str, *args, **kwargs) -> None: ...

def _users(user_id: Union[int, str]) -> UserLoggerProtocol:
    class UserLogger:
        def info(self, msg, *args, **kwargs):
            if user_id in _enabled_users:
                user_logger.info(f"[{user_id}] {msg}", *args, stacklevel=2, **kwargs)
        def warning(self, msg, *args, **kwargs):
            if user_id in _enabled_users:
                user_logger.warning(f"[{user_id}] {msg}", *args, stacklevel=2, **kwargs)
        def debug(self, msg, *args, **kwargs):
            if user_id in _enabled_users:
                user_logger.debug(f"[{user_id}] {msg}", *args, stacklevel=2, **kwargs)
        def error(self, msg, *args, **kwargs):
            if user_id in _enabled_users:
                user_logger.error(f"[{user_id}] {msg}", *args, stacklevel=2, **kwargs)
        def critical(self, msg, *args, **kwargs):
            if user_id in _enabled_users:
                user_logger.critical(f"[{user_id}] {msg}", *args, stacklevel=2, **kwargs)
    return UserLogger()

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

    # Library file handler
    fh = logging.FileHandler(LOG_FOLDER / "library.log", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    library_logger.addHandler(fh)

    # User file handler
    ufh = logging.FileHandler(LOG_FOLDER / "users.log", encoding="utf-8")
    ufh.setLevel(logging.DEBUG)
    ufh.setFormatter(formatter_lineno)
    user_logger.addHandler(ufh)

    # Server file handler
    sfh = logging.FileHandler(LOG_FOLDER / "server.log", encoding="utf-8")
    sfh.setLevel(logging.DEBUG)
    sfh.setFormatter(formatter_nofile)
    server_logger.addHandler(sfh)

# ------------------------------
# Typed convenience wrapper
# ------------------------------
class LoggerWrapper:
    library: logging.Logger = library_logger
    server: logging.Logger = server_logger
    enable_user_logging: Callable[..., None] = enable_user_logging
    enable_file_logging: Callable[..., None] = enable_file_logging

    def users(self, user_id: int | str):
        return _users(user_id)

logger: LoggerWrapper = LoggerWrapper()

__all__ = ["logger", "enable_user_logging", "enable_file_logging"]