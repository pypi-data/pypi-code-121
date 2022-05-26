from scipy.optimize import minimize_scalar


def f(x, temp):
    return (x - 2) * x * (x + 2)**2 + temp


res = minimize_scalar(f, args=(1))
print(res.x)
