from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np


def promax():
    taper = np.linspace(0, 1, 128)
    taper2 = np.concatenate((np.zeros(64), np.linspace(0, 1, 64)))
    r = np.concatenate((taper, np.ones(128)))
    g = np.concatenate((taper, taper[::-1]))
    b = np.concatenate((taper, taper2[::-1]))
    r = np.expand_dims(r, axis=1)
    g = np.expand_dims(g, axis=1)
    b = np.expand_dims(b, axis=1)
    rgb = np.concatenate((r, g, b), axis=1)
    colormap = ListedColormap(rgb)
    return colormap


if __name__ == '__main__':
    x = np.random.random([16, 16])
    plt.figure()
    plt.imshow(x, cmap=promax())
    plt.colorbar()
    plt.show()
