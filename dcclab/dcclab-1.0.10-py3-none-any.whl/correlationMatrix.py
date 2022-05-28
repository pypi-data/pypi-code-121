import numpy as np
import pandas as pd
from .DCCExceptions import *
import seaborn as sns
import matplotlib.pyplot as plt
import typing as tp
from datetime import datetime


class CSVReader:

    def __init__(self, filename: str, separator: str = ","):
        self.dataframe: pd.DataFrame = None
        self.filename = filename
        try:
            self.dataframe = pd.read_csv(filename, sep=separator)
        except Exception as e:
            raise InvalidFileFormatException(
                "Problem occurred while reading '{}'. Please make sure it is a valid csv file. Exception message:\n{}".format(
                    filename, e))


class CorrelationMatrix:

    def __init__(self, dataframe: pd.DataFrame = None, array: np.ndarray = None,
                 headers: tp.Union[list, np.ndarray] = None):
        if dataframe is None and array is None:
            raise ValueError("A dataframe or an array is required to compute a correlation matrix.")
        if dataframe is not None and array is not None:
            raise ValueError(
                "A dataframe and an array were given. Please choose one of the two objects to compute the correlation matrix")
        if dataframe is not None and not isinstance(dataframe, pd.DataFrame):
            raise TypeError("Dataframe parameter must be a pandas.Dataframe instance.")
        if array is not None:
            self.dataframe = pd.DataFrame(array, columns=headers)
        else:
            self.dataframe = dataframe

    def computeCorrelationMatrix(self, castTo: type = float, columnsToDrop: list = None):
        if columnsToDrop is not None:
            if all(isinstance(x, int) for x in columnsToDrop):
                self.dataframe.drop(self.dataframe.columns[columnsToDrop], axis=1, inplace=True)
            elif all(isinstance(x, str) for x in columnsToDrop):
                self.dataframe.drop(columnsToDrop, axis=1, inplace=True)
            else:
                raise ValueError("The list of columns to drop must consist of integers only or strings only.")
        corr = self.dataframe.astype(castTo).corr()
        return corr

    def showCorrelationMatrix(self, castTo: type = float, annotation: bool = True, fontScale: float = 0.5,
                              title: str = None, titleFontSize: int = 16):
        corr = self.computeCorrelationMatrix(castTo)
        sns.set(font_scale=fontScale)
        ax = sns.heatmap(
            corr,
            vmin=-1, vmax=1, center=0,
            cmap=sns.diverging_palette(20, 220, n=200),
            square=True,
            annot=annotation
        )
        ax.set_xticklabels(
            ax.get_xticklabels(),
            rotation=45,
            horizontalalignment='right'
        )
        plt.title(title, fontsize=titleFontSize)
        plt.show()

    def correlationCoefficientsInOrder(self, correlationMatrix: pd.DataFrame):
        corrMatrix = np.array(correlationMatrix)
        nbLines, nbCols = corrMatrix.shape
        if nbLines != nbCols:
            raise ValueError("The number of lines and the number of columns are not the same.")
        dictOfCoeffAndTags = dict()
        for i in range(1, nbCols):
            for j in range(0, i):
                dictOfCoeffAndTags[f"{correlationMatrix.columns[i]} - {correlationMatrix.columns[j]}"] = corrMatrix[
                    i, j]
        orderedDict = dict()
        for key in sorted(dictOfCoeffAndTags, key=dictOfCoeffAndTags.get, reverse=True):
            orderedDict[key] = dictOfCoeffAndTags[key]
        return orderedDict


class PermutationCorrelations:

    def __init__(self, dataframe: pd.DataFrame = None, array: np.ndarray = None,
                 headers: tp.Union[list, np.ndarray] = None, numberOfPermutations: int = 1000, castTo: type = float):
        if dataframe is None and array is None:
            raise ValueError("A dataframe or an array is required to compute a correlation matrix.")
        if dataframe is not None and array is not None:
            raise ValueError(
                "A dataframe and an array were given. Please choose one of the two objects to compute the correlation matrix")
        if dataframe is not None and not isinstance(dataframe, pd.DataFrame):
            raise TypeError("Dataframe parameter must be a pandas.Dataframe instance.")
        if array is not None:
            self.dataframe = pd.DataFrame(array, columns=headers)
        else:

            self.dataframe = dataframe.astype(castTo)
        self.columns = self.dataframe.columns
        self.nbRows, self.nbColumns = self.dataframe.shape
        self.numberOfPermutations = numberOfPermutations
        self.arrayOfPermutations = None
        self.correlationTensor = None
        self.pvaluesDatframe = None

    def _computePermutations(self, columnsToDrop: list = None):
        if columnsToDrop is not None:
            if all(isinstance(x, int) for x in columnsToDrop):
                self.dataframe.drop(self.dataframe.columns[columnsToDrop], axis=1, inplace=True)
            elif all(isinstance(x, str) for x in columnsToDrop):
                self.dataframe.drop(columnsToDrop, axis=1, inplace=True)
            else:
                raise ValueError("The list of columns to drop must consist of integers only or strings only.")
            self.columns = self.dataframe.columns
            self.nbRows, self.nbColumns = self.dataframe.shape
        array = np.array(self.dataframe)
        self.arrayOfPermutations = np.dstack([array for _ in range(self.numberOfPermutations)])
        # The first slice is the original dataframe, no permutations.
        self.arrayOfPermutations = np.dstack(
            (array, np.apply_along_axis(np.random.permutation, 0, self.arrayOfPermutations)))

    def computeCorrelationTensor(self, columnsToDrop: list = None):
        self._computePermutations(columnsToDrop=columnsToDrop)
        self.correlationTensor = np.dstack([np.array(pd.DataFrame(self.arrayOfPermutations[:, :, i]).corr()) for i in
                                            range(self.numberOfPermutations + 1)])

    def computePValue(self):
        pvalues = dict()
        pvaluesArray = np.full((self.nbColumns, self.nbColumns), np.nan)
        if self.correlationTensor is None:
            raise ValueError("Please compute de correlation tensor.")
        for column in range(1, self.nbColumns):
            for row in range(0, column):
                observable = f"{self.columns[row]} - {self.columns[column]}"
                correlationCoefficients = self.correlationTensor[row, column, :]
                nbOfObservations = len(correlationCoefficients)
                originalCoefficient = correlationCoefficients[0]
                pvalue = np.nan
                if not np.all(np.isnan(originalCoefficient)):
                    if originalCoefficient < 0:
                        # We exclude the first value because it is the original value
                        pvalue = np.sum(correlationCoefficients[1:] <= originalCoefficient) / (nbOfObservations - 1)
                    else:
                        # We exclude the first value because it is the original value
                        pvalue = np.sum(correlationCoefficients[1:] >= originalCoefficient) / (nbOfObservations - 1)
                pvalues[observable] = pvalue
                pvaluesArray[row, column] = pvalue
                pvaluesArray[column, row] = pvalue
                self.pvaluesDatframe = pd.DataFrame(pvaluesArray, index=self.columns, columns=self.columns)

        return pvalues

    def displayPValues(self, threshold: float, displayWithOriginalCorrelationMatrix: bool = True, title: str = None):
        if displayWithOriginalCorrelationMatrix:
            fig, (ax1, ax2) = plt.subplots(1, 2)
            fig.suptitle(title)
            sns.set(font_scale=0.5)
            first = sns.heatmap(
                (self.pvaluesDatframe < threshold),
                vmin=-1, vmax=1, center=0,
                cmap=sns.diverging_palette(20, 220, n=200),
                square=True,
                annot=True,
                ax=ax1
            )
            first.set_xticklabels(
                first.get_xticklabels(),
                rotation=45,
                horizontalalignment='right'
            )
            originalCorrelationMatrix = pd.DataFrame(self.correlationTensor[:, :, 0], self.columns, self.columns)
            second = sns.heatmap(
                originalCorrelationMatrix,
                vmin=-1, vmax=1, center=0,
                cmap=sns.diverging_palette(20, 220, n=200),
                square=True,
                annot=True,
                ax=ax2
            )
            second.set_xticklabels(
                second.get_xticklabels(),
                rotation=45,
                horizontalalignment='right'
            )
            plt.show()
        else:
            sns.set(font_scale=0.5)
            ax = sns.heatmap(
                (self.pvaluesDatframe < threshold),
                vmin=-1, vmax=1, center=0,
                cmap=sns.diverging_palette(20, 220, n=200),
                square=True,
                annot=True
            )
            ax.set_xticklabels(
                ax.get_xticklabels(),
                rotation=45,
                horizontalalignment='right'
            )
            plt.title(title)
            plt.show()

    @staticmethod
    def arePValuesValid(pvalues: dict, threshold: float = 1 / 100):
        valid = dict()
        for key in pvalues.keys():
            valid[key] = (pvalues[key] <= threshold, pvalues[key])
        return valid


class DataframeUtils:

    @staticmethod
    def ageOfMouse(dataframe: pd.DataFrame, format: str = "%Y-%m-%d"):
        age = np.nan
        dateOfBirth = dataframe["DDN"]
        dateOfDeath = dataframe["date_mort"]
        if dateOfBirth != " " and dateOfDeath != " ":
            dateOfBirth = datetime.strptime(dateOfBirth, format)
            dateOfDeath = datetime.strptime(dateOfDeath, format)
            age = dateOfDeath - dateOfBirth
            age = age.days
            if age < 0:
                age = np.nan
        return age

    @staticmethod
    def nbDaysBetweenDeathAndUse(dataframe: pd.DataFrame, format: str = "%Y-%m-%d"):
        days = np.nan
        dateUse = dataframe["date_utilisation"]
        dateOfDeath = dataframe["date_mort"]
        if dateOfDeath != " " and dateUse != " ":
            dateUse = datetime.strptime(dateUse, format)
            dateOfDeath = datetime.strptime(dateOfDeath, format)
            days = dateUse - dateOfDeath
            days = days.days
        if days < 0:
            days = np.nan
        return days

    @staticmethod
    def injectionVolume(dataframe: pd.DataFrame):
        volumeInjection = dataframe["volume_injection"]
        if volumeInjection == "2 x 200 nl (G+D)":
            injVol = 400
        else:
            try:
                injVol = float(volumeInjection)
            except ValueError:
                injVol = np.nan
        return injVol

    @staticmethod
    def usedValuesStatsPerColumn(dataframe: pd.DataFrame):
        d = dict()
        for column in dataframe.columns:
            array = np.array(dataframe[column])
            total = array.size
            nonNan = np.count_nonzero(~np.isnan(array))
            d[column] = (nonNan / total, nonNan, total)
        return d

    @staticmethod
    def dropRowsWithCertainValues(dataframe: pd.DataFrame, value, columnName: str) -> pd.DataFrame:
        newDataframe = dataframe[dataframe[columnName] != value]
        return newDataframe
