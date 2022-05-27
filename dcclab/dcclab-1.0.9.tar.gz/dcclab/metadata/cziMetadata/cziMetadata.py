import xml.etree.ElementTree as et
from .cziChannel import CZIChannel as chnnl
from .cziFilter import CZIFilter as fltr
from dcclab.cziUtil import readCziImage, extractMetadataFromCziFileObject
import re
import os


class CZIMetadata:
    def __init__(self, filePath, name=None):
        self.filePath = filePath
        if name is not None:
            self.name = name
        else:
            self.name = self.nameFromPath()
        self.root = self.createElementTreeRoot()

        # Filters and channels are lists of objects.
        self.filters = self.findFiltersInRoot()
        self.channels = self.findChannelsInRoot()

        self.mouseId = self.setMouseId()
        self.viralVectors = self.setViralVectors()
        self.injectionSite = self.setInjectionSite()
        self.microscope = self.setMicroscope()
        self.objective = self.setObjective()
        self.xScale = self.setXScale()
        self.yScale = self.setYScale()
        self.xSize = self.setXSize()
        self.ySize = self.setYSize()
        self.tags = self.setTags()

    def __repr__(self):
        return '{};{};{}'.format(self.filePath, self.filters, self.channels)

    def __eq__(self, other):
        return repr(self) == repr(other)

    def asDict(self):
        channelsAsDict = {}
        for channel in self.channels:
            channelsAsDict['{}'.format(channel.channel)] = channel.asDict()
        metadataAsDict = {'file_path': self.filePath, 'channels': self.numberOfChannels, 'microscope': self.microscope,
                          'objective': self.objective, 'x_size': self.xSize, 'y_size': self.ySize,
                          'x_scale': self.xScale, 'y_scale': self.yScale, 'x_scaled': self.xScaled,
                          'y_scaled': self.yScaled, 'name': self.name, 'mouse_id': self.mouseId,
                          'viral_vectors': self.viralVectors, 'injection_site': self.injectionSite, 'tags': self.tags}
        return {'metadata': metadataAsDict, 'channels': channelsAsDict}

    @property
    def numberOfChannels(self):
        try:
            return len(self.channels)
        except:
            return 0

    @property
    def keys(self):
        channelsKeys = {}
        if self.channels:
            channelsKeys = self.channels[0].keys
        metadataKeys = {'file_path': 'TEXT PRIMARY KEY', 'channels': 'INTEGER', 'microscope': 'TEXT', 'objective': 'TEXT',
                        'x_size': 'INTEGER', 'y_size': 'INTEGER', 'x_scale': 'REAL', 'y_scale': 'REAL',
                        'x_scaled': 'REAL', 'y_scaled': 'REAL', 'name': 'TEXT', 'mouse_id': 'INTEGER',
                        'viral_vectors': 'TEXT', 'injection_site': 'TEXT', 'tags': 'TEXT'}
        return {'cziMetadata': metadataKeys, 'cziChannels': channelsKeys}

    def nameFromPath(self):
        try:
            return os.path.basename(self.filePath)
        except Exception:
            return None

    def cziImageObjectFromPath(self):
        try:
            return readCziImage(self.filePath)
        except FileNotFoundError:
            raise
        except ValueError:
            raise

    def xmlFromCziImageObject(self, cziImageObject):
        try:
            return extractMetadataFromCziFileObject(cziImageObject)
        except AttributeError:
            raise

    def createElementTreeRoot(self):
        cziImageObject = self.cziImageObjectFromPath()
        stringXML = self.xmlFromCziImageObject(cziImageObject)
        cziImageObject.close()
        return et.fromstring(stringXML)

    def checkIfElementHasChildren(self, element):
        if element is None:
            return False
        try:
            if not list(element):
                return False
            return True
        except Exception:
            return False

    def setMouseId(self):
        # Pattern is s followed by 1 to 4 digits and ignoring lower or upper case.
        # Return the digits.
        try:
            return re.search(r's\d{1,4}', self.name, re.IGNORECASE).group()[1:]
        except AttributeError:
            return None

    def setViralVectors(self):
        try:
            vectors = self.findAAVVectors() + ';' + self.findRabVectors()
            vectors = vectors.lstrip(';')
            vectors = vectors.rstrip(';')
            return vectors
        except Exception:
            return None

    def findRabVectors(self):
        # We can have either rab#.# or rabv#.# so we try to find either patterns.
        try:
            rabList = re.findall(r'(rabv?\d(?:\.\d)?)', self.name, re.IGNORECASE)
            rabs = ';'.join(rabList)
            return rabs
        except Exception:
            return None

    def findAAVVectors(self):
        # We can have either very distinct AAV### patterns or AAV###+### or AAV###-###.
        # We have to search for all three. AAV###-### and AAV###+### are splitted into different vectors and their
        # names are normalized to AAV###.
        try:
            aavList = re.findall(r'AAV\d{3,4}(?:[-+]\d{3,4})?', self.name, re.IGNORECASE)
            aavs = ';'.join(aavList)
            aavs = re.sub(r'[-+]', ';AAV', aavs)
            return aavs
        except Exception:
            return None

    def setInjectionSite(self):
        try:
            return re.search(r'patte|IV', self.name, re.IGNORECASE).group()
        except Exception:
            return None

    def setMicroscope(self):
        try:
            return self.root.find('./Metadata/Information/Instrument/Microscopes/Microscope').attrib['Name']
        except Exception:
            return None

    def setObjective(self):
        try:
            return self.root.find('./Metadata/Information/Instrument/Objectives/Objective').attrib['Name']
        except Exception:
            return None

    def setXScale(self):
        try:
            return float(self.root.find('./Metadata/Scaling/Items/Distance[@Id="X"]/Value').text)
        except Exception:
            return None

    def setYScale(self):
        try:
            return float(self.root.find('./Metadata/Scaling/Items/Distance[@Id="Y"]/Value').text)
        except Exception:
            return None

    def setXSize(self):
        try:
            return int(self.root.find('./Metadata/Information/Image/SizeX').text)
        except Exception:
            return None

    def setYSize(self):
        try:
            return int(self.root.find('./Metadata/Information/Image/SizeY').text)
        except Exception:
            return None

    @property
    def xScaled(self):
        try:
            return (int(self.xSize) * float(self.xScale)) * 1000
        except Exception:
            return None

    @property
    def yScaled(self):
        try:
            return (int(self.ySize) * float(self.yScale)) * 1000
        except Exception:
            return None

    def findFiltersInRoot(self):
        newFilters = []
        try:
            filters = self.root.find('./Metadata/Information/Instrument/Filters')
            if self.checkIfElementHasChildren(filters):
                for filter in filters:
                    filterId = filter.attrib['Id']
                    newFilters.append(fltr(filterId, self.root))
            return newFilters
        except Exception:
            return newFilters

    def findChannelsInRoot(self):
        newChannels = []
        try:
            channels = self.root.find('./Metadata/Information/Image/Dimensions/Channels')
            if self.checkIfElementHasChildren(channels):
                for channel in channels:
                    channelInformation = [channel.attrib['Id'], channel.attrib['Name'], self.filePath]
                    newChannels.append(chnnl(channelInformation, self.filters, self.root))
            return newChannels
        except Exception:
            return newChannels

    def setTags(self):
        try:
            tagList = re.findall(r'moelle|neurones|drg|BB|anti\s?mcherry|anti\s?rabbit|cre|cx3cr1', self.name, re.IGNORECASE)

            newTagList = []
            for tag in tagList:
                if newTagList.count(tag) < 1:
                    newTagList.append(tag)
            tags = ';'.join(newTagList)
            tags = re.sub(' ', '', tags)
            return tags
        except Exception:
            return []
