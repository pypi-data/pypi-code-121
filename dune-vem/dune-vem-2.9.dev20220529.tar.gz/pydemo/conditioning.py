import pickle
from matplotlib import pyplot
import numpy
results1 = pickle.load(open('conditioning1A.dump','rb'))
results2 = pickle.load(open('conditioning2A.dump','rb'))
results3 = pickle.load(open('conditioning3.dump','rb'))
resultsL = pickle.load(open('conditioningLagrange.dump','rb'))

x = []
N = []
for i,r in enumerate(results1):
    N.append(r[0])
    x.append(r[1])
x = list(set(x))
N = list(set(N))
x.sort()
N.sort()
y1 = numpy.zeros((len(N),len(x)))
y2 = numpy.zeros((len(N),len(x)))
y3 = numpy.zeros((len(N),len(x)))
yL = numpy.zeros((len(N),len(x)))

for r1,r2,r3,rL in zip(results1,results2,results3,resultsL):
    n = N.index(r1[0])
    o = x.index(r1[1])
    # y1[n][o] = r1[5][1]
    y1[n][o] = r1[6]["conditioning"]
    # y2[n][o] = r2[5][1]
    y2[n][o] = r2[6]["conditioning"]
    # y3[n][o] = r3[5][1]
    y3[n][o] = r3[6]["conditioning"]
    # yL[n][o] = rL[5][1]
    yL[n][o] = rL[6]["conditioning"]

for i in range(len(y1)):
    # pyplot.semilogy(x,y1[i])
    pyplot.semilogy(x,y2[i])
    pyplot.semilogy(x,y3[i])
    pyplot.semilogy(x,yL[i])
pyplot.show()
