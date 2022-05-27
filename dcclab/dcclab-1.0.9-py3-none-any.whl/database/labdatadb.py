from .database import *
import numpy as np
import re
from collections.abc import Iterable

class LabdataDB(Database):
    """
    This is a general database tool to access all information about projects,
    files, and spectral datasets of the DCCLab. You use it with:

    ```
    db = LabdataDB() # or db=SpectraDB() to get a few specific spectra functions
    ```
    The database has the following tables:

    +-------------------+
    | Tables_in_labdata |
    +-------------------+
    | datapoints        |
    | datasets          |
    | files             |
    | projects          |
    | scanlog           |
    | spectra           |
    | users             |
    | volumes           |
    | wines             |
    +-------------------+


    The database is on Cafeine3 and can be accessed with the dcclab username and normal password via a
    secure shell, and then via mysql also with dcclab and the same password.
    The database is called labdata, and the default value of the URL
    to access it is set to:
    mysql+ssh://dcclab@cafeine2.crulrg.ulaval.ca:cafeine3.crulrg.ulaval.ca/dcclab@labdata
    which can be interpreted as:
    mysql://ssh_username@ssh_host:mysql_host/mysql_user@mysql_database

    You can provide your own link if you have a local version on your computer, such as:
    db = LabdataDB("mysql://127.0.0.1/dcclab@labdata")

    In the case of 127.0.0.1 (or localhost), it will not use ssh and will connnect
    directly.
    """
    def __init__(self, databaseURL=None):
        """
        The Database is initialized to:
        mysql+ssh://dcclab@cafeine2.crulrg.ulaval.ca:cafeine3.crulrg.ulaval.ca/dcclab@labdata

        which allows access from outside the CERVO Center.  The first time, you will have to provide the password for
        dcclab on cafeine2.crulrg.ulaval.ca and on the MySQL server dcclab on cafeine3.crulrg.ulaval.ca
        """
        if databaseURL is None:
            databaseURL = "mysql+ssh://dcclab@cafeine2.crulrg.ulaval.ca:cafeine3.crulrg.ulaval.ca/dcclab@labdata"

        self.constraints = []
        super().__init__(databaseURL)

    def getProjectIds(self):
        """
        The database

        :return:
        """

        self.execute("select projectId from projects")
        rows = self.fetchAll()
        projects = []
        for row in rows:
            projects.append(row["projectId"])

        return projects

    def describeProjects(self):
        self.execute("select projectId, description from projects order by projectId")
        rows = self.fetchAll()
        for row in rows:
            description = "Dataset: {0}".format(row["projectId"])
            print(description)
            print("-"*len(description))
            print("{0}\n".format(row["description"]))

    def getDatasets(self):
        self.execute("select datasetId from datasets")
        rows = self.fetchAll()
        datasets = []
        for row in rows:
            datasets.append(row["datasetId"])

        return datasets

    def describeDatasets(self, datasetId=None):
        if datasetId is not None:
            self.execute("select datasetId, description from datasets where datasetId = %s order by datasetId", (datasetId,))
        else:
            self.execute("select datasetId, description from datasets order by datasetId")
        rows = self.fetchAll()

        for row in rows:
            description = "Dataset: {0}".format(row["datasetId"])
            print(description)
            print("-"*len(description))
            print("{0}\n".format(row["description"]))

    def getSpectrumIds(self, **args ):
        datasetId = args.get("datasetId")
        genericToUserLabels, userToGenericLabels = self.getUserIdLabelsMapping(datasetId)

        conditions = []
        bindings = []
        for field, value in args.items():
            if field in userToGenericLabels.keys():
                field = userToGenericLabels.get(field) # change userIdLabels to genericIdLabels

            if value is not None:
                if isinstance(value, tuple) or isinstance(value, list):
                    conditions.append("{0} in {1}".format(field, value))
                else:
                    conditions.append("{0} = %s".format(field))
                    bindings.append(value)
        whereClause = ' and '.join(conditions)

        return self.executeSelectFetchOneField("select spectrumId from spectra where {0}".format(whereClause), bindings )

    def getDataTypes(self):
        self.execute("select distinct dataType from spectra")
        rows = self.fetchAll()
        dataTypes = []
        for row in rows:
            dataTypes.append(row["dataType"])

        return dataTypes

    def getDatasetId(self, spectrumId):
        return self.executeSelectOne(
            "select datasetId from spectra where spectrumId = %s", (spectrumId,)
        )

    def createNewDataset(
        self, datasetId, id1Label, id2Label, id3Label, id4Label, description, projectId
    ):
        self.execute(
            """
            insert into datasets (datasetId, id1Label, id2Label, id3Label, id4Label, description, projectId)
            values(%s, %s, %s, %s, %s, %s, %s)
            """,
            (datasetId,
            id1Label,
            id2Label,
            id3Label,
            id4Label,
            description,
            projectId)
        )

    def getSpectrum(self, spectrumId):
        datasetId = self.getDatasetId(spectrumId)

        whereConstraints = []
        whereConstraints.append("spectra.spectrumId = '{0}'".format(spectrumId))

        if len(whereConstraints) != 0:
            whereClause = "where " + " and ".join(whereConstraints)
        else:
            whereClause = ""

        stmnt = """
        select x, y from datapoints left join spectra on datapoints.spectrumId = spectra.spectrumId
        {0} 
        order by x """.format(
            whereClause
        )

        self.execute(stmnt)

        rows = self.fetchAll()
        intensity = []
        for i, row in enumerate(rows):
            intensity.append(float(row["y"]))

        return np.array(intensity)

    def getSpectra(self, datasetId=None, **args):
        if datasetId is not None:
            spectrumIds = self.getSpectrumIds(datasetId=datasetId, **args)

        spectra = None

        for spectrumId in spectrumIds:
            spectrum = self.getSpectrum(spectrumId)
            if spectra is None:
                spectra = spectrum
            else:
                spectra = np.vstack((spectra, spectrum))

        return spectra.T,  spectrumIds

    def getFrequencies(self, datasetId=None, **args):
        if datasetId is not None:
            genericToUserLabels, userToGenericLabels = self.getUserIdLabelsMapping(datasetId)

            conditions = ['spectra.datasetId = %s']
            bindings = [datasetId]
            for field, value in args.items():
                if field in userToGenericLabels.keys():
                    field = userToGenericLabels.get(field)  # change userIdLabels to genericIdLabels

                if value is not None:
                    if isinstance(value, tuple) or isinstance(value, list):
                        conditions.append("{0} in {1}".format(field, value))
                    else:
                        conditions.append("{0} = %s".format(field))
                        bindings.append(value)
            whereClause = ' and '.join(conditions)

            if len(whereClause) == 0:
                self.execute(
                    r"select distinct(x) from datapoints left join spectra on spectra.spectrumId = datapoints.spectrumId "
                    r"where {0}".format(whereClause), bindings
                )
            else:
                self.execute(
                    r"select distinct(x) from datapoints left join spectra on spectra.spectrumId = datapoints.spectrumId "
                    r"where {0}".format(whereClause), bindings
                )
        else:
            self.execute(
                r"select distinct(x) from datapoints where spectrumId = %s",
                (spectrumId,)
            )

        rows = self.fetchAll()
        nTotal = len(rows)

        freq = np.zeros(shape=(nTotal))
        for i, row in enumerate(rows):
            freq[i] = row["x"]

        return freq

    def getIdTypes(self, datasetId):
        idTypes = {}
        for fieldName in ["id1", "id2", "id3", "id4"]:
            values = self.executeSelectFetchOneField(f"select distinct({fieldName}) from spectra where datasetId = %s", (datasetId,))
            inferredType = self._inferListType(values)
            idTypes[fieldName] = inferredType

        return idTypes

    def getUserIdLabelsMapping(self, datasetId):
        row = self.executeSelectFetchOneRow(r"select id1Label, id2Label, id3Label, id4Label from datasets where datasetId = %s", (datasetId,))

        userIdLabels = list(filter(None, [row["id1Label"],row["id2Label"],row["id3Label"],row["id4Label"]]))
        genericIdLabels = ["id1", "id2", "id3", "id4"][0:len(userIdLabels)]

        return dict(zip(genericIdLabels, userIdLabels)), dict(zip(userIdLabels, genericIdLabels))

    def getPossibleIdValues(self, datasetId):
        genericToUserIdLabels, _ = self.getUserIdLabelsMapping(datasetId)

        idValues = {}
        for i, genericFieldName in enumerate(genericToUserIdLabels.keys()):
            values = self.executeSelectFetchOneField(f"select distinct({genericFieldName}) from spectra where datasetId = %s", (datasetId,))
            inferredType = self._inferListType(values)
            idValues[genericFieldName] = list(map(inferredType, values))
            userFieldName = genericToUserIdLabels[genericFieldName]
            idValues[userFieldName] = idValues[genericFieldName]

        return idValues

    def _inferListType(self, values):
        try :
            if False not in [str(int(v)) == v for v in values]:
                return int
        except Exception as err:
            pass

        try :
            if False not in [float(v) for v in values]:
                return float

        except Exception as err:
            pass

        return str

    def getSpectrumIdFormat(self, datasetId):
        return self.executeSelectOne(r"select spectrumIdFormatString from datasets where datasetId = %s", (datasetId,))

    def castIdsToDatasetType(self, row, idTypes=None):
        if idTypes is None:
            idTypes = self.getIdTypes(row["datasetId"])

        for fieldName in ["id1", "id2", "id3", "id4"]:
            if fieldName in row.keys():
                typeToCastTo = idTypes[fieldName]
                row[fieldName] = typeToCastTo(row[fieldName])
        return row

    def formatSpectrumId(self, **row):
        if "datasetId" not in row:
            raise ValueError("You must provide datasetId as a named argument")

        datasetId = row["datasetId"]
        genericFieldNames = ["id1", "id2", "id3", "id4"]
        isUsingGenericFieldNames = True in (fieldName in row.keys() for fieldName in genericFieldNames)

        if isUsingGenericFieldNames:
            row = self.castIdsToDatasetType(row)
            theCoords = tuple( row.get(idField) for idField in genericFieldNames)
            formatString = self.getSpectrumIdFormat(datasetId=datasetId)
            try:
                return formatString.format(datasetId, *theCoords)
            except Exception as err:
                raise ValueError("Unable to convert {0} with format string '{1}'", row, formatString )

class SpectraDB(LabdataDB):
    def __init__(self, databaseURL=None):
        super().__init__(databaseURL)

    def readOceanInsightFile(self, filePath):
        # text_file = open(filePath, "br")
        # hash = hashlib.md5(text_file.read()).hexdigest()
        # text_file.close()

        # We collect all the extra lines and assumes they contain the header info
        acquisitionInfo = []
        with open(filePath, "r") as text_file:
            lines = text_file.read().splitlines()

            wavelengths = []
            intensities = []
            for line in lines:
                # FIXME? On some computers with French settings, a comma is used. We substitute blindly.
                line = re.sub(",", ".", line)

                match = re.match(r"^\s*(\d+[.,]?\d+)\s+(-?\d*[.,]?\d*)", line)
                if match is not None:
                    intensity = match.group(2)
                    wavelength = match.group(1)
                    wavelengths.append(wavelength)
                    intensities.append(intensity)
                else:
                    acquisitionInfo.append(line)

        return wavelengths, intensities, "\n".join(acquisitionInfo)

    def insertSpectralDataFromFiles(self, filePaths, dataType="raw"):
        inserted = 0
        for filePath in filePaths:
            match = re.search(r"([A-Z]{1,2})_?(\d{1,3})\.", filePath)
            if match is None:
                raise ValueError(
                    "The file does not appear to have a valid name: {0}".format(
                        filePath
                    )
                )

            wineId = int(ord(match.group(1)) - ord("A"))
            sampleId = int(match.group(2))
            spectrumId = "{0:04}-{1:04d}".format(wineId, sampleId)

            wavelengths, intensities, acquisitionInfo = self.readOceanInsightFile(filePath)
            try:
                self.insertSpectralData(
                    spectrumId, wavelengths, intensities
                )
                print("Inserted {0}".format(filePath))
                inserted += 1
            except ValueError as err:
                print(err)

        return inserted

    def insertSpectralData(self, spectrumId, x, y):
        try:
            for i, j in zip(x, y):
                statement = (
                    "insert into datapoints (spectrumId, x, y) values(%s, %s, %s)"
                )
                self.execute(statement, (spectrumId, i, j))
        except Exception as err:
            raise ValueError("Unable to insert spectral data: {0}".format(err))

    def subtractFluorescence(self, rawSpectra, polynomialDegree=5):

        """
        Remove fluorescence background from the data.
        :return: A corrected data without the background.
        """

        correctedSpectra = np.empty_like(rawSpectra)
        for i in range(rawSpectra.shape[1]):
            spectrum = rawSpectra[:, i]
            correctedSpectra[:, i] = BaselineRemoval(spectrum).IModPoly(
                polynomialDegree
            )

        return correctedSpectra
