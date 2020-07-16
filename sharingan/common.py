"""
    Sharingan project
    We will try to find your visible basic footprint from social media as much as possible
"""
import pathlib
import httpx
import re
import string
from retry import retry


def init_dir(path: pathlib.Path) -> pathlib.Path:
    path.mkdir(exist_ok=True)
    return path


def str_to_num(strs: str) -> int or str:
    strs = strs.replace(",", "")
    strs = "0" if not strs else strs
    return int(strs) if strs.isalpha() else strs


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
    with pathlib.Path("templates.py").open("w") as file:
        model_str = """
    @staticmethod
    def {}():
        T = yield from upload({})
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
            if types == "status_code":
                pass
            elif types == "message":
                conf += f"error_type='text',error_msg='''{msg}''',"
            elif types == "response_url":
                conf += f"error_type='func',error_msg = lambda resp: resp.url == '''{val['urlMain']}'''"
            file.write(model_str.format(key, conf).replace(URLCODE, "{}"))
    print(f"{all_types=}")


if __name__ == "__main__":
    extract_maker_with_sherlock()
