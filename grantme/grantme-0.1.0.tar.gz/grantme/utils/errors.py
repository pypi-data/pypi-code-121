class GrantmeError(RuntimeError):
    def __init__(self, msg, code):
        super().__init__(msg)

        self.msg = msg
        self.code = code


# Error messages and codes
UNEXPECTED_ERROR_CODE = 255

UPGRADE_FAILURE_MSG = "Failed to upgrade shared permission to exclusive permission."
UPGRADE_FAILURE_CODE = 6
GRANT_FAILURE_MSG = "Failed to grant permission."
GRANT_FAILURE_CODE = 7
