import time, math, sys
from ufl import *
from dune.ufl import DirichletBC, Constant
from dune.grid import structuredGrid, cartesianDomain
from dune.alugrid import aluCubeGrid as cubeGrid
from dune.alugrid import aluSimplexGrid as simplexGrid
from dune.fem.view import adaptiveLeafGridView as adaptive
from dune.fem.space import lagrange, dgonbhp, raviartThomas
from dune.fem.scheme import galerkin
from dune.femdg import femDGOperator
from dune.femdg.rk import femdgStepper
from dune.grid import reader, Marker
from dune.fem import parameter, adapt

import timeit

parameter.append({"fem.verboserank": 0})

#gridView = cubeGrid(cartesianDomain([0,0],[1,1],[50,50]))
domain = (reader.gmsh, "circlemeshquad.msh")
gridView = adaptive( grid=cubeGrid(constructor=domain, dimgrid=2) )

hgrid = gridView.hierarchicalGrid
hgrid.globalRefine(1)

#domain = (reader.gmsh, "circlemesh.msh")
#gridView = adaptive( grid=simplexGrid(constructor=domain, dimgrid=2) )
#gridView.hierarchicalGrid.globalRefine(2)

def mark( element ):
    center = element.geometry.center
    print("Called Mark", center)
    if (sqrt(center[0]*center[0] + center[1]*center[1])) < 15.:
        print ("Return refine")
        return Marker.refine
    else:
        return Marker.keep

print("Grid size = ", gridView.size(0))

# initial adapt
for i in range(0,4):
    hgrid.mark(mark)
    hgrid.adapt()
    hgrid.loadBalance()

gridView = adaptive( grid=hgrid )

print("Grid size = ", gridView.size(0))

dimRange          = 3
space             = dgonbhp( gridView, order=2, dimRange = dimRange)
u_h               = space.interpolate(dimRange*[0], name='u_h')
pressureSpace     = lagrange(gridView, order=1, dimRange=1, storage='istl')
pressure          = pressureSpace.interpolate([0],name="pressure") # Andreas: why not zero?
velocitySpace     = raviartThomas(gridView,order=1,dimRange=1)

print("Velocity projection")
start = time.time()
transportVelocity = velocitySpace.interpolate([0,0],name="velocity")
print("Done.", time.time()-start)

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
    #Qw = 1.14e5
    Qw = 1.25e-1

    Qp = 1.25e-3
    cu_in = 2000 # in the report 5000
    Qcu = Qp * cu_in

    cb_in = 0.01
    Qcb = Qp * cb_in
    #
    # Dispersivity (constant):
    #
    D_mol = 1.587e-9  # molecular diffusion
    alpha_long = 0.01  # longitudinal dispersivity
    # CONSTANT
    D_mech = 1e-6
    #D = D_mol
    powPhi = 1.4 # approx pow( 0.2, 1./3.)
    D = D_mech * powPhi # Constant( D_mech * powPhi, "D" )

    #D.value = D_mech * powPhi

    # FULL TENSOR
    # I = Identity(dim)

    kub = 0.01
    kurease = 706.7
    ke = kub * kurease
    Ku = 355  # Ku = KU * rho_w = 0.355 * 1e3

    # unspecific attachment rate
    ka = 4e-6

    # Biomass
    b0 = 3.18e-7  # decay rate coeff.

    K = 1.0e-12
    # Misc. other parameters
    mu = 0.0008  # viscosity of water

    K_mu = -1./mu * K

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
        return conditional(( x[0]*x[0] + x[1]*x[1] ) < 0.4*0.4, 1., 0. )

    def darcyVelocity( p ):
        return Model.K_mu * grad(p[0])

    def qu( phi, cu, cb ):
        return Model.ke * Model.Mb * phi * cb * cu / (Model.Ku + cu )

    # form for pressure equation
    def pressureForm( time ):
        u    = TrialFunction(pressureSpace)
        v    = TestFunction(pressureSpace)
        x    = SpatialCoordinate(pressureSpace)
        dbc  = DirichletBC(pressureSpace,[ 0 ])
        phi, cu, cb = Model.toPrim( u_h )
        qu   = Model.qu( phi, cu, cb )
        hour = time / Model.secperhour
        Qw1_t = Model.inlet( x ) * conditional( hour > 3., conditional( hour < 35., Model.Qw, 0), 0 )
        Qw2_t = Model.inlet( x ) * conditional( hour > 37., conditional( hour < 50., Model.Qw, 0), 0 )
        pressureRhs = as_vector([ qu + Qw1_t + Qw2_t ])
        return [ inner(grad(u),grad(v)) * dx == inner(pressureRhs, v) * dx,
                 dbc ]

    def S_i(t,x,U,DU): # or S_i for a stiff source
        phi, cu, cb = Model.toPrim( U )

        qu = Model.qu( phi, cu, cb )
        qc = qu # Assumption in the report, before eq 3.12
        qb = cb * ( phi * ( Model.b0 + Model.ka) + qc * Model.Mc_rhoc )

        hour = t / Model.secperhour
        Qu_t = Model.inlet(x) * conditional( hour > 35., conditional( hour < 37., Model.Qcu, 0), 0 )
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
        # TODO remove diffusion for phi, comp 0
        return Model.D * DU
        #return as_matrix([ Model.dimDomain*[0],
        #                  [*(Model.D * DU[1])],
        #                  [*(Model.D * DU[2])] ])
    def maxDiffusion(t,x,U):
       return Model.D
    def physical(t,x,U):
        #phi, cu, cb = Model.toPrim( U )
        # U should be positive
        #return conditional( phi>=0,1,0)*conditional(cu>=0,1,0)*conditional(cb>=0,1,0)
        return conditional(U[0]>1e-10,1,0)*conditional(U[1]>=0,1,0)*conditional(U[2]>=0,1,0)
    def dirichletValue(t,x,u):
        return Model.initial
    boundary = {1: dirichletValue}
    endTime = 250 * secperhour
    name = "micap"

#### main program ####

print("Start main program")

linearSolver = False
newtonSolver = False
odeParam={"fem.ode.verbose": "none",
          "fem.solver.verbose": linearSolver,
          "fem.solver.newton.verbose": newtonSolver,
          "fem.solver.newton.linear.verbose": linearSolver,
          "fem.solver.newton.tolerance": 1e-6,
          "fem.solver.newton.linear.tolerance": 1e-8,
          "fem.solver.method": "cg",
          "fem.solver.gmres.restart": 50,
          "fem.adaptation.finestLevel": 5,
          "fem.adaptation.coarsestLevel": 3,
          "fem.adaptation.method": "callback",
          "fem.adaptation.refineTolerance": 0.5,
          "fem.adaptation.coarsenPercent": 0.05,
          "femdg.stepper.endtime": Model.endTime,
          "fem.adaptation.markingStrategy": "grad",
          "dgdiffusionflux.theoryparameters": 1}
parameter.append( odeParam )

#operator = femDGOperator(Model, space, limiter='scaling', diffusionScheme = 'cdg2', threading=True)
operator = femDGOperator(Model, space, limiter='scaling', diffusionScheme = 'ip', threading=True)
pressureScheme = galerkin(Model.pressureForm( operator._t ), solver="cg",
                          parameters={"newton.linear.verbose":False,
                                      "newton.verbose":False,
                                      "istl.preconditioning.method": "ilu"} )
stepper = femdgStepper(order=1, rkType="IMEX")(operator)
u_h.interpolate(Model.initial)
operator.applyLimiter( u_h )

vtk = gridView.sequencedVTK("micap", subsampling=1, celldata=[transportVelocity], pointdata=[pressure,u_h])
#vtk = gridView.sequencedVTK("micap", pointdata=[pressure,u_h])
#vtk = gridView.sequencedVTK("micap", celldata=[transportVelocity], pointdata=[pressure,u_h])
vtk() # output initial solution

def updateVelocity( ):
    # re-compute pressure
    pressureScheme.solve(target=pressure)
    # project into rt space
    transportVelocity.interpolate( Model.darcyVelocity(pressure) )

t        = 0
tcount   = 0
saveStep = Model.secperhour # Model.endTime/100
saveTime = saveStep

print("Start time loop #el = ", gridView.size(0))

while t < Model.endTime:
    # update operator time
    operator.setTime(t)

    if t / Model.secperhour > 9.5:
        updateVelocity()

    # measure CPU time
    start = time.time()

    dt = stepper(u_h, dt=360)

    # compute indicator and mark cells
    # operator.estimateMark( u_h, dt )

    # adapt grid
    # adapt([u_h,pressure,transportVelocity])

    runTime = time.time()-start
    print("Stepper used ", runTime)

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
        print('[',tcount,']','dt = ', dt, 'time = ',t / Model.secperhour,
                'dtEst = ',operator.timeStepEstimate,
                'elements = ',gridView.size(0), flush=True )
        vtk()
        saveTime += saveStep

vtk() # output final solution
