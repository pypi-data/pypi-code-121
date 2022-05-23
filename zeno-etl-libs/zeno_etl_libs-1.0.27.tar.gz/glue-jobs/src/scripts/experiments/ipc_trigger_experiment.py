import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
import boto3
import json
import os
import requests

sys.path.append('../../../..')
from zeno_etl_libs.helper.run_notebook import run_notebook

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'env', 'parameters', 'script_name', 'script_location', 'in_vpc'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
env = args['env']
parameters = args['parameters']
parameters = json.loads(parameters)[0]
parameters['env'] = env
script_name = args['script_name']
script_location = args['script_location']
in_vpc = args['in_vpc']
os.environ['env'] = env
run_notebook.execute_notebook(
        image = env + "-notebook-runner",
        input_path=f"s3://aws-{env}-glue-assets-921939243643-ap-south-1/artifact/ipc-jobs/scripts/" + script_location + "/" + script_name,
        output_prefix=run_notebook.get_output_prefix(),
        notebook=script_location + '/' + script_name,
        parameters=parameters,
        role="arn:aws:iam::921939243643:role/service-role/AmazonSageMaker-ExecutionRole-20220412T145187",
        instance_type="ml.m5.large",
        session=None,
        in_vpc=in_vpc,
        timeout_in_sec=3600
    )
job.init(args['JOB_NAME'], args)
job.commit()