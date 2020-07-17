"""
    Sharingan project
    We will try to find your visible basic footprint from social media as much as possible
"""
import logging

from termcolor import colored

# logging.basicConfig(format="[%(asctime)s]%(message)s", level=logging.INFO)
logging.basicConfig(format="%(message)s", level=logging.INFO)
loger = logging.getLogger("Sharingan")


def info(txt: str) -> None:
    loger.info(colored(txt, "blue"))


def success(txt: str) -> None:
    loger.info(colored(txt, "green"))


def warning(txt: str) -> None:
    loger.warning(colored(txt, "yellow"))


def error(txt: str) -> None:
    loger.error(colored(txt, "red"))


def critical(txt: str) -> None:
    loger.error(colored(txt, "red"))
