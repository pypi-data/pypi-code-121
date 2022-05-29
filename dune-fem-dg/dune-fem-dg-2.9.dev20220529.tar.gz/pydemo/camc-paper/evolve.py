import functools
print = functools.partial(print, flush=True)
import time, math

from dune.generator import path, algorithm
from dune.typeregistry import generateTypeName
from dune.fem import markNeighbors, adapt, loadBalance
from dune.fem.space import dgonb, dglegendre, finiteVolume, dglagrange
from dune.fem.function import levelFunction, partitionFunction
from dune.femdg import femDGModels, femDGOperator, smoothnessIndicator
from dune.femdg.rk import femdgStepper, ExplSSP3
from residual import residualIndicator

spaces = {
          'onb':dgonb,
          'legendre':dglegendre,
          'lagrange': lambda *args,**kwargs: dglagrange(*args,**kwargs),
          'equidistant': lambda *args,**kwargs: dglagrange(*args,**kwargs,pointType="equidistant"),
          'lobatto': lambda *args,**kwargs: dglagrange(*args,**kwargs,pointType="lobatto"),
          'gauss': lambda *args,**kwargs: dglagrange(*args,**kwargs,pointType="gauss")
        }

def getSpace( gridView, order, dimRange, space ):
    if order==0:
        return finiteVolume( gridView, dimRange=dimRange )
    else:
        return space( gridView, dimRange=dimRange, order=order, codegen=False)

def parprint(output, *args, **kwargs):
    if output:
        print(*args, **kwargs)


def evolve(gridView, order, Model, outName,
           limiter="default", space='onb',
           maxLevel=-1, startTime=0.,
           parameters={},
           stepper="femdg",
           codegen=True, outputs=100, threading=True,
           **kwargs):
    isRank0 = gridView.comm.rank == 0

    parprint(isRank0, 'evolve:', order, outName, limiter, space, maxLevel, parameters,
           codegen, outputs, threading)

    space = getSpace(gridView, order, dimRange=Model.dimRange, space=spaces[space])
    U_h   = space.interpolate(Model.U0, name="solution")

    if limiter == "modal":
        try:
            component = kwargs["modalComponent"]
        except KeyError:
            component = "density"
        parprint(isRank0,"using modal indicator based on",component)
        models = femDGModels(Model,space)
        clsName,includes = generateTypeName("ModalIndicator",models[1], U_h)
        indicator = smoothnessIndicator(clsName,
                             [path(__file__)+"modalindicator.hh"]+includes,
                             U_h,ctorArgs=[models[1],1.,space,component])
        limiter = ["minmod",indicator]
    else:
        models = Model

    operator = femDGOperator(models, space, limiter=limiter,
                     codegen=codegen,
                     threading=threading,
                     defaultQuadrature=True,
                     parameters=parameters)

    rkOrder  = max(space.order-1,2) if order>0 else (1 if limiter is None else 2)
    if stepper == "femdg":
        print("Using femdg stepper")
        stepper  = femdgStepper(order=rkOrder, operator=operator,
        parameters=parameters) # , cfl=0.1)
    else:
        print("Using ssp3 stepper")
        stepper = ExplSSP3(4,operator)

    t = startTime
    if outputs>0:
        saveInterval = Model.endTime * 1/outputs
    elif outputs==0: # no output
        saveInterval = 2*Model.endTime
    else: # output each time step
        saveInterval = 0
    saveStep = saveInterval

    if maxLevel > 0:
        un = U_h.copy()
        indicator, residualOperator = residualIndicator(Model, space, un)

    fvspc = finiteVolume( gridView, dimRange=space.dimRange)
    fvU = fvspc.interpolate( U_h, name = "fvU" )
    pointdata = [U_h]
    celldata  = [partitionFunction(gridView),fvU]
    if maxLevel > 0:
        celldata += [indicator, levelFunction(gridView)]
    if hasattr(Model,"exact"):
        exact = space.interpolate(Model.exact(gridView,startTime),name="exact")
        pointdata += [exact]
    vtk = gridView.sequencedVTK(outName, pointdata=pointdata, celldata=celldata,subsampling=2)

    operator.applyLimiter(U_h)

    maxSize  = gridView.comm.sum( operator.gridSizeInterior() )
    maxSize *= 2**(gridView.dimension*maxLevel)

    minMax = lambda U_h: None
    if limiter == "scaling":
        minMax = algorithm.load('minMax', 'utility.hh', U_h )
    if maxLevel > 0:
        for i in range(maxLevel+1):
            un.assign(U_h)
            dt = stepper(U_h)

            residualOperator.model.dt = dt
            residualOperator(U_h,indicator)
            for k in range(len(indicator.dofVector)):
                if math.isnan(indicator.dofVector[k]):
                    indicator.dofVector[k]=1
                    print(indicator.dofVector[k])

            timeTol = gridView.comm.sum( sum(indicator.dofVector) ) / Model.endTime
            hTol = timeTol * dt / maxSize
            markNeighbors(indicator, refineTolerance=hTol, coarsenTolerance=0.2*hTol,
                          minLevel=0, maxLevel=maxLevel)
            adapt(U_h)
            loadBalance(U_h)

            U_h.interpolate(Model.U0)
            operator.applyLimiter(U_h)
            gridSize = gridView.comm.sum( operator.gridSizeInterior() )
            minMax( U_h )
            parprint(isRank0,i,": size=",gridSize,", maxSize = ",maxSize," dt=",dt," tol=",hTol)

    fvU.interpolate( U_h  )
    try:
        exact.interpolate(Model.exact(gridView,t))
    except:
        pass
    vtk()

    # take start time for later measurement
    timeSteps = 0
    startTime = time.time()

    while t < Model.endTime:
        if maxLevel > 0:
            un.assign(U_h)

        operator.setTime(t)
        dt = stepper(U_h)
        timeSteps += 1

        if maxLevel > 0:
            residualOperator.model.dt = dt
            residualOperator(U_h,indicator)
            hTol = timeTol * dt / maxSize

        t += dt

        if t > saveStep:
            gridSize = gridView.comm.sum( operator.gridSizeInterior() )
            minMax( U_h )
            parprint(isRank0,"# t,dt,size,tol: ",t,dt,gridSize,-1 if maxLevel<=0 else hTol)
            fvU.interpolate( U_h )
            try:
                exact.interpolate(Model.exact(gridView,t))
            except:
                pass
            vtk()
            saveStep += saveInterval

        if maxLevel > 0:
            markNeighbors(indicator, refineTolerance=hTol, coarsenTolerance=0.1*hTol,
                          minLevel=0, maxLevel=maxLevel)
            adapt(U_h)
            loadBalance(U_h)

    runTime = time.time() - startTime

    if t > saveStep and maxLevel>0:
        residualOperator(U_h,indicator)
    fvU.interpolate( U_h )
    try:
        exact.interpolate(Model.exact(gridView,t))
    except:
        pass
    vtk()
    parprint(isRank0,"Finished, CPU time in sec: ", runTime, "time steps: ",timeSteps)
    return U_h, t, runTime, timeSteps
