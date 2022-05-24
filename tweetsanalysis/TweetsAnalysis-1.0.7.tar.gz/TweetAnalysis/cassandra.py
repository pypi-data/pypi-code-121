import os
import sys

from pyspark.sql import SparkSession


from TweetAnalysis.config.core import config
from TweetAnalysis.config import logging_config


_logger = logging_config.get_logger(__name__)


class CassandraApi(object):
    def __init__(self):
        self.__spark = SparkSession.builder.master("local[2]").appName("cassandra reader")\
            .config("spark.some.config.option", "some-value")\
            .config("spark.cassandra.connection.host", config.cassandra.CASSANDRA_HOST)\
            .getOrCreate()

    def get_all_data(self):
        _logger.info('reading data from cassandra...')

        df = self.__spark \
            .read \
            .format("org.apache.spark.sql.cassandra") \
            .options(table="tweets", keyspace="tweetsstream") \
            .load()

        return df

    def get_data_on_topic(self, topic):
        _logger.info('reading data from cassandra...')

        df = self.__spark \
            .read \
            .format("org.apache.spark.sql.cassandra") \
            .options(table="tweets", keyspace="tweetsstream") \
            .load()

        df = df.filter(df.topic == topic)

        return df