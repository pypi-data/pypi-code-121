from importlib import resources

from tecton_spark.logger import get_logger

logger = get_logger("udf_jar")


def get_udf_jar_path():
    with resources.path("tecton_spark.jars", "tecton-udfs-spark-3.jar") as p:
        return str(p)
