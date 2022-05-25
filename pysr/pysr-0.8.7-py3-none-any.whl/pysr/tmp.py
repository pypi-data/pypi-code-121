import warnings
warnings.filterwarnings("ignore")
import numpy as np
from matplotlib import pyplot as plt
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel, ConstantKernel
from time import time

for n in [500, 1000]:#[100, 200, 300, 400]:
    rstate = np.random.RandomState(0)
    X = rstate.randn(n, 8)
    # True equation:
    ytrue = np.sin(X[:, 0] ** 2) - np.exp(- X[:, 0] ** 2)

    # Add noise:
    y = ytrue + rstate.randn(n) * 0.1

    gp_kernel = RBF(np.ones(X.shape[1])) + WhiteKernel(1e-1) + ConstantKernel()
    gpr = GaussianProcessRegressor(kernel=gp_kernel, n_restarts_optimizer=50)

    for i in range(2):
        start = time()
        gpr.fit(X, y)
        ypredict = gpr.predict(X)
        end = time()

        print("n=%d, time=%f" % (n, end - start))
        # print(np.square(ytrue - ypredict).sum())
        # print(np.square(ytrue - y).sum())