import time, math, sys
from ufl import *
from dune.generator import algorithm
from dune.ufl import DirichletBC, Constant
from dune.grid import structuredGrid, cartesianDomain
from dune.alugrid import aluCubeGrid as cubeGrid
from dune.alugrid import aluSimplexGrid as simplexGrid
from dune.fem.view import adaptiveLeafGridView as adaptive
from dune.fem.space import lagrange, dgonb, raviartThomas
from dune.fem.scheme import galerkin
from dune.femdg import femDGOperator
from dune.femdg.rk import femdgStepper
from dune.grid import reader
from dune.fem import parameter
from dune.fem.operator import linear as linearOperator

#gridView = cubeGrid(cartesianDomain([0,0],[1,1],[50,50]))
domain = (reader.gmsh, "circlemeshquad.msh")
gridView = adaptive( grid=cubeGrid(constructor=domain, dimgrid=2) )
gridView.hierarchicalGrid.globalRefine(2)

dimRange          = 3
space             = dgonb( gridView, order=1, dimRange = dimRange)
u_h               = space.interpolate(dimRange*[0], name='u_h')
pressureSpace     = lagrange(gridView, order=1, dimRange=1, storage='istl')
pressure          = pressureSpace.interpolate([1e-7],name="pressure") # Andreas: why not zero?
pressureRhs       = pressureSpace.interpolate([0],name="pressureRhs") # Andreas: why not zero?
velocitySpace     = raviartThomas(gridView,order=1,dimRange=1)
transportVelocity = velocitySpace.interpolate([0,0],name="velocity")

# Model
class Model:
    dimDomain = gridView.dimension
    dimRange = space.dimRange # three unknowns: (phi, phi cu, phi cb)^T

    # Set up time
    secperhour = 3600
    # Andreas: what is t_start? t = Constant(t_start, "time")  # time variable

    # reaction, diffusion and other coefficients
    phi_crit = 0.1
    rhoc = 2710  # density calcite
    Mb = 1.0  # Molar mass suspended biomass
    Mc = 0.1  # Molar mass calcite

    Mc_rhoc = Mc / rhoc

    # Well
    Qw = 1.14e5
    # source_p = Well(mesh=mesh, Q=Qp, degree=1)  # UNCOMMENT
    # Pressure (natural)
    # p0_in = Constant(1.25e7)

    Qp = 1.25e-3

    cu_in = 2000
    Qcu = Qp * cu_in

    cb_in = 0.0001
    Qcb = Qp * cb_in
    #
    # Dispersivity (constant):
    #
    D_mol = 1.587e-9  # molecular diffusion
    alpha_long = 0.01  # longitudinal dispersivity
    # CONSTANT
    # D_mech = Constant(1e-6)
    D = D_mol

    # FULL TENSOR
    # I = Identity(dim)

    kub = 0.01
    kurease = 706.7
    ke = kub * kurease
    Ku = 355  # Ku = KU * rho_w = 0.355 * 1e3

    # unspecific attachment rate
    ka = 8.51e-7 # 4e-6 # from Birane, in the report page 28: 8.51e-7

    # Biomass
    b0 = 3.18e-7  # decay rate coeff.

    K = 1.0e-12

    # Misc. other parameters
    mu = 0.0008  # viscosity of water

    ### initial ###
    phi0 = 0.2
    cu0  = 0
    cb0  = 0
    initial = as_vector([phi0, cu0, cb0])

    ### Model functions ###
    def toPrim(U):
        # ( phi, phi cu, phi cb ) --> (phi, cu, cb)
        return U[0], U[1] / U[0], U[2] / U[0]

    def toCons(U):
        # ( phi, cu, cb ) --> (phi, phi cu, phi cb)
        return U[0], U[1] * U[0], U[2] * U[0]

    # circle of 0.3 around center
    def inlet( x ):
        #return conditional(x[0]>-0.3,1.,0.) * conditional(x[1]>-0.3,1.,0.) * conditional(x[0]<0.3,1.,0.) * conditional(x[1]<0.3,1.,0.)
        #return conditional(x[0]>-0.3,1.,0.) * conditional(x[1]>-0.3,1.,0.) * conditional(x[0]<0.3,1.,0.) * conditional(x[1]<0.3,1.,0.)
        return conditional(sqrt( x[0]*x[0] + x[1]*x[1] ) < 2., 1., 0. )

    def darcyVelocity( p ):
        return -1./Model.mu * Model.K * grad(p[0])

    # form for pressure equation
    def pressureRHS( time ):
        u    = TrialFunction(pressureSpace)
        v    = TestFunction(pressureSpace)
        x    = SpatialCoordinate(pressureSpace)
        phi, cu, cb = Model.toPrim( u_h )
        qu   = Model.ke * phi * Model.Mb * cb * cu / (Model.Ku + cu )
        hour = time / Model.secperhour
        Qw1_t = Model.inlet( x ) * conditional( hour > 1., conditional( hour < 25., Model.Qw, 0), 0 )
        Qw2_t = Model.inlet( x ) * conditional( hour > 45., conditional( hour < 60., Model.Qw, 0), 0 )
        rhs = as_vector([ qu + Qw1_t + Qw2_t ])
        return rhs

    # form for pressure equation
    def pressureForm():
        u    = TrialFunction(pressureSpace)
        v    = TestFunction(pressureSpace)
        x    = SpatialCoordinate(pressureSpace)
        dbc  = DirichletBC(pressureSpace,[ 1e7 ])
        return [ inner(grad(u),grad(v)) * dx == inner(pressureRhs, v) * dx,
                 dbc ]

    def S_i(t,x,U,DU): # or S_i for a stiff source
        phi, cu, cb = Model.toPrim( U )

        qu = Model.ke * phi * Model.Mb * cb * cu / (Model.Ku + cu )
        qc = qu # Assumption in the report, before eq 3.12
        qb = cb * ( phi * ( Model.b0 + Model.ka) + qc * Model.Mc_rhoc )

        hour = t / Model.secperhour
        Qu_t = Model.inlet(x) * conditional( hour > 35., conditional( hour < 45., Model.Qcu, 0), 0 )
        Qb_t = Model.inlet(x) * conditional( hour < 20., Model.Qcb, 0 )
        return as_vector([ -qu * Model.Mc_rhoc,
                           -qu + Qu_t,
                           -qb + Qb_t
                         ])
    def F_c(t,x,U):
        phi, cu, cb = Model.toPrim(U)
        # first flux should be zero since porosity is simply an ODE
        return as_matrix([ Model.dimDomain*[0],
                           [*(Model.velocity(t,x,U) * cu)],
                           [*(Model.velocity(t,x,U) * cb)]
                         ])
    def maxWaveSpeed(t,x,U,n):
        return abs(dot(Model.velocity(t,x,U),n))
    def velocity(t,x,U):
        return transportVelocity
    def F_v(t,x,U,DU):
        # eps * phi^(1/3) * grad U
        return Model.D * pow(U[0], 1./3.) * DU
    def maxDiffusion(t,x,U):
       return Model.D * pow(U[0], 1./3.)
    def physical(t,x,U):
        #phi, cu, cb = Model.toPrim( U )
        # U should be positive
        #return conditional( phi>=0,1,0)*conditional(cu>=0,1,0)*conditional(cb>=0,1,0)
        return conditional(U[0]>1e-10,1,0)*conditional(U[1]>=0,1,0)*conditional(U[2]>=-1e-10,1,0)
    def dirichletValue(t,x,u):
        return Model.initial
    boundary = {1: dirichletValue}
    endTime = 250 * secperhour
    name = "micap"

#### main program ####

operator = femDGOperator(Model, space, limiter="scaling", threading=True)
pressureScheme = galerkin(Model.pressureForm()
                          #parameters={"newton.linear.verbose":True,
                          #            "newton.verbose":True}
                         )

odeVerbose = False
parameter.append({"fem.verboserank": 0 if odeVerbose else -1})
stepper = femdgStepper(order=3, rkType="IMEX",
        parameters={"fem.solver.verbose": False,
                    "fem.solver.newton.verbose": odeVerbose,
                   })(operator) # Andreas: move away from 'EX'?

u_h.interpolate(Model.initial)
operator.applyLimiter( u_h )

A    = linearOperator(pressureScheme)
Ainv = pressureScheme.inverseLinearOperator(A,parameters={"method":"cg","tolerance":1e-10, "istl.preconditioning.method": ":ilu", "verbose":True})

vtk = gridView.sequencedVTK("micap", subsampling=1, celldata=[transportVelocity], pointdata=[pressure,u_h])
vtk() # output initial solution

pRHS = Model.pressureRHS( operator._t )

def updateVelocity():
    pressureRhs.interpolate( pRHS )
    Ainv( pressureRhs, pressure )
    #if ureaPresent:
    # re-compute pressure
    #pressureScheme.solve(target=pressure)
    # Darcy velocity
    velocity = Model.darcyVelocity(pressure)
    # project into rt space
    transportVelocity.interpolate( velocity )

t        = 0
tcount   = 0
saveStep = Model.secperhour # Model.endTime/100
saveTime = saveStep

operator.setTime(t)
updateVelocity()
while t < Model.endTime:
    print("Time step: ",tcount," t=",operator._t.value)
    operator.setTime(t)

    if t > 9.9:
        updateVelocity()

    dt = stepper(u_h, dt=360)
    t += dt
    tcount += 1
    # check that solution is meaningful
    if math.isnan( u_h.scalarProductDofs( u_h ) ):
        vtk()
        print('ERROR: dofs invalid t =', t,flush=True)
        print('[',tcount,']','dt = ', dt, 'time = ',t, flush=True )
        sys.exit(1)
    if t > saveTime:
        # TODO: issue with time step estimate: here the 'fullPass' is used
        # but that is not set for IMEX
        print('[',tcount,']','dt = ', dt, 'time = ',t / Model.secperhour,' h',
                'dtEst = ',operator.timeStepEstimate,
                'elements = ',gridView.size(0), flush=True )
        vtk()
        saveTime += saveStep

vtk() # output final solution
