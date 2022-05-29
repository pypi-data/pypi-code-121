import pickle
from matplotlib import pyplot
import numpy
from math import log

results = pickle.load(open('interpolation.dump','rb'))
# [ [ m, gridVidth, space.size, errors ], [...],... ]
# m = [*,*,testSpaces]
# errors = [[name,err],...]

# get different gridWidth and space size values, method and error names
gw = []
for r in results:
    gw.append(r[0][1])
    numberOfErrors  = len(r[0][3])
    methods = []
    for m in r:
        methods.append(m[0][3])
    errorNames  = []
    for e in r[0][3]:
        errorNames.append(e[0])
dofs   = numpy.zeros((len(methods),len(gw)))
errors = numpy.zeros((len(methods),len(gw),numberOfErrors))
eocs   = numpy.zeros((len(methods),len(gw)-1,numberOfErrors))
print(errors.shape)

for i,r in enumerate(results):
    for j,m in enumerate(r):
        dofs[j,i]     = m[2]
        errors[j,i,:] = [i[1] for i in m[3]]
for j in range( errors.shape[0] ):
    for i in range( errors.shape[2] ):
        eocs[j,:,i] = numpy.log( errors[j,1:,i] / errors[j,:-1,i] ) / numpy.log(0.5)

# the following should be improved on...
markers = ['x-', 's-', '+-', 'o-', '<-', '>-', '*-']
colors  = ['coral', 'skyblue', 'indianred', 'blueviolet', 'green']

for e, errName in enumerate(errorNames):
    pyplot.figure()
    pyplot.ylabel(errName+' error',fontsize=20)
    for i in range(dofs.shape[0]):
        pyplot.loglog(dofs[i],errors[i,:,e],
                 markers[i%7], color=colors[i%5], markersize=15, label=methods[i])
    pyplot.grid(True)
    pyplot.tick_params(axis='both', which='minor', labelsize=32)
    pyplot.xlabel('number of dofs',fontsize=20)
    pyplot.legend(loc="lower left")
    pyplot.savefig('interpolationError'+errName+'.eps')
    pyplot.show()

    pyplot.figure()
    pyplot.ylabel(errName+' eoc',fontsize=20)
    for i in range(dofs.shape[0]):
        pyplot.semilogx(dofs[i,1:],eocs[i,:,e],
                 markers[i%7], color=colors[i%5], markersize=15, label=methods[i])
    pyplot.grid(True)
    pyplot.tick_params(axis='both', which='minor', labelsize=32)
    pyplot.xlabel('number of dofs',fontsize=20)
    pyplot.legend(loc="lower left")
    pyplot.savefig('interpolationEoc'+errName+'.eps')
    pyplot.show()
