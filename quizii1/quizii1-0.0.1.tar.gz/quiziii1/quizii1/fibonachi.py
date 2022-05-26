
def fib():
     x1 = 0
     x2 = 1
     while True:
        y = x1 + x2
        print(y)
        yield x1, x2
        x1 = x2
        x2 = y


z = fib()
fib_next = next(z)