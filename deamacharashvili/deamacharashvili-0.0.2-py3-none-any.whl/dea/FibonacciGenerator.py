class FibonacciGenerator:
    def __init__(self):
        self.first = 0
        self.second = 1

    def print_next_fib(self):
        print(self.first)
        self.first, self.second = self.second, self.first + self.second