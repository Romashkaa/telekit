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

from typing import Any, Callable
import heapq
import itertools
import queue
import threading
import time

from ._logger import _library

__all__ = ["configure_timeouts", "timeout_stats"]

_DEFAULT_MAX_WORKERS = 16
_DEFAULT_IDLE_TIMEOUT = 60.0
_COMPACT_MIN_SIZE = 1024


def _invoke(callback: Callable[[], None]) -> None:
    try:
        callback()
    except Exception:
        _library.exception("Unhandled exception in timeout callback")


# ---------------------------------------------------------------------------
# Worker pool
# ---------------------------------------------------------------------------

class _WorkerPool:
    """
    Minimal thread pool with lazy worker creation and idle retirement.

    Accounting (all under `_lock`):
      _workers  - existing worker threads
      _idle     - workers waiting for a task
      _pending  - tasks put in the queue and not yet taken by a worker
    A new worker is started only if `_pending > _idle`.
    """

    def __init__(
        self,
        max_workers: int = _DEFAULT_MAX_WORKERS,
        idle_timeout: float = _DEFAULT_IDLE_TIMEOUT,
        log_worker_changes: bool = False,
        warn_on_max_workers: bool = True,
    ):
        self.max_workers = max_workers
        self.idle_timeout = idle_timeout
        self.log_worker_changes = log_worker_changes
        self.warn_on_max_workers = warn_on_max_workers

        self._queue: "queue.Queue[Callable[[], None]]" = queue.Queue()
        self._lock = threading.Lock()
        self._workers = 0
        self._idle = 0
        self._pending = 0
        self._saturated = False
        self._ids = itertools.count(1)

    def submit(self, callback: Callable[[], None]) -> None:
        with self._lock:
            self._queue.put(callback)
            self._pending += 1

            if self._pending <= self._idle:
                return  # an idle worker will take it

            if self._workers < self.max_workers:
                self._start_worker()
            elif not self._saturated:
                self._saturated = True
                if self.warn_on_max_workers:
                    _library.warning(
                        f"Timeout worker pool is saturated: all {self._workers} "
                        f"workers are busy and {self._pending} callback(s) are waiting. "
                        "Increase the limit with telekit.configure_timeouts(max_workers=...) "
                        "or make timeout callbacks faster."
                    )

    def _start_worker(self) -> None:
        """Must be called with the lock held."""
        thread = threading.Thread(
            target=self._worker,
            name=f"telekit-timeout-{next(self._ids)}",
            daemon=True,
        )
        self._workers += 1
        try:
            thread.start()
        except RuntimeError:
            self._workers -= 1
            _library.exception("Cannot start a timeout worker thread")
            return

        if self.log_worker_changes:
            _library.info(
                f"Timeout worker started ({self._workers}/{self.max_workers}, "
                f"{self._idle} idle, {self._pending} pending)"
            )

    def _retire(self, reason: str) -> None:
        """Must be called with the lock held."""
        self._workers -= 1
        if self.log_worker_changes:
            _library.info(
                f"Timeout worker stopped: {reason} "
                f"({self._workers}/{self.max_workers} left)"
            )

    def _worker(self) -> None:
        while True:
            with self._lock:
                if self._workers > self.max_workers:
                    self._retire("pool was shrunk")
                    return
                self._idle += 1

            try:
                callback = self._queue.get(timeout=self.idle_timeout)
            except queue.Empty:
                with self._lock:
                    self._idle -= 1
                    if self._queue.empty():
                        self._retire(f"idle for {self.idle_timeout:g}s")
                        return
                continue  # a task arrived at the last moment

            with self._lock:
                self._idle -= 1
                self._pending -= 1
                if self._pending == 0:
                    self._saturated = False

            _invoke(callback)

    def stats(self) -> dict[str, int]:
        with self._lock:
            return {
                "workers": self._workers,
                "workers_idle": self._idle,
                "workers_busy": self._workers - self._idle,
                "tasks_pending": self._pending,
                "max_workers": self.max_workers,
            }


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class _TimeoutScheduler:

    def __init__(self):
        self._heap: list[tuple[float, int, "Timeout"]] = []
        self._seq = itertools.count(1)
        self._cond = threading.Condition()
        self._thread: threading.Thread | None = None
        self._compact_at = _COMPACT_MIN_SIZE
        self.pool = _WorkerPool()

    def next_seq(self) -> int:
        return next(self._seq)

    def push(self, deadline: float, seq: int, timeout: "Timeout") -> None:
        with self._cond:
            heapq.heappush(self._heap, (deadline, seq, timeout))

            if len(self._heap) > self._compact_at:
                self._compact()

            if self._thread is None or not self._thread.is_alive():
                self._thread = threading.Thread(
                    target=self._run, name="telekit-timeout-scheduler", daemon=True
                )
                self._thread.start()

            # wake the scheduler only if the nearest deadline changed
            if self._heap[0][1] == seq:
                self._cond.notify()

    def _compact(self) -> None:
        """
        Drops dead entries (cancelled / orphaned).

        ! Must be called with the lock held !
        """
        alive = [entry for entry in self._heap if entry[2]._keep(entry[1])]
        heapq.heapify(alive)
        self._heap = alive
        self._compact_at = max(_COMPACT_MIN_SIZE, 2 * len(alive))

    def _run(self) -> None:
        while True:
            with self._cond:
                while True:
                    if not self._heap:
                        self._cond.wait()
                        continue
                    delay = self._heap[0][0] - time.monotonic()
                    if delay <= 0:
                        break
                    self._cond.wait(delay)
                _, seq, timeout = heapq.heappop(self._heap)

            try:
                callback = timeout._on_due(seq)
                if callback is not None:
                    self.pool.submit(callback)
            except Exception:
                _library.exception("Timeout scheduler error")

    def stats(self) -> dict[str, Any]:
        with self._cond:
            total = len(self._heap)
            live = sum(1 for _, seq, t in self._heap if t._is_live(seq))
            compact_at = self._compact_at

        return {
            "heap_total": total,
            "heap_live": live,
            "heap_dead": total - live,
            "heap_compact_at": compact_at,
            **self.pool.stats(),
        }


_scheduler = _TimeoutScheduler()


def configure_timeouts(
    max_workers: int | None = None,
    *,
    idle_timeout: float | None = None,
    log_worker_changes: bool | None = None,
    warn_on_max_workers: bool | None = None,
) -> None:
    """
    Configures the timeout worker pool. Only the passed values are changed.

    :param max_workers: Upper bound of worker threads (default 16). Workers are
        created lazily; if the pool is shrunk, surplus workers stop after
        their current task.
    :param idle_timeout: Seconds an idle worker waits for work before it stops
        (default 60). Affects workers on their next wait.
    :param log_worker_changes: Log every worker start / stop (default False).
    :param warn_on_max_workers: Log a warning when all workers are busy and
        callbacks have to wait (default True). Logged once per saturation episode.
    """
    pool = _scheduler.pool

    if max_workers is not None:
        if max_workers < 1:
            raise ValueError("max_workers must be >= 1")
        pool.max_workers = max_workers
    if idle_timeout is not None:
        if idle_timeout <= 0:
            raise ValueError("idle_timeout must be > 0")
        pool.idle_timeout = idle_timeout
    if log_worker_changes is not None:
        pool.log_worker_changes = log_worker_changes
    if warn_on_max_workers is not None:
        pool.warn_on_max_workers = warn_on_max_workers


def timeout_stats() -> dict[str, Any]:
    """
    Returns a snapshot of the timeout internals (for debugging).

    - ``heap_total`` / ``heap_live`` / ``heap_dead``: entries in the scheduler
      heap; dead = cancelled (or replaced) entries waiting to be dropped
    - ``heap_compact_at``: heap size that triggers the next compaction
    - ``workers`` / ``workers_idle`` / ``workers_busy``: worker threads
    - ``tasks_pending``: callbacks waiting for a free worker
    - ``max_workers``: current limit
    """
    return _scheduler.stats()


# ---------------------------------------------------------------------------
# Timeout
# ---------------------------------------------------------------------------

class Timeout:
    """
    A re-startable timeout. One object = at most one live heap entry.
    """

    __slots__ = (
        "callback", "_deadline", "_queued_seq", "_queued_deadline", "_lock"
    )

    def __init__(self):
        self.callback: Callable[[], None] | None = None
        self._deadline: float | None = None       # None -> inactive
        self._queued_seq: int | None = None       # seq of the valid heap entry
        self._queued_deadline: float = 0.0        # deadline of that entry
        self._lock = threading.Lock()

    # API

    def start(self, callback: Callable[[], None], total_seconds: float) -> None:
        """(Re)starts the timeout: it fires `total_seconds` from now."""
        deadline = time.monotonic() + total_seconds

        with self._lock:
            self.callback = callback
            self._deadline = deadline

            if self._queued_seq is not None and self._queued_deadline <= deadline:
                # an existing entry fires earlier; it will re-queue itself
                return

            seq = _scheduler.next_seq()
            self._queued_seq = seq
            self._queued_deadline = deadline

        _scheduler.push(deadline, seq, self)

    def cancel(self) -> None:
        """
        Cancels the timeout and releases the callback (and its closure).
        """
        with self._lock:
            self._deadline = None
            self.callback = None

    # Scheduler hooks

    def _on_due(self, seq: int) -> Callable[[], None] | None:
        """
        Called by the scheduler when the heap entry `seq` is due.
        Returns the callback to run, or None if there is nothing to run.
        """
        requeue: tuple[float, int] | None = None

        with self._lock:
            if self._queued_seq != seq:
                return None  # orphan entry, a newer one exists

            if self._deadline is None:
                self._queued_seq = None  # cancelled
                return None

            if self._deadline > time.monotonic():
                # restarted with a later deadline: move the entry, don't fire
                new_seq = _scheduler.next_seq()
                self._queued_seq = new_seq
                self._queued_deadline = self._deadline
                requeue = (self._deadline, new_seq)
            else:
                callback = self.callback
                self.callback = None
                self._deadline = None
                self._queued_seq = None
                return callback

        _scheduler.push(requeue[0], requeue[1], self)
        return None

    def _keep(self, seq: int) -> bool:
        """Compaction check: should the heap entry `seq` stay in the heap?"""
        with self._lock:
            if self._queued_seq != seq:
                return False  # orphan
            if self._deadline is not None:
                return True
            self._queued_seq = None  # cancelled: forget the entry
            return False

    def _is_live(self, seq: int) -> bool:
        """Read-only version of `_keep` (for stats)."""
        with self._lock:
            return self._queued_seq == seq and self._deadline is not None


class TimeoutHandler:
    def __init__(self):
        self.total_seconds: int = 0
        self.callback: Callable | None = None
        self.timeout: Timeout = Timeout()

    def set_time(self, seconds=0, minutes=0, hours=0):
        self.total_seconds = seconds + minutes * 60 + hours * 3600

    def set_callback(self, callback: Callable):
        self.callback = callback

    def maybe_start(self) -> bool:
        """
        Starts the timeout counting from now. If it was already running,
        it is restarted (the previous countdown is discarded).
        """
        if self.callback and self.total_seconds:
            self.timeout.start(self.callback, self.total_seconds)
            return True

        self.timeout.cancel()
        return False

    def cancel(self):
        self.timeout.cancel()

    def remove(self):
        self.cancel()
        self.callback = None
        self.total_seconds = 0
