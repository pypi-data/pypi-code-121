import pytest

from tecton_spark.udf_jar import get_udf_jar_path


@pytest.fixture(scope="session")
def tecton_pytest_spark_session():
    try:
        from pyspark.sql import SparkSession
    except ImportError:
        pytest.fail("Cannot create a SparkSession if `pyspark` is not installed.")

    active_session = SparkSession.getActiveSession()
    if active_session:
        pytest.fail(
            f"Cannot create SparkSession `tecton_pytest_spark_session` when there is already an active session: {active_session.sparkContext.appName}"
        )

    try:
        spark = (
            SparkSession.builder.appName("tecton_pytest_spark_session")
            .config("spark.jars", get_udf_jar_path())
            .getOrCreate()
        )
    except Exception as e:
        # Unfortunately we can't do much better than parsing the error message since Spark raises `Exception` rather than a more specific type.
        if str(e) == "Java gateway process exited before sending its port number":
            pytest.fail(
                "Failed to start Java process for Spark, perhaps Java isn't installed or the 'JAVA_HOME' environment variable is not set?"
            )

        raise e

    try:
        yield spark
    finally:
        spark.stop()
