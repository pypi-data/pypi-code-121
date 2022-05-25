from typing import Iterator

from google.protobuf.empty_pb2 import Empty
from ondewo.utils.base_services_interface import BaseServicesInterface

from ondewo.s2t.speech_to_text_pb2 import (
    ListS2tDomainsRequest,
    ListS2tDomainsResponse,
    ListS2tLanguagesRequest,
    ListS2tLanguagesResponse,
    ListS2tPipelinesRequest,
    ListS2tPipelinesResponse,
    S2tPipelineId,
    Speech2TextConfig,
    TranscribeFileRequest,
    TranscribeFileResponse,
    TranscribeStreamRequest,
    TranscribeStreamResponse,
)
from ondewo.s2t.speech_to_text_pb2_grpc import Speech2TextStub


class Speech2Text(BaseServicesInterface):
    """
    Exposes the s2t endpoints of ONDEWO s2t in a user-friendly way.

    See speech_to_text.proto.
    """

    @property
    def stub(self) -> Speech2TextStub:
        stub: Speech2TextStub = Speech2TextStub(channel=self.grpc_channel)
        return stub

    def transcribe_file(self, request: TranscribeFileRequest) -> TranscribeFileResponse:
        response: TranscribeFileResponse = self.stub.TranscribeFile(request)
        return response

    def transcribe_stream(
        self,
        request_iterator: Iterator[TranscribeStreamRequest],
    ) -> Iterator[TranscribeStreamResponse]:
        response: Iterator[TranscribeStreamResponse] = self.stub.TranscribeStream(request_iterator)
        return response

    def get_s2t_pipeline(self, request: S2tPipelineId) -> Speech2TextConfig:
        response: Speech2TextConfig = self.stub.GetS2tPipeline(request)
        return response

    def create_s2t_pipeline(self, request: Speech2TextConfig) -> S2tPipelineId:
        response: S2tPipelineId = self.stub.CreateS2tPipeline(request)
        return response

    def delete_s2t_pipeline(self, request: S2tPipelineId) -> Empty:
        response: Empty = self.stub.DeleteS2tPipeline(request)
        return response

    def update_s2t_pipeline(self, request: Speech2TextConfig) -> Empty:
        response: Empty = self.stub.UpdateS2tPipeline(request)
        return response

    def list_s2t_pipelines(self, request: ListS2tPipelinesRequest) -> ListS2tPipelinesResponse:
        response: ListS2tPipelinesResponse = self.stub.ListS2tPipelines(request)
        return response

    def list_s2t_languages(self, request: ListS2tLanguagesRequest) -> ListS2tLanguagesResponse:
        response: ListS2tLanguagesResponse = self.stub.ListS2tLanguages(request)
        return response

    def list_s2t_domains(self, request: ListS2tDomainsRequest) -> ListS2tDomainsResponse:
        response: ListS2tDomainsResponse = self.stub.ListS2tDomains(request)
        return response
