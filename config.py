from nonebot import get_driver
from pydantic import BaseModel


class Config(BaseModel):
    apikey: str


config = Config.parse_obj(get_driver().config)
