def __getattr__(name: str):
    if name == "App":
        from .app import App
        return App
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["App"]
