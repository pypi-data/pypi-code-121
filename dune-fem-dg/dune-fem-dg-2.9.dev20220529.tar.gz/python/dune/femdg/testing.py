import time, math, sys
from dune.grid import structuredGrid, cartesianDomain, OutputType
import dune.create as create
from dune.fem.function import integrate
from dune.ufl import Constant, expression2GF
from ufl import dot, SpatialCoordinate
from dune.femdg import femDGOperator, rungeKuttaSolver, createLimiter
from dune.femdg.rk import femdgStepper

from collections import namedtuple

def run(Model, Stepper=None,
        polOrder=1, limiter="default", startLevel=0,
        primitive=None, saveStep=None, subsamp=0,
        dt=None,cfl=None,grid="yasp", space="dgonb", threading=True,
        codegen=True,
        parameters=None,
        modifyModel=None):

    # if no parameters is passed set default Runge-Kutta order to be p+1
    rkOrder = None
    if parameters is None or not 'fem.ode.order' in parameters:
        rkOrder = polOrder+1

    if Stepper is None:
        Stepper = femdgStepper(order=rkOrder,parameters=parameters)
    try:
        exact = Model.exact
    except:
        exact = None

    if grid == "polygon":
        subsamp=None
        print('Disabling subsampling for PolygonGrid')

    print("*************************************")
    print("**** Running simulation",Model.name)
    print("*************************************")
    try: # passed in a [xL,xR,N] tripple
        x0,x1,N = Model.domain
        periodic=[True,]*len(x0)
        if hasattr(Model,"boundary"):
            bnd=set()
            for b in Model.boundary:
                bnd.update(b)
            for i in range(len(x0)):
                if 2*i+1 in bnd:
                    assert(2*i+2 in bnd)
                    periodic[i] = False
        # periodic boundaries do not work for YaspGrid because the concept
        # is different from ALUGrid and SPGrid which is the concept used in
        # dune-fem-dg
        elif grid == 'yasp':
           errorstr = "YaspGrid (grid='"+grid+"') does not work with periodic  boundaries!\nChoose grid='alucube' or grid='spbisection'"
           raise Exception(errorstr)

        # create domain and grid
        domain   = cartesianDomain(x0,x1,N,periodic=periodic,overlap=0)
        grid     = create.grid(grid,domain)
        print("Setting periodic boundaries",periodic,flush=True)
    except TypeError: # assume the 'domain' is already a gridview
        grid = Model.domain
    # initial refinement of grid
    if startLevel>0: # note this call clears all discrete function e.g. the velocity in the chemical problem
        grid.hierarchicalGrid.globalRefine(startLevel)
    dimR     = Model.dimRange
    t        = 0
    tcount   = 0
    saveTime = saveStep

    # create discrete function space
    try:
        if type(space) in [list,tuple]:
            space = create.space( space[0], grid, dimRange=dimR, order=polOrder,
                       pointType=space[1] )
        elif space.lower() == "finitevolume":
            space = create.space( space, grid, dimRange=dimR)
        else:
            space = create.space( space, grid, order=polOrder, dimRange=dimR)
    except:
        assert space.dimRange > 0
    if modifyModel is not None:
        Model = modifyModel(Model,space)

    operator = femDGOperator(Model, space,
        limiter=limiter, threading=threading, parameters=parameters,
        defaultQuadrature=True, codegen=codegen
        )
    stepper  = Stepper(operator, cfl)
    # create and initialize solution
    u_h = space.interpolate(Model.initial, name='u_h')
    operator.applyLimiter( u_h )

    # preparation for output
    vtk = lambda : None
    if saveStep is not None and Model.name is not None:
        x = SpatialCoordinate(space.cell())
        tc = Constant(0.0,"time")
        try:
            velo = create.function("ufl",space.gridView, ufl=Model.velocity(tc,x,u_h), order=2, name="velocity")
        except AttributeError:
            velo = None
        vtk = grid.sequencedVTK(Model.name, subsampling=subsamp,
               celldata=[u_h],
               pointdata=primitive(Model,u_h) if primitive else [u_h],
               cellvector=[velo]
            )
        try:
            velo.setConstant("time",[t])
        except:
            pass
    vtk()

    # measure CPU time
    start = time.time()

    # if dt is given then set fixed time step size
    if dt is not None:
        stepper.setTimeStepSize(dt)

    # tracemalloc.start()

    # make sure initial data is meaningful
    assert not math.isnan( u_h.scalarProductDofs( u_h ) )

    t = 0
    while t < Model.endTime:
        operator.setTime(t)
        dt = stepper(u_h)
        t += dt
        tcount += 1

        # check that solution is meaningful
        if math.isnan( u_h.scalarProductDofs( u_h ) ):
            vtk()
            print('ERROR: dofs invalid t =', t,flush=True)
            print('[',tcount,']','dt = ', dt, 'time = ',t, flush=True )
            sys.exit(1)
        if t > saveTime:
            print('[',tcount,']','dt = ', dt, 'time = ',t,
                    'dtEst = ',operator.localTimeStepEstimate,
                    'elements = ',grid.size(0), flush=True )
            try:
                velo0.setConstant("time",[t])
            except:
                pass
            vtk()
            saveTime += saveStep
        # snapshot = tracemalloc.take_snapshot()
        # display_top(snapshot)

    runTime = time.time()-start
    print("time loop:",runTime,flush=True)
    print("number of time steps ", tcount,flush=True)
    try:
        velo.setConstant("time",[t])
        vtk()
    except:
        pass

    # output the final result and compute error (if exact is available)
    if exact is not None and Model.name is not None:
        tc = Constant(0, "time")
        # using '0' here because uusing 't'
        # instead means that this value is added to the generated code so
        # that slight changes to 't' require building new local functions -
        # should be fixed in dune-fem
        try:
            u = expression2GF(grid,exact(tc),order=5)
        except:
            u = exact(grid,t)
        tc.value = t
        grid.writeVTK(Model.name+'-final', subsampling=subsamp,
                celldata=[u_h], pointdata={"exact":u})
        # TODO make the gridfunctions from dune-python work nicely with ufl...
        # error = integrate( grid, dot(u-u_h,u-u_h), order=5 )
        error = integrate( grid, dot(u-u_h,u-u_h), order=5 )
        try:
            error = integrate( grid, dot(u-u_h,u-u_h), order=5 )
        except:
            error = 0
            pass
    elif Model.name is not None:
        grid.writeVTK(Model.name+'-final', subsampling=subsamp, celldata=[u_h])
        error = integrate( grid, dot(u_h,u_h), order=5 )
    error = math.sqrt(error)
    print("*************************************")
    print("**** Completed simulation",Model.name)
    print("**** error:", error)
    print("*************************************",flush=True)
    return u_h, [error, runTime, tcount, operator.counter()]
