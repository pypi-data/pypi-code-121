from pyspark.sql import SparkSession
from pyspark import SparkConf
from .config import starting_config

def spark_initializer(app_name, args, additional_config=[]):

    # Create list of configurations
    additional_config = starting_config + auto_conf_generator(args) + additional_config

    config = SparkConf().setAll(additional_config)

    spark = SparkSession.builder.appName(app_name).config(conf=config).getOrCreate()

    return spark



# Translate automatically configurations from services' arguments to spark properties
def auto_conf_generator(args):
    
    args_name = {
        # Hive
        "spark.sql.warehouse.dir" : "spark.sql.warehouse.dir",
        "hiveMetastoreUris" : "hive.metastore.uris",
        "hiveMetastoreUris" : "hive.metastore.uris",
        # MinIO
        "minIO_URL" : "spark.hadoop.fs.s3a.endpoint",
        "minIO_ACCESS_KEY" : "spark.hadoop.fs.s3a.access.key",
        "minIO_SECRET_KEY" : "spark.hadoop.fs.s3a.secret.key" ,
    }

    result = []

    # for key in args_name:
    #     if key in args:
    #         result.append((args_name[key], args[key]))
    
    for key in args_name:
        for arg in args:
            if key in arg:
                result.append((args_name[key], args[arg]))
    
    return result

