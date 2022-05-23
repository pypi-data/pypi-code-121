import glob
import os
from pysparkutilities import ds_initializer
from pysparkutilities.spark_initializer import spark_initializer
from bdaserviceutils import get_args


def from_spark_to_pandas_df_using_disk(df, path='/tmp/tmp_csv_df'):

    df = df.to_pandas_on_spark()
    df.to_csv(path, header=True, num_files=1, mode="overwrite")

    extension = 'csv'
    os.chdir(path)
    result = glob.glob('*.{}'.format(extension))[0]

    return result

def init_spark():
    return spark_initializer("Test-model", get_args(), additional_config=[('spark.sql.execution.arrow.enabled', True)])


def get_path():
    df = ds_initializer.load_dataset(sc=init_spark(), read_all=False)
    return from_spark_to_pandas_df_using_disk(df)

