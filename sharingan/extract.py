"""
    Sharingan project
    We will try to find your visible basic footprint from social media as much as possible
"""
from json import loads
from typing import Generator
from urllib.parse import urljoin

import moment
from box import Box

from sharingan.models import config, person


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
        T.title = T.html.pq("title").text()
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

        T.title = T.html.pq("title").text()
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
            url="https://github.com/{}",
            error_type="text",
            error_msg="Not Found",
        )
        card = T.html.pq(".h-card")

        T.title = T.html.pq("title").text()
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

        T = yield from upload(
            url="https://mobile.twitter.com/{}",
            proxy=True,
        )

        _ = T.html.pq("#container")

        T.title = T.html.pq("title").text()
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

    @staticmethod
    def hackone() -> Generator:
        T = yield from upload(url="https://hackerone.com/{}?type=user", proxy=True)
        T.title = T.html.pq("title").text()
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
        T = yield from upload(
            url="""https://2Dimensions.com/a/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def site_3dnews():
        T = yield from upload(
            url="""http://forum.3dnews.ru/member.php?username={}""",
            error_type="text",
            error_msg="""Пользователь не зарегистрирован и не имеет профиля для просмотра.""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def site_4pda():
        T = yield from upload(
            url="""https://4pda.ru/forum/index.php?act=search&source=pst&noform=1&username={}""",
            error_type="text",
            error_msg="""К сожалению, Ваш поиск не дал никаких результатов.""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def site_500px():
        T = yield from upload(
            url="""https://500px.com/{}""",
            error_type="text",
            error_msg="""Oops! This page doesn’t exist.""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def site_7Cups():
        T = yield from upload(
            url="""https://www.7cups.com/@{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def About_me():
        T = yield from upload(
            url="""https://about.me/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Academia_edu():
        T = yield from upload(
            url="""https://independent.academia.edu/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Alik_cz():
        T = yield from upload(
            url="""https://www.alik.cz/u/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def AllTrails():
        T = yield from upload(
            url="""https://www.alltrails.com/members/{}""",
            error_type="text",
            error_msg="""User could not be found.""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Anobii():
        T = yield from upload(
            url="""https://www.anobii.com/{}/profile""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Aptoide():
        T = yield from upload(
            url="""https://{}.en.aptoide.com/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Archive_org():
        T = yield from upload(
            url="""https://archive.org/details/@{}""",
            error_type="text",
            error_msg="""cannot find account""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Asciinema():
        T = yield from upload(
            url="""https://asciinema.org/~{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Ask_Fedora():
        T = yield from upload(
            url="""https://ask.fedoraproject.org/u/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def AskFM():
        T = yield from upload(
            url="""https://ask.fm/{}""",
            error_type="text",
            error_msg="""Well, apparently not anymore.""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Audiojungle():
        T = yield from upload(
            url="""https://audiojungle.net/user/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Avizo():
        T = yield from upload(
            url="""https://www.avizo.cz/{}/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def BLIP_fm():
        T = yield from upload(
            url="""https://blip.fm/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def BOOTH():
        T = yield from upload(
            url="""https://{}.booth.pm/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Badoo():
        T = yield from upload(
            url="""https://badoo.com/profile/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Bandcamp():
        T = yield from upload(
            url="""https://www.bandcamp.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Bazar_cz():
        T = yield from upload(
            url="""https://www.bazar.cz/{}/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Behance():
        T = yield from upload(
            url="""https://www.behance.net/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def BitBucket():
        T = yield from upload(
            url="""https://bitbucket.org/{}/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def BitCoinForum():
        T = yield from upload(
            url="""https://bitcoinforum.com/profile/{}""",
            error_type="text",
            error_msg="""The user whose profile you are trying to view does not exist.""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Blogger():
        T = yield from upload(
            url="""https://{}.blogspot.com""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def BodyBuilding():
        T = yield from upload(
            url="""https://bodyspace.bodybuilding.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Bookcrossing():
        T = yield from upload(
            url="""https://www.bookcrossing.com/mybookshelf/{}/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def BuyMeACoffee():
        T = yield from upload(
            url="""https://buymeacoff.ee/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def BuzzFeed():
        T = yield from upload(
            url="""https://buzzfeed.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def CNET():
        T = yield from upload(
            url="""https://www.cnet.com/profiles/{}/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Carbonmade():
        T = yield from upload(
            url="""https://{}.carbonmade.com""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Career_habr():
        T = yield from upload(
            url="""https://career.habr.com/{}""",
            error_type="text",
            error_msg="""<h1>Ошибка 404</h1>""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def CashMe():
        T = yield from upload(
            url="""https://cash.me/${}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Cent():
        T = yield from upload(
            url="""https://beta.cent.co/@{}""",
            error_type="text",
            error_msg="""<title>Cent</title>""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Championat():
        T = yield from upload(
            url="""https://www.championat.com/user/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Chatujme_cz():
        T = yield from upload(
            url="""https://profil.chatujme.cz/{}""",
            error_type="text",
            error_msg="""Neexistujicí profil""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Chess():
        T = yield from upload(
            url="""https://www.chess.com/ru/member/{}""",
            error_type="text",
            error_msg="""Missing page... somebody made a wrong move.""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Cloob():
        T = yield from upload(
            url="""https://www.cloob.com/name/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def CloudflareCommunity():
        T = yield from upload(
            url="""https://community.cloudflare.com/u/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Clozemaster():
        T = yield from upload(
            url="""https://www.clozemaster.com/players/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Codecademy():
        T = yield from upload(
            url="""https://www.codecademy.com/profiles/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Codechef():
        T = yield from upload(
            url="""https://www.codechef.com/users/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Codewars():
        T = yield from upload(
            url="""https://www.codewars.com/users/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Contently():
        T = yield from upload(
            url="""https://{}.contently.com/""",
            error_type="text",
            error_msg="""We can't find that page!""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Coroflot():
        T = yield from upload(
            url="""https://www.coroflot.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Cracked():
        T = yield from upload(
            url="""https://www.cracked.com/members/{}/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Crevado():
        T = yield from upload(
            url="""https://{}.crevado.com""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Crunchyroll():
        T = yield from upload(
            url="""https://www.crunchyroll.com/user/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def DEV_Community():
        T = yield from upload(
            url="""https://dev.to/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def DailyMotion():
        T = yield from upload(
            url="""https://www.dailymotion.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Designspiration():
        T = yield from upload(
            url="""https://www.designspiration.net/{}/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def DeviantART():
        T = yield from upload(
            url="""https://{}.deviantart.com""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Discogs():
        T = yield from upload(
            url="""https://www.discogs.com/user/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Discuss_Elastic_co():
        T = yield from upload(
            url="""https://discuss.elastic.co/u/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Disqus():
        T = yield from upload(
            url="""https://disqus.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Docker_Hub():
        T = yield from upload(
            url="""https://hub.docker.com/u/{}/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Dribbble():
        T = yield from upload(
            url="""https://dribbble.com/{}""",
            error_type="text",
            error_msg="""Whoops, that page is gone.""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Duolingo():
        T = yield from upload(
            url="""https://www.duolingo.com/profile/{}""",
            error_type="text",
            error_msg="""{"users":[]}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Ebay():
        T = yield from upload(
            url="""https://www.ebay.com/usr/{}""",
            error_type="text",
            error_msg="""The User ID you entered was not found""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Ello():
        T = yield from upload(
            url="""https://ello.co/{}""",
            error_type="text",
            error_msg="""We couldn't find the page you're looking for""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Etsy():
        T = yield from upload(
            url="""https://www.etsy.com/shop/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Euw():
        T = yield from upload(
            url="""https://euw.op.gg/summoner/userName={}""",
            error_type="text",
            error_msg="""This summoner is not registered at OP.GG. Please check spelling.""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def EyeEm():
        T = yield from upload(
            url="""https://www.eyeem.com/u/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def F3_cool():
        T = yield from upload(
            url="""https://f3.cool/{}/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Facebook():
        T = yield from upload(
            url="""https://www.facebook.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Facenama():
        T = yield from upload(
            url="""https://facenama.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Fandom():
        T = yield from upload(
            url="""https://www.fandom.com/u/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Filmogs():
        T = yield from upload(
            url="""https://www.filmo.gs/users/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Fiverr():
        T = yield from upload(
            url="""https://www.fiverr.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Flickr():
        T = yield from upload(
            url="""https://www.flickr.com/people/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Flightradar24():
        T = yield from upload(
            url="""https://my.flightradar24.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Flipboard():
        T = yield from upload(
            url="""https://flipboard.com/@{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Football():
        T = yield from upload(
            url="""https://www.rusfootball.info/user/{}/""",
            error_type="text",
            error_msg="""Пользователь с таким именем не найден""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def FortniteTracker():
        T = yield from upload(
            url="""https://fortnitetracker.com/profile/all/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Freelance_habr():
        T = yield from upload(
            url="""https://freelance.habr.com/freelancers/{}""",
            error_type="text",
            error_msg="""<div class="icon_user_locked"></div>""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Freelancer_com():
        T = yield from upload(
            url="""https://www.freelancer.com/api/users/0.1/users?usernames%5B%5D={}&compact=true""",
            error_type="text",
            error_msg=""""users":{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Freesound():
        T = yield from upload(
            url="""https://freesound.org/people/{}/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def GDProfiles():
        T = yield from upload(
            url="""https://gdprofiles.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Gamespot():
        T = yield from upload(
            url="""https://www.gamespot.com/profile/{}/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Giphy():
        T = yield from upload(
            url="""https://giphy.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def GitHub():
        T = yield from upload(
            url="""https://www.github.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def GitLab():
        T = yield from upload(
            url="""https://gitlab.com/{}""",
            error_type="text",
            error_msg="""[]""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Gitee():
        T = yield from upload(
            url="""https://gitee.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def GoodReads():
        T = yield from upload(
            url="""https://www.goodreads.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Gravatar():
        T = yield from upload(
            url="""http://en.gravatar.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Gumroad():
        T = yield from upload(
            url="""https://www.gumroad.com/{}""",
            error_type="text",
            error_msg="""Page not found.""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def GunsAndAmmo():
        T = yield from upload(
            url="""https://forums.gunsandammo.com/profile/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def GuruShots():
        T = yield from upload(
            url="""https://gurushots.com/{}/photos""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def HackTheBox():
        T = yield from upload(
            url="""https://forum.hackthebox.eu/profile/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def HackerNews():
        T = yield from upload(
            url="""https://news.ycombinator.com/user?id={}""",
            error_type="text",
            error_msg="""No such user.""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def HackerOne():
        T = yield from upload(
            url="""https://hackerone.com/{}""",
            error_type="text",
            error_msg="""Page not found""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def HackerRank():
        T = yield from upload(
            url="""https://hackerrank.com/{}""",
            error_type="text",
            error_msg="""Something went wrong""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def House_Mixes_com():
        T = yield from upload(
            url="""https://www.house-mixes.com/profile/{}""",
            error_type="text",
            error_msg="""Profile Not Found""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Houzz():
        T = yield from upload(
            url="""https://houzz.com/user/{}""",
            error_type="text",
            error_msg="""The page you requested was not found.""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def HubPages():
        T = yield from upload(
            url="""https://hubpages.com/@{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Hubski():
        T = yield from upload(
            url="""https://hubski.com/user/{}""",
            error_type="text",
            error_msg="""No such user""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def IFTTT():
        T = yield from upload(
            url="""https://www.ifttt.com/p/{}""",
            error_type="text",
            error_msg="""The requested page or file does not exist""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def ImageShack():
        T = yield from upload(
            url="""https://imageshack.us/user/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def ImgUp_cz():
        T = yield from upload(
            url="""https://imgup.cz/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Instagram():
        T = yield from upload(
            url="""https://www.instagram.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Instructables():
        T = yield from upload(
            url="""https://www.instructables.com/member/{}""",
            error_type="text",
            error_msg="""404: We're sorry, things break sometimes""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Issuu():
        T = yield from upload(
            url="""https://issuu.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Itch_io():
        T = yield from upload(
            url="""https://{}.itch.io/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Jimdo():
        T = yield from upload(
            url="""https://{}.jimdosite.com""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Kaggle():
        T = yield from upload(
            url="""https://www.kaggle.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Kali_community():
        T = yield from upload(
            url="""https://forums.kali.org/member.php?username={}""",
            error_type="text",
            error_msg="""This user has not registered and therefore does not have a profile to view.""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def KanoWorld():
        T = yield from upload(
            url="""https://api.kano.me/progress/user/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Keybase():
        T = yield from upload(
            url="""https://keybase.io/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Kik():
        T = yield from upload(
            url="""https://ws2.kik.com/user/{}""",
            error_type="text",
            error_msg="""The page you requested was not found""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Kongregate():
        T = yield from upload(
            url="""https://www.kongregate.com/accounts/{}""",
            error_type="text",
            error_msg="""Sorry, no account with that name was found.""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def LOR():
        T = yield from upload(
            url="""https://www.linux.org.ru/people/{}/profile""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Launchpad():
        T = yield from upload(
            url="""https://launchpad.net/~{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def LeetCode():
        T = yield from upload(
            url="""https://leetcode.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Letterboxd():
        T = yield from upload(
            url="""https://letterboxd.com/{}""",
            error_type="text",
            error_msg="""Sorry, we can’t find the page you’ve requested.""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Lichess():
        T = yield from upload(
            url="""https://lichess.org/@/{}""",
            error_type="text",
            error_msg="""Page not found!""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def LiveJournal():
        T = yield from upload(
            url="""https://{}.livejournal.com""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def LiveLeak():
        T = yield from upload(
            url="""https://www.liveleak.com/c/{}""",
            error_type="text",
            error_msg="""channel not found""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Lobsters():
        T = yield from upload(
            url="""https://lobste.rs/u/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Lolchess():
        T = yield from upload(
            url="""https://lolchess.gg/profile/na/{}""",
            error_type="text",
            error_msg="""No search results""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Medium():
        T = yield from upload(
            url="""https://medium.com/@{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def MeetMe():
        T = yield from upload(
            url="""https://www.meetme.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Memrise():
        T = yield from upload(
            url="""https://www.memrise.com/user/{}/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def MixCloud():
        T = yield from upload(
            url="""https://www.mixcloud.com/{}/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def MyAnimeList():
        T = yield from upload(
            url="""https://myanimelist.net/profile/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Myspace():
        T = yield from upload(
            url="""https://myspace.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def NICommunityForum():
        T = yield from upload(
            url="""https://www.native-instruments.com/forum/members?username={}""",
            error_type="text",
            error_msg="""The specified member cannot be found""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def NPM():
        T = yield from upload(
            url="""https://www.npmjs.com/~{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def NPM_Package():
        T = yield from upload(
            url="""https://www.npmjs.com/package/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def NameMC__Minecraft_net_skins_():
        T = yield from upload(
            url="""https://namemc.com/profile/{}""",
            error_type="text",
            error_msg="""Profiles: 0 results""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def NationStates_Nation():
        T = yield from upload(
            url="""https://nationstates.net/nation={}""",
            error_type="text",
            error_msg="""Was this your nation? It may have ceased to exist due to inactivity, but can rise again!""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def NationStates_Region():
        T = yield from upload(
            url="""https://nationstates.net/region={}""",
            error_type="text",
            error_msg="""does not exist.""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Newgrounds():
        T = yield from upload(
            url="""https://{}.newgrounds.com""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def OK():
        T = yield from upload(
            url="""https://ok.ru/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def OpenCollective():
        T = yield from upload(
            url="""https://opencollective.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def OpenStreetMap():
        T = yield from upload(
            url="""https://www.openstreetmap.org/user/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Oracle_Community():
        T = yield from upload(
            url="""https://community.oracle.com/people/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Otzovik():
        T = yield from upload(
            url="""https://otzovik.com/profile/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def OurDJTalk():
        T = yield from upload(
            url="""https://ourdjtalk.com/members?username={}""",
            error_type="text",
            error_msg="""The specified member cannot be found""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def PCGamer():
        T = yield from upload(
            url="""https://forums.pcgamer.com/members/?username={}""",
            error_type="text",
            error_msg="""The specified member cannot be found. Please enter a member's entire name.""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def PCPartPicker():
        T = yield from upload(
            url="""https://pcpartpicker.com/user/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def PSNProfiles_com():
        T = yield from upload(
            url="""https://psnprofiles.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Packagist():
        T = yield from upload(
            url="""https://packagist.org/packages/{}/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Pastebin():
        T = yield from upload(
            url="""https://pastebin.com/u/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Patreon():
        T = yield from upload(
            url="""https://www.patreon.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Periscope():
        T = yield from upload(
            url="""https://www.periscope.tv/{}/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Photobucket():
        T = yield from upload(
            url="""https://photobucket.com/user/{}/library""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Pinkbike():
        T = yield from upload(
            url="""https://www.pinkbike.com/u/{}/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Pinterest():
        T = yield from upload(
            url="""https://www.pinterest.com/{}/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def PlayStore():
        T = yield from upload(
            url="""https://play.google.com/store/apps/developer?id={}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Pling():
        T = yield from upload(
            url="""https://www.pling.com/u/{}/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Plug_DJ():
        T = yield from upload(
            url="""https://plug.dj/@/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Pokemon_Showdown():
        T = yield from upload(
            url="""https://pokemonshowdown.com/users/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def PokerStrategy():
        T = yield from upload(
            url="""http://www.pokerstrategy.net/user/{}/profile/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Polygon():
        T = yield from upload(
            url="""https://www.polygon.com/users/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def ProductHunt():
        T = yield from upload(
            url="""https://www.producthunt.com/@{}""",
            error_type="text",
            error_msg="""Product Hunt is a curation of the best new products""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def PromoDJ():
        T = yield from upload(
            url="""http://promodj.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Quora():
        T = yield from upload(
            url="""https://www.quora.com/profile/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Rajce_net():
        T = yield from upload(
            url="""https://{}.rajce.idnes.cz/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Rate_Your_Music():
        T = yield from upload(
            url="""https://rateyourmusic.com/~{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Realmeye():
        T = yield from upload(
            url="""https://www.realmeye.com/player/{}""",
            error_type="text",
            error_msg="""Sorry, but we either:""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Redbubble():
        T = yield from upload(
            url="""https://www.redbubble.com/people/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Reddit():
        T = yield from upload(
            url="""https://www.reddit.com/user/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Repl_it():
        T = yield from upload(
            url="""https://repl.it/@{}""",
            error_type="text",
            error_msg="""404""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def ResearchGate():
        T = yield from upload(
            url="""https://www.researchgate.net/profile/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def ReverbNation():
        T = yield from upload(
            url="""https://www.reverbnation.com/{}""",
            error_type="text",
            error_msg="""Sorry, we couldn't find that page""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Roblox():
        T = yield from upload(
            url="""https://www.roblox.com/user.aspx?username={}""",
            error_type="text",
            error_msg="""Page cannot be found or no longer exists""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def RubyGems():
        T = yield from upload(
            url="""https://rubygems.org/profiles/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Sbazar_cz():
        T = yield from upload(
            url="""https://www.sbazar.cz/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Scratch():
        T = yield from upload(
            url="""https://scratch.mit.edu/users/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Scribd():
        T = yield from upload(
            url="""https://www.scribd.com/{}""",
            error_type="text",
            error_msg="""Page not found""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def ShitpostBot5000():
        T = yield from upload(
            url="""https://www.shitpostbot.com/user/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Signal():
        T = yield from upload(
            url="""https://community.signalusers.org/u/{}""",
            error_type="text",
            error_msg="""Oops! That page doesn’t exist or is private.""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Slack():
        T = yield from upload(
            url="""https://{}.slack.com""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def SlideShare():
        T = yield from upload(
            url="""https://slideshare.net/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Smashcast():
        T = yield from upload(
            url="""https://www.smashcast.tv/api/media/live/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Smule():
        T = yield from upload(
            url="""https://www.smule.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def SoundCloud():
        T = yield from upload(
            url="""https://soundcloud.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def SourceForge():
        T = yield from upload(
            url="""https://sourceforge.net/u/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Speedrun_com():
        T = yield from upload(
            url="""https://speedrun.com/user/{}""",
            error_type="text",
            error_msg="""not found.""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Splits_io():
        T = yield from upload(
            url="""https://splits.io/users/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Sporcle():
        T = yield from upload(
            url="""https://www.sporcle.com/user/{}/people""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def SportsRU():
        T = yield from upload(
            url="""https://www.sports.ru/profile/{}/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Spotify():
        T = yield from upload(
            url="""https://open.spotify.com/user/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Star_Citizen():
        T = yield from upload(
            url="""https://robertsspaceindustries.com/citizens/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Steam():
        T = yield from upload(
            url="""https://steamcommunity.com/id/{}""",
            error_type="text",
            error_msg="""The specified profile could not be found""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def SteamGroup():
        T = yield from upload(
            url="""https://steamcommunity.com/groups/{}""",
            error_type="text",
            error_msg="""No group could be retrieved for the given URL""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Steamid():
        T = yield from upload(
            url="""https://steamid.uk/profile/{}""",
            error_type="text",
            error_msg="""<div class="alert alert-warning">Profile not found</div>""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def SublimeForum():
        T = yield from upload(
            url="""https://forum.sublimetext.com/u/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def T_MobileSupport():
        T = yield from upload(
            url="""https://support.t-mobile.com/people/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Taringa():
        T = yield from upload(
            url="""https://www.taringa.net/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Tellonym_me():
        T = yield from upload(
            url="""https://tellonym.me/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Tinder():
        T = yield from upload(
            url="""https://www.gotinder.com/@{}""",
            error_type="text",
            error_msg="""Looking for Someone?""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def TrackmaniaLadder():
        T = yield from upload(
            url="""http://en.tm-ladder.com/{}_rech.php""",
            error_type="text",
            error_msg="""player unknown or invalid""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def TradingView():
        T = yield from upload(
            url="""https://www.tradingview.com/u/{}/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Trakt():
        T = yield from upload(
            url="""https://www.trakt.tv/users/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def TrashboxRU():
        T = yield from upload(
            url="""https://trashbox.ru/users/{}""",
            error_type="text",
            error_msg="""Пользователь не найден""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Trello():
        T = yield from upload(
            url="""https://trello.com/{}""",
            error_type="text",
            error_msg="""model not found""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def TripAdvisor():
        T = yield from upload(
            url="""https://tripadvisor.com/members/{}""",
            error_type="text",
            error_msg="""This page is on vacation…""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Twitch():
        T = yield from upload(
            url="""https://www.twitch.tv/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Typeracer():
        T = yield from upload(
            url="""https://data.typeracer.com/pit/profile?user={}""",
            error_type="text",
            error_msg="""Profile Not Found""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Ultimate_Guitar():
        T = yield from upload(
            url="""https://ultimate-guitar.com/u/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Unsplash():
        T = yield from upload(
            url="""https://unsplash.com/@{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def VK():
        T = yield from upload(
            url="""https://vk.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def VSCO():
        T = yield from upload(
            url="""https://vsco.co/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Velomania():
        T = yield from upload(
            url="""https://forum.velomania.ru/member.php?username={}""",
            error_type="text",
            error_msg="""Пользователь не зарегистрирован и не имеет профиля для просмотра.""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Venmo():
        T = yield from upload(
            url="""https://venmo.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Viadeo():
        T = yield from upload(
            url="""http://fr.viadeo.com/en/profile/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Vimeo():
        T = yield from upload(
            url="""https://vimeo.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Virgool():
        T = yield from upload(
            url="""https://virgool.io/@{}""",
            error_type="text",
            error_msg="""۴۰۴""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def VirusTotal():
        T = yield from upload(
            url="""https://www.virustotal.com/ui/users/{}/trusted_users""",
            error_type="text",
            error_msg="""not found""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Wattpad():
        T = yield from upload(
            url="""https://www.wattpad.com/user/{}""",
            error_type="text",
            error_msg="""userError-404""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def We_Heart_It():
        T = yield from upload(
            url="""https://weheartit.com/{}""",
            error_type="text",
            error_msg="""Oops! You've landed on a moving target!""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def WebNode():
        T = yield from upload(
            url="""https://{}.webnode.cz/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Whonix_Forum():
        T = yield from upload(
            url="""https://forums.whonix.org/u/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Wikidot():
        T = yield from upload(
            url="""http://www.wikidot.com/user:info/{}""",
            error_type="text",
            error_msg="""User does not exist.""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Wikipedia():
        T = yield from upload(
            url="""https://www.wikipedia.org/wiki/User:{}""",
            error_type="text",
            error_msg="""is not registered.""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Wix():
        T = yield from upload(
            url="""https://{}.wix.com""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def WordPress():
        T = yield from upload(
            url="""https://{}.wordpress.com/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def WordPressOrg():
        T = yield from upload(
            url="""https://profiles.wordpress.org/{}/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def YandexCollection():
        T = yield from upload(
            url="""https://yandex.ru/collections/user/{}/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def YouNow():
        T = yield from upload(
            url="""https://www.younow.com/{}/""",
            error_type="text",
            error_msg="""No users found""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def YouPic():
        T = yield from upload(
            url="""https://youpic.com/photographer/{}/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def Zomato():
        T = yield from upload(
            url="""https://www.zomato.com/pl/{}/foodjourney""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def akniga():
        T = yield from upload(
            url="""https://akniga.org/profile/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def allmylinks():
        T = yield from upload(
            url="""https://allmylinks.com/{}""",
            error_type="text",
            error_msg="""Page not found""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def authorSTREAM():
        T = yield from upload(
            url="""http://www.authorstream.com/{}/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def babyRU():
        T = yield from upload(
            url="""https://www.baby.ru/u/{}/""",
            error_type="text",
            error_msg="""Упс, страница, которую вы искали, не существует""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def babyblogRU():
        T = yield from upload(
            url="""https://www.babyblog.ru/user/info/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def chaos_social():
        T = yield from upload(
            url="""https://chaos.social/@{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def couchsurfing():
        T = yield from upload(
            url="""https://www.couchsurfing.com/people/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def d3RU():
        T = yield from upload(
            url="""https://d3.ru/user/{}/posts""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def dailykos():
        T = yield from upload(
            url="""https://www.dailykos.com/user/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def datingRU():
        T = yield from upload(
            url="""http://dating.ru/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def devRant():
        T = yield from upload(
            url="""https://devrant.com/users/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def drive2():
        T = yield from upload(
            url="""https://www.drive2.ru/users/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def eGPU():
        T = yield from upload(
            url="""https://egpu.io/forums/profile/{}/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def eintracht():
        T = yield from upload(
            url="""https://community.eintracht.de/fans/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def fixya():
        T = yield from upload(
            url="""https://www.fixya.com/users/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def fl():
        T = yield from upload(
            url="""https://www.fl.ru/users/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def forum_guns():
        T = yield from upload(
            url="""https://forum.guns.ru/forummisc/blog/{}""",
            error_type="text",
            error_msg="""action=https://forum.guns.ru/forummisc/blog/search""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def forumhouseRU():
        T = yield from upload(
            url="""https://www.forumhouse.ru/members/?username={}""",
            error_type="text",
            error_msg="""Указанный пользователь не найден. Пожалуйста, введите другое имя.""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def geocaching():
        T = yield from upload(
            url="""https://www.geocaching.com/profile/?u={}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def gfycat():
        T = yield from upload(
            url="""https://gfycat.com/@{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def habr():
        T = yield from upload(
            url="""https://habr.com/ru/users/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def hackster():
        T = yield from upload(
            url="""https://www.hackster.io/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def hunting():
        T = yield from upload(
            url="""https://www.hunting.ru/forum/members/?username={}""",
            error_type="text",
            error_msg="""Указанный пользователь не найден. Пожалуйста, введите другое имя.""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def iMGSRC_RU():
        T = yield from upload(
            url="""https://imgsrc.ru/main/user.php?user={}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def igromania():
        T = yield from upload(
            url="""http://forum.igromania.ru/member.php?username={}""",
            error_type="text",
            error_msg="""Пользователь не зарегистрирован и не имеет профиля для просмотра.""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def interpals():
        T = yield from upload(
            url="""https://www.interpals.net/{}""",
            error_type="text",
            error_msg="""The requested user does not exist or is inactive""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def irecommend():
        T = yield from upload(
            url="""https://irecommend.ru/users/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def jeuxvideo():
        T = yield from upload(
            url="""http://www.jeuxvideo.com/profil/{}?mode=infos""",
            error_type="text",
            error_msg="""Vous êtes""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def kwork():
        T = yield from upload(
            url="""https://kwork.ru/user/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def labpentestit():
        T = yield from upload(
            url="""https://lab.pentestit.ru/profile/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def last_fm():
        T = yield from upload(
            url="""https://last.fm/user/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def leasehackr():
        T = yield from upload(
            url="""https://forum.leasehackr.com/u/{}/summary/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def livelib():
        T = yield from upload(
            url="""https://www.livelib.ru/reader/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def mastodon_cloud():
        T = yield from upload(
            url="""https://mastodon.cloud/@{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def mastodon_social():
        T = yield from upload(
            url="""https://mastodon.social/@{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def mastodon_technology():
        T = yield from upload(
            url="""https://mastodon.technology/@{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def mastodon_xyz():
        T = yield from upload(
            url="""https://mastodon.xyz/@{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def metacritic():
        T = yield from upload(
            url="""https://www.metacritic.com/user/{}""",
            error_type="text",
            error_msg="""User not found""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def mixer_com():
        T = yield from upload(
            url="""https://mixer.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def moikrug():
        T = yield from upload(
            url="""https://moikrug.ru/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def mstdn_io():
        T = yield from upload(
            url="""https://mstdn.io/@{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def nightbot():
        T = yield from upload(
            url="""https://nightbot.tv/t/{}/commands""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def nnRU():
        T = yield from upload(
            url="""https://{}.www.nn.ru/""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def notabug_org():
        T = yield from upload(
            url="""https://notabug.org/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def note():
        T = yield from upload(
            url="""https://note.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def opennet():
        T = yield from upload(
            url="""https://www.opennet.ru/~{}""",
            error_type="text",
            error_msg="""Имя участника не найдено""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def opensource():
        T = yield from upload(
            url="""https://opensource.com/users/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def osu_():
        T = yield from upload(
            url="""https://osu.ppy.sh/users/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def phpRU():
        T = yield from upload(
            url="""https://php.ru/forum/members/?username={}""",
            error_type="text",
            error_msg="""Указанный пользователь не найден. Пожалуйста, введите другое имя.""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def pikabu():
        T = yield from upload(
            url="""https://pikabu.ru/@{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def pr0gramm():
        T = yield from upload(
            url="""https://pr0gramm.com/api/profile/info?name={}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def radio_echo_msk():
        T = yield from upload(
            url="""https://echo.msk.ru/users/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def satsisRU():
        T = yield from upload(
            url="""https://satsis.info/user/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def segmentfault():
        T = yield from upload(
            url="""https://segmentfault.com/u/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def social_tchncs_de():
        T = yield from upload(
            url="""https://social.tchncs.de/@{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def soylentnews():
        T = yield from upload(
            url="""https://soylentnews.org/~{}""",
            error_type="text",
            error_msg="""The user you requested does not exist, no matter how much you wish this might be the case.""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def sparkpeople():
        T = yield from upload(
            url="""https://www.sparkpeople.com/mypage.asp?id={}""",
            error_type="text",
            error_msg="""We couldn't find that user""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def spletnik():
        T = yield from upload(
            url="""https://spletnik.ru/user/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def svidbook():
        T = yield from upload(
            url="""https://www.svidbook.ru/user/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def toster():
        T = yield from upload(
            url="""https://www.toster.ru/user/{}/answers""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def tracr_co():
        T = yield from upload(
            url="""https://tracr.co/users/1/{}""",
            error_type="text",
            error_msg="""No search results""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def travellerspoint():
        T = yield from upload(
            url="""https://www.travellerspoint.com/users/{}""",
            error_type="text",
            error_msg="""Wooops. Sorry!""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def uid():
        T = yield from upload(
            url="""http://uid.me/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def warriorforum():
        T = yield from upload(
            url="""https://www.warriorforum.com/members/{}.html""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def windy():
        T = yield from upload(
            url="""https://community.windy.com/user/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def mercadolivre():
        T = yield from upload(
            url="""https://www.mercadolivre.com.br/perfil/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def kofi():
        T = yield from upload(
            url="""https://ko-fi.com/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T

    @staticmethod
    def aminoapp():
        T = yield from upload(
            url="""https://aminoapps.com/u/{}""",
        )

        T.title = T.html.pq("title").text()
        yield T
