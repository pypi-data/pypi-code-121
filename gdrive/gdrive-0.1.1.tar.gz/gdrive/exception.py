class SettingsException(RuntimeError):
    pass


class GDriveException(RuntimeError):
    pass


class GDriveNoSuchFileException(GDriveException):
    pass


class GDriveNoSuchFileMetaException(GDriveException):
    pass
