"""
    Sharingan project
    We will try to find your visible basic footprint from social media as much as possible
"""
import asyncio
from pathlib import Path
from base64 import b64encode
from dataclasses import dataclass
from itertools import product
from pprint import pprint
from json import dumps

import click
import httpx
from progressbar import ProgressBar
from requests_html import HTML

from extract import Extractor
from log import error, info, success, warning
from models import config, error_types, person, web_images


@dataclass
class StareAt:
    name: str
    proxy: str
    save_path: str = "./events"
    pass_history: bool = False
    max_keepalive: int = 5
    max_conns: int = 101
    image_available_key = {"avatar", "images"}
    save_block_keys = {"resp", "html", "conf"}

    sites = list(filter(lambda _: "__" not in _, dir(Extractor)))
    datas = {}

    def mount(self) -> None:
        """
            init other configurations
        """
        self.save_path = Path(self.save_path)
        self.save_path.mkdir(exist_ok=True)
        limits = httpx.PoolLimits(
            max_keepalive=self.max_keepalive, max_connections=self.max_conns
        )
        self.client = httpx.AsyncClient(pool_limits=limits, http2=True)
        self.client_out = httpx.AsyncClient(
            pool_limits=limits, http2=True, proxies={"all": self.proxy},
        )
        # self.bar = ProgressBar(max_value=len(self.sites))

    async def single(self, key: str, indexs: int, target: object, data: config) -> None:
        """
            singel proccess to get target data
        """
        try:
            client = self.client_out if data.proxy else self.client
            url = data.url.format(self.name)
            if (method := data.method) == "post":
                req = client.post(
                    url,
                    data=data.data,
                    json=data.json,
                    headers=data.headers,
                    cookies=data.cookies,
                )
            else:
                req = client.get(url, headers=data.headers, cookies=data.cookies)
            resp = await req
            self.assert_proccess(resp, data)
            pure_info = target.send((key, resp, HTML(html=resp.text), data))
            await self.loop_images(client, pure_info)
            self.datas[key] = pure_info
        except AssertionError:
            pass
        except Exception as e:
            self.datas[key] = {"error": f"{e.__class__.__name__}: {e}"}
        # finally:
        # self.bar.update(indexs + 1)

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

    async def fetch_image_b64(self, client: httpx.AsyncClient, url: str) -> str:
        """
            download an images and covert to base64 encoding 
        """
        resp = await client.get(url)
        if (
            resp.status_code == 200
            and resp.headers.get("Content-Type") in web_images._value2member_map_
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
                image_source = getattr(data, key)
            except AttributeError:
                continue
            if isinstance(image_source, str):
                image = await self.fetch_image_b64(client, image_source)
                setattr(data, f"{key}_b64", image)
            elif isinstance(params, (list, tuple, set)):
                await asyncio.gather(
                    self.fetch_image_b64(client, _) for _ in image_source
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
            tasks.append(self.single(key, indexs, target, data))
        await asyncio.gather(*tasks)

    def save(self) -> None:
        """
            save or export the results
        """
        for key, val in self.datas.items():
            if isinstance(val, dict):
                error(f'{key}: {val["error"]}')
            elif isinstance(val, object):
                success(f"{key}[{val.resp.url}]: {val._name}")

        filename = f'{self.name +  ( str(moment.now().format("YYYY-MM-DD HH:mm:ss"))  if self.pass_history else "" ) }.json'
        filepath = self.save_path / filename
        final_data = {
            key: val.report()
            for key, val in self.datas.items()
            if not isinstance(val, dict)
        }
        with filepath.open("w") as file:
            file.write(dumps(final_data, indent=4, ensure_ascii=False))
            info(f"datas saved to: {filepath}")

    def run(self) -> None:
        self.mount()
        asyncio.run(self.loop())
        self.save()


@click.command()
@click.option("--name", default="blue")
@click.option("--proxy", default="http://127.0.0.1:1087")
@click.option("--save_path", default="../events")
@click.option("--pass_history", is_flag=True)
def main(name: str, proxy: str, save_path: str, pass_history: bool) -> None:
    StareAt(name, proxy, save_path).run()


if __name__ == "__main__":
    main()
