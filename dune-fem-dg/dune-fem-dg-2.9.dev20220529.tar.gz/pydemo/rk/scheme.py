import time, math
from dune.grid import structuredGrid, cartesianDomain, OutputType
import dune.create as create
from dune.fem.function import integrate
from dune.ufl import Constant
from ufl import dot, SpatialCoordinate
from dune.femdg import femDGOperator, rungeKuttaSolver

def run(Model, initial, x0,x1,N, endTime, name, exact,
        polOrder, limiter="default", startLevel=0,
        primitive=None, saveStep=None, subsamp=0,
        dt=None,grid="yasp", space="dgonb", threading=True,
        parameters={}):
    periodic=[True,]*len(x0)
    if hasattr(Model,"boundary"):
        bnd=set()
        for b in Model.boundary:
            bnd.update(b)
        for i in range(len(x0)):
            if 2*i+1 in bnd:
                assert(2*i+2 in bnd)
                periodic[i] = False
    print("Setting periodic boundaries",periodic,flush=True)

    # create domain and grid
    domain   = cartesianDomain(x0,x1,N,periodic=periodic,overlap=0)
    grid     = create.grid(grid,domain)
    # initial refinement of grid
    grid.hierarchicalGrid.globalRefine(startLevel)

    dimR     = Model.dimRange
    t        = 0
    count    = 0
    saveTime = saveStep

    # create discrete function space
    space = create.space( space, grid, order=polOrder, dimRange=dimR)
    # create and initialize solution
    u_h = space.interpolate(initial, name='u_h')

    # create solution scheme, i.e. operator and ODE solver
    operator = femDGOperator( Model, space, limiter=limiter, threading=True, parameters=parameters )
    ode = rungeKuttaSolver( operator, imex='EX', parameters=parameters )

    # limit initial data if necessary
    operator.applyLimiter( u_h );

    print("number of elements: ",grid.size(0),flush=True)

    # preparation for output
    if saveStep is not None:
        x = SpatialCoordinate(space.cell())
        tc = Constant(0.0,"time")
        try:
            velo = [create.function("ufl",space.grid, ufl=Model.velocity(tc,x,u_h), order=2, name="velocity")]
        except AttributeError:
            velo = None
        vtk = grid.writeVTK(name, subsampling=subsamp, write=False,
               celldata=[u_h],
               pointdata=primitive(Model,u_h) if primitive else None,
               cellvector=velo
            )
        try:
            velo[0].setConstant("time",[t])
        except:
            pass
        vtk.write(name, count) # , outputType=OutputType.appendedraw)

    # measure CPU time
    start = time.time()

    tcount = 0
    # time loop
    while t < endTime:
        # set time step size to ODE solver
        if dt is not None:
            operator.setTimeStepSize(dt)
        # solver time step
        ode.solve(u_h)
        # obtain new time step size
        dt = ode.deltaT()
        # check that solution is meaningful
        if math.isnan( u_h.scalarProductDofs( u_h ) ):
            grid.writeVTK(name, subsampling=subsamp, celldata=[u_h])
            print('ERROR: dofs invalid t =', t,flush=True)
            print('[',tcount,']','dt = ', dt, 'time = ',t, 'count = ',count, flush=True )
            exit(0)
        # increment time and time step counter
        t += dt
        tcount += 1

        # output
        if tcount%100 == 0:
            print('[',tcount,']','dt = ', dt, 'time = ',t, 'count = ',count, flush=True )
        if saveStep is not None and t > saveTime:
            count += 1
            try:
                velo[0].setConstant("time",[t])
            except:
                pass
            vtk.write(name, count, outputType=OutputType.appendedraw)
            saveTime += saveStep

    print("time loop:",time.time()-start,flush=True)
    print("number of time steps ", tcount,flush=True)
    if saveStep is not None:
        try:
            velo[0].setConstant("time",[t])
        except:
            pass
        vtk.write(name, count, outputType=OutputType.appendedraw)

    # output the final result and compute error (if exact is available)
    if exact is not None:
        grid.writeVTK(name, subsampling=subsamp,
                celldata=[u_h], pointdata={"exact":exact(t)})
        error = integrate( grid, dot(u_h-exact(t),u_h-exact(t)), order=5 )
        print("error:", math.sqrt(error),flush=True )
    else:
        grid.writeVTK(name, subsampling=subsamp, celldata=[u_h])
