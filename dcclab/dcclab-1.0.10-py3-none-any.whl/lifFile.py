from .lifReader import LIFReader
from .zStack import ZStack
from .imageFile import ImageFile
from typing import Union, List
import json


class LIFFile(ImageFile):
    supportedFormats = ['lif']

    def __init__(self, path):
        ImageFile.__init__(self, path)

        self.file = open(path, 'rb')
        try:
            self.__lifObject = LIFReader(self.file)
        except Exception as e:
            self.file.close()
            raise e
        self.series = self.__lifObject.getSeries()

    @property
    def numberOfSeries(self):
        return len(self.series)

    def __len__(self):
        return self.numberOfSeries

    def __getitem__(self, indices: Union[int, tuple, list, slice]=None):
        if indices is None:
            return self.series
        if type(indices) is slice:
            return self.series[indices]
        elif type(indices) is int:
            return self.series[indices]
        elif type(indices) is tuple:
            indices = list(indices)

        if type(indices) is list:
            return [self.series[i] for i in indices]

    def keepSeries(self, indices):
        self.series = self[indices]
        if type(self.series) is not list:
            self.series = [self.series]

    def removeAt(self, index: int):
        self.series.pop(index)

    def zStackData(self, seriesIndex: int=None, channelIndices=None, crop=False) -> 'ZStack':
        if seriesIndex is None:
            assert self.numberOfSeries == 1, "Cannot infer the right series to take since the file has more than one series."
            seriesIndex = 0

        print("... Loading serie")
        stackArray = self.series[seriesIndex].getStack(channelIndices)
        print("... Loading ZStack Collection")
        zStack = ZStack(imagesArray=stackArray, cropAtInit=crop)
        return zStack

    def zStacksData(self, seriesIndices=None, channelIndices=None, crop=False) -> List['ZStack']:
        if type(seriesIndices) is int:
            seriesIndices = [seriesIndices]

        series = self[seriesIndices]

        zStacks = []
        for i, serie in enumerate(series):
            print("... Loading serie {}/{}".format(i+1, len(series)))
            stackArray = serie.getStack(channelIndices)
            print("... Loading ZStack Collection")
            zStack = ZStack(imagesArray=stackArray, cropAtInit=crop)
            zStacks.append(zStack)

        return zStacks

    def imageDataFromPath(self):
        # todo ?  not sure we need to implement this method. It's not a parent method but I see that all other child classes have this method defined...
        return None

    def metadata(self, serieIndex: int=None, asJson: bool=False):
        if serieIndex is None:
            metadata = []
            for i, serie in enumerate(self.series):
                metadata.append({'serie %i' % i: serie.getMetadata()})
        else:
            metadata = self.series[serieIndex].getMetadata()

        if asJson:
            return json.dumps(metadata, indent=4)
        return metadata

    def close(self):
        self.file.close()
