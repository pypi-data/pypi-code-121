from io import StringIO

import pandas as pd


def write_to_s3(df, bucket, path, client):
    with StringIO() as csv_buffer:
        df.to_csv(csv_buffer, index=False)

        client.put_object(Bucket=bucket, Key=path, Body=csv_buffer.getvalue())


def load_from_s3(bucket, path, client):
    obj = client.get_object(Bucket=bucket, Key=path)
    body = obj["Body"]
    csv_string = body.read().decode("utf-8")
    df = pd.read_csv(StringIO(csv_string))
    return df
