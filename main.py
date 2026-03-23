from asyncio import CancelledError
from asyncio import run
import sys

from src.application import TikTokDownloader


async def main():
    async with TikTokDownloader() as downloader:
        try:
            await downloader.run()
        except (
                KeyboardInterrupt,
                CancelledError,
        ):
            return


if __name__ == "__main__":
    if "--gui" in sys.argv:
        from src.gui_edition.gui_main import launch_gui
        launch_gui()
    else:
        run(main())

