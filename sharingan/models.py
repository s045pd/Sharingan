from httpx import Response
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum, unique

from box import Box


class error_types:
    @staticmethod
    def code(resp: Response, msg: int) -> bool:
        return resp.status_code == int(msg)

    @staticmethod
    def text(resp: Response, msg: str) -> bool:
        return msg in resp.text

    @staticmethod
    def func(resp: Response, msg: object) -> bool:
        return msg(resp)


@dataclass
class config:
    """
        method_1
        error_type = "xxxx"
        error_msg = "xxxx"

        method_2
        error_type = ["xxxxA","xxxxB"]
        error_msg = ["xxxxa","xxxxb"]
    """

    url: str
    method: str = "get"
    data: str = None
    json: str = None
    headers: dict = None
    cookies: dict = None
    proxy: bool = False
    lang: str = "en"
    error_type: str = "func"
    error_msg: str = lambda resp: resp.status_code != 200


@dataclass
class person:
    source: str
    resp: object
    html: object
    conf: dict
    _name: str = ""
    _sign: str = ""
    _avatar: str = ""
    _avatar_b64: str = ""
    _extras: dict = None

    def report(self):
        return {
            "name": self._name,
            "sign": self._sign,
            "avatar": self._avatar_b64,
            "html": self.html.text,
            "headers": dict(self.resp.headers),
        }

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, v: str) -> None:
        self._name = v

    @property
    def sign(self) -> str:
        return self._sign

    @sign.setter
    def sign(self, v: str) -> str:
        if isinstance(v, str):
            self._sign = v

    @property
    def avatar(self) -> str:
        return self._avatar

    @avatar.setter
    def avatar(self, v: str) -> None:
        self._avatar = v

    @property
    def avatar_b64(self) -> str:
        return self._avatar_b64

    @avatar_b64.setter
    def avatar_b64(self, v: str) -> None:
        self._avatar_b64 = v


@unique
class web_images(Enum):
    png = "image/png"
    jpeg = "image/jpeg"
