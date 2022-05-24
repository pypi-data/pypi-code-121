from .. import CoreService_pb2 as pb
from ..entities.ingest import Ingest


class IngestHistory:
    def __init__(self, stub, feature_set):
        self._feature_set = feature_set
        self._stub = stub
        self._ingest_history = self.__load_history()

    def list(self):
        return [
            Ingest(self._stub, self._feature_set, ingest)
            for ingest in self._ingest_history
        ]

    def refresh(self):
        self._ingest_history = self.__load_history()

    @property
    def size(self):
        return len(self._ingest_history)

    @property
    def first(self):
        if self.list():
            return Ingest(self._stub, self._feature_set, self._ingest_history[0])
        else:
            raise Exception("No ingest has been performed so far.")

    @property
    def last(self):
        if self.list():
            return Ingest(self._stub, self._feature_set, self._ingest_history[-1])
        else:
            raise Exception("No ingest has been performed so far.")

    def get(self, ingest_id):
        ingests = [
            ingest for ingest in self._ingest_history if ingest.ingest_id == ingest_id
        ]
        if ingests:
            return Ingest(self._stub, self._feature_set, ingests[0])
        else:
            raise Exception("No ingest has been found for the ingest id " + ingest_id)

    def __load_history(self):
        request = pb.GetIngestHistoryRequest()
        request.feature_set.CopyFrom(self._feature_set)
        response = self._stub.GetIngestHistory(request)
        return response.ingest_history
