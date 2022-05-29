import matplotlib
matplotlib.rc( 'image', cmap='jet' )
from matplotlib import pyplot

from ufl import SpatialCoordinate, CellVolume, TrialFunction, TestFunction,\
                inner, dot, div, grad, dx, as_vector, transpose, Identity
from dune.ufl import Constant, DirichletBC

from dune.fem.operator import linear as linearOperator
from dune.fem import parameter
parameter.append({"fem.verboserank": 0})

useCartesian  = False
uzawaPreconditioner = True
storage="petsc"

mu_   = 0.1
nu_   = 10.0

def compute(useVem,order,version,plot=False):
    print("########################################################")
    print(useVem,order,version)
    print("########################################################")
    # grid construction
    from dune.grid import structuredGrid, cartesianDomain
    from dune.vem import polyGrid        as leafGridView
    domain = cartesianDomain([0,0],[3,1],[30,10])
    if useCartesian:
        constructor = domain
    else:
        from dune.vem import voronoiCells
        constructor = voronoiCells(domain,300,"uzawaseeds",True)
    grid = leafGridView( constructor )
    if plot: grid.plot()

    # spaces and schemes
    from dune.fem.operator import galerkin   as galerkinOperator
    if not useVem:
        from dune.fem.space    import lagrange   as velocitySpace
        from dune.fem.scheme   import galerkin   as velocityScheme
        if version=="TH":
            from dune.fem.space  import lagrange as pressureSpace
            from dune.fem.scheme import galerkin as pressureScheme
            useDGPressure = False
        else:
            from dune.fem.space  import dgonb    as pressureSpace
            from dune.fem.scheme import dg       as pressureScheme
            useDGPressure = True
        spcU = velocitySpace(grid, dimRange=grid.dimension, order=order, storage=storage)
        spcP = pressureSpace(grid, dimRange=1, order=order-1, storage=storage),
    else:
        if version=="TH":
            veloTestSpaces = [order,   [0,order-2,order-2]]
            presTestSpaces = [order-1, [0,order-3,order-3]]
            useDGPressure = False
        if version=="mini":
            veloTestSpaces = [order,   [0,order-2,order-1]]
            presTestSpaces = [order,   [0,order-2,order-2]]
            useDGPressure = False
        if version=="non-conf":
            veloTestSpaces = [order,   [-1,order-1,order-2]]
            presTestSpaces = order-1
            useDGPressure = True
        if version=="SV":
            veloTestSpaces = [order,   [0,order-2,order-2]]
            presTestSpaces = order-1
            useDGPressure = True
        from dune.vem import vemSpace   as velocitySpace
        from dune.vem import vemScheme  as velocityScheme
        if not useDGPressure:
            from dune.vem import vemSpace   as pressureSpace
            from dune.vem import vemScheme  as pressureScheme
            spcU = velocitySpace(grid, dimRange=grid.dimension, storage=storage,
                      order=veloTestSpaces[0], testSpaces=veloTestSpaces[1])
            spcP = pressureSpace(grid, dimRange=1, storage=storage,
                      order=presTestSpaces[0], testSpaces=presTestSpaces[1])
        else:
            from dune.vem import bbdgSpace  as pressureSpace
            from dune.vem import bbdgScheme as pressureScheme
            spcU = velocitySpace(grid, dimRange=grid.dimension, storage=storage,
                      order=veloTestSpaces[0], testSpaces=veloTestSpaces[1])
            spcP = pressureSpace(grid, dimRange=1, storage=storage,
                      order=presTestSpaces)

    velocity = spcU.interpolate([0,]*spcU.dimRange, name="velocity")
    pressure = spcP.interpolate([0], name="pressure")
    print("size of pressure space:",spcP.size)
    print("size of velocity space:",spcU.size)

    # setting up the problem
    cell  = spcU.cell()
    x     = SpatialCoordinate(cell)
    mu    = Constant(mu_,  "mu")
    nu    = Constant(nu_,  "nu")
    u     = TrialFunction(spcU)
    v     = TestFunction(spcU)
    p     = TrialFunction(spcP)
    q     = TestFunction(spcP)

    # exact solution and resulting forcing
    exact_u     = as_vector( [x[1] * (1.-x[1]), 0] )
    exact_p     = as_vector( [ (-2*x[0] + 2)*mu ] )
    f           = as_vector( [0,]*grid.dimension )
    f          += nu*exact_u

    # ufl forms
    mainModel   = (nu*dot(u,v) + mu*inner(grad(u)+grad(u).T, grad(v)) - dot(f,v)) * dx
    gradModel   = -inner( p[0]*Identity(grid.dimension), grad(v) ) * dx
    divModel    = -div(u)*q[0] * dx
    massModel   = inner(p,q) * dx
    preconModel = inner(grad(p),grad(q)) * dx

    # operators and schemes
    if not useVem:
        mainOp       = velocityScheme([mainModel==0,DirichletBC(spcU,exact_u,1)])
        if useDGPressure:
            preconOp = pressureScheme(preconModel==0, parameters={"penalty":20})
        else:
            preconOp = pressureScheme(preconModel==0)
    else:
        mainOp       = velocityScheme([mainModel==0,DirichletBC(spcU,exact_u,1)],
                             gradStabilization=as_vector([2*mu_,2*mu_]),
                             massStabilization=as_vector([nu_,nu_]) )
        if useDGPressure:
            preconOp = pressureScheme(preconModel==0, parameters={"penalty":20})
        else:
            preconOp = pressureScheme(preconModel==0, gradStabilization=1)
    mainOp.model.mu = mu_
    mainOp.model.nu = nu_

    gradOp      = galerkinOperator(gradModel)
    divOp       = galerkinOperator(divModel)
    massOp      = pressureScheme(massModel==0)

    A = linearOperator(mainOp)
    G = linearOperator(gradOp)
    D = linearOperator(divOp)
    M = linearOperator(massOp)
    P = linearOperator(preconOp)

    solver = {"method":"cg","tolerance":1e-10, "verbose":False}
    Ainv   = mainOp.inverseLinearOperator(A,parameters=solver)
    Minv   = massOp.inverseLinearOperator(M,parameters=solver)
    Pinv   = preconOp.inverseLinearOperator(P,solver)

    # auxiliary variables for uzawa algorithm
    rhsVelo  = velocity.copy()
    rhsPress = pressure.copy()
    r      = rhsPress.copy()
    d      = rhsPress.copy()
    precon = rhsPress.copy()
    xi     = rhsVelo.copy()

    # compute initial residual
    mainOp(velocity,rhsVelo)
    rhsVelo *= -1
    G(pressure,xi)
    rhsVelo -= xi
    mainOp.setConstraints(rhsVelo)
    mainOp.setConstraints(velocity)

    Ainv(rhsVelo, velocity)
    D(velocity,rhsPress)
    Minv(rhsPress, r)

    if uzawaPreconditioner and mainOp.model.nu > 0:
        precon.clear()
        Pinv(rhsPress, precon)
        r *= mainOp.model.mu
        r.axpy(mainOp.model.nu,precon)

    d.assign(r)
    delta = r.scalarProductDofs(rhsPress)
    print("delta:",delta,flush=True)
    assert delta >= 0

    # start iteration
    for m in range(100):
        xi.clear()
        G(d,rhsVelo)
        mainOp.setConstraints(\
            [0,]*grid.dimension, rhsVelo)
        Ainv(rhsVelo, xi)
        D(xi,rhsPress)
        rho = delta /\
           d.scalarProductDofs(rhsPress)
        pressure.axpy(rho,d)
        velocity.axpy(-rho,xi)
        D(velocity, rhsPress)
        Minv(rhsPress,r)
        if uzawaPreconditioner and mainOp.model.nu > 0:
            precon.clear()
            Pinv(rhsPress,precon)
            r *= mainOp.model.mu
            r.axpy(mainOp.model.nu,precon)
        oldDelta = delta
        delta = r.scalarProductDofs(rhsPress)
        print("delta:",delta,flush=True)
        if delta < 1e-9: break
        gamma = delta/oldDelta
        d *= gamma
        d += r
    if plot:
        velocity.plot(colorbar="horizontal")
        pressure.plot(colorbar="horizontal")
    return velocity,pressure

fig = pyplot.figure(figsize=(40,20))
order = 2
solutions = []
solutions += [compute(True, order, "TH")]
solutions[0][0].plot(figure=(fig,421),gridLines=None, colorbar=None)
solutions[0][1].plot(figure=(fig,422),gridLines=None, colorbar=None)
solutions += [compute(True, order-1, "mini")]
solutions[1][0].plot(figure=(fig,423),gridLines=None, colorbar=None)
solutions[1][1].plot(figure=(fig,424),gridLines=None, colorbar=None)
solutions += [compute(True, order, "non-conf")]
solutions[2][0].plot(figure=(fig,425),gridLines=None, colorbar=None)
solutions[2][1].plot(figure=(fig,426),gridLines=None, colorbar=None)
solutions += [compute(True, order, "SV")]
solutions[3][0].plot(figure=(fig,427),gridLines=None, colorbar=None)
solutions[3][1].plot(figure=(fig,428),gridLines=None, colorbar=None)
pyplot.tight_layout()
pyplot.show()
