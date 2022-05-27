import pickle
import boto3
from pandas import DataFrame, read_csv
from io import StringIO
import os
import logging
logging.basicConfig(level=logging.INFO)

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
        csv_name = os.path.split(object_name)[1]
        logging.info("Successfully dumped " + csv_name + " data into s3")

    def read_pkl_from_S3(
            self,
            bucket_name=None,
            object_name=None,
            resource=None
    ):
        """
        Function to write pkl in S3
        :param bucket_name: Name of the bucket where pkl shall be stored
        :param object_name: Path of the object in S3
        :param resource: Connection object
        :return: pkl object
        """
        try:
            response = resource.Bucket(bucket_name).Object(object_name).get()
            body_string = response['Body'].read()
            loaded_pickle = pickle.loads(body_string)
            return loaded_pickle
        except:
            logging.info("Unable to find file {}. No such file exists".format(object_name))

    def write_pkl_to_s3(
            self,
            bucket_name=None,
            object_name=None,
            data=None,
            resource=None
    ) -> None:
        """
        Function to write pkl in S3

        :param bucket_name: Name of the bucket where pkl shall be stored
        :param object_name: Path of the object in S3
        :param data: file to be stored as pkl, like dataframe, dict, list
        :param resource: Connection object
        :return: None
        """
        try:
            pkl_obj = pickle.dumps(data)
            resource.Object(bucket_name, object_name).put(Body=pkl_obj)
            pkl_name = os.path.split(object_name)[1]
            logging.info("Successfully dumped " + pkl_name + " data into s3")
        except Exception as e:
            logging.info(f"Error while dumping {object_name} to S3, Exception: {e}")