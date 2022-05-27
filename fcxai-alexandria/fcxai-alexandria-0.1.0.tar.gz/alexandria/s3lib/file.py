def write_bytes_to_s3(data, bucket, path, client):
    client.put_object(Bucket=bucket, Key=path, Body=data)


def load_bytes_from_s3(bucket, path, client):
    return client.get_object(Bucket=bucket, Key=path)["Body"].read()
