"""Download task manager — bridges the GUI with backend async operations.

Manages a queue of download tasks, creates ProgressCard widgets, and
runs backend functions via AsyncHandler.  Each task tracks its own
progress, status, and cancellation state.
"""

from __future__ import annotations

import asyncio
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
    ) -> None:
        self._ah = async_handler
        self._on_card_update = on_card_update
        self._tasks: Dict[str, TaskInfo] = {}

    # ── public API ----------------------------------------------------------

    @property
    def tasks(self) -> Dict[str, TaskInfo]:
        return dict(self._tasks)

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
            self._start(info, backend_coro_factory)
        else:
            # Mark as queued — the GUI will show "Waiting…"
            self._notify(info)

        return info

    def cancel(self, task_id: str) -> None:
        info = self._tasks.get(task_id)
        if info and info.future and not info.future.done():
            info.future.cancel()
            info.status = TaskStatus.CANCELLED
            self._notify(info)

    def cancel_all(self) -> None:
        for tid in list(self._tasks):
            self.cancel(tid)

    # ── internal ------------------------------------------------------------

    def _start(self, info: TaskInfo, coro_factory: Callable) -> None:
        info.status = TaskStatus.RUNNING
        self._notify(info)

        coro = coro_factory(info.urls)

        def _on_done(_result: Any) -> None:
            info.status = TaskStatus.DONE
            self._notify(info)

        def _on_error(exc: BaseException) -> None:
            info.status = TaskStatus.ERROR
            info.error_msg = str(exc)
            self._notify(info)

        info.future = self._ah.run_async(coro, on_done=_on_done, on_error=_on_error)

    def _notify(self, info: TaskInfo) -> None:
        if self._on_card_update:
            self._on_card_update(info)
