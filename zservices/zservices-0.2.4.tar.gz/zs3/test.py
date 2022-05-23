from zs3 import s3

# variables for testing
connection_params = {
    'region': '',
    's3_key_id': '',
    's3_key_secret': '',
    's3_upload_bucket_name': '',
    's3_bucket_name': ''
}
bucket_name = ""
upload_from_url = ""
upload_from_file = ""
s3_conn = s3.S3(connection_params)


# testing return values
try:
    t1 = s3_conn.url_upload_to_s3(upload_from_url, object_id="test1", bucket='')
    print(f"success: {t1}")
except Exception as e:
    print(e)

try:
    t2 = s3_conn.file_upload_to_s3(upload_from_file, object_id="test2", bucket='')
    print(f"success: {t2}")
except Exception as e:
    print(e)
