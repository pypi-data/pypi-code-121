import numpy as np
import matplotlib.pyplot as plt
from matplotlib import offsetbox


def embedding_plot(X, images, title):
    x_min, x_max = np.min(X, axis=0), np.max(X, axis=0)
    X = (X - x_min) / (x_max - x_min)
    plt.figure()
    ax = plt.subplot(aspect='equal')
    sc = ax.scatter(X[:, 0], X[:, 1], lw=0, s=40)
    shown_images = np.array([[1., 1.]])
    for i in range(X.shape[0]):
        if np.min(np.sum((X[i] - shown_images)**2, axis=1)) < 1e-2:
            continue
        shown_images = np.r_[shown_images, [X[i]]]
        ax.add_artist(
            offsetbox.AnnotationBbox(offsetbox.OffsetImage(images[i]), X[i]))
    plt.xticks([]), plt.yticks([])
    plt.title(title)
