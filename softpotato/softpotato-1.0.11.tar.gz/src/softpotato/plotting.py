import matplotlib.pyplot as plt

def format(xlab, ylab, legend=False, show=False, fileName=False):
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.xlabel(xlab, fontsize=18)
    plt.ylabel(ylab, fontsize=18)
    plt.grid()
    plt.tight_layout()
    if legend[0]:
        plt.legend()
    if fileName:
        plt.savefig(fileName + '.png')
    if show:
        plt.show()

def plot(x, y, xlab='$E$ / V', ylab='$i$ / A', mark='-', legend=False, fig=1, show=False, fileName=False):
    '''
        Function to plot curves without all the hassle. By default, y is a list 
        and mark is a string. To use different markers for each curve, include them as 
        a list where each item is a different marker / line style. y can also be a
        numpy array.

        Example:
        > import numpy as np
        > x = np.array([1,2,3,4])
        > y = [x, x**2, x***3]
        > mark = ['-', '--', 'or-']
        > legend = ['x', 'x^2', 'x^3']
        > sp.plotting.plot(x, y, xlab='x', ylab='y', mark=mark, legend=legend, show=1)
    '''
    # By default, y should be a list, if it is just a numpy array then
    # convert it into list to be used in the for loop afterwards:
    if (type(y) != list):
        y = [y]
    ny = len(y)
    # Even with multiple plots, the user may want to have the same marker or
    # line stile for each curve, so if it is not a list, convert it into one
    if (type(mark) != list):
        mark = [mark]*ny
    # Legend can also be just one or a list:
    if (type(legend) != list):
        legend = [legend]*ny
    plt.figure(fig)
    for n in range(ny):
        plt.plot(x, y[n], mark[n], label=legend[n])
    
    format(xlab, ylab, legend, show, fileName)


if __name__ == '__main__':
    import numpy as np
    x = np.array([1,2,3,4])
    y = [x, x**2, x**3]
    mark = ['-vg', '--b', '-or']
    legend = ['x', 'x^2', 'x^3']
    plot(x, y, xlab='x', ylab='y', mark=mark, legend=legend, show=1)
