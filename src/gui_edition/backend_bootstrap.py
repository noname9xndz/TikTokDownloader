"""Initialise the TikTokDownloader backend for the Desktop GUI.

This module replicates the init chain of ``TikTokDownloader`` without the
terminal menu.  It opens the SQLite database, loads config/option rows,
creates ``Settings``/``Cookie``/``Parameter``/``DownloadRecorder`` objects
and starts the periodic cookie-refresh thread — exactly as the CLI does.

All heavy work is async and runs on the ``AsyncHandler`` loop so the GUI
thread never blocks.

Usage from ``App.__init__``::

    self.backend = BackendBootstrap(self.console)
    self.async_handler.run_async(
        self.backend.start(),
        on_done=self._on_backend_ready,
        on_error=self._on_backend_error,
    )
"""

from __future__ import annotations

import asyncio
from threading import Event, Thread
from time import sleep
from typing import TYPE_CHECKING, Optional

from src.config import Parameter, Settings
from src.custom import (
    COOKIE_UPDATE_INTERVAL,
    PROJECT_ROOT,
    TEXT_REPLACEMENT,
)
from src.manager import Database, DownloadRecorder
from src.module import Cookie, MigrateFolder
from src.record import BaseLogger, LoggerManager
from src.tools import RenameCompatible
from src.translation import switch_language

if TYPE_CHECKING:
    from .console_adapter import GUIConsole

__all__ = ["BackendBootstrap"]


class BackendBootstrap:
    """Owns every shared backend object the GUI needs."""

    def __init__(self, console: "GUIConsole") -> None:
        self.console = console

        # ── will be populated by start() ──────────────────────────────
        self.database: Optional[Database] = None
        self.settings: Optional[Settings] = None
        self.cookie: Optional[Cookie] = None
        self.parameter: Optional[Parameter] = None
        self.recorder: Optional[DownloadRecorder] = None
        self.logger = None

        self.config: dict = {}   # DB config rows  {NAME: VALUE}
        self.option: dict = {}   # DB option rows   {NAME: VALUE}

        # cookie-refresh thread bookkeeping
        self._event_cookie = Event()
        self._params_task: Optional[Thread] = None

        self._ready = False

    # ── public API ────────────────────────────────────────────────────

    @property
    def is_ready(self) -> bool:
        return self._ready

    async def start(self) -> None:
        """Run the full init chain (call on AsyncHandler loop)."""
        # 1. File-rename migration (sync, lightweight)
        RenameCompatible.migration_file()

        # 2. Open database
        self.database = Database()
        await self.database.__aenter__()

        # 3. Read config + option tables
        raw_config = await self.database.read_config_data()
        raw_option = await self.database.read_option_data()
        self.config = self._format(raw_config)
        self.option = self._format(raw_option)

        # 4. Set UI language
        switch_language(self.option.get("Language", "zh_CN"))

        # 5. Build recorder + logger selector (mirrors check_config)
        self._build_recorder_and_logger()

        # 6. Build Settings / Cookie
        self.settings = Settings(PROJECT_ROOT, self.console)
        self.cookie = Cookie(self.settings, self.console)

        # 7. Build Parameter (mirrors check_settings(restart=False))
        await self._build_parameter(restart=False)

        self._ready = True

    async def shutdown(self) -> None:
        """Tear down backend resources (call before app exit)."""
        self._ready = False
        # Stop cookie-refresh thread
        self._event_cookie.set()
        if self._params_task and self._params_task.is_alive():
            self._params_task.join(timeout=5)
        # Close HTTP clients
        if self.parameter:
            await self.parameter.close_client()
            self._close_folders()
        # Close database connection
        if self.database:
            await self.database.__aexit__(None, None, None)

    async def reload_parameter(self) -> None:
        """Re-create Parameter after settings/cookie change.

        Call after the user edits settings.json or pastes a new cookie.
        """
        await self._build_parameter(restart=True)

    # ── mirrors TikTokDownloader.check_config ─────────────────────────

    def _build_recorder_and_logger(self) -> None:
        self.recorder = DownloadRecorder(
            self.database,
            self.config.get("Record", 1),
            self.console,
        )
        self.logger = {1: LoggerManager, 0: BaseLogger}.get(
            self.config.get("Logger", 0), BaseLogger
        )

    # ── mirrors TikTokDownloader.check_settings ───────────────────────

    async def _build_parameter(self, restart: bool = True) -> None:
        if restart and self.parameter:
            await self.parameter.close_client()

        self.parameter = Parameter(
            self.settings,
            self.cookie,
            logger=self.logger,
            console=self.console,
            **self.settings.read(),
            recorder=self.recorder,
        )
        MigrateFolder(self.parameter).compatible()
        self.parameter.set_headers_cookie()
        self._restart_cycle_task(restart)
        self.parameter.CLEANER.set_rule(TEXT_REPLACEMENT, True)

    # ── cookie refresh thread (mirrors TikTokDownloader) ──────────────

    def _periodic_update_params(self) -> None:
        async def _inner() -> None:
            while not self._event_cookie.is_set():
                await self.parameter.update_params()
                self._event_cookie.wait(COOKIE_UPDATE_INTERVAL)

        asyncio.run(_inner())

    def _restart_cycle_task(self, restart: bool = True) -> None:
        if restart:
            self._event_cookie.set()
            if self._params_task and self._params_task.is_alive():
                while self._params_task.is_alive():
                    sleep(1)
        self._params_task = Thread(
            target=self._periodic_update_params,
            daemon=True,
            name="CookieRefresh",
        )
        self._event_cookie.clear()
        self._params_task.start()

    # ── helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _format(rows: list) -> dict:
        """Convert [{NAME: ..., VALUE: ...}, ...] to {NAME: VALUE, ...}."""
        return {r["NAME"]: r["VALUE"] for r in rows}

    def _close_folders(self) -> None:
        """Remove empty download folders on exit."""
        from src.tools import remove_empty_directories

        if self.parameter and self.parameter.folder_mode:
            remove_empty_directories(self.parameter.ROOT)
            remove_empty_directories(self.parameter.root)
