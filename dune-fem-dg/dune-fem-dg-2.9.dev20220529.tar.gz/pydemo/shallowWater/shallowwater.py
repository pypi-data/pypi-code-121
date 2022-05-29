# Parameters need fixing

from dune.grid import cartesianDomain, yaspGrid
from dune.fem.space import dgonb
from dune.alugrid import aluCubeGrid
from ufl import *

def ShallowWater(topo,g):
    dim = 2
    class Model:
        def velo(U):
            return as_vector( [U[i]/U[0] for i in range(1,dim+1)] )
        def toCons(V):
            return as_vector( [V[0]-topo]+[V[i] for i in range(1,dim+1)] )
        def toPrim(U):
            return as_vector( [U[0]+topo] + [v for v in Model.velo(U)] )

        # interface methods
        dimRange = dim+1
        def F_c(t,x,U):
            assert dim==2
            h, v = U[0], Model.velo(U)
            p = 0.5*g*h*h
            return as_matrix([
                    [h*v[0], h*v[1]],
                    [h*v[0]*v[0] + p, h*v[0]*v[1]],
                    [h*v[0]*v[1], h*v[1]*v[1] + p] ] )
        def maxWaveSpeed(t,x,U,n):
            h,v = U[0], Model.velo(U)
            return abs(dot(v,n)) + sqrt(g*h)
        def velocity(t,x,U):
            return Model.velo(U)
        def physical(t,x,U):
            return conditional( U[0]>1e-8, 1, 0 )
        def jump(t,x,U,V):
            hL, hR = U[0], V[0]
            return (hL - hR)/(0.5*(hL + hR))
        def S_e(t,x,U,DU): # or S_i for a stiff source
            return as_vector( [0, *(-U[0]*g*grad(topo)) ])
        # boundary = {range(1,5): lambda t,x,u,n: Model.F_c(t,x,u)*n}
        boundary = {range(1,5): lambda t,x,u: u}
        topography   = topo
        def NumericalF_c(model,clsName,includes):
            print("NumericalFlux_c")
            from dune.generator.importclass import load
            from dune.generator import path
            return load(clsName,[path(__file__)+"llf.hh"]+includes,model)

    return Model

def bgModel(OrigModel,space):
    # Set tildeu = u-bg
    # -> dt tildeu = dt u - dt bg = S(u)-F(u) - S(bg)+F(bg)
    # -> dt tildeu + F(tildeu+bg) - F(bg) = S(tildeu+bg) - S(bg)
    # here bg = C-B
    # toPrim(th)   = th+bg+B = th + C-B + B = th + C
    # toCons(th+C) = th+C-bg-B = th+C - (C-B) - B = th+C-C+B-B=th
    x = SpatialCoordinate(triangle)
    bg_h = OrigModel.bg_h
    class Model(OrigModel):
        def toCons(V):
            return OrigModel.toCons(V-bg_h)
        def toPrim(U):
            return OrigModel.toPrim(U+bg_h)

        # interface methods
        dimRange = OrigModel.dimRange
        def F_c(t,x,U):
            # V = OrigModel.toPrim(U)
            # U = OrigModel.toCons(V+bg_h)
            # return OrigModel.F_c(t,x,U)-OrigModel.F_c(t,x,bg_h)
            return OrigModel.F_c(t,x,U+bg_h)-OrigModel.F_c(t,x,bg_h)
        def maxWaveSpeed(t,x,U,n):
            return OrigModel.maxWaveSpeed(t,x,U+bg_h,n)
        def velocity(t,x,U):
            return OrigModel.velocity(t,x,U+bg_h)
        def physical(t,x,U):
            return OrigModel.physical(t,x,U+bg_h)
        def jump(t,x,U,V):
            hL, hR = U[0], V[0]
            return (hL - hR)/(0.5*(hL + hR))
            # note: can't use bg directly here because skeleton terms not
            # fully supported by ellipticModel - VGF evaluated with edge value
            return OrigModel.jump(t,x,U+OrigModel.bg,V+OrigModel.bg)
        def S_e(t,x,U,DU): # or S_i for a stiff source
            return OrigModel.S_e(t,x,U+bg_h,DU+grad(bg_h)) - OrigModel.S_e(t,x,bg_h,grad(bg_h))
        # might want something like: U+bg(entity)-bg(boundary)
        boundary = {(1,2,3,4): lambda t,x,U: U}
        # boundary = {(1,2): lambda t,x,U: U, (3,4): lambda t,x,U: as_vector([U[0],U[1],-U[0]])}
        # boundary = {range(1,5): lambda t,x,U,n: Model.F_c(t,x,U)*n}
        initial = OrigModel.initial - OrigModel.bg_h
    return Model


# example 5.1 and 7.1 from
# https://www.sciencedirect.com/science/article/pii/S0021999198960582
def leVeque(dim, polOrder):
    eta = 1
    x = SpatialCoordinate(triangle)
    if dim == 1:
        topography = lambda x: conditional(abs(x[0]-0.5)<0.1, 1./4.*(cos(10*pi*(x[0]-0.5))+1), 0)
        initial = conditional(abs(x[0]-0.15)<0.05,eta+0.2,eta)
        Model = ShallowWater(topography,1)
        Model.initial=Model.toCons(as_vector( [initial,0,0] ))
        Model.domain=[[0, 0], [1, 0.25], [64, 16]]
        Model.endTime=0.7
        Model.name="leVeque1D"
    else:
        # domain = cartesianDomain( [0, 0], [2, 1], [80, 40] )
        domain = cartesianDomain( [-1, 0], [2, 1], [120, 40] )
        # coarse domain = cartesianDomain( [-1, -0.25], [2, 1.25], [120, 60] )
        # fine   domain = cartesianDomain( [-1, -0.25], [2, 1.25], [300, 150] )
        domain = yaspGrid(domain) # aluCubeGrid(domain)
        space  = dgonb(domain,order=polOrder)
        x = SpatialCoordinate(space)
        topography = 0.8*exp(-5*(x[0]-0.9)**2-50*(x[1]-0.5)**2)
        topography_h = space.interpolate( topography, name="topography_h" )
        initial = conditional(abs(x[0]-0.1)<0.05,eta+0.01,eta) # this is the free surface
        Model = ShallowWater(topography_h,g=1)
        Model.initial = Model.toCons(as_vector( [initial,0,0] ))
        Model.endTime = 1.8
        Model.name = "leVeque2D"
        # Model.space = space
        Model.domain = domain
    Model.bg   = as_vector([eta-topography,0,0])
    Model.bg_h = as_vector([eta-topography_h,0,0])
    return Model

leVeque1D = lambda: leVeque(1)
leVeque2D = lambda: leVeque(2)
problems = [leVeque1D,leVeque2D]
