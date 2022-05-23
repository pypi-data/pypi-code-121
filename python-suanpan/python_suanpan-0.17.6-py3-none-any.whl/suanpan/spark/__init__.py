# coding=utf-8
from __future__ import absolute_import, print_function

from contextlib import contextmanager

from pyspark.sql import SparkSession  # pylint: disable=import-error
from suanpan import g
from suanpan.components import Component
from suanpan.log import logger
from suanpan.objects import Context, HasName


class SparkComponent(Component, HasName):
    def beforeInit(self):
        logger.logDebugInfo()
        logger.debug(f"SparkComponent {self.name} starting...")
        g.spark = (
            SparkSession.builder.appName(self.runFunc.__name__)
            .enableHiveSupport()
            .getOrCreate()
        )

    def initBase(self, args):
        logger.setLogger(self.name)

    def afterSave(self, context):  # pylint: disable=unused-argument
        logger.debug(f"SparkComponent {self.name} done.")

    def afterClean(self):
        g.spark.stop()
