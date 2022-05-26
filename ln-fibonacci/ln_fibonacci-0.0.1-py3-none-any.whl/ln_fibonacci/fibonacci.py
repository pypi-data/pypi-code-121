import random

def fibonacci():
    n1 = 0
    n2 = 1
    num_list = []

    for i in range(20):
        num_list.append(n1)
        n = n1 + n2
        n1 = n2
        n2 = n
    print(random.choice(num_list))
fibonacci()