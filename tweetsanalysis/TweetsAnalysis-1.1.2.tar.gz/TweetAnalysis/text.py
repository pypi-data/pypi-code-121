import os
import sys
import time
import threading

import pyspark.pandas as ps

from pyspark.sql import dataframe, functions as F
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.types import StringType, DoubleType, DateType, MapType, StructType, StructField

from TweetAnalysis.config.core import config
from TweetAnalysis.config import logging_config
from TweetAnalysis.spark_streamer import SparkStreamer
from TweetAnalysis.text_cleaner import TextCleaner
from TweetAnalysis.text_processor import TextProcessor

_logger = logging_config.get_logger(__name__)

tc = TextCleaner()
tp = TextProcessor()

strip_non_ascii_udf = udf(tc.strip_non_ascii, StringType())
check_blanks_udf = udf(tc.check_blanks, StringType())
# check_lang_udf = udf(tc.check_lang, StringType())
fix_abbreviation_udf = udf(tc.fix_abbreviation, StringType())
remove_stops_udf = udf(tc.remove_stops, StringType())
remove_features_udf = udf(tc.remove_features, StringType())
tag_and_remove_udf = udf(tc.tag_and_remove, StringType())
lemmatize_udf = udf(tc.lemmatize, StringType())



def clean(df):
    cols = df.columns

    df = df.withColumn('non_asci', strip_non_ascii_udf(df['text']))
    df = df.select(cols+['non_asci'])\
    .withColumn('fixed_abbrev', fix_abbreviation_udf(df['non_asci']))

    df = df.select(cols+['fixed_abbrev'])\
    .withColumn('stop_text', remove_stops_udf(df['fixed_abbrev']))
    df = df.select(cols+['stop_text'])\
    .withColumn('feat_text', remove_features_udf(df['stop_text']))
    df = df.select(cols+['feat_text'])\
    .withColumn('tagged_text', tag_and_remove_udf(df['feat_text']))
    df = df.select(cols+['tagged_text']) \
    .withColumn('lemm_text', lemmatize_udf(df['tagged_text']))
    # df=df.select(cols+['lemm_text']).withColumn("is_blank", check_blanks_udf(df["lemm_text"]))

    return df

def get_words_count(df, col_name='lemm_text'):
    dict = tp.word_count(df, col_name)
    return dict

