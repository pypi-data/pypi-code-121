import os
import time
from io import StringIO  # python3; python2: BytesIO

import boto3
from pandas import ExcelWriter

from zeno_etl_libs.config.common import Config


class S3:
    def __init__(self, bucket_name=None, region=None):
        configobj = Config.get_instance()
        secrets = configobj.get_secrets()
        self.bucket_name = bucket_name or 'aws-glue-temporary-921939243643-ap-south-1'
        self.region = region if region else 'ap-south-1'
        self.aws_access_key_id = secrets['AWS_ACCESS_KEY_ID']
        self.aws_secret_access_key = secrets['AWS_SECRET_ACCESS_KEY_ID']
        self.s3_resource = boto3.resource('s3', self.region, aws_access_key_id=self.aws_access_key_id,
                                          aws_secret_access_key=self.aws_secret_access_key)
        self.s3_client = boto3.client('s3', self.region, aws_access_key_id=self.aws_access_key_id,
                                      aws_secret_access_key=self.aws_secret_access_key)

    def save_df_to_s3(self, df, file_name=None, index_label=False, index=False, header=True):
        file_name = file_name or f"temp_{int(time.time() * 1000)}.csv"
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index_label=index_label, index=index, header=header)
        self.s3_resource.Object(self.bucket_name, file_name).put(Body=csv_buffer.getvalue())
        s3_uri = f"s3://{self.bucket_name}/{file_name}"
        return s3_uri

    def get_file_object(self, uri):
        names = uri.split("//")[-1].split("/")
        self.bucket_name = names[0]
        key = "/".join(names[1:])
        obj = self.s3_resource.Object(self.bucket_name, key).get()
        big_str = obj["Body"].read().decode("utf-8")
        return big_str

    def write_to_db_from_s3_csv(self, table_name, file_s3_uri, db, schema=None):
        if schema:
            table_location = f"""{schema}"."{table_name}"""
        else:
            """ temp tables have session specific schema which has no name """
            table_location = table_name

        query = f"""
            COPY 
                "{table_location}"
            FROM
                '{file_s3_uri}'
            CREDENTIALS 
                'aws_access_key_id={self.aws_access_key_id};aws_secret_access_key={self.aws_secret_access_key}' 
            -- for better copy performance
            COMPUPDATE OFF
            STATUPDATE OFF  
            REGION 'ap-south-1'
            IGNOREHEADER 1
            FORMAT AS csv
            MAXERROR 1 ;
        """
        db.execute(query=query)

    def write_df_to_db(self, df, table_name, db, schema=None):
        file_name = f"temp_{int(time.time() * 1000)}.csv"
        file_s3_uri = self.save_df_to_s3(df=df, file_name=file_name)  # eg. "s3://{self.bucket_name}/df.csv"
        self.write_to_db_from_s3_csv(table_name=table_name, file_s3_uri=file_s3_uri, db=db, schema=schema)
        self.delete_s3_obj(uri=file_s3_uri)

    def write_to_text_file_on_s3(self, file_name):
        file_name = f"temp_{int(time.time() * 1000)}.txt" or file_name
        csv_buffer = StringIO()
        self.s3_resource.Object(self.bucket_name, file_name).put(Body=csv_buffer.getvalue())
        s3_uri = f"s3://{self.bucket_name}/{file_name}"
        return s3_uri

    def write_df_to_excel(self, data, file_name):
        """
        df: data frame
        file_name: with reference to /tmp folder
        sheet_name:
        """
        path = "/".join(os.getcwd().split("/")[:-2]) + "/tmp/"

        if not os.path.exists(path):
            os.mkdir(path, 0o777)

        local_file_full_path = path + file_name
        with ExcelWriter(local_file_full_path) as writer:
            for sheet_name, df in data.items():
                df.to_excel(writer, sheet_name=sheet_name)

        return local_file_full_path

    def write_text_to_file(self, text, file_name):
        path = "/".join(os.getcwd().split("/")[:-2]) + "/tmp/"

        if not os.path.exists(path):
            os.mkdir(path, 0o777)

        local_file_full_path = path + file_name
        file_p = open(local_file_full_path, "w")
        file_p.writelines(text)

        return local_file_full_path

    def upload_file_to_s3(self, file_name):
        local_file_full_path = "/".join(os.getcwd().split("/")[:-2]) + "/tmp/" + file_name
        s3_file_full_path = file_name
        self.s3_client.upload_file(
            Filename=local_file_full_path,
            Bucket=self.bucket_name,
            Key=s3_file_full_path,
        )
        s3_uri = f"s3://{self.bucket_name}/{s3_file_full_path}"
        return s3_uri

    def download_file_from_s3(self, file_name):
        path = "/".join(os.getcwd().split("/")[:-2]) + "/tmp/"
        print(f"path: {path}")
        if not os.path.exists(path):
            os.mkdir(path, 0o777)
        head, tail = os.path.split(file_name)
        local_file_full_path = path + tail
        s3_file_full_path = file_name
        self.s3_client.download_file(
            Bucket=self.bucket_name,
            Key=s3_file_full_path,
            Filename=local_file_full_path
        )
        return local_file_full_path

    def delete_s3_obj(self, uri):
        names = uri.split("//")[-1].split("/")
        self.bucket_name = names[0]
        key = "/".join(names[1:])
        response = self.s3_resource.Object(self.bucket_name, key).delete()
        print(f"S3 object(uri: {uri}) delete response: {response}")

    def move_s3_obj(self, source, target_key):
        try:
            self.s3_client.copy_object(
                Bucket=self.bucket_name,
                CopySource=source,
                Key=target_key
            )
        except self.s3_client.exceptions.ObjectNotInActiveTierError as e:
            print(f"Copying s3 obj failed: {e}")
            raise e

        self.delete_s3_obj(uri=f"s3:/{source}")
