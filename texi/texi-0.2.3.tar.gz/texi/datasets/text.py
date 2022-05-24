# -*- coding: utf-8 -*-

import glob
import json
import os
from typing import Type, TypeVar, Union

from texi.datasets.dataset import Datasets, JSONDatasets


class News2016Zh(JSONDatasets):
    # References:
    # https://github.com/brightmart/nlp_chinese_corpus#2%E6%96%B0%E9%97%BB%E8%AF%AD%E6%96%99json%E7%89%88news2016zh

    files = {
        "train": "news2016zh_train.json",
        "val": "news2016zh_valid.json",
    }


class WebText2019Zh(JSONDatasets):
    # References:
    # https://github.com/brightmart/nlp_chinese_corpus#4%E7%A4%BE%E5%8C%BA%E9%97%AE%E7%AD%94json%E7%89%88webtext2019zh-%E5%A4%A7%E8%A7%84%E6%A8%A1%E9%AB%98%E8%B4%A8%E9%87%8F%E6%95%B0%E6%8D%AE%E9%9B%86

    files = {
        "train": "web_text_zh_train.json",
        "val": "web_text_zh_valid.json",
        "test": "web_text_zh_testa.json",
    }


class Wiki2019Zh(Datasets):
    # Reference:
    # https://github.com/brightmart/nlp_chinese_corpus#1%E7%BB%B4%E5%9F%BA%E7%99%BE%E7%A7%91json%E7%89%88wiki2019zh

    T = TypeVar("T", bound="Wiki2019Zh")

    @classmethod
    def from_dir(cls: Type[T], dirname: Union[str, os.PathLike]) -> T:
        examples = []
        for filename in glob.iglob(os.path.join(dirname, "**/*"), recursive=True):
            if os.path.isdir(filename):
                continue

            with open(filename) as f:
                for line in f:
                    line = line.rstrip()
                    if line:
                        example = json.loads(line)
                        examples += [example]

        return cls(train=examples)


class WeixinPublicCorpus(JSONDatasets):
    files = {
        "train": "articles.json",
    }
