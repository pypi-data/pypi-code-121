def Fibonacci_sequence(num):
    if num == 1:
        return 0
    if num == 2:
        return 1
    return Fibonacci_sequence(num - 1) + Fibonacci_sequence(num - 2)
