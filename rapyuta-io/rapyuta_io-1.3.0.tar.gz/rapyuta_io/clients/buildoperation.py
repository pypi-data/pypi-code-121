from __future__ import absolute_import
from rapyuta_io.utils.error import InvalidParameterException
from rapyuta_io.utils import ObjDict
import six


class BuildOperationInfo(ObjDict):

    """
    BuildOperationInfo represents information about the operation which will be performed on the build.

    :ivar buildGuid: Represents GUID of the build
    :ivar buildGenerationNumber: Represents build generation number of the build.
    :ivar triggerName: Represents trigger name of the build
    :ivar tagName: Represents tag name of the build

    """
    def __init__(self, buildGuid, buildGenerationNumber=None, triggerName=None, tagName=None):
        self.validate(buildGuid, buildGenerationNumber, triggerName, tagName)
        self.buildGUID = buildGuid
        if buildGenerationNumber:
            self.buildGenerationNumber = buildGenerationNumber
        if triggerName:
            self.triggerName = triggerName
        if tagName:
            self.tagName = tagName
        super(ObjDict, self).__init__()

    @staticmethod
    def validate(buildGuid, buildGenerationNumber, triggerName, tagName):
        if not buildGuid or not isinstance(buildGuid, six.string_types):
            raise InvalidParameterException('buildGuid must be a non-empty string')

        if buildGenerationNumber and not isinstance(buildGenerationNumber, int):
            raise InvalidParameterException('buildGenerationNumber should be a integer')

        if triggerName is not None and not isinstance(triggerName, six.string_types) or triggerName == "":
            raise InvalidParameterException('triggerName must be a non-empty string')

        if tagName is not None and not isinstance(tagName, six.string_types) or tagName == "":
            raise InvalidParameterException('tagName must be a non-empty string')


class BuildOperation(ObjDict):
    """
    BuildOperation represents Build Operation

    :ivar buildOperationInfo: represents a list of information about the operation which will be performed on
                              the build list(:py:class:`~rapyuta_io.clients.buildoperation.BuildOperationInfo`).

    """
    def __init__(self, buildOperationInfo):
        self.validate(buildOperationInfo)
        self.buildOperationInfo = buildOperationInfo
        super(ObjDict, self).__init__()

    @staticmethod
    def validate(buildOperationInfo):
        if not isinstance(buildOperationInfo, list):
            raise InvalidParameterException('buildOperationInfo must be an instance of list')
        for buildOp in buildOperationInfo:
            if not isinstance(buildOp, BuildOperationInfo):
                raise InvalidParameterException('Every buildOperation must be an instance of '
                                                'rapyuta_io.clients.buildoperation.BuildOperationInfo')
