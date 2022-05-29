from ufl import *
from dune.ufl import DirichletBC
from dune.fem.space import lagrange
from dune.fem.scheme import galerkin

def model(gridView,order):
    def computeVelocity():
        streamSpace = lagrange(gridView, order=order)
        Psi  = streamSpace.interpolate(0,name="streamFunction")
        u,v  = TrialFunction(streamSpace), TestFunction(streamSpace)
        x    = SpatialCoordinate(streamSpace)
        form = ( inner(grad(u),grad(v)) - 5*sin(x[0])*sin(x[1]) * v ) * dx
        streamScheme = galerkin([form == 0, DirichletBC(streamSpace,0) ])
        streamScheme.solve(target=Psi)
        return as_vector([-Psi.dx(1),Psi.dx(0)])

    class Model:
        transportVelocity = computeVelocity()
        dimRange = 3
        def S_e(t,x,U,DU):
            P1 = as_vector([0.2*pi,0.2*pi]) # midpoint of first source
            P2 = as_vector([1.8*pi,1.8*pi]) # midpoint of second source
            f1 = conditional(dot(x-P1,x-P1) < 0.2, 1, 0)
            f2 = conditional(dot(x-P2,x-P2) < 0.2, 1, 0)
            f  = conditional(t<5, as_vector([f1,f2,0]), as_vector([0,0,0]))
            r = 10*as_vector([U[0]*U[1], U[0]*U[1], -2*U[0]*U[1]])
            return f - r
        def F_c(t,x,U):
            return as_matrix([ [*(Model.velocity(t,x,U)*u)] for u in U ])
        def maxWaveSpeed(t,x,U,n):
            return abs(dot(Model.velocity(t,x,U),n))
        def velocity(t,x,U):
            return Model.transportVelocity
        def F_v(t,x,U,DU):
            return 0.02*DU
        def physical(t,x,U):
            return conditional(U[0]>=0,1,0)*conditional(U[1]>=0,1,0)*\
                   conditional(U[2]>=0,1,0)

        class Indicator:
            def eta(t,x,U):
                return U[0]
            def F(t,x,U,DU):
                return Model.F_c(t,x,U)[0] + Model.F_v(t,x,U,DU)[0]
            def S(t,x,U,DU):
                return Model.S_e(t,x,U)[0]

        boundary = {range(1,5): as_vector([0,0,0])}

    Model.U0 = [0,0,0]
    Model.endTime = 10

    return Model
