"""
First version (very basic and naive) of what I think would be the best way to handle files without using a specific file
reader.

The main purpose of this file is to be a fileObject factory, where fileObject is the resulting instance of our multiple
file readers/handlers/wrappers. That way, one can have direct access to the object and its properties.

Examples:
    loader = Loader("myFile.jpg")
    # Here, image is an instance of PILFile. PILFile could be derived from Image, because most files read by PIL are
    # single image files.
    image = loader.load()
    for channel in image.channels:
        channel.display()

    loaderCZI = Loader("myCzi.czi")
    # Here czi is an instance of CZIFile. CZIFile could be composed of ImageCollection instances (z-stack, time series,
    # map, etc.), because it is not always in the same format. Some files can contain z-stack, while others are just
    # one image of 3 channels, or 48 * 3 tiles making an image of 3 channels. Inheritance is not the best way to go
    # with czi files.
    czi = loader.load()
    if czi.isZStack:
        images = czi.zstack
    elif czi.isTimeSeries:
        images = czi.timeSeries
"""
from dcclab.imageFile import *


class Loader(object):
    supportedClasses = [CZIFile_, TIFFFile, PILFile, MATLABFile]
    supportedFormats = []

    # Not sure if the init should take args or not...
    def __int__(self, path=None, pathPattern=None):
        self.__path = path
        # Not really at ease with how pathPattern works...
        self.__pathPattern = pathPattern
        self.__fileObject = None

    # Method used to load a file. Returns an object of the right reader class. Maybe another method should be used
    # when using pathPattern instead of a plain path.
    def load(self):
        if self.__fileObject is not None:
            raise FileAlreadyLoadedException(self.__path)
        if self.__path is not None:
            self.__fileObject = self.__loadFromSimglePath()
        elif self.__pathPattern is not None:
            self.__fileObject = self.__loadFromPathPattern()
        else:
            raise AttributeError("No path/path pattern to load")
        return self.__fileObject


    def __loadFromSimglePath(self):
        fileObject = None
        for supportedClass in Loader.supportedClasses:
            try:
                fileObject = supportedClass(self.__path)
            # We should normalize exception raised by supported classes when the file is not in the right format,
            # because catching all exception is really a bad idea. Exception raised by other methods (not related to
            # the file format) are also stopped.
            except Exception:
                continue
        if fileObject is None:
            message = "Cannot read '{0}': not a recognized image format ({1})".format(self.__path,
                                                                                      Loader.supportedFormats)
            raise InvalidFileFormatException(message)
            # When returning the object itself, we get access to all its properties.
        return fileObject

    def __loadFromPathPattern(self):
        raise NotImplementedError

    @property
    def path(self):
        return self.__path
