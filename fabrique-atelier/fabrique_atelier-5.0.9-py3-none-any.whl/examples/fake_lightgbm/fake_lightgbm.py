import numpy as np

wht = np.exp(-0.1 * np.arange(24))


class Booster:
    def __init__(self, model_file=None):
        assert model_file, "Can't work without model params"
        with open(model_file) as f:
            data = f.read()
            assert data, "model file is empty"

    def predict(self, features_batch):
        res_lst = []
        for rawX in features_batch:
            X = rawX.reshape((10, 24))
            weightedX = X * wht
            predicted_proba = weightedX.sum(1)
            res_lst.append(predicted_proba)
        return np.array(res_lst)
