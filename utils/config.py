# -*- coding: utf-8 -*-

import tomllib
from typing import Any

_config = {}


def load():
    global _config
    with open("config.toml", "rb") as fp:
        _config = tomllib.load(fp)


def get(*args: str, default: Any = None, required: bool = False):
    find_path: list[str] = []
    _c = _config
    for arg in args:
        if arg in _c:
            _c = _c[arg]
            find_path.append(arg)
        else:
            current_path = ".".join(find_path + [arg])
            if required:
                raise KeyError(f"Cannot find config '{current_path}'")
            else:
                return default
    return _c


load()

__all__ = ["get", "load"]
