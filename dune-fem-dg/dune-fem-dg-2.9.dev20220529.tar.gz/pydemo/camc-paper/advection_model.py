from ufl import *
from dune.ufl import Space

# Basic model for hyperbolic conservation law
def model(dim):
    space = Space(dim,1)
    x = SpatialCoordinate(space.cell())

    eps = None

    center  = as_vector([ 0.5,0.5 ])
    x0 = x[0] - center[0]
    x1 = x[1] - center[1]

    v = as_vector([-x1,x0])

    class Model:
        dimRange = 1
        if v is not None:
            def F_c(t,x,U):
                return as_matrix( [[ *(v*U[0]) ]] )
            def maxWaveSpeed(t,x,U,n):
                return abs(dot(v,n))
            def velocity(t,x,U):
                return v
        if eps is not None:
            def F_v(t,x,U,DU):
                return eps*DU
            # TODO: this method is used in an IMEX method allough the
            # diffusion is implicit - should we change that behaviour?
            # commented out for test of IMEX
            def maxDiffusion(t,x,U):
               return eps

        # def physical(t,x,U):
        #     return ( conditional( U[0]>-1e-8, 1.0, 0.0 ) *
        #              conditional( U[0]<1.0+1e-8, 1.0, 0.0 ) )

        def jump(t,x,U,V):
            return U-V

        class Indicator:
            def eta(t,x,U):
                return U[0]
            def F(t,x,U,DU):
                q = Model.F_c(t,x,U)[0]
                if eps is not None:
                    q += Model.F_v(t,x,U,DU)[0]
                return q
            def S(t,x,U,DU):
                return 0

        # simple 'dirchlet' boundary conditions on all boundaries
        boundary = {range(1,5): lambda t,x,U: as_vector([0])}

    if dim == 2:
        # cube [0.6,0.8] x [0.2,0.4]
        cube  = ( conditional( x[0]>0.6, 1., 0. )*
                  conditional( x[0]<0.8, 1., 0. )*
                  conditional( x[1]>0.2, 1., 0. )*
                  conditional( x[1]<0.4, 1., 0. ) )

        radiusSqr = 0.01
        # slotted cylinder with center (0.5,0.75) and radius 0.1
        cyl = ( conditional( (x[0] - 0.5)**2 + (x[1] - 0.75)**2 < radiusSqr, 1.0, 0.0 ) *
               (conditional( abs(x[0] - 0.5) >= 0.02, 1.0, 0.0)*
                conditional( x[1] < 0.8, 1.0, 0.0) + conditional( x[1] >= 0.8, 1., 0.)) )

        # smooth hump with center (0.25,0.5)
        hump = ( conditional( (x[0] - 0.25)**2 + (x[1] - 0.5)**2 < radiusSqr, 1.0, 0.0 ) *
                 2/3*(0.5 + cos(pi * sqrt( (x[0] - 0.25)**2 +  (x[1] - 0.5)**2 ) / 0.15 )) )

        Model.U0 = [cube+cyl+hump]
        Model.endTime = 3.141592

    return Model
