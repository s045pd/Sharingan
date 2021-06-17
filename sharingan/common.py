"""
    Sharingan project
    We will try to find your visible basic footprint from social media as much as possible
"""
import pathlib
import re
import string

import httpx
from retry import retry
from termcolor import colored

from sharingan.log import info


def init_dir(path: pathlib.Path) -> pathlib.Path:
    """
    specified a directory and init it
    """
    path.mkdir(exist_ok=True)
    return path


def str_to_num(strs: str) -> int or str:
    strs = strs.replace(",", "")
    strs = "0" if not strs else strs
    return int(strs) if strs.isalpha() else strs


def status_print(resp, txt) -> str:
    """
    print crawled results with different status color
    """
    maps = {
        "1": lambda txt: colored(txt, "blue"),
        "2": lambda txt: colored(txt, "green"),
        "3": lambda txt: colored(txt, "yellow"),
        "4": lambda txt: colored(txt, "red"),
        "5": lambda txt: colored(txt, "red"),
    }
    print(maps.get(str(resp.status_code)[0], maps[list(maps.keys())[-1]])(txt))


@retry(tries=3)
def extract_maker_with_sherlock():
    """
    create extract model from sherlock config.json
    """
    URLCODE = "__URLCODE__"
    reg = re.compile(f"[{string.punctuation+string.whitespace}]")
    all_types = set()
    datas = httpx.get(
        "https://raw.githubusercontent.com/sherlock-project/sherlock/master/sherlock/resources/data.json",
        verify=False,
    ).json()
    script = pathlib.Path("templates.py")
    with script.open("w") as file:
        model_str = """
    @staticmethod
    def {}():
        T = yield from upload({})

        T.title = T.html.pq('title').text()
        yield T
        """
        for key, val in datas.items():
            conf = f"url='''{val['url'].replace('{}',URLCODE)}''',"
            key = reg.sub("_", key)
            if not key[0].isalpha():
                key = f"site_{key}"
            types, msg = val.get("errorType"), val.get("errorMsg")
            all_types.add(types)
            if not types:
                continue
            if types in {"status_code", "response_url"}:
                pass
            elif types == "message":
                conf += f"error_type='text',error_msg='''{msg}''',"
            file.write(model_str.format(key, conf).replace(URLCODE, "{}"))
    info(f"{all_types=}")
    info(f"file saved: {str(script.absolute())}")


if __name__ == "__main__":
    extract_maker_with_sherlock()
