import sys
from datetime import datetime
from typing import List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

ContentRangePattern = str
ContentType = str
ETag = str
ErrorMessage = str
ItemName = str
ListLimit = int
ListPathNaming = str
PaginationToken = str
PathNaming = str
RangePattern = str
SHA256Hash = str
StringPrimitive = str
statusCode = int


class ItemType(str):
    OBJECT = "OBJECT"
    FOLDER = "FOLDER"


class StorageClass(str):
    TEMPORAL = "TEMPORAL"


class UploadAvailability(str):
    STANDARD = "STANDARD"
    STREAMING = "STREAMING"


class ContainerNotFoundException(ServiceException):
    """The specified container was not found for the specified account."""

    Message: Optional[ErrorMessage]


class InternalServerError(ServiceException):
    """The service is temporarily unavailable."""

    Message: Optional[ErrorMessage]


class ObjectNotFoundException(ServiceException):
    """Could not perform an operation on an object that does not exist."""

    Message: Optional[ErrorMessage]


class RequestedRangeNotSatisfiableException(ServiceException):
    """The requested content range is not valid."""

    Message: Optional[ErrorMessage]


class DeleteObjectRequest(ServiceRequest):
    Path: PathNaming


class DeleteObjectResponse(TypedDict, total=False):
    pass


class DescribeObjectRequest(ServiceRequest):
    Path: PathNaming


TimeStamp = datetime
NonNegativeLong = int


class DescribeObjectResponse(TypedDict, total=False):
    ETag: Optional[ETag]
    ContentType: Optional[ContentType]
    ContentLength: Optional[NonNegativeLong]
    CacheControl: Optional[StringPrimitive]
    LastModified: Optional[TimeStamp]


class GetObjectRequest(ServiceRequest):
    Path: PathNaming
    Range: Optional[RangePattern]


PayloadBlob = bytes


class GetObjectResponse(TypedDict, total=False):
    Body: Optional[PayloadBlob]
    CacheControl: Optional[StringPrimitive]
    ContentRange: Optional[ContentRangePattern]
    ContentLength: Optional[NonNegativeLong]
    ContentType: Optional[ContentType]
    ETag: Optional[ETag]
    LastModified: Optional[TimeStamp]
    StatusCode: statusCode


class Item(TypedDict, total=False):
    """A metadata entry for a folder or object."""

    Name: Optional[ItemName]
    Type: Optional[ItemType]
    ETag: Optional[ETag]
    LastModified: Optional[TimeStamp]
    ContentType: Optional[ContentType]
    ContentLength: Optional[NonNegativeLong]


ItemList = List[Item]


class ListItemsRequest(ServiceRequest):
    Path: Optional[ListPathNaming]
    MaxResults: Optional[ListLimit]
    NextToken: Optional[PaginationToken]


class ListItemsResponse(TypedDict, total=False):
    Items: Optional[ItemList]
    NextToken: Optional[PaginationToken]


class PutObjectRequest(ServiceRequest):
    Body: PayloadBlob
    Path: PathNaming
    ContentType: Optional[ContentType]
    CacheControl: Optional[StringPrimitive]
    StorageClass: Optional[StorageClass]
    UploadAvailability: Optional[UploadAvailability]


class PutObjectResponse(TypedDict, total=False):
    ContentSHA256: Optional[SHA256Hash]
    ETag: Optional[ETag]
    StorageClass: Optional[StorageClass]


class MediastoreDataApi:

    service = "mediastore-data"
    version = "2017-09-01"

    @handler("DeleteObject")
    def delete_object(self, context: RequestContext, path: PathNaming) -> DeleteObjectResponse:
        """Deletes an object at the specified path.

        :param path: The path (including the file name) where the object is stored in the
        container.
        :returns: DeleteObjectResponse
        :raises ContainerNotFoundException:
        :raises ObjectNotFoundException:
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("DescribeObject")
    def describe_object(self, context: RequestContext, path: PathNaming) -> DescribeObjectResponse:
        """Gets the headers for an object at the specified path.

        :param path: The path (including the file name) where the object is stored in the
        container.
        :returns: DescribeObjectResponse
        :raises ContainerNotFoundException:
        :raises ObjectNotFoundException:
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("GetObject")
    def get_object(
        self, context: RequestContext, path: PathNaming, range: RangePattern = None
    ) -> GetObjectResponse:
        """Downloads the object at the specified path. If the object’s upload
        availability is set to ``streaming``, AWS Elemental MediaStore downloads
        the object even if it’s still uploading the object.

        :param path: The path (including the file name) where the object is stored in the
        container.
        :param range: The range bytes of an object to retrieve.
        :returns: GetObjectResponse
        :raises ContainerNotFoundException:
        :raises ObjectNotFoundException:
        :raises RequestedRangeNotSatisfiableException:
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("ListItems")
    def list_items(
        self,
        context: RequestContext,
        path: ListPathNaming = None,
        max_results: ListLimit = None,
        next_token: PaginationToken = None,
    ) -> ListItemsResponse:
        """Provides a list of metadata entries about folders and objects in the
        specified folder.

        :param path: The path in the container from which to retrieve items.
        :param max_results: The maximum number of results to return per API request.
        :param next_token: The token that identifies which batch of results that you want to see.
        :returns: ListItemsResponse
        :raises ContainerNotFoundException:
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("PutObject")
    def put_object(
        self,
        context: RequestContext,
        body: PayloadBlob,
        path: PathNaming,
        content_type: ContentType = None,
        cache_control: StringPrimitive = None,
        storage_class: StorageClass = None,
        upload_availability: UploadAvailability = None,
    ) -> PutObjectResponse:
        """Uploads an object to the specified path. Object sizes are limited to 25
        MB for standard upload availability and 10 MB for streaming upload
        availability.

        :param body: The bytes to be stored.
        :param path: The path (including the file name) where the object is stored in the
        container.
        :param content_type: The content type of the object.
        :param cache_control: An optional ``CacheControl`` header that allows the caller to control
        the object's cache behavior.
        :param storage_class: Indicates the storage class of a ``Put`` request.
        :param upload_availability: Indicates the availability of an object while it is still uploading.
        :returns: PutObjectResponse
        :raises ContainerNotFoundException:
        :raises InternalServerError:
        """
        raise NotImplementedError
