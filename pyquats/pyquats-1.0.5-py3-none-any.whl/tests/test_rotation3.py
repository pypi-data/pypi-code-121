#!/usr/bin/env python3
#
# Przyklad jednoczesnego sortowania wartosci wlasnych i wektorow wlasnych.
# The eigenvalues are not necessarily ordered.
# help(numpy.argsort)
# argsort(a, axis=-1, kind='quicksort', order=None)
# Returns the indices that would sort an array.
#
# https://stackoverflow.com/questions/33037616/large-matrix-diagonalization-python

import math
import numpy

A = numpy.array([[3,1,-1], [1,3,-1], [-1,-1,5]], dtype=float)
print ( A )
# Wartosci wlasne to 2, 3, 6, ale kolejnosc moze byc rozna.
# Wektory wlasne beda ulozone kolumnami!
# The column vec[:,i] is the eigenvector corresponding to the eigenvalue w[i].
w, vec =  numpy.linalg.eig(A)
#print (w, vec)
print ("eigenvalues", w)
print ("unit eigenvectors (in columns)")
print (vec)

# Zmieniam kolejnosc wartosci wlasnych i wektorow wlasnych.
print ( "Zmiana kolejnosci ..." )
idx = w.argsort()[::-1] #large to small
# idx = w.argsort() #small to large
# idx to jest index_array : ndarray, int.
w = w[idx]   # to dziala elementwise, faktycznie sortuje w
vec = vec[:,idx]   # wiersze po kolei, kolumny wg idx
print (w, vec)
# now they are ordered and you can iterate through your results
# to write them to your file

print ( "Sprawdzenie dzialania macierzy na wektory ..." )
# Mnozenie macierzy i wektora wlasnego ma byc rowne mnozeniu
# wartosci wlasnej i wektora wlasnego.
v0 = vec[:,0] # kolejne wektory wlasne z kolumn
v1 = vec[:,1]
v2 = vec[:,2]
print ( "A v", numpy.dot(A,v0) )
print ( "lam v", w[0] * v0 )
print ( "A v", numpy.dot(A,v1) )
print ( "lam v", w[1] * v1 )
print ( "A v", numpy.dot(A,v2) )
print ( "lam v", w[2] * v2 )   # bledy maszynowe

print ( "Diagonalizacja B^T A B ..." )
print ( numpy.dot(numpy.transpose(vec), numpy.dot(A,vec)) ) # dziala!

# EOF
