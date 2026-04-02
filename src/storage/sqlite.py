from pathlib import Path
from re import sub

from aiosqlite import connect
from sqlite3 import OperationalError

from rich.text import Text
from rich import print

from ..custom import ERROR
from ..translation import _
from .sql import BaseSQLLogger

__all__ = ["SQLLogger"]


class SQLLogger(BaseSQLLogger):
    """Save data to SQLite database"""

    def __init__(
        self,
        root: Path,
        db_name: str,
        title_line: tuple,
        title_type: tuple,
        field_keys: tuple,
        old=None,
        name="Download",
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.db = None  # database
        self.cursor = None  # cursor object
        self.name = (old, name)  # table name
        self.file = db_name  # database file name
        self.path = root.joinpath(self.file)
        self.title_line = title_line  # table column names
        self.title_type = title_type  # table data types
        self.field_keys = field_keys

    async def __aenter__(self):
        self.db = await connect(self.path)
        self.cursor = await self.db.cursor()
        await self.update_sheet()
        await self.create()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.db.close()

    async def create(self):
        create_sql = f"""CREATE TABLE IF NOT EXISTS {self.name} ({
            ", ".join([f"{i} {j}" for i, j in zip(self.title_line, self.title_type)])
        });"""
        await self.cursor.execute(create_sql)
        await self.db.commit()

    async def _save(self, data, *args, **kwargs):
        insert_sql = f"""REPLACE INTO {self.name} ({
            ", ".join(self.title_line)
        }) VALUES ({", ".join(["?" for _ in self.title_line])});"""
        await self.cursor.execute(insert_sql, data)
        await self.db.commit()

    async def update_sheet(self):
        old_sheet, new_sheet = self.__clean_sheet_name(self.name)
        mark = new_sheet.split("_", 1)
        if not old_sheet or mark[-1] == old_sheet:
            self.name = new_sheet
            return
        mark[-1] = old_sheet
        old_sheet = "_".join(mark)
        if await self.__check_sheet_exists(old_sheet):
            try:
                await self.cursor.execute(self.UPDATE_SQL.format(old_name=old_sheet, new_name=new_sheet))
            except OperationalError as e:
                print(
                    Text(
                        " ".join(
                            (
                                _(
                                    "Error updating table name. Rename failed, please report to the author!"
                                ),
                                str(e),
                                old_sheet,
                                new_sheet,
                            )
                        ),
                        style=ERROR,
                    )
                )
                self.name = old_sheet
                return
            await self.db.commit()
        self.name = new_sheet

    async def __check_sheet_exists(self, sheet: str) -> bool:
        await self.cursor.execute(self.CHECK_SQL, (sheet,))
        exists = await self.cursor.fetchone()
        return exists[0] > 0

    def __clean_sheet_name(self, name: tuple) -> tuple:
        return self.__clean_characters(name[0]), self.__clean_characters(name[1])

    def __clean_characters(self, text: str | None) -> str | None:
        if isinstance(text, str):
            text = self.SHEET_NAME.sub("_", text)
            text = sub(r"_+", "_", text)
        return text
