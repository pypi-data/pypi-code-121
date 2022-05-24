# -*- coding: utf-8 -*-

from texi.datasets import classification, question_answering, text, translation
from texi.datasets.classification import (
    AFQMC,
    CAIL2019SCM,
    CCKS2018,
    CHIP2019,
    LCQMC,
    NCOV2019,
    PAWSX,
    BQCorpus,
    ChineseSNLI,
    ChineseSTSB,
    Dianping,
    Sohu2021,
    THUCNews,
    ToutiaoNews,
)
from texi.datasets.dataset import (
    Dataset,
    Datasets,
    DatasetTransformMixin,
    JSONDatasets,
    MaskableMixin,
    SplitableMixin,
)
from texi.datasets.question_answering import Baike2018QA, ZhidaoQA
from texi.datasets.text import News2016Zh, WebText2019Zh, WeixinPublicCorpus, Wiki2019Zh
from texi.datasets.translation import Translate2019Zh

__all__ = [
    "classification",
    "dataset",
    "question_answering",
    "text",
    "translation",
    "DatasetTransformMixin",
    "MaskableMixin",
    "SplitableMixin",
    "Dataset",
    "Datasets",
    "JSONDatasets",
    "classification",
    "CHIP2019",
    "NCOV2019",
    "LCQMC",
    "BQCorpus",
    "PAWSX",
    "AFQMC",
    "CCKS2018",
    "ChineseSNLI",
    "ChineseSTSB",
    "CAIL2019SCM",
    "THUCNews",
    "Sohu2021",
    "ToutiaoNews",
    "Dianping",
    "translation",
    "Translate2019Zh",
    "text",
    "News2016Zh",
    "WebText2019Zh",
    "Wiki2019Zh",
    "WeixinPublicCorpus",
    "question_answering",
    "Baike2018QA",
    "ZhidaoQA",
]
