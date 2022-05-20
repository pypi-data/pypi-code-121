# autogenerated
# mypy: ignore-errors
# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from rime_sdk.protos.test_run_results import test_run_results_pb2 as protos_dot_test__run__results_dot_test__run__results__pb2


class ResultsReaderStub(object):
    """All fields of entity messages are assumed to be immutable unless otherwise
    specified.
    For example, we mark the "resolved" field of TestCase as mutable
    with a comment, and thus it is present in the TestCaseWriteMask.

    One set of CRUD RPCs that operate the entire test run tree is too
    complicated to use, so we chose to have CRUD endpoints at each level
    of the test run endpoints.
    Clients can fetch individual nodes of the test run tree more easily and
    we can worry less about running into the 4mb Protobuf message size limit.

    Create methods allow immutable methods to be set and thus should only be used
    by clients with appropriate privileges.
    Internal services such as the RIME engine can use these RPCs.

    ResultsReader is a service for querying test run results.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetTestRun = channel.unary_unary(
                '/rime.ResultsReader/GetTestRun',
                request_serializer=protos_dot_test__run__results_dot_test__run__results__pb2.GetTestRunRequest.SerializeToString,
                response_deserializer=protos_dot_test__run__results_dot_test__run__results__pb2.GetTestRunResponse.FromString,
                )
        self.ListTestBatches = channel.unary_unary(
                '/rime.ResultsReader/ListTestBatches',
                request_serializer=protos_dot_test__run__results_dot_test__run__results__pb2.ListTestBatchesRequest.SerializeToString,
                response_deserializer=protos_dot_test__run__results_dot_test__run__results__pb2.ListTestBatchesResponse.FromString,
                )
        self.ListTestCases = channel.unary_unary(
                '/rime.ResultsReader/ListTestCases',
                request_serializer=protos_dot_test__run__results_dot_test__run__results__pb2.ListTestCasesRequest.SerializeToString,
                response_deserializer=protos_dot_test__run__results_dot_test__run__results__pb2.ListTestCasesResponse.FromString,
                )


class ResultsReaderServicer(object):
    """All fields of entity messages are assumed to be immutable unless otherwise
    specified.
    For example, we mark the "resolved" field of TestCase as mutable
    with a comment, and thus it is present in the TestCaseWriteMask.

    One set of CRUD RPCs that operate the entire test run tree is too
    complicated to use, so we chose to have CRUD endpoints at each level
    of the test run endpoints.
    Clients can fetch individual nodes of the test run tree more easily and
    we can worry less about running into the 4mb Protobuf message size limit.

    Create methods allow immutable methods to be set and thus should only be used
    by clients with appropriate privileges.
    Internal services such as the RIME engine can use these RPCs.

    ResultsReader is a service for querying test run results.
    """

    def GetTestRun(self, request, context):
        """
        ----- Read operations for test runs -----
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ListTestBatches(self, request, context):
        """
        ----- Read operations for test batches -----

        Size-unbounded data like failing rows and sensitivity will be returned
        in separate endpoints.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ListTestCases(self, request, context):
        """
        ----- Read operations for test cases -----
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ResultsReaderServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetTestRun': grpc.unary_unary_rpc_method_handler(
                    servicer.GetTestRun,
                    request_deserializer=protos_dot_test__run__results_dot_test__run__results__pb2.GetTestRunRequest.FromString,
                    response_serializer=protos_dot_test__run__results_dot_test__run__results__pb2.GetTestRunResponse.SerializeToString,
            ),
            'ListTestBatches': grpc.unary_unary_rpc_method_handler(
                    servicer.ListTestBatches,
                    request_deserializer=protos_dot_test__run__results_dot_test__run__results__pb2.ListTestBatchesRequest.FromString,
                    response_serializer=protos_dot_test__run__results_dot_test__run__results__pb2.ListTestBatchesResponse.SerializeToString,
            ),
            'ListTestCases': grpc.unary_unary_rpc_method_handler(
                    servicer.ListTestCases,
                    request_deserializer=protos_dot_test__run__results_dot_test__run__results__pb2.ListTestCasesRequest.FromString,
                    response_serializer=protos_dot_test__run__results_dot_test__run__results__pb2.ListTestCasesResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'rime.ResultsReader', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ResultsReader(object):
    """All fields of entity messages are assumed to be immutable unless otherwise
    specified.
    For example, we mark the "resolved" field of TestCase as mutable
    with a comment, and thus it is present in the TestCaseWriteMask.

    One set of CRUD RPCs that operate the entire test run tree is too
    complicated to use, so we chose to have CRUD endpoints at each level
    of the test run endpoints.
    Clients can fetch individual nodes of the test run tree more easily and
    we can worry less about running into the 4mb Protobuf message size limit.

    Create methods allow immutable methods to be set and thus should only be used
    by clients with appropriate privileges.
    Internal services such as the RIME engine can use these RPCs.

    ResultsReader is a service for querying test run results.
    """

    @staticmethod
    def GetTestRun(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/rime.ResultsReader/GetTestRun',
            protos_dot_test__run__results_dot_test__run__results__pb2.GetTestRunRequest.SerializeToString,
            protos_dot_test__run__results_dot_test__run__results__pb2.GetTestRunResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ListTestBatches(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/rime.ResultsReader/ListTestBatches',
            protos_dot_test__run__results_dot_test__run__results__pb2.ListTestBatchesRequest.SerializeToString,
            protos_dot_test__run__results_dot_test__run__results__pb2.ListTestBatchesResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ListTestCases(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/rime.ResultsReader/ListTestCases',
            protos_dot_test__run__results_dot_test__run__results__pb2.ListTestCasesRequest.SerializeToString,
            protos_dot_test__run__results_dot_test__run__results__pb2.ListTestCasesResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
