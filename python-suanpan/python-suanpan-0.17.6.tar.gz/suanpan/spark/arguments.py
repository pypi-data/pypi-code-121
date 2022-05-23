# coding=utf-8
from __future__ import absolute_import, print_function

import os

from pyspark2pmml import PMMLBuilder  # pylint: disable=import-error
from pyspark.ml import PipelineModel  # pylint: disable=import-error
from suanpan import arguments as base
from suanpan import g
from suanpan.spark import db, io
from suanpan.utils import json

Int = base.Int
String = base.String
Float = base.Float
Bool = base.Bool
List = base.List
ListOfInt = base.ListOfInt
ListOfString = base.ListOfString
ListOfFloat = base.ListOfFloat
ListOfBool = base.ListOfBool
Json = base.Json
IntOrFloat = base.IntOrFloat
IntFloatOrString = base.IntFloatOrString
BoolOrString = base.BoolOrString
BoolOrInt = base.BoolOrInt


class SparkArg(base.Arg):
    pass


class Table(SparkArg):
    def __init__(self, key, table, partition, sortColumns=None, required=False):
        super().__init__(key)
        sortColumns = sortColumns or f"{table}SortColumns"
        self.table = String(key=table, required=required)
        self.partition = String(key=partition)
        self.sortColumns = ListOfString(key=sortColumns, default=[])
        self.value = None

    def load(self, args):
        self.table.load(args)
        self.partition.load(args)
        self.sortColumns.load(args)
        if self.table.value:
            self.value = {
                "table": self.table.value,
                "partition": self.partition.value,
                "sortColumns": self.sortColumns.value,
            }
        return self

    def transform(self, value):
        if not value:
            return None
        return db.readTable(g.spark, self.table.value, self.partition.value).sort(
            self.sortColumns.value
        )

    def save(self, result):
        data = result.value
        db.writeTable(g.spark, self.table.value, data)
        self.logSaved(self.table.value)


class DataFrame(Table):
    pass


class SparkModel(SparkArg):
    def __init__(self, key, **kwargs):
        kwargs.update(required=True)
        super().__init__(key, **kwargs)

    def transform(self, value):
        return PipelineModel.load(io.getStoragePath(g.spark, value))

    def save(self, result):
        modelPath = io.getStoragePath(g.spark, self.value)
        pmmlPath = modelPath + "/pmml"

        result.value.model.write().overwrite().save(modelPath)
        with io.open(g.spark, pmmlPath, mode="w") as file:
            pmmlBuilder = PMMLBuilder(
                g.spark.sparkContext, result.value.data, result.value.model
            ).putOption(result.value.classifier, "compact", True)
            pmml = pmmlBuilder.buildByteArray()
            file.write(pmml)


class PmmlModel(SparkArg):
    def __init__(self, key, **kwargs):
        kwargs.update(required=True)
        super().__init__(key, **kwargs)

    def transform(self, value):
        with io.open(g.spark, self.pmml_path(value), mode="r") as file:
            return file.read()

    def pmml_path(self, value):
        modelPath = io.getStoragePath(g.spark, value)
        pmmlPath = modelPath + "/pmml"
        return pmmlPath


class OdpsTable(SparkArg):
    def __init__(
        self,
        key,
        accessId,
        accessKey,
        odpsUrl,
        tunnelUrl,
        project,
        table,
        partition,
        overwrite,
        numPartitions,
    ):
        super().__init__(key)
        self.accessId = String(key=accessId, required=True)
        self.accessKey = String(key=accessKey, required=True)
        self.odpsUrl = String(key=odpsUrl, required=True)
        self.tunnelUrl = String(key=tunnelUrl, required=True)
        self.project = String(key=project, required=True)
        self.table = String(key=table, required=True)
        self.partition = String(key=partition)
        self.overwrite = Bool(key=overwrite, default=False)
        self.numPartitions = Int(key=numPartitions, default=2)

    def load(self, args):
        self.accessId.load(args)
        self.accessKey.load(args)
        self.odpsUrl.load(args)
        self.tunnelUrl.load(args)
        self.project.load(args)
        self.table.load(args)
        self.partition.load(args)
        self.overwrite.load(args)
        self.numPartitions.load(args)
        self.value = dict(
            accessId=self.accessId.value,
            accessKey=self.accessKey.value,
            odpsUrl=self.odpsUrl.value,
            tunnelUrl=self.tunnelUrl.value,
            table=self.table.value,
            partition=self.partition.value,
            overwrite=self.overwrite.value,
            numPartitions=self.numPartitions.value,
        )
        return self

    def transform(self, value):
        return db.readOdpsTable(
            g.spark,
            accessId=self.accessId.value,
            accessKey=self.accessKey.value,
            odpsUrl=self.odpsUrl.value,
            tunnelUrl=self.tunnelUrl.value,
            project=self.project.value,
            table=self.table.value,
            partition=self.partition.value,
            numPartitions=self.numPartitions.value,
        )

    def save(self, result):
        db.writeOdpsTable(
            g.spark,
            accessId=self.accessId.value,
            accessKey=self.accessKey.value,
            odpsUrl=self.odpsUrl.value,
            tunnelUrl=self.tunnelUrl.value,
            project=self.project.value,
            table=self.table.value,
            data=result.value,
            partition=self.partition.value,
            overwrite=self.overwrite.value,
        )


class Visual(SparkArg):
    def __init__(self, key, **kwargs):
        kwargs.update(required=True)
        super().__init__(key, **kwargs)

    def save(self, result):
        visualPath = io.getStoragePath(g.spark, self.value) + "/part-00000"
        with io.open(g.spark, visualPath, mode="w") as file:
            file.write(result.value)


class JsonFile(SparkArg):
    def transform(self, value):
        with io.open(g.spark, self.filePath(value), mode="r") as file:
            return json.load(file)

    def save(self, result):
        with io.open(g.spark, self.filePath(self.value), mode="w") as file:
            json.dump(result.value, file)

    def filePath(self, value):
        dataPath = io.getStoragePath(g.spark, value)
        jsonPath = os.path.join(dataPath, "data.json")
        return jsonPath
