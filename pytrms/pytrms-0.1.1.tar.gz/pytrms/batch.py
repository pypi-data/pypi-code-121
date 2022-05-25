from .measurement import Measurement, FinishedMeasurement


class Batch:
    '''
# TODO :: ein Batch ist eine Collection von (stopped) Measurements, sortiert nach
# timezero.
    '''

    def __init__(self, *paths):
        self.sources = [Measurement(path) for path in paths]

    def add_file(path):
        self.sources = sorted(self.sources + [H5Source(path)], key=attrgetter('timezero'))


    def iterrows(self):
        '''Iterate over the rows of each of the datafiles.
        '''
        raise NotImplementedError

