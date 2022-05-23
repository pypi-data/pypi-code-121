import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
import json
import os

sys.path.append('../../../..')
from zeno_etl_libs.helper.run_notebook import run_notebook
from zeno_etl_libs.logger import get_logger

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'env', 'in_vpc', 'instance_type', 'timeout_in_sec', 'parameters', 'script_name', 'script_location'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
env = args['env']
os.environ['env'] = env
logger = get_logger()
in_vpc = args['in_vpc']
instance_type = args['instance_type']
timeout_in_sec = args['timeout_in_sec']
parameters = args['parameters']
parameters = json.loads(parameters)
logger.info(type(parameters))
parameters['env'] = env
script_name = args['script_name']
script_location = args['script_location']
run_notebook.execute_notebook(
        image = env + "-notebook-runner",
        input_path=f"s3://aws-{env}-glue-assets-921939243643-ap-south-1/artifact/sagemaker-jobs/scripts/" + script_location + "/" + script_name,
        output_prefix=run_notebook.get_output_prefix(),
        notebook=script_location + '/' + script_name,
        parameters=parameters,
        role="arn:aws:iam::921939243643:role/service-role/AmazonSageMaker-ExecutionRole-20220412T145187",
        env=env,
        instance_type=instance_type,
        session=None,
        in_vpc=in_vpc,
        timeout_in_sec=int(timeout_in_sec)
    )
job.init(args['JOB_NAME'], args)
job.commit()