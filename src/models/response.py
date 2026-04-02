from datetime import datetime

from pydantic import BaseModel, computed_field


class DataResponse(BaseModel):
    message: str
    data: dict | list[dict] | None = None
    params: dict | None

    @computed_field
    @property
    def time(self) -> str:
        """Formatted time string"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class UrlResponse(BaseModel):
    message: str
    url: str | None = None
    params: dict | None

    @computed_field
    @property
    def time(self) -> str:
        """Formatted time string"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
