import os
import sys

from memory_profiler import profile
from pyspark.context import SparkContext
from pyspark.sql import SQLContext

sys.path.append('../../../..')

from zeno_etl_libs.config.common import Config
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3

os.environ['env'] = 'dev'

sc = SparkContext()
sq = SQLContext(sc)
logger = get_logger()
s3 = S3()

@profile
def read_data():
    logger.info("trying to read data from redshift")
    query = f"""select * from "prod2-generico".sales limit 10;"""
    df = rs_db.get_df(query=query)
    for c in df.columns:
        df[c] = df[c].astype('str')
    sparkDF = sq.createDataFrame(df)
    logger.info("spark dataframe created")
    return sparkDF


def process_data(df):
    new_df = df.groupBy(["bill-id", "patient-id"]).count()
    new_df.show()
    logger.info("processing of data completed")
    return new_df


def write_df_to_redshift_table(df, redshift_table, redshift_schema, load_mode, db_secrets):

    host = db_secrets['REDSHIFT_HOST'],
    database = db_secrets['REDSHIFT_DB'],
    user = db_secrets['REDSHIFT_USER'],
    password = db_secrets['REDSHIFT_PASSWORD'],
    port = int(db_secrets['REDSHIFT_PORT']),
    redshift_url = "jdbc:{}://{}:{}/{}".format(
        "redshift",
        host,
        port,
        database,
    )
    load_mode = "append"
    temp_bucket = "s3://{}/{}/".format("aws-glue-temporary-921939243643-ap-south-1", "temp")
    schema_qualified_table = '"prod2-generico".sales'
    logger.info("Attempting to write dataframe into:{}".format(schema_qualified_table))
    try:
        df.write.format("com.databricks.spark.redshift").option(
            "url",
            redshift_url
            + "?user="
            + user
            + "&password="
            + password,
        ).option("dbtable", schema_qualified_table).option(
            "tempdir", temp_bucket
        ).save(
            mode=load_mode
        )

        status = True
        logger.info("Dataframe written successfully into table:{}".format(schema_qualified_table))
    except Exception as exception:
        status = False

        raise Exception("{}".format(exception))
    return status


if __name__ == '__main__':
    try:
        configObj = Config.get_instance()
        secrets = configObj.get_secrets()
        rs_db = DB()
        rs_db.open_connection()
        df = read_data()
        processed_df = process_data(df)
        processed_df = processed_df.toPandas()
        # status = write_df_to_redshift_table(processed_df, "spark-example-temp", "prod2-generico", "append", secrets)
        s3.write_df_to_db(df=processed_df, table_name="spark-example-temp", db=rs_db,
                          schema="prod2-generico")
        rs_db.close_connection()
    except Exception as error:
        raise Exception(error)