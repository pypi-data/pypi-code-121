import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from IPython.core.interactiveshell import InteractiveShell

InteractiveShell.ast_node_interactivity = "all"
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)


def Stackedbar(titlename, xlabel, label, botV, cenV, topV):
    plt.title(titlename)
    N = len(xlabel)
    ind = np.arange(N)  # [ 0  1  2  3  4  5  6  7  8 ]
    plt.xticks(ind, xlabel)

    # plt.ylabel('Scores')
    Bottom, Center, Top = botV, cenV, topV

    d = []
    for i in range(0, len(Bottom)):
        sum = Bottom[i] + Center[i]
        d.append(sum)

    colors = list(mcolors.TABLEAU_COLORS.keys())

    p1 = plt.bar(ind, Bottom, color=colors[0])
    p2 = plt.bar(ind, Center, bottom=Bottom, color=colors[1])
    p3 = plt.bar(ind, Top, bottom=d, color=colors[2])

    plt.legend((p1[0], p2[0], p3[0]), label, loc=2)

    plt.show()


def multiplebar(n=2, total_width=0.5, size=5):
    print('待修改')
    x = np.arange(size)
    a = np.random.random(size)
    b = np.random.random(size)
    c = np.random.random(size)

    # total_width, n = 0.8, 3
    width = total_width / n
    x = x - (total_width - width) / 2

    plt.bar(x, a, width=width, label='a')
    plt.bar(x + width, b, width=width, label='b')
    plt.bar(x + 2 * width, c, width=width, label='c')
    plt.legend()

    plt.plot(x, a)
    plt.plot(x + width, b)
    plt.plot(x + 2 * width, c)
    # plt.plot(x, y, "r", marker='*', ms=10, label="a")
    # plt.xticks(rotation=45)
    # plt.legend(loc="upper left")

    plt.show()
