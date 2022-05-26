def fib():
    first = 0
    second = 1
    while True:
        yield first + second
        temp = first
        first = second
        second += temp
    
def main():
    fib_gen = fib()
    n = int(input('How many fibonacci numbers?: '))
    for i in range(n):
        print(next(fib_gen))


if __name__ == '__main__':
    main()