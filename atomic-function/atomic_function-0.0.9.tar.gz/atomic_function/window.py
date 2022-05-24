import numpy as np


def up(N):

    x = np.linspace(-1, 1, N)

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

    return 0.5+sum


def ha(N, a):

    if a <= 1:
        raise Exception('a must be greater than 1')

    x = np.linspace(-1/(a-1), 1/(a-1), N)

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

    return (a-1)*(0.5+sum)


def upm(N, m):

    if m <= 0:
        raise Exception('a must be greater than 0')

    x = np.linspace(-1, 1, N)

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

    return 0.5+sum
