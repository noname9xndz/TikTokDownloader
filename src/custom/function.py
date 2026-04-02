from asyncio import sleep
from random import randint
from typing import TYPE_CHECKING
from src.translation import _

if TYPE_CHECKING:
    from src.tools import ColorfulConsole


async def wait() -> None:
    """
    Set network request interval, only affects data fetching, not file downloads
    """
    # 随机延时
    await sleep(randint(5, 20) * 0.1)
    # 固定延时
    # await sleep(1)
    # 取消延时
    # pass


def failure_handling() -> bool:
    """Whether to continue when batch download mode encounters data fetch failures"""
    # 询问用户
    # return bool(input(_("输入任意字符继续处理账号/合集，直接回车停止处理账号/合集: ")))
    # 继续执行
    return True
    # 结束执行
    # return False


def condition_filter(data: dict) -> bool:
    """
    Custom post filter rules, e.g. filter by likes, type, video resolution, etc.
    Return False to exclude the post, True to include it
    """
    # if data["ratio"] in ("720p", "540p"):
    #     return False  # 过滤低分辨率的视频作品
    return True


async def suspend(count: int, console: "ColorfulConsole") -> None:
    """
    Enable this function for large data collection. It pauses after processing a set amount of data, then resumes
    batches: max items per batch before pausing, e.g. pause after every 10 items
    rest_time: pause duration in seconds, e.g. pause 5 minutes after every 10 items
    Only applies to batch download account/mix modes
    Note: one data item here means one account or one mix, not one data packet
    """
    # 启用该函数
    batches = 10  # adjust as needed
    if not count % batches:
        rest_time = 60 * 5  # adjust as needed
        console.print(
            _(
                "Processed {batches} items consecutively. To avoid rate-limiting or account/IP restrictions,"
                "the program has paused and will resume in {rest_time} seconds!"
            ).format(batches=batches, rest_time=rest_time),
        )
        await sleep(rest_time)
    # 禁用该函数
    # pass


def is_valid_token(token: str) -> bool:
    """Token validation for Web API and Web UI modes"""
    return True
