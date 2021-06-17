"""
    Sharingan project
    We will try to find your visible basic footprint from social media as much as possible
"""
from dataclasses import dataclass, field
from enum import Enum, unique
from typing import Dict, Set

from httpx import Response


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
    key: str
    source: str
    resp: object
    html: object
    conf: dict
    debug: bool = False
    available: bool = True
    _name: str = ""
    _title: str = ""
    _age: int = 0
    _gender: int = 0
    _sign: str = ""
    _avatar: str = ""
    _avatar_b64: str = ""
    _locations: Set[str] = field(default_factory=set)
    _websites: Set[str] = field(default_factory=set)
    _extras: Dict = field(default_factory=dict)

    def report(self) -> dict:
        """
        format results data ,filter all the empty ket:val
        """
        results = {
            "title": self._title,
            "name": self._name,
            "sign": self._sign,
            "age": self._age,
            "gender": self._gender,
            "avatar": self._avatar_b64,
            "locations": list(self._locations),
            "websites": list(self._websites),
            "extra": self._extras,
        }
        if self.debug:
            results.update({"html": self.html.text, "headers": dict(self.resp.headers)})
        results = dict(filter(lambda _: _[-1], results.items()))
        if results:
            results["url"] = str(self.resp.url)
        return results

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, v: str) -> None:
        self._name = v

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, v: str) -> None:
        self._title = v

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

    @property
    def location(self) -> str:
        return self._locations

    @location.setter
    def location(self, v: str) -> None:
        self._locations.add(v)

    @property
    def website(self) -> str:
        return self._websites

    @website.setter
    def website(self, v: str) -> None:
        self._websites.add(v)

    def extra(self, k, v: dict) -> None:
        self._extras[k] = v


@unique
class web_images(Enum):
    png = "image/png"
    jpeg = "image/jpeg"
