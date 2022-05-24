"""
The exeptions returned by Limonade library. All derive from LimonadeExeption.
"""
class LimonadeException(Exception):
    pass

class LimonadeDataNotFoundError(LimonadeException):
    pass

class LimonadeDataError(LimonadeException):
    pass

class LimonadeTimeCacheError(LimonadeException):
    pass

class LimonadeDataStoreError(LimonadeException):
    pass

class LimonadeMetadataError(LimonadeException):
    pass

class LimonadeMetadataSetError(LimonadeMetadataError):
    pass

class LimonadeTimestampError(LimonadeException):
    pass

class LimonadeCalibrationError(LimonadeException):
    pass

class LimonadeConfigurationError(LimonadeException):
    pass

class LimonadePlotError(LimonadeException):
    pass