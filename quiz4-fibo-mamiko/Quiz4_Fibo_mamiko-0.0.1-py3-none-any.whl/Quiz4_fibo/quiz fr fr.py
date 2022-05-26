import random
n1=0
n2=1
terms=random.randint(2,20)
count=0

for i in range (10):
    if count < terms:
        print("Fibonacci sequence:")
        while count < terms:
            print(n1)
            nth = n1 + n2
            n1 = n2
            n2 = nth
            count += 1