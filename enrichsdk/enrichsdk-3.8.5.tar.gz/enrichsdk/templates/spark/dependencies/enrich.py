import os
import json
import argparse
from pyspark.sql import SQLContext

from .spark import start_spark

"""
This is a wrapper around start_spark function. This 
will take the configuration parameters specified in 
'config' and also enrich environment to create the 
spark session 
"""


def start_spark_session(config):
    """
    Main script

    :return: None
    """

    # Collect parameters
    name = config["name"]

    if "master" in config:
        master = config["master"]
    elif "ENRICH_SPARK_MASTER" in os.environ:
        master = os.environ["ENRICH_SPARK_MASTER"]
    else:
        master = "local"

    jar_packages = config.get("jar_packages", [])
    spark_config = config.get("spark_config", {})

    # start Spark application and get Spark session, logger and config
    spark, log, extra_config = start_spark(
        app_name=name,
        master=master,
        jar_packages=jar_packages,
        spark_config=spark_config,
    )

    # Save it...
    sc = spark.sparkContext
    sqlsc = SQLContext(sc)

    config["spark"] = spark
    config["sc"] = sc
    config["sqlsc"] = sqlsc
    config["applicationid"] = sc.applicationId
    config["logger"] = log

    # log that main ETL job is starting
    log.warn("Pipeline is up-and-running")

    return


def stop_spark_session(config):

    spark = config["spark"]
    log = config["log"]

    log.warn("test_etl_job is finished")

    spark.stop()

    return None
