from poseutils.datasets.transformation.Transformation import Transformation
from .CalculateMetrics import CalculateMetrics
from .CropAndScale import CropAndScale
from .Normalize import Normalize
from .RootCenter import RootCenter
from .Unnormalize import Unnormalize

def crop_scaled_normalization():

    t2d = [
        CropAndScale(),
        RootCenter(),
        CalculateMetrics(),
        Normalize()
    ]

    t3d = [
        RootCenter(),
        CalculateMetrics(),
        Normalize()
    ]

    return t2d, t3d

def basic_normalization():

    transformations = [
        RootCenter(),
        CalculateMetrics(),
        Normalize()
    ]

    return transformations