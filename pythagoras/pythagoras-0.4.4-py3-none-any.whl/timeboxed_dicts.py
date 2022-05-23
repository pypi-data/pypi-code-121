from pythagoras.persistent_dicts import SimplePersistentDict


class TimeboxedFileDirDict(SimplePersistentDict):
    """ A persistent Dict that stores key-value pairs in local files for a limited time.

    A new file is created for each key-value pair.
    A key is either a filename (without an extension),
    or a sequence of directory names that ends with a filename.
    A value can be any Python object, which is stored in a file.

    Timeboxed_FileDirDict can store objects in binary files (as pickles)
    or in human-readable text files (using jsonpickles).

    Objects in Timeboxed_FileDirDict can exist only for a duration of their TTL, defined in seconds.
    """

    def __init__(self, dir_name: str = "FileDirDict", file_type: str = "pkl", ttl = 60*60*24):
        pass