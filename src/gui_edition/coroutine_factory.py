"""Coroutine factory — builds async callables for DownloadManager.

Each factory function returns an *async* callable that accepts a list of
URLs (or an empty list for data modes) and runs the corresponding backend
download / collection pipeline through the ``TikTok`` helper class.

The factories close over ``parameter`` and ``database`` from BackendBootstrap
and instantiate a fresh ``TikTok`` object per task so concurrent tasks won't
share mutable state.

Usage from DownloadFrame::

    factory = make_link_factory(backend.parameter, backend.database)
    manager.submit("link", "douyin", urls=urls, backend_coro_factory=factory)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Coroutine, Any, List

from src.application.main_terminal import TikTok

if TYPE_CHECKING:
    from src.config import Parameter
    from src.manager import Database

__all__ = [
    "make_link_factory",
    "make_account_factory",
    "make_mix_factory",
    "make_live_factory",
    "make_comment_factory",
    "make_user_factory",
    "make_collection_factory",
    "make_collects_factory",
    "make_collection_music_factory",
    "make_search_factory",
    "make_hot_factory",
]

# Type alias for clarity
CoroFactory = Callable[[List[str]], Coroutine[Any, Any, None]]


def _new_tiktok(
    parameter: "Parameter",
    database: "Database",
) -> TikTok:
    """Create a fresh TikTok instance configured for GUI (server_mode=True)."""
    return TikTok(parameter, database, server_mode=True)


# ── Link (detail) downloads ───────────────────────────────────────────


def make_link_factory(
    parameter: "Parameter",
    database: "Database",
    tiktok: bool = False,
) -> CoroFactory:
    """Factory for batch link/detail downloads.

    The returned coroutine extracts video/image IDs from *urls*, fetches
    detail data, extracts metadata, and downloads files.
    """

    async def _run(urls: List[str]) -> None:
        t = _new_tiktok(parameter, database)
        link_obj = t.links_tiktok if tiktok else t.links
        root, params, logger = t.record.run(parameter)
        async with logger(root, console=parameter.console, **params) as record:
            for url in urls:
                ids = await link_obj.run(url)
                if not any(ids):
                    parameter.logger.warning(f"{url} — failed to extract IDs")
                    continue
                await t._handle_detail(ids, tiktok, record)

    return _run


# ── Account downloads ─────────────────────────────────────────────────


def make_account_factory(
    parameter: "Parameter",
    database: "Database",
    tiktok: bool = False,
) -> CoroFactory:
    """Factory for account (user profile) downloads.

    Each URL should be an account homepage.  The factory resolves the
    ``sec_user_id`` and downloads all posts.
    """

    async def _run(urls: List[str]) -> None:
        t = _new_tiktok(parameter, database)
        link_obj = t.links_tiktok if tiktok else t.links
        for index, url in enumerate(urls, start=1):
            sec_user_id = await link_obj.run(url, "user")
            if not sec_user_id:
                parameter.logger.warning(f"{url} — failed to resolve sec_user_id")
                continue
            sec_id = sec_user_id[0] if len(sec_user_id) > 0 else ""
            if not sec_id:
                continue
            await t.deal_account_detail(
                index,
                sec_user_id=sec_id,
                tiktok=tiktok,
            )

    return _run


# ── Mix (collection/playlist) downloads ───────────────────────────────


def make_mix_factory(
    parameter: "Parameter",
    database: "Database",
    tiktok: bool = False,
) -> CoroFactory:
    """Factory for mix (合集) downloads."""

    async def _run(urls: List[str]) -> None:
        t = _new_tiktok(parameter, database)
        link_obj = t.links_tiktok if tiktok else t.links
        for url in urls:
            ids = await link_obj.run(url, "mix")
            if not ids:
                parameter.logger.warning(f"{url} — failed to extract mix ID")
                continue
            mix_id = ids[0] if len(ids) > 0 else ""
            if mix_id:
                await t.deal_mix_detail(
                    mix_id,
                    tiktok=tiktok,
                )

    return _run


# ── Live stream ───────────────────────────────────────────────────────


def make_live_factory(
    parameter: "Parameter",
    database: "Database",
    tiktok: bool = False,
) -> CoroFactory:
    """Factory for live stream URL extraction."""

    async def _run(urls: List[str]) -> None:
        t = _new_tiktok(parameter, database)
        for url in urls:
            await t.deal_live_detail(url, tiktok=tiktok)

    return _run


# ── Comment collection ────────────────────────────────────────────────


def make_comment_factory(
    parameter: "Parameter",
    database: "Database",
    tiktok: bool = False,
) -> CoroFactory:
    """Factory for collecting comments from works."""

    async def _run(urls: List[str]) -> None:
        t = _new_tiktok(parameter, database)
        link_obj = t.links_tiktok if tiktok else t.links
        for url in urls:
            ids = await link_obj.run(url)
            if not any(ids):
                parameter.logger.warning(f"{url} — failed to extract work ID")
                continue
            for work_id in ids:
                await t.deal_comment_detail(work_id)

    return _run


# ── User info collection ─────────────────────────────────────────────


def make_user_factory(
    parameter: "Parameter",
    database: "Database",
    tiktok: bool = False,
) -> CoroFactory:
    """Factory for collecting user profile metadata."""

    async def _run(urls: List[str]) -> None:
        t = _new_tiktok(parameter, database)
        link_obj = t.links_tiktok if tiktok else t.links
        root, params, logger_cls = t.record.run(parameter)
        async with logger_cls(root, console=parameter.console, **params) as record:
            for url in urls:
                sec_ids = await link_obj.run(url, "user")
                if not sec_ids:
                    continue
                for sec_id in sec_ids:
                    await t.deal_user_detail(
                        sec_user_id=sec_id,
                        record=record,
                        tiktok=tiktok,
                    )

    return _run


# ── Collection / Collects / Collection Music ──────────────────────────


def make_collection_factory(
    parameter: "Parameter",
    database: "Database",
) -> CoroFactory:
    """Factory for downloading starred/collected works (收藏作品)."""

    async def _run(_urls: List[str]) -> None:
        t = _new_tiktok(parameter, database)
        await t.deal_account_detail(
            0,
            sec_user_id=parameter.sec_user_id or "",
            tab="favorite",
            tiktok=False,
        )

    return _run


def make_collects_factory(
    parameter: "Parameter",
    database: "Database",
) -> CoroFactory:
    """Factory for downloading folder-collected works (收藏夹作品)."""

    async def _run(_urls: List[str]) -> None:
        t = _new_tiktok(parameter, database)
        await t.collection_detail_batch()

    return _run


def make_collection_music_factory(
    parameter: "Parameter",
    database: "Database",
) -> CoroFactory:
    """Factory for downloading collected music (收藏音乐)."""

    async def _run(_urls: List[str]) -> None:
        t = _new_tiktok(parameter, database)
        await t.collection_music_batch()

    return _run


# ── Search ────────────────────────────────────────────────────────────


def make_search_factory(
    parameter: "Parameter",
    database: "Database",
    keyword: str = "",
    channel: int = 0,
    pages: int = 1,
) -> CoroFactory:
    """Factory for search result collection.

    Unlike other factories the returned coroutine ignores the *urls*
    argument and uses the provided *keyword* / *channel* / *pages*.
    """

    async def _run(_urls: List[str]) -> None:
        t = _new_tiktok(parameter, database)
        await t.deal_search_detail(
            keyword=keyword,
            channel=channel,
            pages=pages,
        )

    return _run


# ── Hot trending ──────────────────────────────────────────────────────


def make_hot_factory(
    parameter: "Parameter",
    database: "Database",
) -> CoroFactory:
    """Factory for collecting hot/trending board data."""

    async def _run(_urls: List[str]) -> None:
        t = _new_tiktok(parameter, database)
        await t.deal_hot_detail()

    return _run
