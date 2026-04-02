from platform import system
from re import compile
from string import whitespace

from emoji import replace_emoji

try:
    from ..translation import _
except ImportError:
    _ = lambda x: x

__all__ = ["Cleaner"]


class Cleaner:
    CONTROL_CHARACTERS = compile(r"[\x00-\x1F\x7F]")

    def __init__(self):
        """
        Replace illegal characters in strings, generating platform-specific rules by default
        """
        self.rule = self.default_rule()  # default illegal char rules

    @staticmethod
    def default_rule():
        """Generate default illegal character rules based on OS type"""
        if (s := system()) in ("Windows", "Darwin"):
            rule = {
                "/": "",
                "\\": "",
                "|": "",
                "<": "",
                ">": "",
                '"': "",
                "?": "",
                ":": "",
                "*": "",
                "\x00": "",
            }  # Windows and macOS
        elif s == "Linux":
            rule = {
                "/": "",
                "\x00": "",
            }  # Linux
        else:
            print(_("不受支持的操作系统类型，可能无法正常Remove illegal characters！"))
            rule = {}
        cache = {i: "" for i in whitespace[1:]}  # add whitespace chars
        return rule | cache

    def set_rule(self, rule: dict[str, str], update=False):
        """
        Set illegal character rules

        :param rule: replacement rules dict, keys are illegal chars, values are replacements
        :param update: if True, merge with existing rules; otherwise replace
        """
        self.rule = {**self.rule, **rule} if update else rule

    def filter(self, text: str) -> str:
        """
        Remove illegal characters

        :param text: the string to process
        :return: cleaned string, or None if result is empty
        """
        for i in self.rule:
            text = text.replace(i, self.rule[i])
        return text

    def filter_name(
        self,
        text: str,
        default: str = "",
    ) -> str:
        """Filter illegal characters from folder names"""
        text = text.replace(":", ".")

        text = self.remove_control_characters(text)

        text = self.filter(text)

        text = replace_emoji(text)

        text = self.clear_spaces(text)

        text = text.strip().strip(".")

        return text or default

    @staticmethod
    def clear_spaces(string: str):
        """Collapse consecutive spaces into a single space"""
        return " ".join(string.split())

    @classmethod
    def remove_control_characters(
        cls,
        text,
        replace="",
    ):
        # 使用正则表达式匹配所有控制字符
        return cls.CONTROL_CHARACTERS.sub(
            replace,
            text,
        )


if __name__ == "__main__":
    demo = Cleaner()
    print(demo.rule)
    print(demo.filter_name(""))
    print(demo.remove_control_characters("hello \x08world"))
