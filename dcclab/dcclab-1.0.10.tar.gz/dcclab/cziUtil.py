import czifile
import numpy as np
import matplotlib.pyplot as plt
import tifffile
import time
import xml.etree.ElementTree as ET
import os
import fnmatch
import multiprocessing
import warnings
from concurrent.futures import ThreadPoolExecutor

"""
Python script containing utility functions to be used for handling .czi images.

These functions are supposed to work with the CZI format files used with POM images.
Since Python doesn't offer a lot of libraries (and those available are not well documented (some are just not) or
requiring weird stuff) to play with that format, I needed to do a little file so that it's easier to breath in the
.czi jungle.

The main object used in this file is the CziFile object from the czifile library

Hope it works correctly!
"""
"""
First, let's import the useful stuff
"""


def findAllCziFiles(directory):
    allCZIs = []
    for root, directories, files in os.walk(os.path.normpath(directory)):
        for file in files:
            if fnmatch.fnmatch(file, '*.czi'):
                allCZIs.append([file, os.path.join(root, file)])
    return allCZIs


def readCziImage(filename):
    """
    Function that read a .czi file.
    :param filename: Name of the file.
    :return: CziFile object (from czifile package). The file must be closed at the end of the process.
    See close() function below.
    """
    czi = czifile.CziFile(filename)
    return czi


def closeCziFileObject(cziObject):
    """
    Function that closes a CziFile instance object. It must be closed according to the CziFile documentation.
    :param cziObject: The CziFile object to be closed
    :return: Nothing
    """
    cziObject.close()


def extractMetadataFromCziFileObject(cziObject, saveFileName=None):
    """
    Function that raeds the metadata form a CziFile object
    :param cziObject: The CziFile object
    :param saveFileName: Name of the file that is used to save the metadata (XML file). If None (default), doesn't
    save the metadata.
    :return: The metadata in XML formated string.
    """
    meta = cziObject.metadata()
    if saveFileName is not None:
        file_xml = open("{}.xml".format(saveFileName), "w", encoding="utf-8")
        file_xml.write(meta)
        file_xml.close()
    return meta


def getImagesFromCziFileObject(cziObject):
    """
    Function that returns the images from a czi file object, with every channel.
    :param cziObject: The CziFile object
    :return: Numpy array containing the images
    """
    arrayReturn = []
    subblocksIters = cziObject.subblocks()
    i = 0
    for iterator in subblocksIters:
        arrayReturn.append(np.squeeze(iterator.data()))
        i += 1
        if i == 3:
            break
    return np.array(arrayReturn)


def decodeCZIFile(cziObj, showProgress=False):
    """Return image data from file(s) as numpy array and returns the list of tiles

    This is based on the czifil asarray method except it is modified so the data extraction is only done once.
    """
    maxSize = len(cziObj.filtered_subblock_directory)
    if showProgress:
        print("Reading the pixels value of {} tile{}. This may take a few minutes.".format(maxSize,
                                                                                           "s" if maxSize > 1 else ""))
    out = tifffile.create_output(None, cziObj.shape, cziObj.dtype)
    returnList = []

    def func(directory_entry, start=cziObj.start, out=out):
        """Read, decode, and copy subblock data."""
        subblock = directory_entry.data_segment()
        tile = subblock.data()

        index = tuple(slice(i - j, i - j + k) for i, j, k in
                      zip(directory_entry.start, start, tile.shape))
        returnList.append((index, np.squeeze(tile)))
        if showProgress:
            print("{} / {} tile{} read".format(len(returnList), maxSize, "s" if len(returnList) > 1 else ""))
        try:
            out[index] = tile
        except ValueError as e:
            warnings.warn(str(e))

    before = time.perf_counter()
    for directory_entry in cziObj.filtered_subblock_directory:
        func(directory_entry)
    after = time.perf_counter()
    if showProgress:
        print("Reading data took {:.2f} seconds".format(after - before))
    return out, returnList


def showImagesFromCziFileObject(cziObject):
    """
    Function that shows the images in a czi file object. The function shows them one by one, no subplots.
    :param cziObject: CziFile object
    :return: Numpy array of matplotlib.image.AxesImage (each of the matplotlib.image.AxesImage of the initial image)
    """
    subblocksIters = cziObject.subblocks()
    imagesReturn = []
    for iterator in subblocksIters:
        image = (np.squeeze(iterator.data()))
        image_return = plt.imshow(image)
        imagesReturn.append(image_return)
        plt.set_cmap("gray")
        plt.show()
    return np.array(imagesReturn)


def getFormatedMetadata(metadata):
    """
    Function that formats the XMl-string metadata in a more convenient way, easier to read and to browse.
    :param metadata: XML formatted string containing the metadata.
    :return: String containing the formatted metadata
    """
    returnString = ""
    try:
        tree = ET.ElementTree(ET.fromstringlist(metadata))
        for iterator in tree.iter():
            returnString += "{} : {}\n".format(iterator.tag, iterator.text)
    except ET.ParseError as exception:
        raise ValueError("Exception with string \"{}\"; {}".format(
            metadata, exception.msg))
    return returnString


def saveImagesToTIFF(imageArray, filename=None):
    """
    Function that saves every image in an array to a TIFF file.
    :param imageArray: Array of images to be saved. If the array is empty, nothing is done.
    :param filename: The file name to save the new tiff image. If None (default), a default name is given.
    :return: bool. True if the image is saved, False if nothing is done.
    """
    isSaved = False
    if len(imageArray) != 0:
        isSaved = True
        i = 0
        for image in imageArray:
            i += 1
            if filename is not None:
                tifffile.imwrite("{}_{}.tif".format(filename, i), image)
            else:
                tifffile.imwrite("array2tiff_{}.tif".format(i), image)
    return isSaved
