def fibbo():
    a = 0
    b = 1
    for i in range(1000):
        yield a
        a, b = b, a + b

num = iter(fibbo())
print(next(num))
print(next(num))
print(next(num))
print(next(num))