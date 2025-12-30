from typing import Callable
import threading

class Timeout:
    def __init__(self, callback: Callable, total_seconds: int):
        self.total_seconds = total_seconds
        self.callback = callback
        self._timer = None
        self._cancelled = False

    def start(self):
        self._cancelled = False
        self._timer = threading.Timer(self.total_seconds, self._execute)
        self._timer.start()

    def _execute(self):
        if self._cancelled:
            return
        self.callback()

    def cancel(self):
        self._cancelled = True
        if self._timer:
            self._timer.cancel()

class TimeoutHandler:
    def __init__(self):
        self.total_seconds: int = 0
        self.callback: Callable | None = None
        self.timeout: Timeout | None = None

    def set_time(self, seconds=0, minutes=0, hours=0):
        self.total_seconds = seconds + minutes * 60 + hours * 3600

    def set_callback(self, callback: Callable):
        self.callback = callback

    def maybe_start(self) -> bool:
        if self.callback and self.total_seconds:
            self.timeout = Timeout(self.callback, self.total_seconds)
            self.timeout.start()

            return True
        return False

    def cancel(self):
        if self.timeout:
            self.timeout.cancel()
            self.timeout = None

    def remove(self):
        self.cancel()
        self.callback = None
        self.total_seconds = 0
