import boto3
from pandas import DataFrame, read_csv
from io import StringIO


class ConnectS3:

    @staticmethod
    def create_connection(
            aws_access_key_id=None,
            aws_secret_access_key=None,
            region_name=None
    ):
        """
        Create boto connection object

        :return: Connection object
        """

        return boto3.resource(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )

    def read_csv_from_s3(
            self,
            bucket_name=None,
            object_name=None,
            resource=None
    ) -> DataFrame:
        """
        This function returns dataframe object of csv file stored in S3

        :param bucket_name: Name of the bucket where csv is stored
        :param object_name: Path of the object in S3
        :param resource: Connection object
        :return: dataframe object pandas
        """
        content_object = resource.Object(bucket_name, object_name)
        csv_string = content_object.get()['Body'].read().decode('utf - 8')
        df = read_csv(StringIO(csv_string))

        return df

    def write_csv_to_s3(
            self,
            bucket_name=None,
            object_name=None,
            df_to_upload=None,
            resource=None
    ) -> None:
        """
        Function to write csv in S3

        :param bucket_name: Name of the bucket where csv shall be stored
        :param object_name: Path of the object in S3
        :param df_to_upload: dataframe to be stored as csv
        :param resource: Connection object
        :return:
        """
        csv_buffer = StringIO()
        df_to_upload.to_csv(csv_buffer, index=False)
        content_object = resource.Object(bucket_name, object_name)
        content_object.put(Body=csv_buffer.getvalue())
        print('Successfully dumped data into s3')