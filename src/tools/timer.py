from time import time

__all__ = ["run_time"]


def run_time(function):
    def inner(self, *args, **kwargs):
        start = time()
        result = function(self, *args, **kwargs)
        print(f"{function.__name__} elapsed: {time() - start}s")
        return result

    return inner
