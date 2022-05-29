from datetime import timedelta

import minio

from licsber.github import get_secret


class S3Sign:
    def __init__(
            self,
            url: str = 'https://' + get_secret('L_S3_ENDPOINT'),
            access_key: str = get_secret('L_S3_ACCESS'),
            secret_key: str = get_secret('L_S3_SECRET'),
            region: str = ''
    ):
        self.url = url
        self.region = region
        self.cred = minio.api.StaticProvider(access_key, secret_key).retrieve()

    def get(self, bucket: str, path: str, expires: timedelta = timedelta(minutes=5)):
        url = minio.api.BaseURL(self.url, self.region).build(
            method='GET',
            region=self.region,
            bucket_name=bucket,
            object_name=path,
        )

        url = minio.api.presign_v4(
            method='GET',
            url=url,
            region=self.region,
            credentials=self.cred,
            date=minio.api.time.utcnow(),
            expires=int(expires.total_seconds()),
        )
        return minio.api.urlunsplit(url)
