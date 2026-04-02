from json import dump, load
from json.decoder import JSONDecodeError
from platform import system
from shutil import move
from types import SimpleNamespace
from typing import TYPE_CHECKING

from ..custom import USERAGENT
from ..translation import _

if TYPE_CHECKING:
    from pathlib import Path

    from ..tools import ColorfulConsole

__all__ = ["Settings"]


class Settings:
    encode = "UTF-8-SIG" if system() == "Windows" else "UTF-8"
    default = {
        "accounts_urls": [
            {
                "mark": "",
                "url": "",
                "tab": "",
                "earliest": "",
                "latest": "",
                "enable": True,
            },
        ],
        "accounts_urls_tiktok": [
            {
                "mark": "",
                "url": "",
                "tab": "",
                "earliest": "",
                "latest": "",
                "enable": True,
            },
        ],
        "mix_urls": [
            {
                "mark": "",
                "url": "",
                "enable": True,
            },
        ],
        "mix_urls_tiktok": [
            {
                "mark": "",
                "url": "",
                "enable": True,
            },
        ],
        "owner_url": {
            "mark": "",
            "url": "",
            "uid": "",
            "sec_uid": "",
            "nickname": "",
        },
        "owner_url_tiktok": None,
        "root": "",
        "folder_name": "Download",
        "name_format": "create_time type nickname desc",
        "desc_length": 64,
        "name_length": 128,
        "date_format": "%Y-%m-%d %H:%M:%S",
        "split": "-",
        "folder_mode": False,
        "music": False,
        "truncate": 50,
        "storage_format": "",
        "cookie": "",
        "cookie_tiktok": "",
        "dynamic_cover": False,
        "static_cover": False,
        "proxy": "",
        "proxy_tiktok": "",
        "twc_tiktok": "",
        "download": True,
        "max_size": 0,
        "chunk": 1024 * 1024 * 2,  # chunk size per server response
        "timeout": 10,
        "max_retry": 5,  # maximum retry count
        "max_pages": 0,
        "run_command": "",
        "ffmpeg": "",
        "live_qualities": "",
        "douyin_platform": True,
        "tiktok_platform": True,
        "browser_info": {
            "User-Agent": USERAGENT,
            "pc_libra_divert": "Windows",
            "browser_language": "zh-CN",
            "browser_platform": "Win32",
            "browser_name": "Chrome",
            "browser_version": "139.0.0.0",
            "engine_name": "Blink",
            "engine_version": "139.0.0.0",
            "os_name": "Windows",
            "os_version": "10",
            "webid": "",
        },
        "browser_info_tiktok": {
            "User-Agent": USERAGENT,
            "app_language": "zh-Hans",
            "browser_language": "zh-CN",
            "browser_name": "Mozilla",
            "browser_platform": "Win32",
            "browser_version": "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "language": "zh-Hans",
            "os": "windows",
            "priority_region": "US",
            "region": "US",
            "tz_name": "Asia/Shanghai",
            "webcast_language": "zh-Hans",
            "device_id": "",
        },
    }  # default config
    rename_params = (
        (
            "default_mode",
            "run_command",
            "",
        ),
        (
            "update_cookie",
            "douyin_platform",
            True,
        ),
        (
            "update_cookie_tiktok",
            "tiktok_platform",
            True,
        ),
        (
            "original_cover",
            "static_cover",
            False,
        ),
    )  # compatible with older config files

    def __init__(self, root: "Path", console: "ColorfulConsole"):
        self.root = root
        self.file = "settings.json"
        self.path = root.joinpath(self.file)  # config file
        self.console = console

    def __create(self) -> dict:
        """Create default configuration file"""
        with self.path.open("w", encoding=self.encode) as f:
            dump(self.default, f, indent=4, ensure_ascii=False)
        self.console.info(
            _(
                "Default configuration file settings.json created successfully!\n"
                "Please refer to the Quick Start section of the project documentation, set Cookie and re-run!\n"
                "It is recommended to modify settings.json according to your needs!\n"
            ),
        )
        return self.default

    def read(self) -> dict:
        """Read config file, create default if not found"""
        self.compatible()
        try:
            if self.path.exists():
                with self.path.open("r", encoding=self.encode) as f:
                    return self.__check(load(f))
            return self.__create()  # must set cookie to function
        except JSONDecodeError:
            self.console.error(
                _("配置文件 settings.json 格式错误，请检查 JSON 格式！"),
            )
            return self.default  # return defaults on read error

    def __check(self, data: dict) -> dict:
        data = self.__compatible_with_old_settings(data)
        update = False
        for i, j in self.default.items():
            if i not in data:
                data[i] = j
                update = True
                self.console.info(
                    _("配置文件 settings.json 缺少参数 {i}，已自动添加该参数！").format(
                        i=i
                    ),
                )
        if update:
            self.update(data)
        return data

    def update(self, settings: dict | SimpleNamespace):
        """Update configuration file"""
        with self.path.open("w", encoding=self.encode) as f:
            dump(
                settings if isinstance(settings, dict) else vars(settings),
                f,
                indent=4,
                ensure_ascii=False,
            )
        self.console.info(
            _("保存配置成功！"),
        )

    def __compatible_with_old_settings(
        self,
        data: dict,
    ) -> dict:
        """Backward-compatible with older config files"""
        for old, new_, default in self.rename_params:
            if old in data:
                self.console.info(
                    _(
                        "Config parameter {old} has been renamed to {new}, please update your configuration file!"
                    ).format(old=old, new=new_),
                )
                data[new_] = data.get(
                    new_,
                    data.get(
                        old,
                        default,
                    ),
                )
        return data

    def compatible(self):
        if (
            old := self.root.parent.joinpath(self.file)
        ).exists() and not self.path.exists():
            move(old, self.path)
