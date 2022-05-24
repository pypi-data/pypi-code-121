"""Library defining the interface to stress test jobs."""

import time
from datetime import datetime
from typing import Any, Dict, Optional

import grpc
import pandas as pd
from google.protobuf.json_format import MessageToDict
from semver import VersionInfo

from rime_sdk.internal.backend import RIMEBackend
from rime_sdk.internal.protobuf_parser import parse_test_run_metadata
from rime_sdk.protos.jobs.jobs_pb2 import JobMetadata, JobStatus
from rime_sdk.protos.model_testing.model_testing_pb2 import (
    GetLatestLogsRequest,
    GetTestJobRequest,
)
from rime_sdk.protos.test_run_results.test_run_results_pb2 import (
    GetTestRunRequest,
    GetTestRunResponse,
    ListTestCasesRequest,
    ListTestCasesResponse,
)
from rime_sdk.protos.test_run_tracker.test_run_tracker_pb2 import (
    GetOperationStateRequest,
    GetOperationStateResponse,
    OperationStatus,
)
from rime_sdk.protos.test_run_tracker.test_run_tracker_pb2_grpc import (
    TestRunTrackerStub,
)

default_csv_header = ["test_name", "feature(s)", "status"]


class RIMEStressTestJob:
    """An interface to a RIME stress testing job.

    This object provides an interface for monitoring the status of a stress test
    job in the RIME backend.
    """

    def __init__(self, backend: RIMEBackend, job_id: str,) -> None:
        """Create a new RIME Job.

        Args:
            backend: RIMEBackend
                The RIME backend used to query about the status of the job.
            job_id: str
                The identifier for the RIME job that this object monitors.
        """
        self._backend = backend
        self._job_id = job_id

    def __str__(self) -> str:
        """Pretty-print the object."""
        # Ping the backend for the status of the job and detailed info only for
        # succeeded jobs.
        status = self.get_status()
        ret = {
            "job_id": self._job_id,
            "status": status.get("status"),
            "termination_reason": status.get("terminationReason"),
        }
        if status["status"] == JobStatus.Name(JobStatus.JOB_STATUS_SUCCEEDED):
            test_run_res = self.get_test_run_result()
            for k, v in test_run_res.iloc[0].to_dict().items():
                # Omit metrics from the output dictionary.
                if not str(k).startswith("metrics"):
                    ret[k] = v
        return f"RIMEStressTestJob {ret}"

    def __eq__(self, obj: Any) -> bool:
        """Check if this job is equivalent to 'obj'."""
        return isinstance(obj, RIMEStressTestJob) and self._job_id == obj._job_id

    def _get_progress(self, test_tracker: TestRunTrackerStub) -> Optional[str]:
        """Pretty print the progress of the test run."""
        op_res: Optional[GetOperationStateResponse] = None
        try:
            op_req = GetOperationStateRequest(job_id=self._job_id)
            op_res = test_tracker.GetOperationState(op_req)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            else:
                raise e
        if op_res:
            total_batches = len(op_res.test_suite_state.test_batch_states)
            if total_batches == 0:
                return None
            n = sum(
                batch.operation_status == OperationStatus.OPERATION_STATUS_COMPLETED
                for batch in op_res.test_suite_state.test_batch_states
            )
            return "{:<2} / {:>2} tests completed".format(n, total_batches)
        return None

    def get_link(self) -> str:
        """Get the web app URL for a successful stress test job.

        This link directs to your organization's deployment of RIME.
        You can view more detailed information about the results of your stress test\
        in the web app, including helpful visualiziations, key insights, and\
        explanations of test results.

        Note: this is a string that should be copy-pasted into a browser.
        """
        # Retrieve the test run ID iff the job has succeeded.
        test_run_id = self._get_successful_test_run_id()

        # Fetch test run metadata and return a dataframe of the single row.
        req = GetTestRunRequest(test_run_id=test_run_id)
        try:
            with self._backend.get_test_run_results_stub() as results_reader:
                res: GetTestRunResponse = results_reader.GetTestRun(req)
                return res.test_run.metadata.web_app_url.url
        except grpc.RpcError as e:
            raise ValueError(e)

    def _get_successful_test_run_id(self) -> str:
        """Get the test run ID for a successful job.

        Raises:
            ValueError if the job does not have state 'SUCCEEDED.'
        """
        with self._backend.get_model_testing_stub() as model_tester, self._backend.get_test_run_tracker_stub() as test_tracker:  # pylint: disable=line-too-long
            # This first step only prevents a rare case where the RIME engine has
            # signaled the test suite has completed but before the upload has completed.
            job_req = GetTestJobRequest(job_id=self._job_id)
            try:
                job: JobMetadata = model_tester.GetTestJob(job_req).job
            except grpc.RpcError as e:
                # TODO(QuantumWombat): distinguish errors
                raise ValueError(e)
            if job.status != JobStatus.JOB_STATUS_SUCCEEDED:
                raise ValueError(
                    "Job has status {}; it must have status {} to get results".format(
                        JobStatus.Name(job.status),
                        JobStatus.Name(JobStatus.JOB_STATUS_SUCCEEDED),
                    )
                )
            op_req = GetOperationStateRequest(job_id=self._job_id)
            try:
                op_res = test_tracker.GetOperationState(op_req)
            except grpc.RpcError as e:
                # TODO(QuantumWombat): more sophisticated handling of NOT_FOUND.
                raise ValueError(e)
            return op_res.test_suite_state.test_suite_id

    def get_status(
        self,
        verbose: bool = False,
        wait_until_finish: bool = False,
        poll_rate_sec: float = 5.0,
    ) -> Dict:
        """Query the ModelTest service for the job's status.

        This includes flags for blocking until the job is complete and printing
        information to ``stdout``. This method can help with monitoring the
        progress of stress test jobs, because it prints out helpful information
        such as running time and the progress of the test run.

        Arguments:
            verbose: bool
                whether or not to print diagnostic information such as logs.
                If this flag is enabled and the job has failed,
                the logs of the testing engine will be dumped
                to ``stdout`` to help with debuggability.
                Note that these logs have no strict form and will be subject to
                significant change in future versions.
            wait_until_finish: bool
                whether or not to block until the job has succeeded or failed.
                If `verbose` is enabled too, information about the job including
                running time and progress will be printed to ``stdout`` every
                ``poll_rate_sec``.
            poll_rate_sec: float
               the frequency with which to poll the job's status. Units are in seconds.

        Returns:
            A dictionary representing the job's state.

            .. code-block:: python

                {
                "id": str
                "type": str
                "status": str
                "start_time_secs": int64
                "running_time_secs": double
                }

        Example:

        .. code-block:: python

            # Block until this job is finished and dump monitoring info to stdout.
            job_status = job.get_status(verbose=True, wait_until_finish=True)
        """
        # Create backend client stubs to use for the remainder of this session.
        with self._backend.get_model_testing_stub() as model_tester, self._backend.get_test_run_tracker_stub() as test_tracker:  # pylint: disable=line-too-long
            job_req = GetTestJobRequest(job_id=self._job_id)
            try:
                job: JobMetadata = model_tester.GetTestJob(job_req).job
            except grpc.RpcError as e:
                # TODO(QuantumWombat): distinguish errors
                raise ValueError(e)
            if verbose:
                print(
                    "Job '{}' started at {}".format(
                        job.id, datetime.fromtimestamp(job.start_time_secs)
                    )
                )

            # Do not repeat if the job is finished or blocking is disabled.
            while wait_until_finish and not job.status in (
                JobStatus.JOB_STATUS_SUCCEEDED,
                JobStatus.JOB_STATUS_FAILED,
            ):
                time.sleep(poll_rate_sec)
                try:
                    job = model_tester.GetTestJob(job_req).job
                    progress = self._get_progress(test_tracker)
                except grpc.RpcError as e:
                    # TODO(QuantumWombat): distinguish other special errors
                    if e.code() == grpc.StatusCode.UNAVAILABLE:
                        if verbose:
                            print("reconnecting to the RIME backend...")
                        continue
                    raise ValueError(e)
                if verbose:
                    minute, second = divmod(job.running_time_secs, 60)
                    hour, minute = divmod(minute, 60)
                    progress_str = " ({})".format(progress) if progress else ""
                    print(
                        "Status: {}, Running Time: {:02}:{:02}:{:05.2f}{}".format(
                            JobStatus.Name(job.status),
                            int(hour),
                            int(minute),
                            second,
                            progress_str,
                        )
                    )

            # Only get the logs if verbose is enabled and the job has failed, as the
            # primary purpose is debuggability during development.
            if verbose and job.status == JobStatus.JOB_STATUS_FAILED:
                log_req = GetLatestLogsRequest(job_id=self._job_id)
                try:
                    for log_res in model_tester.GetLatestLogs(request=log_req):
                        print(log_res.chunk, end="")
                except grpc.RpcError as e:
                    # TODO(QuantumWombat): distinguish errors
                    raise ValueError(e)

        job_dict = MessageToDict(job)
        return job_dict

    def get_test_cases_result(self, version: Optional[str] = None) -> pd.DataFrame:
        """Retrieve all the test cases for a completed stress test run in a dataframe.

        This gives you the ability to perform granular queries on test cases.
        For example, if you only care about subset performance tests and want to see
        the results on each feature, you can fetch all the test cases in a dataframe,
        then query on that dataframe by test type. This only works on stress test jobs
        that have succeeded.

        Note: this will not work for test runs run on RIME versions <0.14.0.

        Arguments:
            version: Optional[str] = None
                Semantic version of the results to be returned.
                This allows users to pin the version of the results, which is helpful
                if you write any code on top of RIME data. If you upgrade the SDK and
                do not pin the version in your code, it may break because the output
                not guaranteed to be stable across versions.
                The latest output will be returned by default.

        Returns:
            A ``pandas.DataFrame`` object containing the test case results.
            Here is a selected list of columns in the output:
            1. ``test_run_id``: ID of the parent test run.
            2. ``features``: List of features that the test case ran on.
            3. ``test_batch_type``: Type of test that was run (e.g. Subset AUC,\
                Must be Int, etc.).
            4. ``status``: Status of the test case (e.g. Pass, Fail, Skip, etc.).
            5. ``severity``: Metric that denotes the severity of the failure of\
                the test.

        Example:

        .. code-block:: python

            # Wait until the job has finished, since this method only works on
            # SUCCEEDED jobs.
            job.get_status(verbose=True, wait_until_finish=True)
            # Dump the test cases in dataframe ``df``.
            # Pin the version to RIME version 0.14.0.
            df = job.get_test_cases_result(version="0.14.0")
            # Print out the column names and types.
            print(df.columns)
        """
        if version and not VersionInfo.isvalid(version):
            raise ValueError(f"Invalid version string: {version}")

        # Retrieve the test run ID iff the job has succeeded.
        test_run_id = self._get_successful_test_run_id()

        with self._backend.get_test_run_results_stub() as results_reader:
            all_test_cases = []
            # Iterate through the pages of test cases and break at the last page.
            page_token = ""
            while True:
                tc_req = ListTestCasesRequest(
                    test_run_id=test_run_id, page_token=page_token, page_size=20,
                )
                try:
                    res: ListTestCasesResponse = results_reader.ListTestCases(tc_req)
                    tc_dicts = [
                        MessageToDict(
                            tc,
                            including_default_value_fields=True,
                            preserving_proto_field_name=True,
                        )
                        for tc in res.test_cases
                    ]
                    # Concatenate the list of test case dictionaries.
                    all_test_cases += tc_dicts
                    # Advance to the next page of test cases.
                    page_token = res.next_page_token
                except grpc.RpcError as e:
                    if e.code() == grpc.StatusCode.NOT_FOUND:
                        break
                    raise ValueError(e)
                # we've reached the last page of test cases.
                if len(all_test_cases) > 0 and page_token == "":
                    break

            # Drop selected columns from test cases dataframe.
            columns_to_drop = ["importance_score"]
            return pd.DataFrame(all_test_cases).drop(columns=columns_to_drop)

    def get_test_run_result(self, version: Optional[str] = None) -> pd.DataFrame:
        """Retrieve high level summary information for a complete stress test run in a\
        single-row dataframe.

        This dataframe includes information such as model metrics on the reference and\
        evalulation datasets, overall RIME results such as severity across tests,\
        and high level metadata such as the project ID and model task.

        By concatenating these rows together, this allows you to build a table of test
        run results for sake of comparison. This only works on stress test jobs that
        have succeeded.

        Note: this does not work on <0.14.0 RIME test runs.

        Arguments:
            version: Optional[str] = None`
                Semantic version of the results to be returned.
                This allows users to pin the version of the results, which is helpful
                if you write any code on top of RIME data. If you upgrade the SDK and
                do not pin the version in your code, it may break because the output
                not guaranteed to be stable across versions.
                The latest output will be returned by default.

        Returns:
            A `pandas.DataFrame` object containing the test run result.
            There are a lot of columns, so it is worth viewing them with the `.columns`
            method to see what they are. Generally, these columns have information
            about the model and datasets as well as summary statistics like the number
            of failing test cases or number of high severity test cases.

        Example:

        .. code-block:: python

            # Wait until the job has finished, since this method only works on
            # succeeded jobs.
            job.get_status(verbose=True, wait_until_finish=True)
            # Dump the test cases in dataframe ``df``.
            # Pin the version to RIME version 0.14.0.
            df = job.get_test_run_result(version="0.14.0")
            # Print out the column names and types.
            print(df.columns)
        """
        if version and not VersionInfo.isvalid(version):
            raise ValueError(f"Invalid version string: {version}")

        # Retrieve the test run ID iff the job has succeeded.
        test_run_id = self._get_successful_test_run_id()

        with self._backend.get_test_run_results_stub() as results_reader:
            # Fetch test run metadata and return a dataframe of the single row.
            req = GetTestRunRequest(test_run_id=test_run_id)
            try:
                res: GetTestRunResponse = results_reader.GetTestRun(req)
                # Use utility funtion for converting Protobuf to a dataframe.
                return parse_test_run_metadata(res.test_run, version=version)
            except grpc.RpcError as e:
                raise ValueError(e)
