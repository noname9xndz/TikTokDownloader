from pathlib import Path
from platform import system
from re import compile
from typing import TYPE_CHECKING

from ..custom import (
    ERROR,
    INFO,
    WARNING,
)

if TYPE_CHECKING:
    from ..tools import ColorfulConsole
    from .database import Database

__all__ = [
    "DownloadRecorder",
]


class __DownloadRecorder:
    encode = "UTF-8-SIG" if system() == "Windows" else "UTF-8"
    works_id = compile(r"\d{19}")

    def __init__(
        self, switch: bool, folder: Path, state: bool, console: "ColorfulConsole"
    ):
        self.switch = switch
        self.state = state
        self.backup = folder.joinpath("IDRecorder_backup.txt")
        self.path = folder.joinpath("IDRecorder.txt")
        self.file = None
        self.console = console
        self.record = self.__get_set()

    def __get_set(self) -> set:
        return self.__read_file() if self.switch else set()

    def __read_file(self):
        if not self.path.is_file():
            blacklist = set()
        else:
            with self.path.open("r", encoding=self.encode) as f:
                blacklist = self.__restore_data({line.strip() for line in f})
        self.file = self.path.open("w", encoding=self.encode)
        return blacklist

    def __save_file(self, file):
        file.write("\n".join(f"{i}" for i in self.record))

    def update_id(self, id_):
        if self.switch:
            self.record.add(id_)

    def __extract_ids(self, ids: str) -> list[str]:
        ids = ids.split()
        result = []
        for i in ids:
            if id_ := self.works_id.search(i):
                result.append(id_.group())
        return result

    def delete_ids(self, ids: str) -> None:
        if ids.upper() == "ALL":
            self.record.clear()
        else:
            ids = self.__extract_ids(ids)
            [self.record.remove(i) for i in ids if i in self.record]

    def backup_file(self):
        if self.file and self.record:
            # print("Backup IDRecorder")  # 调试代码
            with self.backup.open("w", encoding=self.encode) as f:
                self.__save_file(f)

    def close(self):
        if self.file:
            self.__save_file(self.file)
            self.file.close()
            self.file = None
            # print("Close IDRecorder")  # 调试代码

    def __restore_data(self, ids: set) -> set:
        if self.state:
            return ids
        self.console.print(
            f"The program detected an abnormal exit from the last run. Download records may be lost!\nData file path: {
                self.path.resolve()
            }",
            style=ERROR,
        )
        if self.backup.exists():
            if (
                self.console.input(
                    "IDRecorder backup file detected. Restore last backup? (YES/NO): ",
                    style=WARNING,
                ).upper()
                == "YES"
            ):
                self.path.write_text(self.backup.read_text(encoding=self.encode))
                self.console.print(
                    "IDRecorder backup restored. Please restart the program!", style=INFO
                )
                return set(self.backup.read_text(encoding=self.encode).split())
            else:
                self.console.print(
                    "IDRecorder data not restored. Backup will be overwritten after downloading any post!",
                    style=ERROR,
                )
        else:
            self.console.print(
                "No IDRecorder backup file found. Download records cannot be recovered!",
                style=ERROR,
            )
        return set()


class DownloadRecorder:
    detail = compile(r"\d{19}")

    def __init__(self, database: "Database", switch: bool, console: "ColorfulConsole"):
        self.switch = switch
        self.console = console
        self.database = database

    async def has_id(self, id_: str) -> bool:
        return (
            await self.database.has_download_data(id_) if self.switch and id_ else False
        )

    async def update_id(self, id_: str):
        if self.switch and id_:
            await self.database.write_download_data(id_)

    async def delete_id(self, id_: str) -> None:
        if self.switch and id_:
            await self.database.delete_download_data(id_)

    async def delete_ids(self, ids: str) -> None:
        if ids.upper() == "ALL":
            await self.database.delete_all_download_data()
        else:
            ids = self.__extract_ids(ids)
            await self.database.delete_download_data(ids)

    def __extract_ids(self, ids: str) -> list[str]:
        ids = ids.split()
        result = []
        for i in ids:
            if id_ := self.detail.search(i):
                result.append(id_.group())
        return result
