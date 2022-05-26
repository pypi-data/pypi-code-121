#  Copyright (c) 2020 Caliber Data Labs.
#  All rights reserved.
#
from typing import Dict, Optional

from ..tools import misc
from ..tools.naming import UriParser


class ObjectAccessError(Exception):
    pass


class ObjectAccessMedium:
    PUBLIC_URL = "public-url"
    GS = "gs"
    S3 = "s3"

# examples
# {
#   "medium": "public-url", #optional
#   "url": "http....", #required
#   "filename": "abc.png" #optional
# }
#
# {
#   "medium": "s3",  #optional
#   "uri": "s3://bucket/key", #required
#   "filename": "abc.png", #optional
# }
#


class ObjectAccess(object):
    def __init__(self,
                 filename: Optional[str] = None,
                 url: Optional[str] = None,
                 uri: Optional[str] = None):
        if url:
            self.medium = ObjectAccessMedium.PUBLIC_URL
        elif uri:
            uri_parser = UriParser(uri)
            if uri_parser.cloud_provider == "gs":
                self.medium = ObjectAccessMedium.GS
            elif uri_parser.cloud_provider == "s3":
                self.medium = ObjectAccessMedium.S3
            else:
                raise ObjectAccessError(
                    "invalid cloud storage provider {}".format(
                        uri_parser.cloud_provider))
            if not filename:
                filename = uri_parser.key.split("/")[-1]
        else:
            raise ObjectAccessError(
                "invalid medium- either url, or uri should be specified")

        self.url = url  # optional
        self.uri = uri  # optional
        self.filename = filename  # optional

    def __hash__(self):
        if self.url:
            return self.url.__hash__()
        else:
            return self.uri.__hash__()

    def __eq__(self, other):
        if self.url and other.url:
            return self.url == other.url
        else:
            return self.uri == other.uri

    def to_dic(self) -> dict:
        object_access_dict = {}

        if self.filename:
            object_access_dict["filename"] = self.filename

        if self.url:
            object_access_dict["url"] = self.url

        if self.uri:
            object_access_dict["uri"] = self.uri

        return object_access_dict

    @classmethod
    def from_dict(cls, data: Dict):
        fields = {
            "filename",
            "url",
            "uri"
        }
        return cls(**{field: data.get(field) for field in fields})
