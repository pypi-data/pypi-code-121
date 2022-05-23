import pkg_resources
import pandas as pd


def load_dataM():
    """Return a dataframe about the MicroBiome Dataset.
    """
    # This is a stream-like object. If you want the actual info, call
    # stream.read()
    stream = pkg_resources.resource_stream(__name__, 'data/dataM.csv')
    return pd.read_csv(stream, encoding='latin-1')

def load_dataC():
    """Return a dataframe about the 68 different Roman Emperors.
    """
    # This is a stream-like object. If you want the actual info, call
    # stream.read()
    stream = pkg_resources.resource_stream(__name__, 'data/dataC.csv')
    return pd.read_csv(stream, encoding='latin-1')
