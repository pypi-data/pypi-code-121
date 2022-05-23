from kolibri.utils.common import log10p
import numpy as np

class LogNormaliser():

    def __init__(self, offset=0):
        self.offsets=[offset]

    def fit(self, data, y=None):

        min_value= np.min(data.values, axis=0)

        self.offsets=np.abs(min_value)+1000

        return

    def inverse_transform(self, data):
        return 10**data-self.offsets

    def transform(self, data):
        return log10p(data, self.offsets)

    def fit_transform(self, data, y=None):
        self.fit(data)
        return self.transform(data)