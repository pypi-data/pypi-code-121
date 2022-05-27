from collections import defaultdict


class MDSResponse:
    def __init__(self, response_proto, metadata=defaultdict(str)):
        """
        A wrapper of response protos from metadata server that adds a method to access response headers
        This class is needed since we cannot add an attribute to Python proto Message classes due to their designs which is documented here:
            https://chromium.googlesource.com/chromium/src/third_party/+/master/protobuf/python/google/protobuf/internal/python_message.py

        :param response_proto (:Message): deserialized response proto returned from metadata server
        :param metadata (:defaultdict(str)): response header returned from metadata server
            If metadata is returned from go proxy (direct http), metadata has type Dict[str, List[str]].
            If metadata is returned from go proxy (grpc gateway), metadata has type Dict[str, str] whose value is first str in List[str].
            If metadata is returned from metadata server (direct grpc), metadata has type Dict[str, str].
            Currently, only _CLIENT_VERSION_INFO_RESPONSE_HEADER ad _CLIENT_UPDATE_VERSION_RESPONSE_HEADER metadata is used in the response,
             whose values have str type.
            The default values of keys that don't exist are empty strings in any of the 3 cases.
            It's possible to have other values for response. Some examples could be found here:
                https://grpc.github.io/grpc/python/glossary.html#term-metadata
                and here: https://www.tabnine.com/code/java/classes/io.grpc.Metadata$Key
                so the returned value may change in the future
        """
        self.response_proto = response_proto
        self.metadata = metadata

    def __getattr__(self, name):
        if isinstance(self.response_proto, dict):
            return self.response_proto[name]
        return getattr(self.response_proto, name)

    def _headers(self):
        return self.metadata
