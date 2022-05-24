# -*- coding: utf-8 -*-

from texi.datasets.dataset import JSONDatasets


class Translate2019Zh(JSONDatasets):
    # References:
    # https://github.com/brightmart/nlp_chinese_corpus#5%E7%BF%BB%E8%AF%91%E8%AF%AD%E6%96%99translation2019zh

    files = {
        "train": "translation2019zh_train.json",
        "val": "translation2019zh_train.json",
    }
