# errors
class omniplateError(ValueError):
    pass


class FileNotFound(omniplateError):
    pass


class IgnoreWells(omniplateError):
    pass


class PlotError(omniplateError):
    pass


class UnknownDataFrame(omniplateError):
    pass


class getsubset(omniplateError):
    pass


class GetFitnessPenalty(omniplateError):
    pass


class CorrectAuto(omniplateError):
    pass


class UnknownPlateReader(omniplateError):
    pass
