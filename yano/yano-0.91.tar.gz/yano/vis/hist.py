import matplotlib.pyplot as plt
import numpy as np




def hist(x,y, log=False, bins=0.1, modus="alpha"):
    """
    Plots a histogram of the anomaly scores x, where y is the ground truth
    log=False: if True, the y-axis is logarithmic
    bins=0.1: the number of bins. Also understands relative values to the length of x
    normed: if True, the histogram is normalized
    modus: if "alpha", the alpha channel is used for there to be two plots. if "next" there will be a peak next to a peak. If "stack" then the diagrams will be stacked. stack and next currently require same size of normals as of abnormals
    """

    mn=np.min(x)
    mx=np.max(x)
    if type(bins) is float:
        bins=int(len(x)*bins)

    x0=[xx for xx,yy in zip(x,y) if not yy]
    x1=[xx for xx,yy in zip(x,y) if yy]


    if modus=="alpha":
        plt.hist(x0, bins=bins, alpha=0.5, log=log, range=(mn,mx), label="normal")
        plt.hist(x1, bins=bins, alpha=0.5, log=log, range=(mn,mx), label="abnormal")
    else:

        x0=np.expand_dims(x0, axis=1)
        x1=np.expand_dims(x1, axis=1)
        x=np.concatenate((x0,x1), axis=1)
        plt.hist(x, bins=bins, log=log, alpha=0.5, label=('normal', 'abnormal'),range=(mn,mx), stacked=(modus=="stack"))


    plt.legend()

    return plt.show







