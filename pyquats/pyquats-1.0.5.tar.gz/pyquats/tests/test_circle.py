#!/usr/bin/env python3
#
# Testowanie rozkladu S = s1*s1 + s2*s2, kiedy s1, s2 maja rozklad
# jednorodny w przedziale (-1,1).
# S ma rozklad jednorodny w przedziale (0,1).

n = 100
#n = 1000
D = dict()

for i in range(-n, n+1):
    for j in range(-n, n+1):
        if i*i+j*j < n*n:
            #D[i*i+j*j] = D.get(i*i+j*j, 0) +1
            D[(i*i+j*j)*10 / (n*n)] = D.get((i*i+j*j)*10 / (n*n), 0) +1
print(D)
for i in range(10):
    print(i, D.get(i,0))

# EOF
