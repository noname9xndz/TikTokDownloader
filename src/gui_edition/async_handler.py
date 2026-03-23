"""Thread-safe bridge between CustomTkinter (main thread) and async operations.

Runs a dedicated asyncio event loop on a background daemon thread.
GUI code calls `run_async(coro, on_done, on_error)` which schedules the
coroutine, then posts the result back to the Tk main loop via `root.after()`.
"""

from __future__ import annotations

import asyncio
import threading
from typing import Any, Callable, Coroutine, Optional


class AsyncHandler:
    """Bridges CustomTkinter's main thread with an asyncio event loop."""

    def __init__(self, root):
        """
        Args:
            root: The CTk root window (needed for ``root.after()``).
        """
        self._root = root
        self._loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._run_loop,
            daemon=True,
            name="AsyncHandler-loop",
        )
        self._thread.start()

    # ---- internal --------------------------------------------------------

    def _run_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    # ---- public API -------------------------------------------------------

    def run_async(
        self,
        coro: Coroutine,
        on_done: Optional[Callable[[Any], None]] = None,
        on_error: Optional[Callable[[BaseException], None]] = None,
    ) -> asyncio.Future:
        """Schedule *coro* on the background loop.

        When the coroutine completes, *on_done* (or *on_error*) is called
        **on the Tk main thread** via ``root.after()``.
        """
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        future.add_done_callback(
            lambda f: self._dispatch(f, on_done, on_error),
        )
        return future

    def _dispatch(
        self,
        future: asyncio.Future,
        on_done: Optional[Callable],
        on_error: Optional[Callable],
    ) -> None:
        try:
            result = future.result()
            if on_done:
                self._root.after(0, on_done, result)
        except Exception as exc:
            if on_error:
                self._root.after(0, on_error, exc)

    def shutdown(self) -> None:
        """Stop the background event loop (call on window close)."""
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(timeout=5)

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self._loop
