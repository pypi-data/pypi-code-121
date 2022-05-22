
class negate_output(object):

    def __init__(self, obj):
        self.obj = obj

    def fit(self, *args, **kwargs):
        return self.obj.fit(*args, **kwargs)

    def score_samples(self, *args, **kwargs):
        if hasattr(self.obj, 'score_samples'):
            return -self.obj.score_samples(*args, **kwargs)
        else:
            return -self.obj.decision_function(*args, **kwargs)




