"""
    Sharingan project
    We will try to find your visible basic footprint from social media as much as possible
"""
import pathlib


def init_dir(path: pathlib.Path) -> pathlib.Path:
    path.mkdir(exist_ok=True)
    return path


def str_to_num(strs: str) -> int or str:
    strs = strs.replace(",", "")
    strs = "0" if not strs else strs
    return int(strs) if strs.isalpha() else strs
