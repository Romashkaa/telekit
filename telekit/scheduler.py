import threading

from typing import Callable

# Logging
from ._logger import logger as _logger
_library = _logger.library

class PeriodicTask:
    """
    Represents a periodically scheduled background task.

    Wraps a callable and manages its execution in a daemon thread,
    providing control methods to stop and inspect the task.

    :param func: The function to call periodically.
    :type func: Callable
    :param total_seconds: Interval between calls in seconds.
    :type total_seconds: float

    :Example:

    .. code-block:: python

        task = every(seconds=10)(my_func)
        task.stop()
        task.is_running()
    """

    def __init__(self, func: Callable, total_seconds: float) -> None:
        self._func = func
        self._total_seconds = total_seconds
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._wrapper, daemon=True)
        self._thread.name = f"every/{func.__name__}/{total_seconds}s"
        self._thread.start()

    def _wrapper(self) -> None:
        """
        Internal loop that calls the wrapped function at each interval.

        - First pause occurs **before** the first call (like cron).
        - Exceptions are logged via :mod:`logging`, the loop **does not** stop.
        - Responds to the stop event during the wait (does not get stuck in sleep).
        """
        _library.info(
            "Started periodic task '%s' with interval %.1f sec.",
            self._func.__name__,
            self._total_seconds,
        )
        while not self._stop_event.wait(self._total_seconds):
            try:
                self._func()
            except Exception as exc:  # noqa: BLE001
                _library.exception(
                    "Error in '%s': %s — task continues running.",
                    self._func.__name__,
                    exc,
                )

        _library.info("Stopped task '%s'.", self._func.__name__)

    # ── public API ───────────────────────────────────────────────────────────

    def stop(self) -> None:
        """
        Signals the task to stop after the current iteration completes.

        .. code-block:: python

            task.stop()
        """
        self._stop_event.set()

    def is_running(self) -> bool:
        """
        Returns ``True`` if the background thread is still alive.

        :return: Thread status.
        :rtype: bool
        """
        return self._thread.is_alive()

    def __repr__(self) -> str:
        status = "running" if self.is_running() else "stopped"
        return (
            f"<PeriodicTask func={self._func.__name__!r} "
            f"interval={self._total_seconds}s status={status}>"
        )

    def __call__(self, *args, **kwargs):
        """
        Allows calling the original function directly if needed.

        :return: Result of the wrapped function.
        """
        return self._func(*args, **kwargs)


def every(
    *,
    seconds: int | float = 0,
    minutes: int | float = 0,
    hours: int | float = 0,
    days: int | float = 0,
) -> Callable:
    """
    Decorator for periodically calling a function in a background daemon thread.

    Supports combining time units. Minimum interval is 1 second.
    Exceptions inside the function do not stop the loop — the error is logged
    and calls continue.

    :param seconds: Number of seconds between calls.
    :type seconds: int | float
    :param minutes: Number of minutes between calls.
    :type minutes: int | float
    :param hours: Number of hours between calls.
    :type hours: int | float
    :param days: Number of days between calls.
    :type days: int | float
    :raises ValueError: If the total interval is less than 1 second.
    :return: Decorator that returns a :class:`PeriodicTask` instance.
    :rtype: Callable

    :Example:

    .. code-block:: python

        @every(seconds=30)
        def cleanup():
            db.clear_expired_sessions()

        @every(hours=1, minutes=30)
        def send_digest():
            bot.send_message(ADMIN_ID, "digest...")

        # Control the task:
        cleanup.stop()
        cleanup.is_running()  # False
        print(cleanup)        # <PeriodicTask func='cleanup' interval=30.0s status=stopped>
    """
    total_seconds: float = (
        seconds
        + minutes * 60
        + hours * 3_600
        + days * 86_400
    )

    if total_seconds < 1:
        raise ValueError(
            f"Interval must be at least 1 second, got: {total_seconds}s. "
            f"Provided: days={days}, hours={hours}, minutes={minutes}, seconds={seconds}."
        )

    def decorator(func: Callable) -> PeriodicTask:
        """
        Wraps the function into a :class:`PeriodicTask` and starts it immediately.

        :param func: Synchronous function to call periodically.
        :type func: Callable
        :return: A :class:`PeriodicTask` managing the background execution.
        :rtype: PeriodicTask
        """
        return PeriodicTask(func, total_seconds)

    return decorator