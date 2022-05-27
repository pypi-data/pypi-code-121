from dcclab import ImageCollection, Image
from typing import List
import pandas as pd
import numpy as np
import json
import os

"""
Machine Learning Dataset

It needs to be able to load such data structures: 

<SEMANTIC>
data/
|-- type_A
    |-- 0.png
    |-- ...
|-- type_A_labels
    |-- 0.png
    |-- ...
|-- type_B
|-- type_B_labels
|-- mixed
|-- mixed_labels
|-- ...

OR 

<SEMANTIC>
data/
|-- images
    |-- 0.png  # [each image might contain multiple classes]
    |-- ...
|-- labels
    |-- 0.png
    |-- ...

OR

<NOT semantic>  # labels are foldernames  # ** this structure cannot be infered : user has to specify if its semantic or not
data/
|-- cats
    |-- 0.png
    |-- ...
|-- dogs
    |-- 0.png
    |-- ...


+ some variants considering the fact that the labels might not exist yet.


In the first case it has to separate and remember each type (or source?) by their name.
This looks to me like each type (called class in ML classification) or source, with its labels, is one image collection object. 
This means that a Dataset Class has to load multiple ImageCollections (and remember their names).

I would then define a Dataset class without heritage, that intentiate different ImageCollection objects (or maybe 
a new `MLCollection` object heriting from ImageCollection).
"""


class Dataset:
    def __init__(self, directory: str):
        self.directory = directory
        self.labelTag = 'label'

        self.collections = {}
        self.collectionsInfo = {}
        self.info = {'type': None, 'supervised': None, 'model': None,
                     'labels': {}, 'clsNames': {}, 'hasLabels': None,
                     'validLabel': None, 'hasStringLabels': False}

        self.loadAllCollections()
        self.report()
    @property
    def isSemantic(self):
        return self.info["type"] is not None    

    def loadAllCollections(self):
        folders = self.getFolders(self.directory)
        files = self.getFiles(self.directory)

        if len(folders) != 0:
            assert len(files) == 0, "Cannot infer datafile structure if a directory has folders and files."

            orderedFolders = [f for f in folders if self.labelTag not in f]
            orderedFolders.extend([f for f in folders if self.labelTag in f])
            for folder in orderedFolders:
                self.loadCollectionFiles(os.path.join(self.directory, folder))

        elif len(files) != 0:
            self.loadCollectionFiles(self.directory)

        else:
            raise FileNotFoundError

        self.loadCollectionObjects()

    def loadCollectionFiles(self, source):
        # TODO: support non-semantic structure.
        """ self.collections = {'sourceName': [list(imageFiles), list(labelFiles)], ...} """

        folderName = os.path.basename(source)
        if self.labelTag not in folderName:
            self.collections[folderName] = self.getImageAndLabelFiles(source)
        else:
            folderName = [key for key in self.collections.keys() if key in folderName][0]
            self.collections[folderName][1] = self.getFiles(source, absolute=True)

    def loadCollectionObjects(self):
        """ self.collections = {'sourceName': ImageCollection(), ...} """

        for key in self.collections:
            imageFiles, labelFiles = self.collections[key]
            images = [Image(path=file) for file in imageFiles]
            self.collections[key] = MLImageCollection(images=images)
            self.collections[key].source = key

            if len(labelFiles) != 0:
                labels = [Image(path=file).channels[0] for file in labelFiles]
                self.collections[key].setLabelledComponents(labels=labels)
                self.info['type'] = "Semantic classification"
                self.info['supervised'] = True

    def report(self):
        self.updateCollectionsInfo()
        self.updateDatasetInfo()

        infoKeys = ['source', 'nbOfImages', 'hasLabels', 'clsValues', 'clsRatios', 'sameShape', 'shape']
        infoKeys = [k for k in infoKeys if k in self.collectionsInfo]
        df = pd.DataFrame(self.collectionsInfo, columns=infoKeys)

        print("# Collections Info\n{}\n".format(df.to_string()))

        if self.info["hasLabels"] and not self.info['hasStringLabels']:
            df = self.getClassInfoDF()
            print("# Class Info\n{}\n".format(df.to_string(index=False)))

        df = pd.DataFrame.from_records([self.info], columns=['hasLabels', 'validLabel', 'nbOfClasses', 'type', 'supervised', 'model'])
        print("# Dataset Info\n{}\n".format(df.T.to_string(header=False)))

        # - pixel values for the labels correspond to class indexes
        # - image format is png
        # - classes are balanced (ratio)
        # - the dataset is big enough
        # - ...

    def updateCollectionsInfo(self):
        self.collectionsInfo = {}
        self.info['hasLabels'] = None

        for collection in self.collections.values():
            for k, v in collection.info.items():
                self.collectionsInfo.setdefault(k, []).append(v)

            if collection.hasStringLabels:
                continue

            elif collection.info["hasLabels"]:
                for value, count in zip(collection.info["clsValues"], collection.info["clsCounts"]):
                    if str(value) not in self.info["labels"]:
                        self.info["labels"][str(value)] = int(count)
                    else:
                        self.info["labels"][str(value)] += int(count)

                for value, name in collection.info["clsNames"].items():
                    if str(value) not in self.info["clsNames"]:
                        self.info["clsNames"][str(value)] = name
                    elif self.info["clsNames"][str(value)] != name:
                        self.info["validLabel"] = False
            else:
                self.info['hasLabels'] = False

    def updateDatasetInfo(self):
        if self.info['hasLabels'] is None:
            self.info['hasLabels'] = True

            if self.info['validLabel'] is None:
                self.info['validLabel'] = True

        if self.info['hasLabels']:
            classValues, classCounts = list(self.info["labels"].keys()), list(self.info["labels"].values())
            totalCount = np.sum(classCounts)
            classRatios = [np.round(count / totalCount * 100, 1) for count in classCounts]
            nbOfClasses = len(classValues) if len(classValues) != 0 else None

            self.info.update({"clsValues": classValues, "clsCounts": classCounts,
                              "clsRatios": classRatios, "nbOfClasses": nbOfClasses})

    def getClassInfoDF(self) -> pd.DataFrame:
        classInfo = []
        for i, (value, name) in enumerate(self.info['clsNames'].items()):
            count = self.info['clsCounts'][i]
            ratio = self.info['clsRatios'][i]
            classDict = {'name': name, 'value': value, 'count': count, 'ratio': ratio}
            classInfo.append(classDict)

        df = pd.DataFrame(classInfo, columns=['name', 'value', 'count', 'ratio']).sort_values(by='value')
        df.rename(columns={'name': 'name      '}, inplace=True)
        return df

    def applyLabelsFromSourceNames(self):
        for source in self.collections:
            collection = self.collections[source]
            assert not collection.hasLabelledComponents, "Collection already has labels"

            for image in collection.images:
                for channel in image.channels:
                    channel.setLabelledComponents(source)
            collection.hasStringLabels = True

        self.info['hasStringLabels'] = True
        self.info['type'] = "Classification"
        self.info['supervised'] = True

    def setModel(self, model: str=None):
        if model is None:
            # infer model...
            if self.info['type'] == "Semantic classification":
                # use resnet50... check size...
                pass

        self.info["model"] = model

    def train(self):
        pass

    @staticmethod
    def getFolders(source):
        paths = list(os.walk(source)) 
        if len(paths) == 0:
            raise FileNotFoundError()

        return paths[0][1]

    @staticmethod
    def getFiles(source, absolute=False):
        filenames = list(os.walk(source))[0][2]
        if absolute:
            return [os.path.join(source, fn) for fn in filenames]
        else:
            return filenames

    def getImageAndLabelFiles(self, source) -> list:
        filenames = self.getFiles(source)
        imageFiles = [os.path.join(source, fn) for fn in filenames if self.labelTag not in fn]
        labelFiles = [os.path.join(source, fn) for fn in filenames if self.labelTag in fn]
        return [imageFiles, labelFiles]


class MLImageCollection(ImageCollection):
    def __init__(self, images: List['Image']=None, imagesArray: np.ndarray=None, pathPattern: str=None):
        super().__init__(images, imagesArray, pathPattern)

        self.source = None
        self.hasStringLabels = False

    @property
    def info(self) -> dict:
        info = {"source": self.source}

        if self.hasLabelledComponents and not self.hasStringLabels:
            classValues, classCounts = list(self.labelInfo.keys()), list(self.labelInfo.values())

            totalCount = np.sum(classCounts)
            classRatios = [np.round(count / totalCount * 100, 1) for count in classCounts]

            classNames = {}
            if 0 in classValues and len(classValues) == 2:
                classNames[str(0)] = "background"
                classNames[str(sorted(classValues)[-1])] = self.source

            info.update({"clsValues": classValues, "clsCounts": classCounts,
                         "clsRatios": classRatios, "clsNames": classNames})

        if self.imagesAreSimilar:
            info.update({"shape": self.images[0].shape})

        info.update({"hasLabels": self.hasLabelledComponents,
                     "nbOfImages": self.numberOfImages,
                     "sameShape": self.imagesAreSimilar})

        return info

    def augment(self):
        # Keras image augmentation generator
        pass


if __name__ == '__main__':
    dataset = Dataset(directory="./tests/testData/labelledDataset")
    # dataset = Dataset(directory="./tests/testData/dataset")
    # dataset.applyLabelsFromSourceNames()
    # dataset.report()


"""

Maybe replace ImageCollection with a possible ML Collection ? ...

"""


class MLCollection:
    supportedTypes = ["Image", "Spectra"]

    def __new__(cls, data: List[np.ndarray]):
        # An ML Collection is always a list of samples
        # check data dimensions and try to infer data type

        if data[0].ndim == 1:
            return super(MLCollection, cls).__new__(MLSpectraCollection)
        elif 1 < data[0].ndim <= 3:
            return super(MLCollection, cls).__new__(MLImageCollection)
        else:
            raise NotImplementedError

    def augment(self):
        pass


class MLSpectraCollection:  # ?  (SpectraCollection)

    def augment(self):
        # Spectra augmentation technique
        pass
