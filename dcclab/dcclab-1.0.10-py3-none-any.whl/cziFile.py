from .imageCollection import *
from .timeSeries import TimeSeries
from .zStack import ZStack


class CZIFile(ImageFile):
    supportedFormats = ['czi']
    # See czi documentation for more info about the axes
    allAxes = "XYCZTRSIBMHV"

    def __init__(self, path):
        ImageFile.__init__(self, path)
        self.__cziObj = None
        try:
            self.__cziObj = readCziImage(path)
        except ValueError:
            raise InvalidFileFormatException("Not a compatible format for this reader.")
        self.__mosaic, self.__indexAndTiles = decodeCZIFile(self.__cziObj)
        self.__shape = self.__cziObj.shape
        self.__axes = self.__cziObj.axes
        self.__originalDType = self.__cziObj.dtype
        self.__axesDimAndIndex = self.__findAxesDimAndIndex()
        self.__totalWidth = self.__axesDimAndIndex["X"][0]
        self.__totalHeight = self.__axesDimAndIndex["Y"][0]
        self.__isZStack = self.__axesDimAndIndex["Z"][0] > 1
        self.__isTimeSeries = self.__axesDimAndIndex["T"][0] > 1
        self.__isScenes = self.__axesDimAndIndex["S"][0] > 1

        # Special cases never encountered. To be implemented if needed.
        if self.__isTimeSeries and self.__isScenes:
            raise NotImplementedError("Time series and scenes combination is not implemented")
        if self.__isTimeSeries and self.__isZStack:
            raise NotImplementedError("Time series and z-stack combination is not implemented")
        if self.__isZStack and self.__isScenes:
            raise NotImplementedError("Z-stack and scenes combination is not implemented")

        self.__numberOfChannels = self.__axesDimAndIndex["C"][0]
        self.__tileMap = self.__buildTileMap() if self.__axes != "YX0" else None

    def allData(self) -> np.ndarray:
        return np.squeeze(self.__mosaic)

    def imageData(self):
        if not (self.__isScenes or self.__isTimeSeries or self.__isZStack):
            pixels = np.squeeze(self.__mosaic)
            # We check if ndim == 2 because the Channel dimension may disappear in squeezing if equal to 1
            if pixels.ndim == 2:
                shape = pixels.shape
                pixels = pixels.reshape((1, shape[0], shape[1]))
            image = Image(pixels.transpose((1, 2, 0))) if self.__axes != "YX0" else self.__YX0Image()
        else:
            raise ValueError("This file contains more than just one image.")
        return image

    def mapData(self):
        pass

    def scenesData(self):
        if self.__isScenes:
            scenes = []
            nbScenes = self.__axesDimAndIndex["S"][0]
            mosaic = np.squeeze(self.__mosaic)
            # We check if ndim == 3 because the Channel dimension may disappear in squeezing if equal to 1
            if mosaic.ndim == 3:
                shape = mosaic.shape
                mosaic = mosaic.reshape((shape[0], 1, shape[1], shape[2]))
            for i in range(nbScenes):
                scenes.append(Image(mosaic[i, :, :, :].transpose(1, 2, 0)))
            coll = ImageCollection(scenes)
        else:
            coll = None
        return coll

    def timeSeriesData(self):
        if self.__isTimeSeries:
            tSeries = []
            nbTime = self.__axesDimAndIndex["T"][0]
            mosaic = np.squeeze(self.__mosaic)
            # We check if ndim == 3 because the Channel dimension may disappear in squeezing if equal to 1
            if mosaic.ndim == 3:
                shape = mosaic.shape
                mosaic = mosaic.reshape((shape[0], 1, shape[1], shape[2]))
            for i in range(nbTime):
                tSeries.append(Image(mosaic[i, :, :, :].transpose(1, 2, 0)))
            tSeries = TimeSeries(tSeries)
        else:
            tSeries = None
        return tSeries

    def zStackData(self):
        if self.__isZStack:
            mosaic = np.copy(self.__mosaic)
            channelIndex = self.__axesDimAndIndex["C"][-1]
            zSTackIndex = self.__axesDimAndIndex["Z"][-1]
            # FIXME Find better way/ more efficient way to swap axes
            if channelIndex < zSTackIndex:
                mosaic = np.swapaxes(mosaic, channelIndex, zSTackIndex)
            zStack = []
            nbZ = self.__axesDimAndIndex["Z"][0]
            mosaic = np.squeeze(mosaic)
            # We check if ndim == 3 because the Channel dimension may disappear in squeezing if equal to 1
            if mosaic.ndim == 3:
                shape = mosaic.shape
                mosaic = mosaic.reshape((shape[0], 1, shape[1], shape[2]))
            for i in range(nbZ):
                zStack.append(Image(mosaic[i, :, :, :].transpose(1, 2, 0)))
            zStack = ZStack(zStack)
        else:
            zStack = None
        return zStack

    @property
    def shape(self):
        return self.__shape

    @property
    def totalWidth(self):
        return self.__totalWidth

    @property
    def totalHeight(self):
        return self.__totalHeight

    @property
    def isZstack(self):
        return self.__isZStack

    @property
    def isTimeSerie(self):
        return self.__isTimeSeries

    @property
    def isScenes(self):
        return self.__isScenes

    @property
    def tileMap(self):
        return self.__tileMap

    @property
    def numberOfChannels(self):
        return self.__numberOfChannels

    @property
    def axes(self):
        return self.__axes

    @property
    def originalDType(self):
        return self.__originalDType

    def __YX0Image(self):
        singleImage = None
        if self.__axes == "YX0":
            singleImage = self.__mosaic
        return Image(singleImage)

    def __buildTileMap(self):
        tileMap = {}
        for element in self.__indexAndTiles:
            tile = element[1]
            index = element[0]
            tileChannel = index[self.__axesDimAndIndex["C"][1]].start
            xSlice = index[self.__axesDimAndIndex["X"][1]]
            ySlice = index[self.__axesDimAndIndex["Y"][1]]
            zIndex = index[self.__axesDimAndIndex["Z"][1]].start if self.__isZStack else None
            tIndex = index[self.__axesDimAndIndex["T"][1]].start if self.__isTimeSeries else None
            sIndex = index[self.__axesDimAndIndex["S"][1]].start if self.__isScenes else None
            mapKey = (range(xSlice.start, xSlice.stop), range(ySlice.start, ySlice.stop),
                      zIndex, sIndex, tIndex, tileChannel)
            tileMap[mapKey] = np.squeeze(tile)
        return tileMap

    def __findAxesDimAndIndex(self):
        def findValue(key):
            valueReturn = 0
            index = None
            try:
                index = self.__axes.index(key)
            except ValueError as e:
                del e
                if key == "C":
                    if self.__axes == "YX0":
                        valueReturn = 0
                    else:
                        closeCziFileObject(self.__cziObj)
                        raise ValueError("This image has no channel and is not of shape \"YX0\"")
            if index is not None:
                valueReturn = self.__shape[index]
            return valueReturn, index

        return {key: findValue(key) for key in CZIFile.allAxes}

    def __del__(self):
        try:
            if self.__cziObj is not None:
                closeCziFileObject(self.__cziObj)
        except AttributeError:
            print("Object already deleted")
