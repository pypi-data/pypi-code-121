from .cziMetadata import CZIMetadata
from .dtfMetadata import DTFMetadata
from .xlsxMetadata import PDKXLSXMetadata
from .sciMetadata import sciMetadata
import os
import re
try:
    import deprecated
except:
    exit("pip install deprecated")


class Metadata:
    # Supported research groups.
    supportedResearchGroups = ['POM', 'PDK']
    supportedFormats = ['CZI', 'DTF', 'SCIENTIFICA', 'XLSX']

    # Supported classes and formats for POM.
    pomSupportedClasses = [CZIMetadata, DTFMetadata]
    pomSupportedFormats = ['CZI', 'DTF']

    # Supported classes and formats for PDK.
    pdkSupportedClasses = [sciMetadata, PDKXLSXMetadata]
    pdkSupportedFormats = ['SCIENTIFICA', 'XLSX']

    def __init__(self, path: str):
        if path is not None:
            if not os.path.exists(path):
                raise ValueError("Cannot load '{0}': file does not exist".format(path))
            self.path = path
            self.__researchGroup = self.validateResearchGroup()
            self.__fileObject = self.processFile()
        else:
            self.path = None
            self.__fileObject = None

    def processFile(self):
        if self.__researchGroup == 'POM':
            for supportedClass in Metadata.pomSupportedClasses:
                try:
                    fileObject = supportedClass(self.path)
                    return fileObject
                except:
                    continue
            raise TypeError("Cannot load '{}' : file is not from a recognized format for that research group "
                            "({}).".format(self.path, Metadata.pomSupportedFormats))

        elif self.__researchGroup == 'PDK':
            for supportedClass in Metadata.pdkSupportedClasses:
                try:
                    fileObject = supportedClass(self.path)
                    return fileObject
                except:
                    continue
            raise TypeError("Cannot load '{}' : file is not from a recognized format for that research group "
                            "({}).".format(self.path, Metadata.pdkSupportedFormats))

    def validateResearchGroup(self):
        for researchGroup in Metadata.supportedResearchGroups:
            if re.search(r'[\\/]{}[\\/]'.format(researchGroup), self.path):
                return researchGroup

        raise ValueError("Cannot load '{}' : file is not from a recognized research group database "
                         "({}).".format(self.path, Metadata.supportedResearchGroups))

    @property
    def metaType(self):
        fileType = type(self.__fileObject)
        if fileType == CZIMetadata:
            return 'CZI'
        elif fileType == DTFMetadata:
            return 'DTF'
        elif fileType == PDKXLSXMetadata:
            return 'XLSX'
        elif fileType == sciMetadata:
            return 'SCIENTIFICA'
        else:
            return None

    @property
    def metadata(self) -> dict:
        if isinstance(self.__fileObject, CZIMetadata):
            return self.__fileObject.asDict().get('metadata')
        elif isinstance(self.__fileObject, DTFMetadata) or isinstance(self.__fileObject, PDKXLSXMetadata) \
                or isinstance(self.__fileObject, sciMetadata):
            return self.__fileObject.asDict
        else:
            return {}

    @property
    def channels(self) -> dict:
        if isinstance(self.__fileObject, CZIMetadata):
            return self.__fileObject.asDict().get('channels')
        else:
            return {}

    @property
    def keys(self) -> dict:
        return self.__fileObject.keys
