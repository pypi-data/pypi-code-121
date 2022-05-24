class Error(Exception):
    def __init__(self, message, error, internal=True):
        self.message = message
        self.error_name = error
        self.internal = internal

    def __str__(self):
        return self.error_name + self.message


class AuthenticationError(Error):
    error_name = "Authentication Error - "
    internal = False

    def __init__(self, message=None):
        """
            Data Connector error class raised when a connector could not authenticate or other related authentication
            errors. Raising this exception will result in a regular handled error. This error will also be visible in
            the log output.

            :param message: An error message - WILL BE VISIBLE TO CLIENT
        """
        self.message = message
        self.error_name = "Authentication Error - "
        self.internal = False


class WhitelistError(Error):
    """DataConnector error class raised when a connector cannot connect because the user did not whitelist our
    database """
    error_name = "Whitelist Error - "
    internal = False

    def __init__(self, message=None):
        self.message = message
        self.error_name = "Whitelist Error - "
        self.internal = False


class NoObjectsFoundError(Error):
    """DataConnector error class raised when the connector returns no objects associated with the user's account"""
    error_name = "No Objects Found Error - "
    internal = False

    def __init__(self, message=None):
        self.message = message
        self.error_name = "No Objects Found Error - "
        self.internal = False


class GetObjectsError(Error):
    """DataConnector error class raised when the connector cannot pull the objects associated with the user's
    account """
    error_name = "Get Objects Error - "
    internal = True

    def __init__(self, message=None):
        self.message = message
        self.error_name = "Get Objects Error - "
        self.internal = True


class NoFieldsFoundError(Error):
    """DataConnector error class raised when the connector does not return any fields associated with the object_id"""
    error_name = "No Fields Found Error - "
    internal = False

    def __init__(self, object_id, message=None):
        self.object_id = object_id
        self.message = message
        self.error_name = "No Fields Found Error - "
        self.internal = False

    # def __str__(self):
    #     if self.object_id:
    #         return "The process was terminated because the object {0} did not contain any fields." \
    #             .format(self.object_id)
    #     else:
    #         return "The process was terminated because an error occurred:\n\t" + self.message


class GetFieldsError(Error):
    """DataConnector error class raised when the connector cannot pull the fields associated with the given object_id
    on the user's account """
    error_name = "Get Fields Error - "
    internal = True

    def __init__(self, object_id, message=None):
        self.object_id = object_id
        self.message = message
        self.error_name = "Get Fields Error - "
        self.internal = True

    # def __str__(self):
    #     if self.object_id:
    #         return "The process was terminated because the connector failed to pull the fields in the object " \
    #                "{0}.\n\t:{1}".format(self.object_id, self.message)
    #     else:
    #         return "The process was terminated because an error occurred:\n\t" + self.message


class BadFieldIDError(Error):
    """DataConnector error class raised when the field_id does not belong to the given object_id"""
    error_name = "Bad Field ID Error - "
    internal = True

    def __init__(self, field_id=None, object_id=None, message=None):
        self.field_id = field_id
        self.object_id = object_id
        self.message = message
        self.error_name = "Bad Field ID Error - "
        self.internal = True

    # def __str__(self):
    #     if self.field_id and self.object_id:
    #         return "The process was terminated because the field_id ({0}) was not found in the object {1}." \
    #             .format(self.field_id, self.object_id)
    #     else:
    #         return "The process was terminated because an error occurred:\n\t" + self.message


class FilterDataTypeError(Error):
    """DataConnector error class raised when datatype of the column that is supposed to be filtered is not date or
    datetime """
    error_name = "Filter Data Type Error - "
    internal = True

    def __init__(self, datatype=None, field_to_filter=None, message=None):
        self.datatype = datatype
        self.field = field_to_filter
        self.message = message
        self.error_name = "Filter Data Type Error - "
        self.internal = False

    # def __str__(self):
    #     if self.datatype and self.field:
    #         return "The process was terminated because the datatype of {0} was invalid for filtering. Datatype: {1}" \
    #             .format(self.field, self.datatype)
    #     else:
    #         return "The process was terminated because an error occurred:\n\t" + self.message


class BadObjectIDError(Error):
    """DataConnector error class raised when the object_id is not associated with the user"""
    error_name = "Bad Object ID Error - "
    internal = True

    def __init__(self, object_id=None, message=None):
        self.object_id = object_id
        self.message = message
        self.error_name = "Bad Object ID Error - "
        self.internal = True

    # def __str__(self):
    #     if self.object_id:
    #         return "The process was terminated because the object_id ({0}) could not be found." \
    #             .format(self.object_id)
    #     else:
    #         return "The process was terminated because an error occurred:\n\t" + self.message


class UpdateMethodNotSupportedError(Error):
    """DataConnector error class raised when the chosen update method is invalid for the chosen connector"""
    error_name = "Update Method Not Supported Error - "
    internal = True

    def __init__(self, update_method=None, connector=None, message=None):
        self.update_method = update_method
        self.connector = connector
        self.message = message
        self.error_name = "Update Method Not Supported Error - "
        self.internal = True

    # def __str__(self):
    #     if self.update_method and self.connector:
    #         return "The process was terminated because the update method {0} is not supported by the {1} connector." \
    #             .format(self.update_method, self.connector)
    #     else:
    #         return "The process was terminated because an error occurred:\n\t" + self.message


class MappingError(Error):
    """DataConnector error class raised when the data cannot be mapped to the given columns"""
    error_name = "Mapping Error - "
    internal = True

    def __init__(self, message):
        self.message = message
        self.error_name = "Mapping Error - "
        self.internal = False


class DataError(Error):
    """DataConnector error class raised when the data from the object was unable to be pulled."""
    error_name = "Data Error - "
    internal = True

    def __init__(self, message):
        self.message = message
        self.error_name = "Data Error - "
        self.internal = False


class APIRequestError(Error):
    """DataConnector error class raised when the connector gets an error code from the API"""
    error_name = "API Request Error - "
    internal = True

    def __init__(self, error_code_returned=None, message=None):
        self.error_code = error_code_returned
        self.message = message
        self.error_name = "API Request Error - "
        self.internal = False

    # def __str__(self):
    #     if self.error_code:
    #         return "The process was terminated because the connector's API returned a {0} error".format(self.error_code)
    #     else:
    #         return "The process was terminated because an error occurred:\n\t" + self.message


class APITimeoutError(Error):
    """DataConnector error class raised when the API takes times out"""
    error_name = "API Timeout Error - "
    internal = True

    def __init__(self, message=None):
        self.message = message
        self.error_name = "API Timeout Error - "
        self.internal = False


class FieldDataTypeError(Error):
    """DataConnector error class raised when the datatype of a field is not supported"""
    error_name = "Field Data Type Error - "
    internal = True

    def __init__(self, datatype=None, field=None, message=None):
        self.datatype = datatype
        self.field = field
        self.message = message
        self.error_name = "Field Data Type Error - "
        self.internal = False

    # def __str__(self):
    #     if self.datatype and self.field:
    #         return "The process was terminated because the datatype of {0} was invalid. Datatype: {1}" \
    #             .format(self.field, self.datatype)
    #     else:
    #         return "The process was terminated because an error occurred:\n\t" + self.message


class APIPermissionError(Error):
    """DataConnector error class raised when the connector cannot finish a process it lacks API permissions"""
    error_name = "API Permission Error - "
    internal = True

    def __init__(self, message=None):
        self.message = message
        self.error_name = "API Permission Error - "
        self.internal = False


class LoadDataError(Error):
    """DataConnector error class raised when the connector cannot finish loading data"""
    error_name = "Load Data Error - "
    internal = True

    def __init__(self, message=None):
        self.message = message
        self.error_name = "Load Data Error - "
        self.internal = False


class NotADestinationError(Error):
    """DataConnector error class raised when the load_data function is implemented but the connector is not a destination"""
    error_name = "Not A Destination Error - "
    internal = True

    def __init__(self, message=None):
        self.message = message
        self.error_name = "Not A Destination Error - "
        self.internal = True


class NotImplementedError(Error):
    """DataConnector error class raised when the load_data function is implemented but the connector is not a
    destination """
    error_name = "Not Implemented Error - "
    internal = True

    def __init__(self, message=None):
        self.message = message
        self.error_name = "Not Implemented Error - "
        self.internal = True


class NoRowsFoundError(Error):
    """DataConnector error class raised when the database returns no rows"""
    error_name = "No Rows Found Error - "
    internal = True

    def __init__(self, message=None):
        self.message = message
        self.error_name = "No Rows Found Error - "
        self.internal = True
