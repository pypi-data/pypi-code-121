from poseutils.datasets.transformation.Transformation import Transformation

class CalculateMetrics(Transformation):
    """No-op Transformation class to indicate dataset metrics need to be recalculated.
    """

    def __init__(self):
        super(CalculateMetrics, self).__init__()