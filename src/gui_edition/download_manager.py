"""Download task manager — bridges the GUI with backend async operations.

Manages a queue of download tasks, creates ProgressCard widgets, and
runs backend functions via AsyncHandler.  Each task tracks its own
progress, status, retry state, elapsed time, and cancellation state.

Phase 9: added retry logic, elapsed time tracking, concurrency limits,
pause/resume, and queue position tracking.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

if TYPE_CHECKING:
    from .async_handler import AsyncHandler

__all__ = ["DownloadManager", "TaskInfo", "TaskStatus"]


class TaskStatus(Enum):
    QUEUED = auto()
    RUNNING = auto()
    DONE = auto()
    ERROR = auto()
    CANCELLED = auto()
    RETRYING = auto()


@dataclass
class TaskInfo:
    """Metadata for a single download task."""

    task_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    mode: str = ""          # "account" | "link" | "mix"
    platform: str = ""      # "douyin" | "tiktok"
    label: str = ""         # display name for the progress card
    urls: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.QUEUED
    future: Optional[asyncio.Future] = None
    error_msg: str = ""

    # ── retry fields ──────────────────────────────────────────────────
    attempt: int = 0
    max_retries: int = 3
    retry_delay: float = 2.0  # seconds between retries

    # ── timing fields ─────────────────────────────────────────────────
    started_at: Optional[float] = None   # time.monotonic()
    ended_at: Optional[float] = None

    # ── queue position (set by manager) ───────────────────────────────
    queue_position: int = 0  # 0 = not queued / running

    @property
    def elapsed(self) -> float:
        """Seconds since the task started (or total if finished)."""
        if self.started_at is None:
            return 0.0
        end = self.ended_at if self.ended_at is not None else time.monotonic()
        return end - self.started_at


class DownloadManager:
    """Lightweight task queue that wraps async backend calls.

    Usage from the GUI::

        mgr = DownloadManager(async_handler, on_card_update=...)
        mgr.submit("link", "douyin", urls=["https://..."], label="Link #1")
    """

    def __init__(
        self,
        async_handler: AsyncHandler,
        on_card_update: Optional[Callable[[TaskInfo], None]] = None,
        max_concurrent: int = 3,
    ) -> None:
        self._ah = async_handler
        self._on_card_update = on_card_update
        self._tasks: Dict[str, TaskInfo] = {}
        self._max_concurrent = max(1, max_concurrent)
        self._paused = False

        # Map task_id → coro factory (needed for retries)
        self._factories: Dict[str, Callable] = {}

    # ── public API ----------------------------------------------------------

    @property
    def tasks(self) -> Dict[str, TaskInfo]:
        return dict(self._tasks)

    @property
    def paused(self) -> bool:
        return self._paused

    @property
    def counts(self) -> Dict[str, int]:
        """Return counts of tasks grouped by status."""
        c: Dict[str, int] = {
            "active": 0, "queued": 0, "done": 0, "failed": 0, "cancelled": 0,
        }
        for info in self._tasks.values():
            match info.status:
                case TaskStatus.RUNNING | TaskStatus.RETRYING:
                    c["active"] += 1
                case TaskStatus.QUEUED:
                    c["queued"] += 1
                case TaskStatus.DONE:
                    c["done"] += 1
                case TaskStatus.ERROR:
                    c["failed"] += 1
                case TaskStatus.CANCELLED:
                    c["cancelled"] += 1
        return c

    def submit(
        self,
        mode: str,
        platform: str,
        urls: List[str],
        label: str = "",
        backend_coro_factory: Optional[Callable] = None,
    ) -> TaskInfo:
        """Create and enqueue a download task.

        *backend_coro_factory* is an async callable that produces the
        coroutine to run.  If ``None`` the task is created but not started
        (useful when the backend isn't initialised yet).
        """
        info = TaskInfo(
            mode=mode,
            platform=platform,
            label=label or f"{platform}/{mode}",
            urls=list(urls),
        )
        self._tasks[info.task_id] = info

        if backend_coro_factory is not None:
            self._factories[info.task_id] = backend_coro_factory
            self._try_start_next()
        else:
            # Mark as queued — the GUI will show "Waiting…"
            self._notify(info)

        return info

    def retry(self, task_id: str) -> None:
        """Manually retry a failed task (resets attempt counter)."""
        info = self._tasks.get(task_id)
        if info is None or info.status not in (TaskStatus.ERROR, TaskStatus.CANCELLED):
            return
        info.attempt = 0
        info.error_msg = ""
        info.status = TaskStatus.QUEUED
        info.started_at = None
        info.ended_at = None
        self._notify(info)
        self._try_start_next()

    def cancel(self, task_id: str) -> None:
        info = self._tasks.get(task_id)
        if info and info.future and not info.future.done():
            info.future.cancel()
            info.status = TaskStatus.CANCELLED
            info.ended_at = time.monotonic()
            self._notify(info)
            self._try_start_next()

    def cancel_all(self) -> None:
        for tid in list(self._tasks):
            self.cancel(tid)

    def pause(self) -> None:
        """Pause the queue — running tasks continue, no new ones start."""
        self._paused = True

    def resume(self) -> None:
        """Resume the queue — queued tasks start filling empty slots."""
        self._paused = False
        self._try_start_next()

    def clear_done(self) -> List[str]:
        """Remove all finished / errored / cancelled tasks. Returns removed IDs."""
        terminal = {TaskStatus.DONE, TaskStatus.ERROR, TaskStatus.CANCELLED}
        to_remove = [
            tid for tid, info in self._tasks.items()
            if info.status in terminal
        ]
        for tid in to_remove:
            del self._tasks[tid]
            self._factories.pop(tid, None)
        self._update_queue_positions()
        return to_remove

    # ── internal ------------------------------------------------------------

    def _active_count(self) -> int:
        return sum(
            1 for info in self._tasks.values()
            if info.status in (TaskStatus.RUNNING, TaskStatus.RETRYING)
        )

    def _try_start_next(self) -> None:
        """Start queued tasks if there are free concurrency slots."""
        if self._paused:
            self._update_queue_positions()
            return

        while self._active_count() < self._max_concurrent:
            # Find next QUEUED task (insertion order)
            nxt = next(
                (info for info in self._tasks.values()
                 if info.status == TaskStatus.QUEUED
                 and info.task_id in self._factories),
                None,
            )
            if nxt is None:
                break
            self._start(nxt, self._factories[nxt.task_id])

        self._update_queue_positions()

    def _update_queue_positions(self) -> None:
        """Recalculate queue_position for all QUEUED tasks."""
        pos = 1
        for info in self._tasks.values():
            if info.status == TaskStatus.QUEUED:
                info.queue_position = pos
                pos += 1
            else:
                info.queue_position = 0

    def _start(self, info: TaskInfo, coro_factory: Callable) -> None:
        info.attempt += 1
        info.status = TaskStatus.RUNNING
        info.started_at = time.monotonic()
        info.ended_at = None
        info.queue_position = 0
        self._notify(info)

        coro = coro_factory(info.urls)

        def _on_done(_result: Any) -> None:
            info.status = TaskStatus.DONE
            info.ended_at = time.monotonic()
            self._notify(info)
            self._try_start_next()

        def _on_error(exc: BaseException) -> None:
            if info.attempt < info.max_retries:
                # Auto-retry after delay
                info.status = TaskStatus.RETRYING
                info.error_msg = f"Retry {info.attempt}/{info.max_retries}: {exc}"
                info.ended_at = None
                self._notify(info)
                self._schedule_retry(info, coro_factory)
            else:
                # All retries exhausted
                info.status = TaskStatus.ERROR
                info.error_msg = str(exc)
                info.ended_at = time.monotonic()
                self._notify(info)
                self._try_start_next()

        info.future = self._ah.run_async(coro, on_done=_on_done, on_error=_on_error)

    def _schedule_retry(self, info: TaskInfo, coro_factory: Callable) -> None:
        """Wait *retry_delay* seconds then start the task again."""
        delay_ms = int(info.retry_delay * 1000)

        def _do_retry():
            if info.status != TaskStatus.RETRYING:
                return  # cancelled in the meantime
            self._start(info, coro_factory)

        # Use the Tk root's after() (accessed via _ah._root) to schedule
        # the retry on the main thread
        self._ah._root.after(delay_ms, _do_retry)

    def _notify(self, info: TaskInfo) -> None:
        if self._on_card_update:
            self._on_card_update(info)
