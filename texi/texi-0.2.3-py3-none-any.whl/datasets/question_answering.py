# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Type, TypeVar

from texi.datasets.dataset import JSONDatasets


class Baike2018QA(JSONDatasets):
    files = {
        "train": "baike_qa_train.json",
        "val": "baike_qa_valid.json",
    }


class ZhidaoQA(JSONDatasets):
    T = TypeVar("T", bound="ZhidaoQA")

    files = {
        "train": "zhidao_qa.json",
    }

    @classmethod
    def format(cls: Type[T], x: dict) -> dict:
        x["id"] = x.pop("_id").pop("$oid")

        return x
