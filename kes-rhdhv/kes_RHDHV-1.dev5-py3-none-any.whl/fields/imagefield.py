from dataclasses import dataclass
from typing import ByteString, Optional
from uuid import UUID

from kes.proto.table_pb2_grpc import TableStub
from kes.proto.table_pb2 import LoadImageRequest, SaveImageReply, SaveImageRequest


class ImageField:
    """ This class allows saving and reading images in fields """

    @dataclass
    class ImageRef:
        name: str
        value_id: UUID

    @dataclass
    class ImageUpload:
        name: str
        key: str

    _property_id: UUID
    _ref: ImageRef | ImageUpload | None
    __chunkSize = 60 * 1024  # 64 KiB

    def __init__(self, property_id: UUID, image_ref: Optional[ImageRef] = None):
        """
        The constructor for the ImageField class.

        Parameters:
           property_id (UUID): Id of the image property corresponding to this field
        """
        self._property_id = property_id
        self._ref = image_ref

    def load(self, stub: TableStub) -> Optional[ByteString]:
        if not isinstance(self._ref, self.ImageRef):
            return None

        imageData = bytearray()
        streamingReply = stub.loadImage(LoadImageRequest(
            imageValueId=str(self._ref.value_id), fileName=self._ref.name
        ))
        for reply in streamingReply:
            imageData += reply.chunk

        return imageData

    def save(self, stub: TableStub, name: str, data: bytes):
        """ Writes the given binary stream as the image of this field  """
        response: SaveImageReply = stub.saveImage(self._createChunkStreams(data))
        self._ref = self.ImageUpload(name, response.tempKey)

    def _createChunkStreams(self, image: bytes):
        for i in range(0, len(image), self.__chunkSize):
            chunk = image[i: i + self.__chunkSize]
            yield SaveImageRequest(chunk=chunk)

    def is_empty(self) -> bool:
        return self._ref is None

    @property
    def name(self):
        if self._ref != None:
            return self._ref.name
        else:
            return ""

    @property
    def key(self):
        if isinstance(self._ref, self.ImageUpload):
            return self._ref.key
        else:
            return ""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False

        if not isinstance(other._ref, type(self._ref)):
            return False

        return self._property_id == other._property_id and self._ref == other._ref
