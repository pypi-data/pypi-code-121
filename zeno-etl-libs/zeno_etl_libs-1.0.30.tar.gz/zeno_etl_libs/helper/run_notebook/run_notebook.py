import errno
import json
import os
import re
import time
from subprocess import Popen
from shlex import split
from zeno_etl_libs.config.common import Config
import boto3


def ensure_session(session=None):
    """If session is None, create a default session and return it. Otherwise return the session passed in"""
    if session is None:
        session = boto3.session.Session()
    return session


def get_execution_role(session):
    """Return the role ARN whose credentials are used to call the API.
    Throws an exception if the current AWS identity is not a role.

    Returns:
        (str): The role ARN
    """
    assumed_role = session.client("sts").get_caller_identity()["Arn"]
    if ":user/" in assumed_role:
        user_name = assumed_role[assumed_role.rfind("/") + 1:]
        raise ValueError(
            f"You are running as the IAM user '{user_name}'. You must supply an IAM role to run SageMaker jobs."
        )

    if "AmazonSageMaker-ExecutionRole" in assumed_role:
        role = re.sub(
            r"^(.+)sts::(\d+):assumed-role/(.+?)/.*$",
            r"\1iam::\2:role/service-role/\3",
            assumed_role,
        )
        return role

    role = re.sub(
        r"^(.+)sts::(\d+):assumed-role/(.+?)/.*$", r"\1iam::\2:role/\3", assumed_role
    )

    # Call IAM to get the role's path
    role_name = role[role.rfind("/") + 1:]
    arn = session.client("iam").get_role(RoleName=role_name)["Role"]["Arn"]

    if ":role/" in arn:
        return arn
    message = "The current AWS identity is not a role: {}, therefore it cannot be used as a SageMaker execution role"
    raise ValueError(message.format(arn))


def execute_notebook(
    *,
    image="notebook-runner",
    input_path,
    output_prefix,
    notebook,
    parameters,
    role="arn:aws:iam::921939243643:role/service-role/AmazonSageMaker-ExecutionRole-20220412T145187",
    instance_type="ml.m5.large",
    session,
    in_vpc=True,
    env="stage",
    timeout_in_sec=7200
):
    session = ensure_session(session)

    configobj = Config.get_instance()
    secrets = configobj.get_secrets()

    if not role:
        role = get_execution_role(session)
    elif "/" not in role:
        account = session.client("sts").get_caller_identity()["Account"]
        role = "arn:aws:iam::{}:role/{}".format(account, role)

    if "/" not in image:
        # account = session.client("sts").get_caller_identity()["Account"]
        # region = session.region_name
        account = secrets['AWS_ACCOUNT_ID']
        region = secrets['AWS_REGION']
        image = "{}.dkr.ecr.{}.amazonaws.com/{}:latest".format(account, region, image)

    if notebook == None:
        notebook = input_path

    base = os.path.basename(notebook)
    nb_name, nb_ext = os.path.splitext(base)
    timestamp = time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())

    job_name = (
            (env + "-" + re.sub(r"[^-a-zA-Z0-9]", "-", nb_name))[: 62 - len(timestamp)]
            + "-"
            + timestamp
    )
    input_directory = "/opt/ml/processing/input/"
    local_input = input_directory + os.path.basename(input_path)
    result = "{}-{}{}".format(nb_name, timestamp, nb_ext)
    local_output = "/opt/ml/processing/output/"

    api_args = {
        "ProcessingInputs": [
            {
                "InputName": "notebook",
                "S3Input": {
                    "S3Uri": input_path,
                    "LocalPath": input_directory,
                    "S3DataType": "S3Prefix",
                    "S3InputMode": "File",
                    "S3DataDistributionType": "FullyReplicated",
                },
            },
        ],
        "ProcessingOutputConfig": {
            "Outputs": [
                {
                    "OutputName": "result",
                    "S3Output": {
                        "S3Uri": output_prefix,
                        "LocalPath": local_output,
                        "S3UploadMode": "EndOfJob",
                    },
                },
            ],
        },
        "ProcessingJobName": job_name,
        "ProcessingResources": {
            "ClusterConfig": {
                "InstanceCount": 1,
                "InstanceType": instance_type,
                "VolumeSizeInGB": 40,
            }
        },
        "StoppingCondition": {"MaxRuntimeInSeconds": timeout_in_sec},
        "AppSpecification": {
            "ImageUri": image,
            "ContainerArguments": [
                "run_notebook",
            ],
        },
        "RoleArn": role,
        "Environment": {},
    }
    if in_vpc:
        if env == "stage":
            api_args["NetworkConfig"] = {
                'EnableInterContainerTrafficEncryption': False,
                'EnableNetworkIsolation': False,
                'VpcConfig': {
                    'SecurityGroupIds': [
                        "sg-0101c938006dab959"
                    ],
                    'Subnets': [
                        'subnet-0446eb5f39df5ceca'
                    ]
                }
            }
        elif env == "prod":
            api_args["NetworkConfig"] = {
                'EnableInterContainerTrafficEncryption': False,
                'EnableNetworkIsolation': False,
                'VpcConfig': {
                    'SecurityGroupIds': [
                        "sg-08f218fe121e66d6e"
                    ],
                    'Subnets': [
                        'subnet-0e5470f4100505343'
                    ]
                }
            }
        else:
            raise Exception(f"env(ie. stage, prod) input is must if is_vpc = True")

    api_args["Environment"]["PAPERMILL_INPUT"] = local_input
    api_args["Environment"]["PAPERMILL_OUTPUT"] = local_output + result
    if os.environ.get("AWS_DEFAULT_REGION") is not None:
        api_args["Environment"]["AWS_DEFAULT_REGION"] = os.environ["AWS_DEFAULT_REGION"]
    api_args["Environment"]["PAPERMILL_PARAMS"] = json.dumps(parameters)
    api_args["Environment"]["PAPERMILL_NOTEBOOK_NAME"] = notebook

    api_args["Environment"]["AWS_ACCESS_KEY_ID"] = secrets["AWS_ACCESS_KEY_ID"]
    api_args["Environment"]["AWS_SECRET_ACCESS_KEY"] = secrets["AWS_SECRET_ACCESS_KEY_ID"]
    api_args["Environment"]["REGION_NAME"] = "ap-south-1"

    client = boto3.client("sagemaker")
    result = client.create_processing_job(**api_args)
    job_arn = result["ProcessingJobArn"]
    job = re.sub("^.*/", "", job_arn)
    return job


def default_bucket():
    return "sagemaker-ap-south-1-921939243643"


def upload_notebook(notebook, session=None):
    """Uploads a notebook to S3 in the default SageMaker Python SDK bucket for
    this user. The resulting S3 object will be named "s3://<bucket>/papermill-input/notebook-YYYY-MM-DD-hh-mm-ss.ipynb".

    Args:
      notebook (str):
        The filename of the notebook you want to upload. (Required)
      session (boto3.Session):
        A boto3 session to use. Will create a default session if not supplied. (Default: None)

    Returns:
      The resulting object name in S3 in URI format.
    """
    with open(notebook, "rb") as f:
        return upload_fileobj(f, session)


def upload_fileobj(notebook_fileobj, session=None):
    """Uploads a file object to S3 in the default SageMaker Python SDK bucket for
    this user. The resulting S3 object will be named "s3://<bucket>/papermill-input/notebook-YYYY-MM-DD-hh-mm-ss.ipynb".

    Args:
      notebook_fileobj (fileobj):
        A file object (as returned from open) that is reading from the notebook you want to upload. (Required)
      session (boto3.Session):
        A boto3 session to use. Will create a default session if not supplied. (Default: None)

    Returns:
      The resulting object name in S3 in URI format.
    """

    session = ensure_session(session)
    snotebook = "notebook-{}.ipynb".format(
        time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())
    )

    s3 = session.client("s3")
    key = "papermill_input/" + snotebook
    bucket = default_bucket()
    s3path = "s3://{}/{}".format(bucket, key)
    s3.upload_fileobj(notebook_fileobj, bucket, key)

    return s3path


def get_output_prefix():
    """Returns an S3 prefix in the Python SDK default bucket."""
    return "s3://{}/papermill_output".format(default_bucket())


def wait_for_complete(job_name, progress=True, sleep_time=10, session=None):
    """Wait for a notebook execution job to complete.

    Args:
      job_name (str):
        The name of the SageMaker Processing Job executing the notebook. (Required)
      progress (boolean):
        If True, print a period after every poll attempt. (Default: True)
      sleep_time (int):
        The number of seconds between polls. (Default: 10)
      session (boto3.Session):
        A boto3 session to use. Will create a default session if not supplied. (Default: None)

    Returns:
      A tuple with the job status and the failure message if any.
    """

    session = ensure_session(session)
    client = session.client("sagemaker")
    done = False
    while not done:
        if progress:
            print(".", end="")
        desc = client.describe_processing_job(ProcessingJobName=job_name)
        status = desc["ProcessingJobStatus"]
        if status != "InProgress":
            done = True
        else:
            time.sleep(sleep_time)
    if progress:
        print()
    return status, desc.get("FailureReason")


def download_notebook(job_name, output=".", session=None):
    """Download the output notebook from a previously completed job.

    Args:
      job_name (str): The name of the SageMaker Processing Job that executed the notebook. (Required)
      output (str): The directory to copy the output file to. (Default: the current working directory)
      session (boto3.Session):
        A boto3 session to use. Will create a default session if not supplied. (Default: None)

    Returns:
      The filename of the downloaded notebook.
    """
    session = ensure_session(session)
    client = session.client("sagemaker")
    desc = client.describe_processing_job(ProcessingJobName=job_name)

    prefix = desc["ProcessingOutputConfig"]["Outputs"][0]["S3Output"]["S3Uri"]
    notebook = os.path.basename(desc["Environment"]["PAPERMILL_OUTPUT"])
    s3path = "{}/{}".format(prefix, notebook)

    if not os.path.exists(output):
        try:
            os.makedirs(output)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    p1 = Popen(split("aws s3 cp --no-progress {} {}/".format(s3path, output)))
    p1.wait()
    return "{}/{}".format(output.rstrip("/"), notebook)


def run_notebook(
    image,
    notebook,
    parameters={},
    role=None,
    instance_type="ml.m5.large",
    output_prefix=None,
    output=".",
    session=None,
    in_vpc=False,
    env="stage",
    timeout_in_sec=7200
):
    """Run a notebook in SageMaker Processing producing a new output notebook.

    Args:
        image (str): The ECR image that defines the environment to run the job (required).
        notebook (str): The local notebook to upload and run (required).
        parameters (dict): The dictionary of parameters to pass to the notebook (default: {}).
        role (str): The name of a role to use to run the notebook (default: calls get_execution_role()).
        instance_type (str): The SageMaker instance to use for executing the job (default: ml.m5.large).
        output_prefix (str): The prefix path in S3 for where to store the output notebook
                             (default: determined based on SageMaker Python SDK)
        output (str): The directory to copy the output file to (default: the current working directory).
        session (boto3.Session): The boto3 session to use. Will create a default session if not supplied (default: None).

    Returns:
        A tuple with the processing job name, the job status, the failure reason (or None) and the the path to
        the result notebook. The output notebook name is formed by adding a timestamp to the original notebook name.
    """
    session = ensure_session(session)
    if output_prefix is None:
        output_prefix = get_output_prefix()
    s3path = upload_notebook(notebook, session)
    job_name = execute_notebook(
        image=image,
        input_path=s3path,
        output_prefix=output_prefix,
        notebook=notebook,
        parameters=parameters,
        role="arn:aws:iam::921939243643:role/service-role/AmazonSageMaker-ExecutionRole-20220412T145187",
        instance_type=instance_type,
        session=session,
        in_vpc=in_vpc,
        env=env,
        timeout_in_sec=timeout_in_sec
    )
    print("Job {} started".format(job_name))
    status, failure_reason = wait_for_complete(job_name)
    if status == "Completed":
        local = download_notebook(job_name, output=output)
    else:
        local = None
    return (job_name, status, local, failure_reason)


if __name__ == '__main__':
    # run_notebook(
    #     image="notebook-runner",
    #     notebook="send-glue-job-logs.ipynb",
    #     role="arn:aws:iam::921939243643:role/service-role/AmazonSageMaker-ExecutionRole-20220412T145187",
    #     parameters={"job_name": "prod-8-sales"},
    #     in_vpc=False
    # )
    run_notebook(
        notebook="redshift-write-demo.ipynb",
        parameters={"env": "stage"},
        in_vpc=True,
        env="stage"
    )
    # run_notebook(
    #     image="notebook-runner",
    #     notebook="s3_read_write.ipynb",
    #     role="arn:aws:iam::921939243643:role/service-role/AmazonSageMaker-ExecutionRole-20220412T145187",
    #     in_vpc=False
    # )

    # run_notebook(
    #     image="notebook-runner",
    #     notebook="ml-demo.ipynb",
    #     role="arn:aws:iam::921939243643:role/service-role/AmazonSageMaker-ExecutionRole-20220412T145187",
    #     in_vpc=True
    # )
