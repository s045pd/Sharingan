"""
    Sharingan project
    We will try to find your visible basic footprint from social media as much as possible
"""
import asyncio
from base64 import b64decode, b64encode
from dataclasses import dataclass, field
from itertools import product
from json import dumps, loads
from pathlib import Path
from pprint import pprint
from typing import Dict, List, Set

import click
import httpx
import moment
from requests_html import HTML

from sharingan.common import init_dir, status_print
from sharingan.extract import Extractor
from sharingan.log import error, info, success, warning
from sharingan.models import config, error_types, person, web_images

asyncio.log.logger.setLevel(40)

success(
    """
███████╗██╗  ██╗ █████╗ ██████╗ ██╗███╗   ██╗ ██████╗  █████╗ ███╗   ██╗
██╔════╝██║  ██║██╔══██╗██╔══██╗██║████╗  ██║██╔════╝ ██╔══██╗████╗  ██║
███████╗███████║███████║██████╔╝██║██╔██╗ ██║██║  ███╗███████║██╔██╗ ██║
╚════██║██╔══██║██╔══██║██╔══██╗██║██║╚██╗██║██║   ██║██╔══██║██║╚██╗██║
███████║██║  ██║██║  ██║██║  ██║██║██║ ╚████║╚██████╔╝██║  ██║██║ ╚████║
╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝

[+]REPO_URL: https://github.com/s045pd/Sharingan
[+]AUTHOR:   s045pd
"""
)


@dataclass
class StareAt:
    name: str
    proxy_uri: str
    no_proxy: bool = False
    save_path: str = "./events"
    pass_history: bool = False
    singel: str = ""
    debug: bool = False
    update: bool = False

    workers: int = 20
    max_size: int = 20
    max_timeout: int = 10

    image_available_key = {"avatar", "images"}
    save_block_keys = {"resp", "html", "conf"}

    sites: List[str] = field(init=False)
    datas: Dict = field(default_factory=dict)

    def __post_init__(self):
        """
        other datas init
        """
        if self.singel:
            try:
                getattr(Extractor, self.singel)
                self.sites = [self.singel]
            except AttributeError:
                pass
        else:
            self.sites = list(filter(lambda _: "__" not in _, dir(Extractor)))

        self.save_path = Path(self.save_path)
        self.save_path.mkdir(exist_ok=True)

    def create_client(self, data: person) -> httpx.AsyncClient:
        client = httpx.AsyncClient(
            http2=True, verify=False, timeout=self.max_timeout
        )
        client_out = httpx.AsyncClient(
            http2=True,
            verify=False,
            proxies={"all": self.proxy_uri},
            timeout=self.max_timeout,
        )
        if self.no_proxy:
            return client
        elif data.proxy:
            return client_out
        else:
            return client

    async def single(self, datas: tuple) -> None:
        """
        singel proccess to get target data
        """
        key, indexs, target, data = datas
        try:
            async with self.create_client(data) as client:
                url = data.url.format(self.name)
                if (method := data.method) == "post":
                    req = client.post(
                        url,
                        data=data.data,
                        json=data.json,
                        headers=data.headers,
                        cookies=data.cookies,
                        allow_redirects=False,
                    )
                else:
                    req = client.get(
                        url,
                        headers=data.headers,
                        cookies=data.cookies,
                        allow_redirects=False,
                    )
                resp = await req
                self.assert_proccess(resp, data)
                pure_info = target.send(
                    (
                        self.name,
                        key,
                        resp,
                        HTML(html=resp.text),
                        data,
                        self.debug,
                    )
                )
                await self.loop_images(client, pure_info)
                self.datas[key] = pure_info
                status_print(
                    resp,
                    f"[+]{key.ljust(10)} ({resp.status_code}){resp.url}:  {pure_info._title}",
                )
        except AssertionError:
            pass
        except Exception as e:
            self.datas[key] = {"error": f"{e.__class__.__name__}: {e}"}

    def assert_proccess(self, resp: httpx.Response, data: person) -> None:
        """
        check what if data is ok
        arguments
            resp: response from server
            data: extra target config
        """

        def single(data: person) -> None:
            _type, _msg = data
            assert not getattr(error_types, _type)(resp, _msg)

        e_type = data.error_type
        e_msg = data.error_msg

        check_instance = lambda _: isinstance(_, (list, tuple, set))
        all(map(check_instance, (e_type, e_msg)))

        if isinstance(e_type, str):
            e_type = [e_type]

        if isinstance(e_msg, (str, int, float, object)):
            e_msg = [e_msg]

        assert len(e_type) == len(e_msg)
        assert not any(map(single, product(e_type, e_msg)))

    async def fetch_image_b64(
        self, client: httpx.AsyncClient, url: str
    ) -> str:
        """
        download an images and covert to base64 encoding
        """
        resp = await client.get(url)
        if (
            resp.status_code == 200
            and resp.headers.get("Content-Type")
            in web_images._value2member_map_
        ):
            return bytes.decode(b64encode(resp.content))

    async def loop_images(
        self, client: httpx.AsyncClient, data: person, limits: int = 10
    ) -> None:
        """
        download images which necssary , and encode with base64
        """
        times = 0
        for key in self.image_available_key:
            try:
                params = getattr(data, key)
            except AttributeError:
                continue
            if isinstance(params, str) and params:
                image = await self.fetch_image_b64(client, params)
                setattr(data, f"{key}_b64", image)
            elif isinstance(params, (list, tuple, set)):
                await asyncio.gather(
                    self.fetch_image_b64(client, _) for _ in params if _
                )

    async def loop(self) -> None:
        """
        proccessing all tasks
        """
        tasks = []
        for indexs, key in enumerate(self.sites):
            target = getattr(Extractor, key)()
            if "__next__" not in dir(target):
                continue
            data = next(target)
            tasks.append(self.single((key, indexs, target, data)))
        await asyncio.gather(*tasks)

    def save(self) -> None:
        """
        save or export the results
        """
        save_flag = False
        for key, val in self.datas.items():
            if isinstance(val, object):
                save_flag = True

        if not save_flag:
            return
        file_name = f'{self.name +  ( str(moment.now().format("YYYY-MM-DD HH:mm:ss"))  if self.pass_history else "" ) }.json'

        target_path = init_dir(self.save_path / self.name)
        avatar_path = init_dir(target_path / "avatars")

        file_path = target_path / file_name
        final_data = {}
        for key, val in self.datas.items():
            if isinstance(val, dict):
                continue
            val_data = val.report()
            final_data[key] = val_data
            if not val_data.get("avatar"):
                continue
            with (avatar_path / f"{key}.jpeg").open("wb") as img:
                img.write(b64decode(val.avatar_b64))

        if self.update and file_path.exists():
            with file_path.open("r") as file:
                raw_data = loads(file.read())
                raw_data.update(final_data)
                final_data = raw_data

        with file_path.open("w") as file:
            file.write(dumps(final_data, indent=4, ensure_ascii=False))
            info(f"[=]Saved: {str(file_path.absolute())}")

    def run(self) -> None:
        asyncio.run(self.loop())
        self.save()


@click.command()
@click.argument("name")
@click.option(
    "--proxy_uri",
    default="http://127.0.0.1:1087",
    help="Proxy address in case of need to use a proxy to be used",
)
@click.option(
    "--no_proxy",
    is_flag=True,
    help="All connections will be directly connected",
)
@click.option(
    "--save_path",
    default="./events",
    help="The storage location of the collected results",
)
@click.option(
    "--pass_history",
    is_flag=True,
    help="The file name will be named according to the scan end time",
)
@click.option(
    "--singel",
    default="",
    help="Commonly used for single target information acquisition or testing",
)
@click.option("--debug", is_flag=True, help="Debug model")
@click.option(
    "--update", is_flag=True, help="Do not overwrite the original data results"
)
@click.option(
    "--workers", type=int, default=20, help="Number of concurrent workers"
)
def main(
    name: str,
    proxy_uri: str,
    no_proxy: bool,
    save_path: str,
    pass_history: bool,
    singel: str,
    debug: bool,
    update: bool,
    workers: int,
) -> None:
    StareAt(
        name,
        proxy_uri,
        no_proxy,
        save_path,
        pass_history,
        singel,
        debug,
        update,
        workers,
    ).run()


if __name__ == "__main__":
    # uvloop.install()
    main()
