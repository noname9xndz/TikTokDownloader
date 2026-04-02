from pathlib import Path
from typing import TYPE_CHECKING, Union

from ..tools import Retry

if TYPE_CHECKING:
    from typing import Iterable


def convert_to_string(function):
    async def _convert_to_string(self, data: Union["Iterable", list], *args, **kwargs):
        for index, value in enumerate(data):
            if isinstance(value, (int, float)):  # if value is numeric
                data[index] = str(value)  # convert to string
            elif isinstance(value, list):  # if value is list
                data[index] = " ".join(value)  # join list elements as string
        return await function(self, data, *args, **kwargs)

    return _convert_to_string


class BaseTextLogger:
    def __init__(self, *args, **kwargs):
        self.field_keys = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb): ...

    @convert_to_string
    async def save(self, data: "Iterable", *args, **kwargs):
        # 数据保存方法入口
        return await self._save(data, *args, **kwargs)

    async def _save(self, data: "Iterable", *args, **kwargs): ...

    @classmethod
    def _rename(cls, root: Path, type_: str, old: str, new_: str) -> str:
        mark = new_.split("_", 1)
        if not old or mark[-1] == old:
            return new_
        mark[-1] = old
        old_file = root.joinpath(f"{'_'.join(mark)}.{type_}")
        cls.__rename_file(old_file, root.joinpath(f"{new_}.{type_}"))
        return new_

    @staticmethod
    @Retry.retry_infinite
    def __rename_file(old_file: Path, new_file: Path) -> bool:
        if old_file.exists() and not new_file.exists():
            try:
                old_file.rename(new_file)
                return True
            except PermissionError:
                return False
        return True
