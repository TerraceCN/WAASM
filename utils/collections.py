# -*- coding: utf-8 -*-

from typing import TypeVar, Callable, Any

DataType = TypeVar("DataType")


def deduplicate(data: list[DataType], key: Callable[[DataType], Any] = lambda x: x):
    _data: list[DataType] = []
    key_set = set()
    for d in data:
        k = key(d)
        if k not in key_set:
            key_set.add(k)
            _data.append(d)
    return _data
