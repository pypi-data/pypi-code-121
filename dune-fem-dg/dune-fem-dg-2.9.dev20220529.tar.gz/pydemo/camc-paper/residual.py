import ufl
from dune.ufl import Constant
from dune.fem.operator import galerkin as operator
from dune.fem.space import finiteVolume
def residualIndicator(Model,space,un):
    indicatorSpace = finiteVolume( space.grid )
    indicator = indicatorSpace.interpolate(0,name="indicator")
    u   = ufl.TrialFunction(space)
    phi = ufl.TestFunction(indicatorSpace)
    dt  = Constant(1,"dt")
    t   = Constant(0,"t")
    x   = ufl.SpatialCoordinate(space)
    n   = ufl.FacetNormal(space)
    hT  = ufl.MaxCellEdgeLength(space)
    he  = ufl.avg( ufl.CellVolume(space) ) / ufl.FacetArea(space)

    eta = Model.Indicator.eta
    F   = Model.Indicator.F
    S   = Model.Indicator.S
    eta_new = eta(t+dt,x,u)
    eta_old = eta(t,x,un)
    etaMid  = ( eta(t,x,un) + eta(t+dt,x,u) ) / 2
    qMid    = ( F(t,x,un,ufl.grad(un)) + F(t+dt,x,u,ufl.grad(u)) ) / 2
    SMid    = ( S(t,x,un,ufl.grad(un)) + S(t+dt,x,u,ufl.grad(u)) ) / 2
    Rvol    = (eta_new-eta_old)/dt + ufl.div(qMid) - SMid
    estimator = hT**2 * Rvol**2 * phi * ufl.dx  +\
                he    * ufl.inner(ufl.jump(qMid), n('+'))**2 * ufl.avg(phi) * ufl.dS +\
                1/he  * ufl.jump(etaMid)**2 * ufl.avg(phi) * ufl.dS
    # avoid communication in residual operator since only interior values are needed
    return indicator, operator(estimator, space, indicatorSpace, communicate=False)
