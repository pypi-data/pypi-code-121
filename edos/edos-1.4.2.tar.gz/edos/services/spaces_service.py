import boto3
from botocore.exceptions import ClientError

from edos.exceptions import SpaceCreationError
from edos.settings import conf


class SpacesService:
    def __init__(self):
        session = boto3.session.Session()
        self.client = session.client(
            "s3",
            region_name=conf.AWS_REGION,
            endpoint_url=conf.AWS_ENDPOINT_URL,
            aws_access_key_id=conf.AWS_CONFIG.get("aws_access_key"),
            aws_secret_access_key=conf.AWS_CONFIG.get("aws_secret_key"),
        )

    def get_spaces(self) -> list[str]:
        response = self.client.list_buckets()
        return [space["Name"] for space in response["Buckets"]]

    def create_space(self, name: str):
        try:
            self.client.create_bucket(Bucket=name)
        except ClientError as e:
            raise SpaceCreationError(str(e))
