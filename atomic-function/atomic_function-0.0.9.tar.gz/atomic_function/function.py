import numpy as np


def up(x):

    def fourier_image(x):
        def sinc(x):
            return np.sin(x)/x
        sinc_product = 1
        for k in range(1, 11):
            sinc_product *= sinc(x/2**k)
        return sinc_product

    sum = 0

    for i in range(1, 100):
        sum += fourier_image(np.pi*i)*np.cos(np.pi*i*x)

    up = 0.5+sum

    for i in range(len(up)):
        if x[i] < -1 or x[i] > 1:
            up[i] = 0

    return up


def ha(x, a):

    if a <= 1:
        raise Exception('a must be greater than 1')

    def fourier_image(x):
        def sinc(x):
            return np.sin(x)/x
        sinc_product = 1
        for i in range(1, 11):
            sinc_product *= sinc(x/a**i)
        return sinc_product

    sum = 0

    for i in range(1, 100):
        sum += fourier_image((a-1)*np.pi*i)*np.cos((a-1)*np.pi*i*x)

    ha = (a-1)*(0.5+sum)

    for i in range(len(ha)):
        if x[i] < -1/(a-1) or x[i] > 1/(a-1):
            ha[i] = 0
    return ha


def upm(x, m):

    if m <= 0:
        raise Exception('a must be greater than 0')

    def fourier_image(x):
        def sinc(x):
            return np.sin(x)/x
        sinc_product = 1
        for k in range(1, 11):
            sinc_product *= (sinc((m*x)/((2*m)**k))**2) / \
                (sinc(x/((2*m)**k)))
        return sinc_product

    sum = 0

    for i in range(1, 100):
        sum += fourier_image(np.pi*i)*np.cos(np.pi*i*x)

    upm = 0.5+sum
    for i in range(len(upm)):
        if x[i] < -1 or x[i] > 1:
            upm[i] = 0

    return upm
