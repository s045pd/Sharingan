import asyncio
from base64 import b64encode
from json import loads
from typing import Generator

from box import Box

from models import config, person


def upload(*args, **kwargs):
    return person(*(yield config(*args, **kwargs)))


class Extractor:
    @staticmethod
    def __example() -> Generator:
        """
            fs0c131y
            1. <-- yield your config first
            2. --> then got your datas back 
            3. <-- finally, yield the extracted data back
        """
        T = yield from upload(
            {"url": "http://xxxx", "proxy": True or False, "skip": {}}
        )
        breakpoint()
        yield T

    @staticmethod
    def __zhihu() -> Generator:
        T = yield from upload(
            **{
                "url": "https://www.zhihu.com/people/{}",
                "error_type": "text",
                "error_msg": "你似乎来到了没有知识存在的荒原",
            }
        )
        _ = T.html.pq("div.ProfileHeader-main")

        T.name = _("span.ProfileHeader-name").text()
        T.avatar = _("img.Avatar").attr("src")
        T.sign = _("span.ztext").text()
        T.extra = [
            text
            for item in _(".ProfileHeader-info div.ProfileHeader-infoItem").items()
            if (text := item.text())
        ]
        yield T

    @staticmethod
    def __v2ex() -> Generator:
        T = yield from upload({"url": "https://www.v2ex.com/member/{}"})

    @staticmethod
    def __facebook() -> Generator:
        T = yield from upload(**{"url": "https://www.facebook.com/{}", "proxy": True})
        _ = T.html.pq("#pagelet_timeline_main_column")

        T.name = _("#fb-timeline-cover-name").text()
        T.avatar = _(".photoContainer img:nth-child(1)").attr("src")
        T.sign = _("#intro_container_id").text()
        T.extra = loads(T.html.xpath('//script[@type="application/ld+json"]')[0].text)
        T.extra2 = [item.text() for item in _(".uiList > li ")]
        yield T

    @staticmethod
    def youtube() -> Generator:
        T = yield from upload(
            **{"url": "https://www.youtube.com/{}/about", "proxy": True}
        )

        header = T.html.pq("#channel-header")
        contents = T.html.pq("#contents")

        T.name = header("#text-container").text()
        T.avatar = header("img.yt-img-shadow").attr("src")
        T.sign = contents("#description").text()

        breakpoint()

    # @staticmethod
    # def __twitter():
    #     pass
