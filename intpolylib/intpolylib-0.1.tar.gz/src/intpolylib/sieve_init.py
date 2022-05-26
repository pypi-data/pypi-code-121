import math as mt

MAX_N = 2**16 + 1
spf = [0 for i in range(MAX_N)]
primeNumbers = []

def sieve(MAX_N):
    """ Completes the list with prime numbers up to MAX_N 
        and determines the smallest prime factor of a number
    """
    spf[1] = 1
    for i in range(2, MAX_N):	
        spf[i] = i

    for i in range(4, MAX_N, 2):
        spf[i] = 2

    for i in range(3, mt.ceil(mt.sqrt(MAX_N))):
        if (spf[i] == i):
            for j in range(i * i, MAX_N, i):
                if (spf[j] == j):
                    spf[j] = i

    for i in range(2, MAX_N):
        if i == spf[i]:
            primeNumbers.append(i)

sieve(MAX_N)