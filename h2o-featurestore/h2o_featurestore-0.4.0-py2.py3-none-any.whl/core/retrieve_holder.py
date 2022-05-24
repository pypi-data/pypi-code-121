import os
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

import requests

from . import CoreService_pb2 as pb
from .commons.spark_utils import SparkUtils
from .job_info import JobInfo


class RetrieveAsLinksCommon:
    def _get_job(self, job_id):
        return self._stub.GetJob(job_id)

    def _get_retrieve_links_output(self, job_id):
        return self._stub.GetRetrieveAsLinksJobOutput(job_id)

    def download(self, output_dir=None):
        info = JobInfo(self._stub, self._job_id)
        while not self._get_job(self._job_id).done:
            info.show_progress()
            time.sleep(2)
        info.show_progress()  # there is possibility that some progress was pushed before finishing job
        retrieve_as_links_response = self._get_retrieve_links_output(self._job_id)
        return RetrieveAsLinksCommon._download_all(
            output_dir, retrieve_as_links_response.download_links
        )

    def download_async(self, output_dir=None):
        future = self._thread_pool.submit(self.download, output_dir)
        return DownloadFuture(future)

    @staticmethod
    def _download_all(output_dir, download_links):
        if output_dir is None:
            output_dir = tempfile.mkdtemp()
        for idx, path in list(enumerate(download_links)):
            dest = os.path.join(output_dir, "part_" + str(idx) + ".parquet")
            RetrieveAsLinksCommon._download_single(dest, path)
        return output_dir

    @staticmethod
    def _download_single(dest, origin):
        with requests.get(origin, stream=True) as r:
            r.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return dest


class RetrieveHolder(RetrieveAsLinksCommon):
    def __init__(self, stub, feature_set, start_date_time, end_date_time, ingest_id):
        self._stub = stub
        self._thread_pool = ThreadPoolExecutor(5)
        self._feature_set = feature_set
        self._start_date_time = start_date_time
        self._end_date_time = end_date_time
        self._retrieve_as_spark_response = None
        self._job_id = None
        self._ingest_id = ingest_id

    def _start_retrieve_links_job(self):
        request = self._create_retrieve_request()
        return self._stub.StartRetrieveAsLinksJob(request)

    def download(self, output_dir=None):
        if not self._job_id:
            self._job_id = self._start_retrieve_links_job()
        return super(RetrieveHolder, self).download(output_dir)

    def download_async(self, output_dir=None):
        if not self._job_id:
            self._job_id = self._start_retrieve_links_job()
        return super(RetrieveHolder, self).download_async(output_dir)

    def _start_preview_job(self, num_rows):
        request = pb.PreviewRequest()
        request.feature_set.CopyFrom(self._feature_set)
        if self._start_date_time is not None:
            request.start_date_time = self._start_date_time
        if self._end_date_time is not None:
            request.end_date_time = self._end_date_time
        request.num_rows = num_rows
        request.ingest_id = self._ingest_id
        return self._stub.StartPreviewJob(request)

    def preview(self, num_rows=10):
        if num_rows > 100:
            print(
                "Preview can retrieve at most 100 rows. Please try with a lesser value."
            )
            return

        if not self._job_id:
            self._job_id = self._start_preview_job(num_rows)

        info = JobInfo(self._stub, self._job_id)
        while not self._get_job(self._job_id).done:
            info.show_progress()
            time.sleep(2)
        info.show_progress()  # there is possibility that some progress was pushed before finishing job
        resp = self._stub.GetPreviewJobOutput(self._job_id)
        print(resp.result)

    def as_spark_frame(self, spark_session):
        from pyspark.sql.functions import (
            col,
            from_utc_timestamp,
            lit,
            to_timestamp,
            unix_timestamp,
        )

        if self._retrieve_as_spark_response is None:
            request = self._create_retrieve_request(spark_session)
            self._retrieve_as_spark_response = self._stub.RetrieveAsSpark(request)
        resp = self._retrieve_as_spark_response
        spark_session.conf.set("ai.h2o.featurestore.sessionId", resp.session_id)
        SparkUtils.configure_user_spark(spark_session)
        for k, v in resp.options.items():
            spark_session.conf.set(k, v)
        df = spark_session.read.format("delta").load(resp.cache_path)
        retrieve_scope = resp.retrieve_scope
        start_timestamp = retrieve_scope.start_date_time.seconds
        end_timestamp = retrieve_scope.end_date_time.seconds
        timestamp_col = "timestamp_" + str(round(time.time() * 1000))
        if self._ingest_id:
            output_df = df.filter(col("ingest_id") == lit(self._ingest_id))
        elif self._feature_set.time_travel_column:
            output_df = (
                df.withColumn(
                    timestamp_col,
                    unix_timestamp(
                        from_utc_timestamp(
                            to_timestamp(
                                col("`" + self._feature_set.time_travel_column + "`"),
                                self._feature_set.time_travel_column_format,
                            ),
                            spark_session.conf.get("spark.sql.session.timeZone"),
                        )
                    ),
                )
                .filter(col(timestamp_col) <= end_timestamp)
                .filter(col(timestamp_col) >= start_timestamp)
            ).drop(timestamp_col)
        else:
            output_df = df.filter(
                col("time_travel_column_auto_generated") <= end_timestamp
            ).filter(col("time_travel_column_auto_generated") >= start_timestamp)
        return output_df.drop("ingest_id")

    def _create_retrieve_request(self, spark_session=None):
        session_id = ""
        if spark_session is not None:
            session_id = spark_session.conf.get("ai.h2o.featurestore.sessionId", "")
        request = pb.RetrieveRequest()
        request.feature_set.CopyFrom(self._feature_set)
        request.session_id = session_id
        if self._start_date_time is not None:
            request.start_date_time = self._start_date_time
        if self._end_date_time is not None:
            request.end_date_time = self._end_date_time
        request.ingest_id = self._ingest_id
        return request


class DownloadFuture:
    def __init__(self, future):
        self._future = future
        self._result = None

    def is_done(self) -> bool:
        return self._future.done()

    def get_result(self):
        if not self._result:
            if not self.is_done():
                raise Exception("Job has not finished yet!")
            self._result = self._future.result()
        return self._result
