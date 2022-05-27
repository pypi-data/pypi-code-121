from .imageCollection import *
import numpy as np
import json
import inspect

from matplotlib.widgets import RectangleSelector
from collections import OrderedDict
import PIL.Image as PILImage


class ZStack(ImageCollection):
    def __init__(self, images: List['Image']=None, imagesArray: np.ndarray=None, pathPattern: str=None, cropAtInit=False):
        self.cropX, self.cropY = [], []
        self.cropFig = None
        self.cropRect = None

        if cropAtInit:
            imagesArray = self.crop4DArray(imagesArray)
        super().__init__(images, imagesArray, pathPattern)
        if not self.imagesAreSimilar:
            raise ValueError("Images in z-stack are not all the same shape")

        self.componentsProperties = OrderedDict()
        self.processIn3D = True  # default None ?

    @property
    def imagesAreSimilar(self) -> bool:
        shape = None
        for image in self.images:
            if shape is None:
                shape = image.shape
            elif shape != image.shape:
                return False
        return True

    @property
    def numberOfChannels(self):
        # Can be moved to ImageCollection [addressing the issue in removeChannels()]
        # Not clean, but it works since imagesAreSimilar...
        # Could be stored as a property variable in init instead
        return self.images[0].shape[2]

    @property
    def shape(self):
        x, y, c = self.images[0].shape
        z = len(self)
        return x, y, c, z

    def asArray(self) -> np.ndarray:
        return np.stack([image.asArray() for image in self.images], axis=3)

    def asChannelArray(self, channel: int) -> np.ndarray:
        imagesArray = self.asArray()
        return imagesArray[:, :, channel, :]

    def asOriginalArray(self) -> np.ndarray:
        if self.hasOriginal:
            return np.stack([image.asOriginalArray() for image in self.images if image], axis=3)
        else:
            return self.asArray()

    def asOriginalChannelArray(self, channel: int) -> np.ndarray:
        if self.hasOriginal:
            originalArray = self.asOriginalArray()
            return originalArray[:, :, channel, :]
        else:
            return self.asArray()[:, :, channel, :]

    def apply3DFilter(self, filterFunc, *filterArgs, **filterKwargs):
        """ These Functions should be processed over one Channel at a time """
        if self.processIn3D is None:
            raise ZStackProcessDimensionIsNotDefined
        elif self.processIn3D:
            filteredArrays = []
            for channel in list(range(self.numberOfChannels)):
                array = self.asChannelArray(channel)
                filteredArrays.append(filterFunc(array, *filterArgs, **filterKwargs))
            newStack = np.stack(filteredArrays, axis=2)
            self.replaceFromArray(newStack)
        else:
            callerFunction = inspect.stack()[1].function
            getattr(super(), callerFunction)(*filterArgs)

    def applyOpening(self, size: int=2) -> None:
        self.apply3DFilter(ndimage.grey_opening, size)

    def applyClosing(self, size: int=2) -> None:
        self.apply3DFilter(ndimage.grey_closing, size)

    def applyErosion(self, size: int=2):
        self.apply3DFilter(ndimage.grey_erosion, size)

    def applyDilation(self, size: int=2):
        self.apply3DFilter(ndimage.grey_dilation, size)

    def applyNoiseFilter(self, algorithm: str='ErosionDilation', *filterArgs):
        # fixme: filterArgs hidden from user
        if algorithm == 'ErosionDilation':
            self.applyNoiseFilterWithErosionDilation(*filterArgs)
        else:
            raise NotImplementedError()

    def applyNoiseFilterWithErosionDilation(self, erosion_size=2, dilation_size=2, closing_size=2):
        # todo: maybe try to implement multiple function with args call inside self.apply3DFilter(s)
        # this function actually doesnt really make any sense,
        # its only through specific data noise filtering that such a combo happenned to be effective,
        # I guess this could be removed from the API, but I will look for a way to easily execute multiple filters in one call
        if self.processIn3D is None:
            raise ZStackProcessDimensionIsNotDefined
        elif self.processIn3D:
            filteredArrays = []
            for channel in list(range(self.numberOfChannels)):
                array = self.asChannelArray(channel)
                array = ndimage.grey_erosion(array, erosion_size)
                array = ndimage.grey_dilation(array, dilation_size)
                array = ndimage.grey_closing(array, closing_size)
                filteredArrays.append(array)
            newStack = np.stack(filteredArrays, axis=2)
            self.replaceFromArray(newStack)
        else:
            super().applyNoiseFilterWithErosionDilation(erosion_size, dilation_size, closing_size)

    def getChannelMaskArray(self, channel: int):
        assert self.hasMask, "Masks are not present."
        maskStackArray = np.stack([image.channels[channel].mask.pixels for image in self.images], axis=2)
        return maskStackArray

    def getChannelLabelArray(self, channel: int):
        assert self.hasLabelledComponents, "Labelled Components are not present."
        labelStackArray = np.stack([image.channels[channel].labelledComponents for image in self.images], axis=2)
        return labelStackArray

    def labelMaskComponents(self):
        """ Labelling always need to be processed in 3D """
        for channel in list(range(self.numberOfChannels)):
            maskStackArray = self.getChannelMaskArray(channel)
            labelStackArray, nbObjects = ndimage.label(maskStackArray)
            self.componentsProperties["Channel {}".format(channel)] = OrderedDict()
            self.componentsProperties["Channel {}".format(channel)]["nbOfObjects"] = nbObjects

            self.channelLabelsFromArray(channel, labelStackArray)

    def channelLabelsFromArray(self, channel, labelStackArray):
        for i in range(labelStackArray.shape[2]):
            labelArray = labelStackArray[:, :, i]
            self.images[i].channels[channel].labelledComponents = labelArray

    def analyzeComponents(self):
        for channel in list(range(self.numberOfChannels)):
            properties = self.componentsProperties['Channel {}'.format(channel)]
            if self.hasOriginal:
                originalArray = self.asOriginalChannelArray(channel)
            else:
                originalArray = self.asChannelArray(channel)
            maskArray = self.getChannelMaskArray(channel)
            labelArray = self.getChannelLabelArray(channel)

            properties["objectsSize"] = self.getObjectsSize(maskArray, labelArray)
            properties["totalSize"] = np.sum(properties["objectsSize"]).tolist()
            properties["objectsMass"] = self.getObjectsMass(originalArray, labelArray)
            properties["totalMass"] = np.sum(properties["objectsMass"]).tolist()
            properties["objectsCM"] = self.getObjectsCenterOfMass(originalArray, labelArray)
            properties["totalCM"] = np.average(properties["objectsCM"], axis=0, weights=properties["objectsMass"]).tolist()

    @staticmethod
    def getObjectsSize(maskStack, labelStack):
        nbOfObjects = int(labelStack.max())
        maskSizes = ndimage.sum(maskStack, labelStack, range(1, nbOfObjects + 1))
        return list(maskSizes)

    @staticmethod
    def getObjectsMass(originalStack, labelStack):
        nbOfObjects = int(labelStack.max())
        sumValues = ndimage.sum(originalStack, labelStack, range(1, nbOfObjects + 1))
        return list(sumValues)

    @staticmethod
    def getObjectsCenterOfMass(originalStack, labelStack):
        nbOfObjects = int(labelStack.max())
        centersOfMass = ndimage.center_of_mass(originalStack, labelStack, range(1, nbOfObjects + 1))
        return list(centersOfMass)

    def saveComponentsProperties(self, filePath: str):
        jsonParams = json.dumps(self.componentsProperties, indent=4)
        if filePath.split(".")[-1] != "json":
            filePath += ".json"

        with open(filePath, "w+") as file:
            file.write(jsonParams)

    def crop(self):
        # Cropping will not keep original content since cropping Z axis will change self.numberOfImages
        # So we are using fromArray(), not replaceFromArray()
        cropArray = self.crop4DArray(self.asArray())
        self.fromArray(cropArray)

    # todo: clean method
    def crop4DArray(self, array, axis=-1, bothAxis=True, viewChannelIndex: int=None):
        """ Static method to crop any 4D Arrays
            Careful: this method can be time and memory intensive if array has multiple channels with size around 1 GigaPixel
            :param viewChannelIndex to quickly load crop window of specified channelIndex, while still cropping all channels.
            :param bothAxis to crop both 3D planes
        """
        # todo: maybe add warning if viewChannelIndex=None and array has more than one channel and each channel is around or over 1 Gigapixel
        print("... Loading crop figure")

        if array.shape[2] == 1:
            # Skip useless and slow numpy conversion (a = a + 0.0) of np.mean if theres nothing to average
            projection = array[:, :, 0, :]
        elif viewChannelIndex is not None:
            projection = array[:, :, viewChannelIndex, :]
        else:
            # Careful : numpy.mean gets exponentially slower with array shape and can easily lead to MemoryError
            projection = array.mean(2)
        projection = projection.mean(axis)

        self.ask2DCropIndices(projection, axis)

        if axis == -1:
            array = array[self.cropY[0]: self.cropY[1], self.cropX[0]: self.cropX[1]]
            if bothAxis:
                return self.crop4DArray(array, axis=0)
            else:
                return array
        else:
            array = array[:, self.cropY[0]: self.cropY[1], :, self.cropX[0]: self.cropX[1]]
            return array

    def ask2DCropIndices(self, channelArray, axis=-1):
        # todo: move 2D / 3D crop logic to Channel / Image
        self.cropX = [0, channelArray.shape[axis+1]]
        self.cropY = [0, channelArray.shape[-axis]]

        figure, self.cropFig = plt.subplots()
        self.cropFig.imshow(channelArray, aspect="auto")
        rs = RectangleSelector(self.cropFig, self.__drawRectangleCallback,
                               drawtype='box', useblit=False, button=[1],
                               minspanx=5, minspany=5, spancoords='pixels',
                               interactive=True)
        plt.title("Select ROI", fontsize=18)
        plt.show()

    def __drawRectangleCallback(self, clickEvent, releaseEvent):
        x1, y1 = clickEvent.xdata, clickEvent.ydata
        x2, y2 = releaseEvent.xdata, releaseEvent.ydata

        if self.cropRect is not None:
            self.cropRect.remove()
        self.cropRect = plt.Rectangle((min(x1, x2), min(y1, y2)), np.abs(x1-x2), np.abs(y1-y2), fill=False)
        self.cropFig.add_patch(self.cropRect)
        self.cropX = [int(x1), int(x2)]
        self.cropY = [int(y1), int(y2)]

    def show(self, channel: int, axis=-1):
        stack4DArray = self.asChannelArray(channel)
        plt.imshow(stack4DArray.mean(axis))
        plt.show()

    def showAllStacks(self, channel: int=None, axis=-1):
        if channel is None:
            raise NotImplementedError("Can only plot single channel stacks.")  # TODO
        stacksDict = self.channelStacksInMemory(channel)
        fig, axes = plt.subplots(1, len(stacksDict))
        for i, (key, stack) in enumerate(stacksDict.items()):
            if key in ["Original ", ""]:
                axes[i].imshow(stack.mean(axis))
            else:
                axes[i].imshow(stack.max(axis))
            axes[i].set_title(key + "Stack")
        plt.show()

    def channelStacksInMemory(self, channel) -> dict:
        stacks = OrderedDict()
        if self.hasOriginal:
            stacks["Original "] = self.asOriginalChannelArray(channel)
        stacks[""] = self.asChannelArray(channel)
        if self.hasMask:
            stacks["Mask "] = self.getChannelMaskArray(channel)
        if self.hasLabelledComponents:
            stacks["Label "] = self.getChannelLabelArray(channel)
        return stacks


# FIXME: temporary, merge with pathPattern logic inside ZStack init
# notice that the folder contains one 2Dimage per channel per layer
def getZStackFromFolder(inputDir, channelsToSegment=[0], crop=True):
    files = list(os.walk(inputDir))[0][2]

    channelStacks = []
    for i, channel in enumerate(channelsToSegment):
        print("... Loading channel {}/{}".format(i+1, len(channelsToSegment)))
        channelFilePaths = [os.path.join(inputDir, f) for f in files if str(channel+1) in f.split("_")[-1]]

        channelImages = []
        for filePath in channelFilePaths:
            channelImages.append(np.array(PILImage.open(filePath)))
        stack = np.stack(channelImages, axis=-1)
        channelStacks.append(stack)

    stackArray = np.stack(channelStacks, axis=2)

    return ZStack(imagesArray=stackArray, cropAtInit=crop)
