def Fibonacci(n):
    sequenceList = [0]
    n1 = 0
    n2 = 1
    count = 0
    while count < 100:
        n3 = n1 + n2
        sequenceList.append(n3)
        n1 = n2
        n2 = n3
        count += 1
    print(sequenceList[n-1])


Fibonacci(6)