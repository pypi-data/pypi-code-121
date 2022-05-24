class Transformation(object):
    """Base class for other Transformation classes.
    """

    def __init__(self):
        super(Transformation, self).__init__()

    def __call__(self, X, **kwds):
        raise NotImplementedError