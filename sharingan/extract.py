"""
    Sharingan project
    We will try to find your visible basic footprint from social media as much as possible
"""
import asyncio
from base64 import b64encode
from json import loads
from typing import Generator
from urllib.parse import urljoin

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
    def zhihu() -> Generator:
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
        T.extra(
            "header",
            [
                text
                for item in _(".ProfileHeader-info div.ProfileHeader-infoItem").items()
                if (text := item.text())
            ],
        )
        yield T

    @staticmethod
    def github() -> Generator:
        T = yield from upload(
            url="https://github.com/{}", error_type="text", error_msg="Not Found",
        )
        card = T.html.pq(".h-card")

        x = lambda item: T.html.xpath(item)

        T.name = card(".p-name").text()
        T.avatar = card(".avatar").attr("src")
        T.sign = card(".p-note").text()
        T.location = x("//li[@itemprop='homeLocation']")[0].text
        T.website = x("//li[@data-test-selector='profile-website-url']")[0].text

        T.extra("status", card("div.ws-normal.user-status-message-wrapper").text())
        T.extra("repo_nums", x(f"//a[@href='/{T.key}?tab=repositories']/span")[0].text)
        T.extra("followers", x(f"//a[@href='/{T.key}?tab=followers']/span")[0].text)
        T.extra("following", x(f"//a[@href='/{T.key}?tab=following']/span")[0].text)
        T.extra("stars", x(f"//a[@href='/{T.key}?tab=stars']/span")[0].text)
        T.extra(
            "timeline",
            {
                _.attr("data-date"): _.attr("data-count")
                for _ in T.html.pq("svg.js-calendar-graph-svg rect").items()
            },
        )
        T.extra(
            "top_repos",
            [
                {
                    "name": _("div.d-flex>a").text(),
                    "url": urljoin(str(T.resp.url), link),
                    "description": _("p.pinned-item-desc").text(),
                    "star": x(f'//a[@href="{link}/stargazers"]')[0].text,
                    "fork": x(f'//a[@href="{link}/network/members"]')[0].text,
                }
                for _ in T.html.pq("div.pinned-item-list-item-content").items()
                if (link := _("div.d-flex>a").attr("href"))
            ],
        )
        yield T

    # @staticmethod
    # def __v2ex() -> Generator:
    #     T = yield from upload({"url": "https://www.v2ex.com/member/{}"})

    # @staticmethod
    # def __facebook() -> Generator:
    #     T = yield from upload(**{"url": "https://www.facebook.com/{}", "proxy": True})
    #     _ = T.html.pq("#pagelet_timeline_main_column")

    #     T.name = _("#fb-timeline-cover-name").text()
    #     T.avatar = _(".photoContainer img:nth-child(1)").attr("src")
    #     T.sign = _("#intro_container_id").text()
    #     T.extra = loads(T.html.xpath('//script[@type="application/ld+json"]')[0].text)
    #     T.extra2 = [item.text() for item in _(".uiList > li ")]
    #     yield T

    # @staticmethod
    # def youtube() -> Generator:
    #     T = yield from upload(
    #         **{"url": "https://www.youtube.com/{}/about", "proxy": True}
    #     )

    #     header = T.html.pq("#channel-header")
    #     contents = T.html.pq("#contents")

    #     T.name = header("#text-container").text()
    #     T.avatar = header("img.yt-img-shadow").attr("src")
    #     T.sign = contents("#description").text()

    #     yield T

    # @staticmethod
    # def __twitter():
    #     pass
