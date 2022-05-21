#!/usr/bin/env python
# coding: utf-8
from DPN import *


def DPF(n):
    if n <= 1:
        raise ValueError(f'Can\'t find {n}\'s result.')
    l = prime_number_list(ceil(sqrt(n)))
    rst = []
    cnt = 1
    for i in l:
        f = is_primenumber(n)
        if n == 1 or (f and cnt == 1):
            break
        elif cnt > 1 and f:
            rst.append(n)
            break
        else:
            while n % i == 0:
                rst.append(i)
                n //= i
                cnt += 1
    return rst if rst else False


if __name__ == '__main__':
    a = int(eval((input("Enter a number:"))))
    print(a, ":", DPF(a))
