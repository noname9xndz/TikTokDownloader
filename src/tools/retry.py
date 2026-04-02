from ..custom import RETRY, wait
from ..translation import _

__all__ = ["Retry"]


class Retry:
    """Retry handler for this project"""

    @staticmethod
    def retry(function):
        """Retry on error, decorated function must return a boolean"""

        async def inner(self, *args, **kwargs):
            finished = kwargs.pop("finished", False)
            for i in range(self.max_retry):
                if result := await function(self, *args, **kwargs):
                    return result
                self.log.warning(_("正在进行第 {index} 次重试").format(index=i + 1))
                await wait()
            if not (result := await function(self, *args, **kwargs)) and finished:
                self.finished = True
            return result

        return inner

    @staticmethod
    def retry_lite(function):
        async def inner(*args, **kwargs):
            if r := await function(*args, **kwargs):
                return r
            for _ in range(RETRY):
                if r := await function(*args, **kwargs):
                    return r
                await wait()
            return r

        return inner

    @staticmethod
    def retry_limited(function):
        def inner(self, *args, **kwargs):
            while True:
                if function(self, *args, **kwargs):
                    return
                if self.console.input(
                    _(
                        "To retry, close all windows or programs accessing this object, then press Enter!\n"
                        "To skip, type any character and press Enter!"
                    ),
                ):
                    return

        return inner

    @staticmethod
    def retry_infinite(function):
        def inner(self, *args, **kwargs):
            while True:
                if function(self, *args, **kwargs):
                    return
                self.console.input(
                    _("请关闭所有正在访问该对象的窗口或程序，然后按下回车键继续处理！")
                )

        return inner
