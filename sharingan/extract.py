"""
    Sharingan project
    We will try to find your visible basic footprint from social media as much as possible
"""
import asyncio
from base64 import b64encode
from json import loads
from typing import Generator
from urllib.parse import urljoin

import moment
from box import Box

from models import config, person

# from common import str_to_num


def upload(*args, **kwargs):
    return person(*(yield config(*args, **kwargs)))


def xpath(T, path):
    try:
        target = T.html.xpath(path)
        assert len(target) > 0
        return target
    except:
        return [Box({"text": ""})]


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

        T.name = card(".p-name").text()
        T.avatar = card(".avatar").attr("src")
        T.sign = card(".p-note").text()
        T.location = xpath(T, "//li[@itemprop='homeLocation']")[0].text
        T.website = xpath(T, "//li[@data-test-selector='profile-website-url']")[0].text

        T.extra("status", card("div.ws-normal.user-status-message-wrapper").text())
        T.extra("email", xpath(T, "//li[@itemprop='email']")[0].text)
        T.extra(
            "repo_nums",
            xpath(T, f"//a[@href='/{T.key}?tab=repositories']/span")[0].text,
        )
        T.extra(
            "followers", xpath(T, f"//a[@href='/{T.key}?tab=followers']/span")[0].text
        )
        T.extra(
            "following", xpath(T, f"//a[@href='/{T.key}?tab=following']/span")[0].text
        )
        T.extra("stars", xpath(T, f"//a[@href='/{T.key}?tab=stars']/span")[0].text)
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
                    "star": xpath(T, f'//a[@href="{link}/stargazers"]')[0].text,
                    "fork": xpath(T, f'//a[@href="{link}/network/members"]')[0].text,
                }
                for _ in T.html.pq("div.pinned-item-list-item-content").items()
                if (link := _("div.d-flex>a").attr("href"))
            ],
        )
        yield T

    @staticmethod
    def twitter() -> Generator:
        timestamp_map = {"h": "hour", "m": "minute", "s": "second", "d": "day"}

        T = yield from upload(url="https://mobile.twitter.com/{}", proxy=True,)

        _ = T.html.pq("#container")

        T.name = _("div.fullname").text()
        T.avatar = _("td.avatar>img").attr("src")
        T.location = _("div.location").text()
        T.sign = _("div.bio").text()
        T.website = _("div.url").text()
        T.extra("tweets", _(".profile-stats td:nth-child(1) .statnum").text())
        T.extra("following", _(".profile-stats td:nth-child(2) .statnum").text())
        T.extra("followers", _(".profile-stats td:nth-child(3) .statnum").text())
        T.extra(
            "dynamic",
            [
                {
                    "action": item(".tweet-reply-context").text(),
                    "content": item(".tweet-text").text(),
                    "url": urljoin(str(T.resp.url), item.attr("href")),
                    "datetime": (
                        moment.now().add(
                            **{timestamp_map[end_code]: int(timestamp[:-1])}
                        )
                        if (end_code := timestamp[-1]).isalpha()
                        else moment.date(timestamp)
                    ).format("YYYY-MM-DD HH:mm:ss"),
                }
                for item in _("table.tweet  ").items()
                if (timestamp := item(".timestamp").text())
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


    @staticmethod
    def site_2Dimensions():
        T = yield from upload(url="""https://2Dimensions.com/a/{}""",)
        yield T

    @staticmethod
    def site_3dnews():
        T = yield from upload(
            url="""http://forum.3dnews.ru/member.php?username={}""",
            error_type="text",
            error_msg="""Пользователь не зарегистрирован и не имеет профиля для просмотра.""",
        )
        yield T

    @staticmethod
    def site_4pda():
        T = yield from upload(
            url="""https://4pda.ru/forum/index.php?act=search&source=pst&noform=1&username={}""",
            error_type="text",
            error_msg="""К сожалению, Ваш поиск не дал никаких результатов.""",
        )
        yield T

    @staticmethod
    def site_500px():
        T = yield from upload(
            url="""https://500px.com/{}""",
            error_type="text",
            error_msg="""Oops! This page doesn’t exist.""",
        )
        yield T

    @staticmethod
    def site_7Cups():
        T = yield from upload(url="""https://www.7cups.com/@{}""",)
        yield T

    @staticmethod
    def About_me():
        T = yield from upload(url="""https://about.me/{}""",)
        yield T

    @staticmethod
    def Academia_edu():
        T = yield from upload(url="""https://independent.academia.edu/{}""",)
        yield T

    @staticmethod
    def Alik_cz():
        T = yield from upload(url="""https://www.alik.cz/u/{}""",)
        yield T

    @staticmethod
    def AllTrails():
        T = yield from upload(
            url="""https://www.alltrails.com/members/{}""",
            error_type="text",
            error_msg="""User could not be found.""",
        )
        yield T

    @staticmethod
    def Anobii():
        T = yield from upload(
            url="""https://www.anobii.com/{}/profile""",
            error_type="func",
            error_msg=lambda resp: resp.url == """https://www.anobii.com/""",
        )
        yield T

    @staticmethod
    def Aptoide():
        T = yield from upload(url="""https://{}.en.aptoide.com/""",)
        yield T

    @staticmethod
    def Archive_org():
        T = yield from upload(
            url="""https://archive.org/details/@{}""",
            error_type="text",
            error_msg="""cannot find account""",
        )
        yield T

    @staticmethod
    def Asciinema():
        T = yield from upload(url="""https://asciinema.org/~{}""",)
        yield T

    @staticmethod
    def Ask_Fedora():
        T = yield from upload(url="""https://ask.fedoraproject.org/u/{}""",)
        yield T

    @staticmethod
    def AskFM():
        T = yield from upload(
            url="""https://ask.fm/{}""",
            error_type="text",
            error_msg="""Well, apparently not anymore.""",
        )
        yield T

    @staticmethod
    def Audiojungle():
        T = yield from upload(url="""https://audiojungle.net/user/{}""",)
        yield T

    @staticmethod
    def Avizo():
        T = yield from upload(
            url="""https://www.avizo.cz/{}/""",
            error_type="func",
            error_msg=lambda resp: resp.url == """https://www.avizo.cz/""",
        )
        yield T

    @staticmethod
    def BLIP_fm():
        T = yield from upload(url="""https://blip.fm/{}""",)
        yield T

    @staticmethod
    def BOOTH():
        T = yield from upload(
            url="""https://{}.booth.pm/""",
            error_type="func",
            error_msg=lambda resp: resp.url == """https://booth.pm/""",
        )
        yield T

    @staticmethod
    def Badoo():
        T = yield from upload(url="""https://badoo.com/profile/{}""",)
        yield T

    @staticmethod
    def Bandcamp():
        T = yield from upload(url="""https://www.bandcamp.com/{}""",)
        yield T

    @staticmethod
    def Bazar_cz():
        T = yield from upload(
            url="""https://www.bazar.cz/{}/""",
            error_type="func",
            error_msg=lambda resp: resp.url == """https://www.bazar.cz/""",
        )
        yield T

    @staticmethod
    def Behance():
        T = yield from upload(url="""https://www.behance.net/{}""",)
        yield T

    @staticmethod
    def BitBucket():
        T = yield from upload(url="""https://bitbucket.org/{}/""",)
        yield T

    @staticmethod
    def BitCoinForum():
        T = yield from upload(
            url="""https://bitcoinforum.com/profile/{}""",
            error_type="text",
            error_msg="""The user whose profile you are trying to view does not exist.""",
        )
        yield T

    @staticmethod
    def Blogger():
        T = yield from upload(url="""https://{}.blogspot.com""",)
        yield T

    @staticmethod
    def BodyBuilding():
        T = yield from upload(
            url="""https://bodyspace.bodybuilding.com/{}""",
            error_type="func",
            error_msg=lambda resp: resp.url
            == """https://bodyspace.bodybuilding.com/""",
        )
        yield T

    @staticmethod
    def Bookcrossing():
        T = yield from upload(url="""https://www.bookcrossing.com/mybookshelf/{}/""",)
        yield T

    @staticmethod
    def BuyMeACoffee():
        T = yield from upload(url="""https://buymeacoff.ee/{}""",)
        yield T

    @staticmethod
    def BuzzFeed():
        T = yield from upload(url="""https://buzzfeed.com/{}""",)
        yield T

    @staticmethod
    def CNET():
        T = yield from upload(url="""https://www.cnet.com/profiles/{}/""",)
        yield T

    @staticmethod
    def Carbonmade():
        T = yield from upload(
            url="""https://{}.carbonmade.com""",
            error_type="func",
            error_msg=lambda resp: resp.url == """https://carbonmade.com/""",
        )
        yield T

    @staticmethod
    def Career_habr():
        T = yield from upload(
            url="""https://career.habr.com/{}""",
            error_type="text",
            error_msg="""<h1>Ошибка 404</h1>""",
        )
        yield T

    @staticmethod
    def CashMe():
        T = yield from upload(url="""https://cash.me/${}""",)
        yield T

    @staticmethod
    def Cent():
        T = yield from upload(
            url="""https://beta.cent.co/@{}""",
            error_type="text",
            error_msg="""<title>Cent</title>""",
        )
        yield T

    @staticmethod
    def Championat():
        T = yield from upload(url="""https://www.championat.com/user/{}""",)
        yield T

    @staticmethod
    def Chatujme_cz():
        T = yield from upload(
            url="""https://profil.chatujme.cz/{}""",
            error_type="text",
            error_msg="""Neexistujicí profil""",
        )
        yield T

    @staticmethod
    def Chess():
        T = yield from upload(
            url="""https://www.chess.com/ru/member/{}""",
            error_type="text",
            error_msg="""Missing page... somebody made a wrong move.""",
        )
        yield T

    @staticmethod
    def Cloob():
        T = yield from upload(url="""https://www.cloob.com/name/{}""",)
        yield T

    @staticmethod
    def CloudflareCommunity():
        T = yield from upload(url="""https://community.cloudflare.com/u/{}""",)
        yield T

    @staticmethod
    def Clozemaster():
        T = yield from upload(url="""https://www.clozemaster.com/players/{}""",)
        yield T

    @staticmethod
    def Codecademy():
        T = yield from upload(url="""https://www.codecademy.com/profiles/{}""",)
        yield T

    @staticmethod
    def Codechef():
        T = yield from upload(
            url="""https://www.codechef.com/users/{}""",
            error_type="func",
            error_msg=lambda resp: resp.url == """https://www.codechef.com/""",
        )
        yield T

    @staticmethod
    def Codewars():
        T = yield from upload(url="""https://www.codewars.com/users/{}""",)
        yield T

    @staticmethod
    def Contently():
        T = yield from upload(
            url="""https://{}.contently.com/""",
            error_type="text",
            error_msg="""We can't find that page!""",
        )
        yield T

    @staticmethod
    def Coroflot():
        T = yield from upload(url="""https://www.coroflot.com/{}""",)
        yield T

    @staticmethod
    def Cracked():
        T = yield from upload(
            url="""https://www.cracked.com/members/{}/""",
            error_type="func",
            error_msg=lambda resp: resp.url == """https://www.cracked.com/""",
        )
        yield T

    @staticmethod
    def Crevado():
        T = yield from upload(url="""https://{}.crevado.com""",)
        yield T

    @staticmethod
    def Crunchyroll():
        T = yield from upload(url="""https://www.crunchyroll.com/user/{}""",)
        yield T

    @staticmethod
    def DEV_Community():
        T = yield from upload(url="""https://dev.to/{}""",)
        yield T

    @staticmethod
    def DailyMotion():
        T = yield from upload(url="""https://www.dailymotion.com/{}""",)
        yield T

    @staticmethod
    def Designspiration():
        T = yield from upload(url="""https://www.designspiration.net/{}/""",)
        yield T

    @staticmethod
    def DeviantART():
        T = yield from upload(url="""https://{}.deviantart.com""",)
        yield T

    @staticmethod
    def Discogs():
        T = yield from upload(url="""https://www.discogs.com/user/{}""",)
        yield T

    @staticmethod
    def Discuss_Elastic_co():
        T = yield from upload(url="""https://discuss.elastic.co/u/{}""",)
        yield T

    @staticmethod
    def Disqus():
        T = yield from upload(url="""https://disqus.com/{}""",)
        yield T

    @staticmethod
    def Docker_Hub():
        T = yield from upload(url="""https://hub.docker.com/u/{}/""",)
        yield T

    @staticmethod
    def Dribbble():
        T = yield from upload(
            url="""https://dribbble.com/{}""",
            error_type="text",
            error_msg="""Whoops, that page is gone.""",
        )
        yield T

    @staticmethod
    def Duolingo():
        T = yield from upload(
            url="""https://www.duolingo.com/profile/{}""",
            error_type="text",
            error_msg="""{"users":[]}""",
        )
        yield T

    @staticmethod
    def Ebay():
        T = yield from upload(
            url="""https://www.ebay.com/usr/{}""",
            error_type="text",
            error_msg="""The User ID you entered was not found""",
        )
        yield T

    @staticmethod
    def Ello():
        T = yield from upload(
            url="""https://ello.co/{}""",
            error_type="text",
            error_msg="""We couldn't find the page you're looking for""",
        )
        yield T

    @staticmethod
    def Etsy():
        T = yield from upload(url="""https://www.etsy.com/shop/{}""",)
        yield T

    @staticmethod
    def Euw():
        T = yield from upload(
            url="""https://euw.op.gg/summoner/userName={}""",
            error_type="text",
            error_msg="""This summoner is not registered at OP.GG. Please check spelling.""",
        )
        yield T

    @staticmethod
    def EyeEm():
        T = yield from upload(
            url="""https://www.eyeem.com/u/{}""",
            error_type="func",
            error_msg=lambda resp: resp.url == """https://www.eyeem.com/""",
        )
        yield T

    @staticmethod
    def F3_cool():
        T = yield from upload(url="""https://f3.cool/{}/""",)
        yield T

    @staticmethod
    def Facenama():
        T = yield from upload(
            url="""https://facenama.com/{}""",
            error_type="func",
            error_msg=lambda resp: resp.url == """https://facenama.com/""",
        )
        yield T

    @staticmethod
    def Fandom():
        T = yield from upload(url="""https://www.fandom.com/u/{}""",)
        yield T

    @staticmethod
    def Filmogs():
        T = yield from upload(url="""https://www.filmo.gs/users/{}""",)
        yield T

    @staticmethod
    def Fiverr():
        T = yield from upload(
            url="""https://www.fiverr.com/{}""",
            error_type="func",
            error_msg=lambda resp: resp.url == """https://www.fiverr.com/""",
        )
        yield T

    @staticmethod
    def Flickr():
        T = yield from upload(url="""https://www.flickr.com/people/{}""",)
        yield T

    @staticmethod
    def Flightradar24():
        T = yield from upload(url="""https://my.flightradar24.com/{}""",)
        yield T

    @staticmethod
    def Flipboard():
        T = yield from upload(url="""https://flipboard.com/@{}""",)
        yield T

    @staticmethod
    def Football():
        T = yield from upload(
            url="""https://www.rusfootball.info/user/{}/""",
            error_type="text",
            error_msg="""Пользователь с таким именем не найден""",
        )
        yield T

    @staticmethod
    def FortniteTracker():
        T = yield from upload(url="""https://fortnitetracker.com/profile/all/{}""",)
        yield T

    @staticmethod
    def Freelance_habr():
        T = yield from upload(
            url="""https://freelance.habr.com/freelancers/{}""",
            error_type="text",
            error_msg="""<div class="icon_user_locked"></div>""",
        )
        yield T

    @staticmethod
    def Freelancer_com():
        T = yield from upload(
            url="""https://www.freelancer.com/api/users/0.1/users?usernames%5B%5D={}&compact=true""",
            error_type="text",
            error_msg=""""users":{}""",
        )
        yield T

    @staticmethod
    def Freesound():
        T = yield from upload(url="""https://freesound.org/people/{}/""",)
        yield T

    @staticmethod
    def GDProfiles():
        T = yield from upload(url="""https://gdprofiles.com/{}""",)
        yield T

    @staticmethod
    def Gamespot():
        T = yield from upload(url="""https://www.gamespot.com/profile/{}/""",)
        yield T

    @staticmethod
    def Giphy():
        T = yield from upload(url="""https://giphy.com/{}""",)
        yield T

    @staticmethod
    def GitHub():
        T = yield from upload(url="""https://www.github.com/{}""",)
        yield T

    @staticmethod
    def GitLab():
        T = yield from upload(
            url="""https://gitlab.com/{}""", error_type="text", error_msg="""[]""",
        )
        yield T

    @staticmethod
    def Gitee():
        T = yield from upload(url="""https://gitee.com/{}""",)
        yield T

    @staticmethod
    def GoodReads():
        T = yield from upload(url="""https://www.goodreads.com/{}""",)
        yield T

    @staticmethod
    def Gravatar():
        T = yield from upload(url="""http://en.gravatar.com/{}""",)
        yield T

    @staticmethod
    def Gumroad():
        T = yield from upload(
            url="""https://www.gumroad.com/{}""",
            error_type="text",
            error_msg="""Page not found.""",
        )
        yield T

    @staticmethod
    def GunsAndAmmo():
        T = yield from upload(url="""https://forums.gunsandammo.com/profile/{}""",)
        yield T

    @staticmethod
    def GuruShots():
        T = yield from upload(url="""https://gurushots.com/{}/photos""",)
        yield T

    @staticmethod
    def HackTheBox():
        T = yield from upload(url="""https://forum.hackthebox.eu/profile/{}""",)
        yield T

    @staticmethod
    def HackerNews():
        T = yield from upload(
            url="""https://news.ycombinator.com/user?id={}""",
            error_type="text",
            error_msg="""No such user.""",
        )
        yield T

    @staticmethod
    def HackerOne():
        T = yield from upload(
            url="""https://hackerone.com/{}""",
            error_type="text",
            error_msg="""Page not found""",
        )
        yield T

    @staticmethod
    def HackerRank():
        T = yield from upload(
            url="""https://hackerrank.com/{}""",
            error_type="text",
            error_msg="""Something went wrong""",
        )
        yield T

    @staticmethod
    def House_Mixes_com():
        T = yield from upload(
            url="""https://www.house-mixes.com/profile/{}""",
            error_type="text",
            error_msg="""Profile Not Found""",
        )
        yield T

    @staticmethod
    def Houzz():
        T = yield from upload(
            url="""https://houzz.com/user/{}""",
            error_type="text",
            error_msg="""The page you requested was not found.""",
        )
        yield T

    @staticmethod
    def HubPages():
        T = yield from upload(url="""https://hubpages.com/@{}""",)
        yield T

    @staticmethod
    def Hubski():
        T = yield from upload(
            url="""https://hubski.com/user/{}""",
            error_type="text",
            error_msg="""No such user""",
        )
        yield T

    @staticmethod
    def IFTTT():
        T = yield from upload(
            url="""https://www.ifttt.com/p/{}""",
            error_type="text",
            error_msg="""The requested page or file does not exist""",
        )
        yield T

    @staticmethod
    def ImageShack():
        T = yield from upload(
            url="""https://imageshack.us/user/{}""",
            error_type="func",
            error_msg=lambda resp: resp.url == """https://imageshack.us/""",
        )
        yield T

    @staticmethod
    def ImgUp_cz():
        T = yield from upload(url="""https://imgup.cz/{}""",)
        yield T

    @staticmethod
    def Instagram():
        T = yield from upload(url="""https://www.instagram.com/{}""",)
        yield T

    @staticmethod
    def Instructables():
        T = yield from upload(
            url="""https://www.instructables.com/member/{}""",
            error_type="text",
            error_msg="""404: We're sorry, things break sometimes""",
        )
        yield T

    @staticmethod
    def Issuu():
        T = yield from upload(url="""https://issuu.com/{}""",)
        yield T

    @staticmethod
    def Itch_io():
        T = yield from upload(url="""https://{}.itch.io/""",)
        yield T

    @staticmethod
    def Jimdo():
        T = yield from upload(url="""https://{}.jimdosite.com""",)
        yield T

    @staticmethod
    def Kaggle():
        T = yield from upload(url="""https://www.kaggle.com/{}""",)
        yield T

    @staticmethod
    def Kali_community():
        T = yield from upload(
            url="""https://forums.kali.org/member.php?username={}""",
            error_type="text",
            error_msg="""This user has not registered and therefore does not have a profile to view.""",
        )
        yield T

    @staticmethod
    def KanoWorld():
        T = yield from upload(url="""https://api.kano.me/progress/user/{}""",)
        yield T

    @staticmethod
    def Keybase():
        T = yield from upload(url="""https://keybase.io/{}""",)
        yield T

    @staticmethod
    def Kik():
        T = yield from upload(
            url="""https://ws2.kik.com/user/{}""",
            error_type="text",
            error_msg="""The page you requested was not found""",
        )
        yield T

    @staticmethod
    def Kongregate():
        T = yield from upload(
            url="""https://www.kongregate.com/accounts/{}""",
            error_type="text",
            error_msg="""Sorry, no account with that name was found.""",
        )
        yield T

    @staticmethod
    def LOR():
        T = yield from upload(url="""https://www.linux.org.ru/people/{}/profile""",)
        yield T

    @staticmethod
    def Launchpad():
        T = yield from upload(url="""https://launchpad.net/~{}""",)
        yield T

    @staticmethod
    def LeetCode():
        T = yield from upload(url="""https://leetcode.com/{}""",)
        yield T

    @staticmethod
    def Letterboxd():
        T = yield from upload(
            url="""https://letterboxd.com/{}""",
            error_type="text",
            error_msg="""Sorry, we can’t find the page you’ve requested.""",
        )
        yield T

    @staticmethod
    def Lichess():
        T = yield from upload(
            url="""https://lichess.org/@/{}""",
            error_type="text",
            error_msg="""Page not found!""",
        )
        yield T

    @staticmethod
    def LiveJournal():
        T = yield from upload(url="""https://{}.livejournal.com""",)
        yield T

    @staticmethod
    def LiveLeak():
        T = yield from upload(
            url="""https://www.liveleak.com/c/{}""",
            error_type="text",
            error_msg="""channel not found""",
        )
        yield T

    @staticmethod
    def Lobsters():
        T = yield from upload(url="""https://lobste.rs/u/{}""",)
        yield T

    @staticmethod
    def Lolchess():
        T = yield from upload(
            url="""https://lolchess.gg/profile/na/{}""",
            error_type="text",
            error_msg="""No search results""",
        )
        yield T

    @staticmethod
    def Medium():
        T = yield from upload(url="""https://medium.com/@{}""",)
        yield T

    @staticmethod
    def MeetMe():
        T = yield from upload(
            url="""https://www.meetme.com/{}""",
            error_type="func",
            error_msg=lambda resp: resp.url == """https://www.meetme.com/""",
        )
        yield T

    @staticmethod
    def Memrise():
        T = yield from upload(
            url="""https://www.memrise.com/user/{}/""",
            error_type="func",
            error_msg=lambda resp: resp.url == """https://www.memrise.com/""",
        )
        yield T

    @staticmethod
    def MixCloud():
        T = yield from upload(url="""https://www.mixcloud.com/{}/""",)
        yield T

    @staticmethod
    def MyAnimeList():
        T = yield from upload(url="""https://myanimelist.net/profile/{}""",)
        yield T

    @staticmethod
    def Myspace():
        T = yield from upload(url="""https://myspace.com/{}""",)
        yield T

    @staticmethod
    def NICommunityForum():
        T = yield from upload(
            url="""https://www.native-instruments.com/forum/members?username={}""",
            error_type="text",
            error_msg="""The specified member cannot be found""",
        )
        yield T

    @staticmethod
    def NPM():
        T = yield from upload(url="""https://www.npmjs.com/~{}""",)
        yield T

    @staticmethod
    def NPM_Package():
        T = yield from upload(url="""https://www.npmjs.com/package/{}""",)
        yield T

    @staticmethod
    def NameMC__Minecraft_net_skins_():
        T = yield from upload(
            url="""https://namemc.com/profile/{}""",
            error_type="text",
            error_msg="""Profiles: 0 results""",
        )
        yield T

    @staticmethod
    def NationStates_Nation():
        T = yield from upload(
            url="""https://nationstates.net/nation={}""",
            error_type="text",
            error_msg="""Was this your nation? It may have ceased to exist due to inactivity, but can rise again!""",
        )
        yield T

    @staticmethod
    def NationStates_Region():
        T = yield from upload(
            url="""https://nationstates.net/region={}""",
            error_type="text",
            error_msg="""does not exist.""",
        )
        yield T

    @staticmethod
    def Newgrounds():
        T = yield from upload(url="""https://{}.newgrounds.com""",)
        yield T

    @staticmethod
    def OK():
        T = yield from upload(url="""https://ok.ru/{}""",)
        yield T

    @staticmethod
    def OpenCollective():
        T = yield from upload(url="""https://opencollective.com/{}""",)
        yield T

    @staticmethod
    def OpenStreetMap():
        T = yield from upload(url="""https://www.openstreetmap.org/user/{}""",)
        yield T

    @staticmethod
    def Oracle_Community():
        T = yield from upload(url="""https://community.oracle.com/people/{}""",)
        yield T

    @staticmethod
    def Otzovik():
        T = yield from upload(url="""https://otzovik.com/profile/{}""",)
        yield T

    @staticmethod
    def OurDJTalk():
        T = yield from upload(
            url="""https://ourdjtalk.com/members?username={}""",
            error_type="text",
            error_msg="""The specified member cannot be found""",
        )
        yield T

    @staticmethod
    def PCGamer():
        T = yield from upload(
            url="""https://forums.pcgamer.com/members/?username={}""",
            error_type="text",
            error_msg="""The specified member cannot be found. Please enter a member's entire name.""",
        )
        yield T

    @staticmethod
    def PCPartPicker():
        T = yield from upload(url="""https://pcpartpicker.com/user/{}""",)
        yield T

    @staticmethod
    def PSNProfiles_com():
        T = yield from upload(
            url="""https://psnprofiles.com/{}""",
            error_type="func",
            error_msg=lambda resp: resp.url == """https://psnprofiles.com/""",
        )
        yield T

    @staticmethod
    def Packagist():
        T = yield from upload(
            url="""https://packagist.org/packages/{}/""",
            error_type="func",
            error_msg=lambda resp: resp.url == """https://packagist.org/""",
        )
        yield T

    @staticmethod
    def Pastebin():
        T = yield from upload(
            url="""https://pastebin.com/u/{}""",
            error_type="func",
            error_msg=lambda resp: resp.url == """https://pastebin.com/""",
        )
        yield T

    @staticmethod
    def Patreon():
        T = yield from upload(url="""https://www.patreon.com/{}""",)
        yield T

    @staticmethod
    def Periscope():
        T = yield from upload(url="""https://www.periscope.tv/{}/""",)
        yield T

    @staticmethod
    def Photobucket():
        T = yield from upload(url="""https://photobucket.com/user/{}/library""",)
        yield T

    @staticmethod
    def Pinkbike():
        T = yield from upload(url="""https://www.pinkbike.com/u/{}/""",)
        yield T

    @staticmethod
    def Pinterest():
        T = yield from upload(url="""https://www.pinterest.com/{}/""",)
        yield T

    @staticmethod
    def PlayStore():
        T = yield from upload(
            url="""https://play.google.com/store/apps/developer?id={}""",
        )
        yield T

    @staticmethod
    def Pling():
        T = yield from upload(
            url="""https://www.pling.com/u/{}/""",
            error_type="func",
            error_msg=lambda resp: resp.url == """https://www.pling.com/""",
        )
        yield T

    @staticmethod
    def Plug_DJ():
        T = yield from upload(url="""https://plug.dj/@/{}""",)
        yield T

    @staticmethod
    def Pokemon_Showdown():
        T = yield from upload(url="""https://pokemonshowdown.com/users/{}""",)
        yield T

    @staticmethod
    def PokerStrategy():
        T = yield from upload(url="""http://www.pokerstrategy.net/user/{}/profile/""",)
        yield T

    @staticmethod
    def Polygon():
        T = yield from upload(url="""https://www.polygon.com/users/{}""",)
        yield T

    @staticmethod
    def ProductHunt():
        T = yield from upload(
            url="""https://www.producthunt.com/@{}""",
            error_type="text",
            error_msg="""Product Hunt is a curation of the best new products""",
        )
        yield T

    @staticmethod
    def PromoDJ():
        T = yield from upload(url="""http://promodj.com/{}""",)
        yield T

    @staticmethod
    def Quora():
        T = yield from upload(
            url="""https://www.quora.com/profile/{}""",
            error_type="func",
            error_msg=lambda resp: resp.url == """https://www.quora.com/""",
        )
        yield T

    @staticmethod
    def Rajce_net():
        T = yield from upload(url="""https://{}.rajce.idnes.cz/""",)
        yield T

    @staticmethod
    def Rate_Your_Music():
        T = yield from upload(url="""https://rateyourmusic.com/~{}""",)
        yield T

    @staticmethod
    def Realmeye():
        T = yield from upload(
            url="""https://www.realmeye.com/player/{}""",
            error_type="text",
            error_msg="""Sorry, but we either:""",
        )
        yield T

    @staticmethod
    def Redbubble():
        T = yield from upload(url="""https://www.redbubble.com/people/{}""",)
        yield T

    @staticmethod
    def Reddit():
        T = yield from upload(url="""https://www.reddit.com/user/{}""",)
        yield T

    @staticmethod
    def Repl_it():
        T = yield from upload(
            url="""https://repl.it/@{}""", error_type="text", error_msg="""404""",
        )
        yield T

    @staticmethod
    def ResearchGate():
        T = yield from upload(
            url="""https://www.researchgate.net/profile/{}""",
            error_type="func",
            error_msg=lambda resp: resp.url == """https://www.researchgate.net/""",
        )
        yield T

    @staticmethod
    def ReverbNation():
        T = yield from upload(
            url="""https://www.reverbnation.com/{}""",
            error_type="text",
            error_msg="""Sorry, we couldn't find that page""",
        )
        yield T

    @staticmethod
    def Roblox():
        T = yield from upload(
            url="""https://www.roblox.com/user.aspx?username={}""",
            error_type="text",
            error_msg="""Page cannot be found or no longer exists""",
        )
        yield T

    @staticmethod
    def RubyGems():
        T = yield from upload(url="""https://rubygems.org/profiles/{}""",)
        yield T

    @staticmethod
    def Sbazar_cz():
        T = yield from upload(url="""https://www.sbazar.cz/{}""",)
        yield T

    @staticmethod
    def Scratch():
        T = yield from upload(url="""https://scratch.mit.edu/users/{}""",)
        yield T

    @staticmethod
    def Scribd():
        T = yield from upload(
            url="""https://www.scribd.com/{}""",
            error_type="text",
            error_msg="""Page not found""",
        )
        yield T

    @staticmethod
    def ShitpostBot5000():
        T = yield from upload(url="""https://www.shitpostbot.com/user/{}""",)
        yield T

    @staticmethod
    def Signal():
        T = yield from upload(
            url="""https://community.signalusers.org/u/{}""",
            error_type="text",
            error_msg="""Oops! That page doesn’t exist or is private.""",
        )
        yield T

    @staticmethod
    def Slack():
        T = yield from upload(url="""https://{}.slack.com""",)
        yield T

    @staticmethod
    def SlideShare():
        T = yield from upload(url="""https://slideshare.net/{}""",)
        yield T

    @staticmethod
    def Smashcast():
        T = yield from upload(url="""https://www.smashcast.tv/api/media/live/{}""",)
        yield T

    @staticmethod
    def Smule():
        T = yield from upload(url="""https://www.smule.com/{}""",)
        yield T

    @staticmethod
    def SoundCloud():
        T = yield from upload(url="""https://soundcloud.com/{}""",)
        yield T

    @staticmethod
    def SourceForge():
        T = yield from upload(url="""https://sourceforge.net/u/{}""",)
        yield T

    @staticmethod
    def Speedrun_com():
        T = yield from upload(
            url="""https://speedrun.com/user/{}""",
            error_type="text",
            error_msg="""not found.""",
        )
        yield T

    @staticmethod
    def Splits_io():
        T = yield from upload(url="""https://splits.io/users/{}""",)
        yield T

    @staticmethod
    def Sporcle():
        T = yield from upload(url="""https://www.sporcle.com/user/{}/people""",)
        yield T

    @staticmethod
    def SportsRU():
        T = yield from upload(url="""https://www.sports.ru/profile/{}/""",)
        yield T

    @staticmethod
    def Spotify():
        T = yield from upload(url="""https://open.spotify.com/user/{}""",)
        yield T

    @staticmethod
    def Star_Citizen():
        T = yield from upload(url="""https://robertsspaceindustries.com/citizens/{}""",)
        yield T

    @staticmethod
    def Steam():
        T = yield from upload(
            url="""https://steamcommunity.com/id/{}""",
            error_type="text",
            error_msg="""The specified profile could not be found""",
        )
        yield T

    @staticmethod
    def SteamGroup():
        T = yield from upload(
            url="""https://steamcommunity.com/groups/{}""",
            error_type="text",
            error_msg="""No group could be retrieved for the given URL""",
        )
        yield T

    @staticmethod
    def Steamid():
        T = yield from upload(
            url="""https://steamid.uk/profile/{}""",
            error_type="text",
            error_msg="""<div class="alert alert-warning">Profile not found</div>""",
        )
        yield T

    @staticmethod
    def SublimeForum():
        T = yield from upload(url="""https://forum.sublimetext.com/u/{}""",)
        yield T

    @staticmethod
    def T_MobileSupport():
        T = yield from upload(url="""https://support.t-mobile.com/people/{}""",)
        yield T

    @staticmethod
    def Taringa():
        T = yield from upload(url="""https://www.taringa.net/{}""",)
        yield T

    @staticmethod
    def Tellonym_me():
        T = yield from upload(url="""https://tellonym.me/{}""",)
        yield T

    @staticmethod
    def Tinder():
        T = yield from upload(
            url="""https://www.gotinder.com/@{}""",
            error_type="text",
            error_msg="""Looking for Someone?""",
        )
        yield T

    @staticmethod
    def TrackmaniaLadder():
        T = yield from upload(
            url="""http://en.tm-ladder.com/{}_rech.php""",
            error_type="text",
            error_msg="""player unknown or invalid""",
        )
        yield T

    @staticmethod
    def TradingView():
        T = yield from upload(url="""https://www.tradingview.com/u/{}/""",)
        yield T

    @staticmethod
    def Trakt():
        T = yield from upload(url="""https://www.trakt.tv/users/{}""",)
        yield T

    @staticmethod
    def TrashboxRU():
        T = yield from upload(
            url="""https://trashbox.ru/users/{}""",
            error_type="text",
            error_msg="""Пользователь не найден""",
        )
        yield T

    @staticmethod
    def Trello():
        T = yield from upload(
            url="""https://trello.com/{}""",
            error_type="text",
            error_msg="""model not found""",
        )
        yield T

    @staticmethod
    def TripAdvisor():
        T = yield from upload(
            url="""https://tripadvisor.com/members/{}""",
            error_type="text",
            error_msg="""This page is on vacation…""",
        )
        yield T

    @staticmethod
    def Twitch():
        T = yield from upload(url="""https://www.twitch.tv/{}""",)
        yield T


    @staticmethod
    def Typeracer():
        T = yield from upload(
            url="""https://data.typeracer.com/pit/profile?user={}""",
            error_type="text",
            error_msg="""Profile Not Found""",
        )
        yield T

    @staticmethod
    def Ultimate_Guitar():
        T = yield from upload(url="""https://ultimate-guitar.com/u/{}""",)
        yield T

    @staticmethod
    def Unsplash():
        T = yield from upload(url="""https://unsplash.com/@{}""",)
        yield T

    @staticmethod
    def VK():
        T = yield from upload(
            url="""https://vk.com/{}""",
            error_type="func",
            error_msg=lambda resp: resp.url == """https://vk.com/""",
        )
        yield T

    @staticmethod
    def VSCO():
        T = yield from upload(url="""https://vsco.co/{}""",)
        yield T

    @staticmethod
    def Velomania():
        T = yield from upload(
            url="""https://forum.velomania.ru/member.php?username={}""",
            error_type="text",
            error_msg="""Пользователь не зарегистрирован и не имеет профиля для просмотра.""",
        )
        yield T

    @staticmethod
    def Venmo():
        T = yield from upload(url="""https://venmo.com/{}""",)
        yield T

    @staticmethod
    def Viadeo():
        T = yield from upload(url="""http://fr.viadeo.com/en/profile/{}""",)
        yield T

    @staticmethod
    def Vimeo():
        T = yield from upload(url="""https://vimeo.com/{}""",)
        yield T

    @staticmethod
    def Virgool():
        T = yield from upload(
            url="""https://virgool.io/@{}""", error_type="text", error_msg="""۴۰۴""",
        )
        yield T

    @staticmethod
    def VirusTotal():
        T = yield from upload(
            url="""https://www.virustotal.com/ui/users/{}/trusted_users""",
            error_type="text",
            error_msg="""not found""",
        )
        yield T

    @staticmethod
    def Wattpad():
        T = yield from upload(
            url="""https://www.wattpad.com/user/{}""",
            error_type="text",
            error_msg="""userError-404""",
        )
        yield T

    @staticmethod
    def We_Heart_It():
        T = yield from upload(
            url="""https://weheartit.com/{}""",
            error_type="text",
            error_msg="""Oops! You've landed on a moving target!""",
        )
        yield T

    @staticmethod
    def WebNode():
        T = yield from upload(url="""https://{}.webnode.cz/""",)
        yield T

    @staticmethod
    def Whonix_Forum():
        T = yield from upload(url="""https://forums.whonix.org/u/{}""",)
        yield T

    @staticmethod
    def Wikidot():
        T = yield from upload(
            url="""http://www.wikidot.com/user:info/{}""",
            error_type="text",
            error_msg="""User does not exist.""",
        )
        yield T

    @staticmethod
    def Wikipedia():
        T = yield from upload(
            url="""https://www.wikipedia.org/wiki/User:{}""",
            error_type="text",
            error_msg="""is not registered.""",
        )
        yield T

    @staticmethod
    def Wix():
        T = yield from upload(url="""https://{}.wix.com""",)
        yield T

    @staticmethod
    def WordPress():
        T = yield from upload(
            url="""https://{}.wordpress.com/""",
            error_type="func",
            error_msg=lambda resp: resp.url == """https://wordpress.com""",
        )
        yield T

    @staticmethod
    def WordPressOrg():
        T = yield from upload(
            url="""https://profiles.wordpress.org/{}/""",
            error_type="func",
            error_msg=lambda resp: resp.url == """https://wordpress.org/""",
        )
        yield T

    @staticmethod
    def YandexCollection():
        T = yield from upload(url="""https://yandex.ru/collections/user/{}/""",)
        yield T

    @staticmethod
    def YouNow():
        T = yield from upload(
            url="""https://www.younow.com/{}/""",
            error_type="text",
            error_msg="""No users found""",
        )
        yield T

    @staticmethod
    def YouPic():
        T = yield from upload(url="""https://youpic.com/photographer/{}/""",)
        yield T


    @staticmethod
    def Zomato():
        T = yield from upload(url="""https://www.zomato.com/pl/{}/foodjourney""",)
        yield T

    @staticmethod
    def akniga():
        T = yield from upload(url="""https://akniga.org/profile/{}""",)
        yield T

    @staticmethod
    def allmylinks():
        T = yield from upload(
            url="""https://allmylinks.com/{}""",
            error_type="text",
            error_msg="""Page not found""",
        )
        yield T

    @staticmethod
    def authorSTREAM():
        T = yield from upload(url="""http://www.authorstream.com/{}/""",)
        yield T

    @staticmethod
    def babyRU():
        T = yield from upload(
            url="""https://www.baby.ru/u/{}/""",
            error_type="text",
            error_msg="""Упс, страница, которую вы искали, не существует""",
        )
        yield T

    @staticmethod
    def babyblogRU():
        T = yield from upload(url="""https://www.babyblog.ru/user/info/{}""",)
        yield T

    @staticmethod
    def chaos_social():
        T = yield from upload(url="""https://chaos.social/@{}""",)
        yield T

    @staticmethod
    def couchsurfing():
        T = yield from upload(url="""https://www.couchsurfing.com/people/{}""",)
        yield T

    @staticmethod
    def d3RU():
        T = yield from upload(url="""https://d3.ru/user/{}/posts""",)
        yield T

    @staticmethod
    def dailykos():
        T = yield from upload(url="""https://www.dailykos.com/user/{}""",)
        yield T

    @staticmethod
    def datingRU():
        T = yield from upload(url="""http://dating.ru/{}""",)
        yield T

    @staticmethod
    def devRant():
        T = yield from upload(
            url="""https://devrant.com/users/{}""",
            error_type="func",
            error_msg=lambda resp: resp.url == """https://devrant.com/""",
        )
        yield T

    @staticmethod
    def drive2():
        T = yield from upload(url="""https://www.drive2.ru/users/{}""",)
        yield T

    @staticmethod
    def eGPU():
        T = yield from upload(url="""https://egpu.io/forums/profile/{}/""",)
        yield T

    @staticmethod
    def eintracht():
        T = yield from upload(url="""https://community.eintracht.de/fans/{}""",)
        yield T

    @staticmethod
    def fixya():
        T = yield from upload(url="""https://www.fixya.com/users/{}""",)
        yield T

    @staticmethod
    def fl():
        T = yield from upload(url="""https://www.fl.ru/users/{}""",)
        yield T

    @staticmethod
    def forum_guns():
        T = yield from upload(
            url="""https://forum.guns.ru/forummisc/blog/{}""",
            error_type="text",
            error_msg="""action=https://forum.guns.ru/forummisc/blog/search""",
        )
        yield T

    @staticmethod
    def forumhouseRU():
        T = yield from upload(
            url="""https://www.forumhouse.ru/members/?username={}""",
            error_type="text",
            error_msg="""Указанный пользователь не найден. Пожалуйста, введите другое имя.""",
        )
        yield T

    @staticmethod
    def geocaching():
        T = yield from upload(url="""https://www.geocaching.com/profile/?u={}""",)
        yield T

    @staticmethod
    def gfycat():
        T = yield from upload(url="""https://gfycat.com/@{}""",)
        yield T

    @staticmethod
    def habr():
        T = yield from upload(url="""https://habr.com/ru/users/{}""",)
        yield T

    @staticmethod
    def hackster():
        T = yield from upload(url="""https://www.hackster.io/{}""",)
        yield T

    @staticmethod
    def hunting():
        T = yield from upload(
            url="""https://www.hunting.ru/forum/members/?username={}""",
            error_type="text",
            error_msg="""Указанный пользователь не найден. Пожалуйста, введите другое имя.""",
        )
        yield T

    @staticmethod
    def iMGSRC_RU():
        T = yield from upload(
            url="""https://imgsrc.ru/main/user.php?user={}""",
            error_type="func",
            error_msg=lambda resp: resp.url == """https://imgsrc.ru/""",
        )
        yield T

    @staticmethod
    def igromania():
        T = yield from upload(
            url="""http://forum.igromania.ru/member.php?username={}""",
            error_type="text",
            error_msg="""Пользователь не зарегистрирован и не имеет профиля для просмотра.""",
        )
        yield T

    @staticmethod
    def interpals():
        T = yield from upload(
            url="""https://www.interpals.net/{}""",
            error_type="text",
            error_msg="""The requested user does not exist or is inactive""",
        )
        yield T

    @staticmethod
    def irecommend():
        T = yield from upload(url="""https://irecommend.ru/users/{}""",)
        yield T

    @staticmethod
    def jeuxvideo():
        T = yield from upload(
            url="""http://www.jeuxvideo.com/profil/{}?mode=infos""",
            error_type="text",
            error_msg="""Vous êtes""",
        )
        yield T

    @staticmethod
    def kwork():
        T = yield from upload(url="""https://kwork.ru/user/{}""",)
        yield T

    @staticmethod
    def labpentestit():
        T = yield from upload(
            url="""https://lab.pentestit.ru/profile/{}""",
            error_type="func",
            error_msg=lambda resp: resp.url == """https://lab.pentestit.ru/""",
        )
        yield T

    @staticmethod
    def last_fm():
        T = yield from upload(url="""https://last.fm/user/{}""",)
        yield T

    @staticmethod
    def leasehackr():
        T = yield from upload(url="""https://forum.leasehackr.com/u/{}/summary/""",)
        yield T

    @staticmethod
    def livelib():
        T = yield from upload(url="""https://www.livelib.ru/reader/{}""",)
        yield T

    @staticmethod
    def mastodon_cloud():
        T = yield from upload(url="""https://mastodon.cloud/@{}""",)
        yield T

    @staticmethod
    def mastodon_social():
        T = yield from upload(url="""https://mastodon.social/@{}""",)
        yield T

    @staticmethod
    def mastodon_technology():
        T = yield from upload(url="""https://mastodon.technology/@{}""",)
        yield T

    @staticmethod
    def mastodon_xyz():
        T = yield from upload(url="""https://mastodon.xyz/@{}""",)
        yield T

    @staticmethod
    def metacritic():
        T = yield from upload(
            url="""https://www.metacritic.com/user/{}""",
            error_type="text",
            error_msg="""User not found""",
        )
        yield T

    @staticmethod
    def mixer_com():
        T = yield from upload(url="""https://mixer.com/{}""",)
        yield T

    @staticmethod
    def moikrug():
        T = yield from upload(url="""https://moikrug.ru/{}""",)
        yield T

    @staticmethod
    def mstdn_io():
        T = yield from upload(url="""https://mstdn.io/@{}""",)
        yield T

    @staticmethod
    def nightbot():
        T = yield from upload(url="""https://nightbot.tv/t/{}/commands""",)
        yield T

    @staticmethod
    def nnRU():
        T = yield from upload(url="""https://{}.www.nn.ru/""",)
        yield T

    @staticmethod
    def notabug_org():
        T = yield from upload(url="""https://notabug.org/{}""",)
        yield T

    @staticmethod
    def note():
        T = yield from upload(url="""https://note.com/{}""",)
        yield T

    @staticmethod
    def opennet():
        T = yield from upload(
            url="""https://www.opennet.ru/~{}""",
            error_type="text",
            error_msg="""Имя участника не найдено""",
        )
        yield T

    @staticmethod
    def opensource():
        T = yield from upload(url="""https://opensource.com/users/{}""",)
        yield T

    @staticmethod
    def osu_():
        T = yield from upload(url="""https://osu.ppy.sh/users/{}""",)
        yield T

    @staticmethod
    def phpRU():
        T = yield from upload(
            url="""https://php.ru/forum/members/?username={}""",
            error_type="text",
            error_msg="""Указанный пользователь не найден. Пожалуйста, введите другое имя.""",
        )
        yield T

    @staticmethod
    def pikabu():
        T = yield from upload(url="""https://pikabu.ru/@{}""",)
        yield T

    @staticmethod
    def pr0gramm():
        T = yield from upload(url="""https://pr0gramm.com/api/profile/info?name={}""",)
        yield T

    @staticmethod
    def radio_echo_msk():
        T = yield from upload(url="""https://echo.msk.ru/users/{}""",)
        yield T

    @staticmethod
    def satsisRU():
        T = yield from upload(url="""https://satsis.info/user/{}""",)
        yield T

    @staticmethod
    def segmentfault():
        T = yield from upload(url="""https://segmentfault.com/u/{}""",)
        yield T

    @staticmethod
    def social_tchncs_de():
        T = yield from upload(url="""https://social.tchncs.de/@{}""",)
        yield T

    @staticmethod
    def soylentnews():
        T = yield from upload(
            url="""https://soylentnews.org/~{}""",
            error_type="text",
            error_msg="""The user you requested does not exist, no matter how much you wish this might be the case.""",
        )
        yield T

    @staticmethod
    def sparkpeople():
        T = yield from upload(
            url="""https://www.sparkpeople.com/mypage.asp?id={}""",
            error_type="text",
            error_msg="""We couldn't find that user""",
        )
        yield T

    @staticmethod
    def spletnik():
        T = yield from upload(url="""https://spletnik.ru/user/{}""",)
        yield T

    @staticmethod
    def svidbook():
        T = yield from upload(url="""https://www.svidbook.ru/user/{}""",)
        yield T

    @staticmethod
    def toster():
        T = yield from upload(url="""https://www.toster.ru/user/{}/answers""",)
        yield T

    @staticmethod
    def tracr_co():
        T = yield from upload(
            url="""https://tracr.co/users/1/{}""",
            error_type="text",
            error_msg="""No search results""",
        )
        yield T

    @staticmethod
    def travellerspoint():
        T = yield from upload(
            url="""https://www.travellerspoint.com/users/{}""",
            error_type="text",
            error_msg="""Wooops. Sorry!""",
        )
        yield T

    @staticmethod
    def uid():
        T = yield from upload(url="""http://uid.me/{}""",)
        yield T

    @staticmethod
    def warriorforum():
        T = yield from upload(url="""https://www.warriorforum.com/members/{}.html""",)
        yield T

    @staticmethod
    def windy():
        T = yield from upload(url="""https://community.windy.com/user/{}""",)
        yield T

    @staticmethod
    def mercadolivre():
        T = yield from upload(url="""https://www.mercadolivre.com.br/perfil/{}""",)
        yield T

    @staticmethod
    def kofi():
        T = yield from upload(
            url="""https://ko-fi.com/{}""",
            error_type="func",
            error_msg=lambda resp: resp.url == """https://ko-fi.com""",
        )
        yield T

    @staticmethod
    def aminoapp():
        T = yield from upload(url="""https://aminoapps.com/u/{}""",)
        yield T
