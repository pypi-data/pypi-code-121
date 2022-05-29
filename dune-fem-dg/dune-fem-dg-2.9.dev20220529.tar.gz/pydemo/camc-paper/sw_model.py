# Parameters need fixing

from dune.grid import cartesianDomain, yaspGrid
from dune.fem.space import lagrange, dgonb
from ufl import *

def modelOrig(gridView, order, g, topo, T, U, bndConditions):
    dim = 2
    class Model:
        topography = dgonb(gridView,order=order).interpolate( topo, name="topography_h" )
        gravity = g
        def toCons(V):
            h = V[0]-Model.topography
            return as_vector( [h]+[V[i]*h for i in range(1,dim+1)] )
        def toPrim(U):
            v = as_vector( [U[i]/U[0] for i in range(1,dim+1)] )
            return U[0],v

        # interface methods
        dimRange = dim+1
        def F_c(t,x,U):
            _, v = Model.toPrim(U)
            p = g/2*U[0]*U[0]
            return as_matrix([
                    [U[1],          U[2]],
                    [v[0]*U[1] + p, v[1]*U[1]],
                    [v[0]*U[2],     v[1]*U[2] + p] ])
        def S_e(t,x,U,DU):
            return as_vector([ 0, *(-U[0]*g*grad(Model.topography)) ])

        def maxWaveSpeed(t,x,U,n):
            h, v = Model.toPrim(U)
            return abs(dot(v,n)) + sqrt(g*h)
        def velocity(t,x,U):
            return Model.toPrim(U)[1]
        def physical(t,x,U):
            return conditional( Model.toPrim(U)[0]>0, 1, 0 )
        def jump(t,x,U,V):
            return (U[0] - V[0])/(0.5*(U[0] + V[0]))

        class Indicator:
            def eta(t,x,U):
                return U[0]
            def F(t,x,U,DU):
                return Model.F_c(t,x,U)[0]
            def S(t,x,U,DU):
                return Model.S_e(t,x,U,DU)[0]

        boundary = bndConditions
        endTime = T

    Model.U0 = Model.toCons( U )
    return Model

def modelWB(gridView, g, topo, T, U, bndConditions):
    dim = 2
    class Model:
        gravity = g
        def toCons(V):
            return as_vector( [V[0]+V[dim+1]]+[V[i]*V[0] for i in range(1,dim+1)] )
        def toPrim(U):
            h = U[0]-U[dim+1]
            v = as_vector( [U[i]/h for i in range(1,dim+1)] )
            return h,v

        # interface methods
        dimRange = dim+2
        def F_c(t,x,U):
            _, v = Model.toPrim(U)
            p = g/2*(U[0]*U[0]-2*U[0]*U[dim+1])
            return as_matrix([
                    [U[1],          U[2]],
                    [v[0]*U[1] + p, v[1]*U[1]],
                    [v[0]*U[2],     v[1]*U[2] + p],
                    [0,             0] ])
        def S_e(t,x,U,DU):
            return as_vector([ 0, -U[0]*g*DU[dim+1,0],
                                  -U[0]*g*DU[dim+1,1],
                               0 ])

        def maxWaveSpeed(t,x,U,n):
            h, v = Model.toPrim(U)
            return abs(dot(v,n)) + sqrt(g*h)
        def velocity(t,x,U):
            return Model.toPrim(U)[1]
        def physical(t,x,U):
            return conditional( Model.toPrim(U)[0]>0, 1, 0 )
        def jump(t,x,U,V):
            return (U[0] - V[0])/(0.5*(U[0] + V[0]))

        def S(t,x,U):
            return U[0]
        def Q(t,x,U,DU):
            return Model.F_c(t,x,U)[0] - Model.S_e(t,x,U,DU)[0]

        boundary = bndConditions
        topography = topo
        U0 = U + [topo]
        endTime = T

    return Model

def model(gridView, order, g, problem, wb):
    x = SpatialCoordinate(triangle)
    if problem == "LeVeque":
        # example 7.1 from
        # https://www.sciencedirect.com/science/article/pii/S0021999198960582
        topography = 0.8*exp(-5*(x[0]-0.9)**2-50*(x[1]-0.5)**2)
        eta = conditional(abs(x[0]-0.1)<0.05,1.01,1) # this is the free surface
        U0 = [eta,0,0]
        endTime = 2
        boundary = {range(1,5): lambda t,x,u: u}
    elif problem == "beach":
        # J.A. Zelt. Tsunamis: the response of harbors with sloping boundaries to long wave exitation.
        # Tech. Rep. KH-R-47 1986; California Institute of Technology., Laboratory of Hydraulics and
        # Water Resources, Division of Engineering and Applied Science, California Institute of Technology,1986.
        # http://resolver.caltech.edu/CaltechKHR:KH-R-47
        d0, l, xp = 1.273, 10, 30/pi
        topography = conditional(x[0]>=xp,
                                 d0*(x[0]-xp)/(l*cos(pi*x[1]/l)/pi+xp,0) )
        h0,L,alpha = d0,10,0.02
        xi = sqrt(3*alpha/(4*(h0/L)**2)*(1+alpha))
        sech = lambda z: 2/(exp(z)+exp(-z))
        h = lambda t: h0+alpha*h0*sech(sqrt(g*h0/L)*xi*t)**2
        eta = h(0)+topography
        U0 = [eta,0,0]
        endTime = 2
        boundary = {range(1,5): lambda t,x,u: u}
    elif problem == "dambreak":
        topography = 0
        eta = conditional( x[0] < 0.5, 1, 0.5 )
        U0 = [eta,0,0]
        endTime = 0.2
        boundary = {range(1,5): lambda t,x,u: u}
    return modelWB(gridView,g,topography,endTime,U0,boundary) if wb\
           else modelOrig(gridView,order,g,topography,endTime,U0,boundary)
