# -*- coding: utf-8 -*-

import glob
import json
import os
import zipfile
from typing import Union

import pandas as pd

from texi.datasets.dataset import Dataset, Datasets, JSONDatasets, Type, TypeVar


class CHIP2019(Datasets):
    # References:
    # http://www.cips-chip.org.cn:8088/evaluation

    T = TypeVar("T", bound="CHIP2019")

    @classmethod
    def from_dir(cls: Type[T], dirname: Union[str, os.PathLike]) -> T:
        prefix = "CHIP2019"
        df_train = pd.read_csv(os.path.join(dirname, "train.csv"))
        df_train["id"] = [f"{prefix}_train_{i}" for i in range(len(df_train))]
        df_val = pd.read_csv(os.path.join(dirname, "dev_id.csv"))
        df_val["id"] = df_val["id"].map(lambda x: f"{prefix}_val_{x}")

        new_names = {"question1": "sentence1", "question2": "sentence2"}
        df_train.rename(new_names, axis=1, inplace=True)
        df_val.rename(new_names, axis=1, inplace=True)

        return cls(
            train=df_train.to_dict("records"),
            val=df_val.to_dict("records"),
            dirname=dirname,
        )


class NCOV2019(Datasets):
    # References:
    # https://tianchi.aliyun.com/competition/entrance/231776/introduction

    T = TypeVar("T", bound="NCOV2019")

    @classmethod
    def from_dir(cls: Type[T], dirname: Union[str, os.PathLike]) -> T:
        def _load_data(basename, mode):
            df = pd.read_csv(os.path.join(dirname, f"{basename}.csv"))
            df["id"] = df["id"].map(lambda x: f"{prefix}_{mode}_{x}")
            df.rename(
                {"query1": "sentence1", "query2": "sentence2"}, axis=1, inplace=True
            )

            return df.to_dict("records")

        prefix = "NCOV2019"

        return cls(
            train=_load_data("train", "train"),
            val=_load_data("dev", "val"),
            dirname=dirname,
        )


class LUGETextPairDataset(Datasets):
    # References:
    # https://aistudio.baidu.com/aistudio/competition/detail/45

    T = TypeVar("T", bound="LUGETextPairDataset")

    @classmethod
    def from_dir(cls: Type[T], dirname: Union[str, os.PathLike]) -> T:
        def _load_data(basename, mode):
            columns = ["sentence1", "sentence2"]
            if mode != "test":
                columns += ["label"]

            df = pd.read_csv(
                os.path.join(dirname, f"{basename}.tsv"),
                sep="\t",
                names=columns,
            )
            df["id"] = df.index.map(lambda x: f"{prefix}_{mode}_{x}")

            return df.to_dict("records")

        prefix = "NCOV2019"

        return cls(
            train=_load_data("train", "train"),
            val=_load_data("dev", "val"),
            test=_load_data("test", "test"),
            dirname=dirname,
        )


class LCQMC(LUGETextPairDataset):
    # References:
    # https://aistudio.baidu.com/aistudio/competition/detail/45

    pass


class BQCorpus(LUGETextPairDataset):
    # References:
    # https://aistudio.baidu.com/aistudio/competition/detail/45

    pass


class PAWSX(LUGETextPairDataset):
    # References:
    # https://aistudio.baidu.com/aistudio/competition/detail/45

    pass


class AFQMC(Datasets):
    # References:
    # https://dc.cloud.alipay.com/index#/topic/intro?id=3

    T = TypeVar("T", bound="AFQMC")

    @classmethod
    def from_dir(cls: Type[T], dirname: Union[str, os.PathLike]) -> T:
        def _load_data(basename, mode):
            df = pd.read_csv(
                os.path.join(dirname, f"{basename}.csv"),
                sep="\t",
                names=["id", "sentence1", "sentence2", "label"],
            )
            df["id"] = df["id"].map(lambda x: f"AFQMC_{mode}_{x}")

            return df.to_dict("records")

        train1 = _load_data("atec_nlp_sim_train", "train")
        train2 = _load_data("atec_nlp_sim_train_add", "train")

        return cls(train=train1 + train2, dirname=dirname)


class CCKS2018(Datasets):
    T = TypeVar("T", bound="CCKS2018")

    @classmethod
    def from_dir(cls: Type[T], dirname: Union[str, os.PathLike]) -> T:
        def _load_data(basename, mode):
            columns = ["sentence1", "sentence2"]
            if mode != "train":
                columns = ["id"] + columns
            else:
                columns += ["label"]

            df = pd.read_csv(
                os.path.join(dirname, f"{basename}.txt"),
                sep="\t",
                names=columns,
            )

            if mode == "train":
                df["id"] = df.index.map(lambda x: f"CCKS2018_{mode}_{x}")

            return df.to_dict("records")

        train = _load_data("task3_train", "train")
        val = _load_data("task3_dev", "val")

        test_zip = os.path.join(dirname, "task3_test_data_expand.zip")
        with zipfile.ZipFile(test_zip) as zipf:
            with zipf.open("task3_test_data_expand/test_with_id.txt", mode="r") as f:
                test = pd.read_csv(f, sep="\t", names=["id", "sentence1", "sentence2"])
                test = test.to_dict("records")

        return cls(train=train, val=val, test=test, dirname=dirname)


class ChineseSNLI(Datasets):
    # References:
    # https://github.com/pluto-junzeng/CNSD

    T = TypeVar("T", bound="ChineseSNLI")

    @classmethod
    def from_dir(cls: Type[T], dirname: Union[str, os.PathLike]) -> T:
        def _load_data(basename, mode):
            filename = os.path.join(dirname, f"cnsd_snli_v1.0.{basename}.jsonl")
            with open(filename, mode="r") as f:
                examples = []
                for i, line in enumerate(f):
                    example = json.loads(line.rstrip())
                    example["id"] = f"ChineseSNLI_{mode}_{i}"
                    example["label"] = example.pop("gold_label")
                    examples += [example]

                return examples

        return cls(
            train=_load_data("train", "train"),
            val=_load_data("dev", "val"),
            test=_load_data("test", "test"),
            dirname=dirname,
        )


class ChineseSTSB(Datasets):
    # References:
    # https://github.com/pluto-junzeng/CNSD

    T = TypeVar("T", bound="ChineseSTSB")

    @classmethod
    def from_dir(cls: Type[T], dirname: Union[str, os.PathLike]) -> T:
        def _load_data(basename):
            filename = os.path.join(dirname, f"cnsd-sts-{basename}.txt")
            columns = ["id", "sentence1", "sentence2", "label"]
            with open(filename, mode="r") as f:
                examples = []
                for line in f:
                    id_, sentence1, sentence2, label = line.rstrip().split("||")
                    label = int(label)
                    examples += [dict(zip(columns, [id_, sentence1, sentence2, label]))]

                return examples

        return cls(
            train=_load_data("ntrain"),
            val=_load_data("dev"),
            test=_load_data("test"),
            dirname=dirname,
        )


class CAIL2019SCM(JSONDatasets):
    # References:
    # https://github.com/thunlp/CAIL2019

    files = {
        "train": "train.json",
        "val": "valid.json",
        "test": "test.json",
    }


class THUCNews(Datasets):
    # References:
    # https://thuctc.thunlp.org

    T = TypeVar("T", bound="THUCNews")

    @classmethod
    def from_dir(cls: Type[T], dirname: Union[str, os.PathLike]) -> T:
        def _iter_examples():
            for filename in glob.iglob(
                os.path.join(dirname, "**/*.txt"), recursive=True
            ):
                relname = os.path.relpath(filename, dirname)
                label = os.path.dirname(relname)
                id_ = os.path.splitext(os.path.basename(relname))[0]
                with open(filename) as f:
                    content = f.read()
                    yield {
                        "id": id_,
                        "content": content,
                        "label": label,
                    }

        return cls(train=Dataset(_iter_examples), dirname=dirname)


class Sohu2021(object):
    # References:
    # https://www.biendata.xyz/competition/sohu_2021/

    T = TypeVar("T", bound="Sohu2021")

    def __init__(
        self,
        short_short_a,
        short_long_a,
        long_long_a,
        short_short_b,
        short_long_b,
        long_long_b,
    ):
        self.short_short_a = short_short_a
        self.short_long_a = short_long_a
        self.long_long_a = long_long_a
        self.short_short_b = short_short_b
        self.short_long_b = short_long_b
        self.long_long_b = long_long_b

    @classmethod
    def from_dir(cls: Type[T], dirname: Union[str, os.PathLike]) -> T:
        def _load_data(subdir):
            def _load(basename, mode):
                flag = "A" if "A" in subdir else "B"

                examples = []
                with open(os.path.join(dirname, subdir, f"{basename}.txt")) as f:
                    for i, line in enumerate(f):
                        line = line.rstrip()
                        if line:
                            example = json.loads(line)
                            example["sentence1"] = example.pop("source")
                            example["sentence2"] = example.pop("target")
                            if mode != "test":
                                example["id"] = f"sohu2021-{subdir}-{i}"
                                example["label"] = int(example.pop(f"label{flag}"))
                            examples += [example]

                return Dataset(examples)

            return Datasets(
                train=_load("train", "train"),
                val=_load("valid", "val"),
                test=_load("test_with_id", "test"),
                dirname=dirname,
            )

        types = {
            "short_short_a": "短短匹配A类",
            "short_long_a": "短长匹配A类",
            "long_long_a": "长长匹配A类",
            "short_short_b": "短短匹配B类",
            "short_long_b": "短长匹配B类",
            "long_long_b": "长长匹配B类",
        }

        datasets = {key: _load_data(value) for key, value in types.items()}

        return cls(**datasets)


class ToutiaoNews(Datasets):
    # References:
    # https://github.com/fateleak/toutiao-text-classfication-dataset

    T = TypeVar("T", bound="ToutiaoNews")

    @classmethod
    def from_dir(cls: Type[T], dirname: Union[str, os.PathLike]) -> T:
        examples = []
        with open(os.path.join(dirname, "toutiao_cat_data.txt")) as f:
            for line in f:
                line = line.rstrip()
                if line:
                    id_, category_id, category, title, keywords = line.split("_!_")
                    example = {
                        "id": id_,
                        "category_id": category_id,
                        "category": category,
                        "title": title,
                        "keywords": keywords.split(","),
                    }
                    examples += [example]

        return cls(train=Dataset(examples))


class Dianping(Datasets):
    T = TypeVar("T", bound="Dianping")

    @classmethod
    def from_dir(cls: Type[T], dirname: Union[str, os.PathLike]) -> T:
        def _load_data(filename):
            df = pd.read_csv(
                os.path.join(dirname, filename), header=0, names=["label", "text"]
            )

            return df.to_dict("records")

        files = {
            "train": "train.csv",
            "test": "test.csv",
        }
        data = {key: _load_data(value) for key, value in files.items()}

        return cls(**data, dirname=dirname)
