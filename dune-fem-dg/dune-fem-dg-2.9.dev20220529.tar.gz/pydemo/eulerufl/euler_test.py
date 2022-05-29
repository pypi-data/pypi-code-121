#import numpy as np
##from dolfin import *
#import dolfin as dol
#
##from dolfin_dg import *
#import dolfin_dg as dg
#
#dol.parameters["ghost_mode"] = "shared_facet"
#dol.parameters['form_compiler']['representation'] = 'uflacs'
#dol.parameters['form_compiler']["quadrature_degree"] = 8
#
#run_count = 0
#ele_ns = [4, 8, 16, 32, 64]
#errorl2 = np.zeros(len(ele_ns))
#errorh1 = np.zeros(len(ele_ns))
#hsizes = np.zeros(len(ele_ns))
#p = 1
#
#for ele_n in ele_ns:
#    # Mesh and function space.
#    mesh = dol.RectangleMesh(dol.Point(0, 0), dol.Point(.5*dol.pi, .5*dol.pi), ele_n, ele_n, 'right')
#    V = dol.VectorFunctionSpace(mesh, 'DG', p, dim=4)
#
#    # Set up Dirichlet BC
#    gD = dol.Expression(('sin(2*(x[0]+x[1])) + 4',
#                     '0.2*sin(2*(x[0]+x[1])) + 4',
#                     '0.2*sin(2*(x[0]+x[1])) + 4',
#                     'pow((sin(2*(x[0]+x[1])) + 4), 2)'),
#                    element=V.ufl_element())
#
#    f = dol.Expression(('(4.0L/5.0L)*cos(2*x[0] + 2*x[1])',
#                    '(8.0L/125.0L)*(25*pow(sin(2*x[0] + 2*x[1]), 3) + 302*pow(sin(2*x[0] + 2*x[1]), 2) + 1216*sin(2*x[0] + 2*x[1]) + 1120)*cos(2*x[0] + 2*x[1])/pow(sin(2*x[0] + 2*x[1]) + 4, 2)',
#                    '(8.0L/125.0L)*(25*pow(sin(2*x[0] + 2*x[1]), 3) + 302*pow(sin(2*x[0] + 2*x[1]), 2) + 1216*sin(2*x[0] + 2*x[1]) + 1120)*cos(2*x[0] + 2*x[1])/pow(sin(2*x[0] + 2*x[1]) + 4, 2)',
#                    '(8.0L/625.0L)*(175*pow(sin(2*x[0] + 2*x[1]), 4) + 4199*pow(sin(2*x[0] + 2*x[1]), 3) + 33588*pow(sin(2*x[0] + 2*x[1]), 2) + 112720*sin(2*x[0] + 2*x[1]) + 145600)*cos(2*x[0] + 2*x[1])/pow(sin(2*x[0] + 2*x[1]) + 4, 3)'),
#                   element=V.ufl_element())
#
#    u, v = dol.interpolate(gD, V), dol.TestFunction(V)
#
#    bo = dg.CompressibleEulerOperator(mesh, V, dg.DGDirichletBC(dol.ds, gD))
#    residual = bo.generate_fem_formulation(u, v) - dol.inner(f, v)*dol.dx
#
#    dol.solve(residual == 0, u)
#
#    errorl2[run_count] = dol.errornorm(gD, u, norm_type='l2', degree_rise=3)
#    errorh1[run_count] = dol.errornorm(gD, u, norm_type='h1', degree_rise=3)
#    hsizes[run_count] = mesh.hmax()
#
#    run_count += 1
#
#if dol.MPI.rank(mesh.mpi_comm()) == 0:
#    print(np.log(errorl2[0:-1]/errorl2[1:])/np.log(hsizes[0:-1]/hsizes[1:]))
#    print(np.log(errorh1[0:-1]/errorh1[1:])/np.log(hsizes[0:-1]/hsizes[1:]))


import numpy as np
#from dolfin import *
#import dolfin as dol

import dolfin_dg as dg

#####  ????
#dol.parameters["ghost_mode"] = "shared_facet"
#dol.parameters['form_compiler']['representation'] = 'uflacs'
#dol.parameters['form_compiler']["quadrature_degree"] = 8

run_count = 0
ele_ns = [4, 8, 16, 32, 64]
errorl2 = np.zeros(len(ele_ns))
hsizes = np.zeros(len(ele_ns))
p = 1

from numpy import pi

from dune.fem.space import dglegendre
from dune.alugrid import aluCubeGrid
from dune.fem.function import uflFunction
from dune.grid import cartesianDomain
from dune.fem.scheme import galerkin as solutionScheme
from dune.fem.function import integrate

import ufl

order = 2
for ele_n in ele_ns:
    # Mesh and function space.
    domain = cartesianDomain([0, 0], [0.5*pi, 0.5*pi], [ele_n, ele_n])
    mesh   = aluCubeGrid(domain)

    V = dglegendre(mesh, dimRange = 4, storage = 'istl', order = order)


    x = ufl.SpatialCoordinate(ufl.quadrilateral)
    # Set up Dirichlet BC
    gD = uflFunction(mesh, name = "gD", order = order,
                     ufl = ufl.as_vector([ufl.sin(2*(x[0]+x[1])) + 4,
                     0.2*ufl.sin(2*(x[0]+x[1])) + 4,
                     0.2*ufl.sin(2*(x[0]+x[1])) + 4,
                     (ufl.sin(2*(x[0]+x[1])) + 4)**2]))

    f = uflFunction(mesh, name = "f", order = order,
                    ufl = ufl.as_vector([(4.0/5.0)*ufl.cos(2*x[0] + 2*x[1]),
                    (8.0/125.0)*(25*(ufl.sin(2*x[0] + 2*x[1]))**3 + 302*(ufl.sin(2*x[0] + 2*x[1]))**2 + 1216*ufl.sin(2*x[0] + 2*x[1]) + 1120)*ufl.cos(2*x[0] + 2*x[1])/(ufl.sin(2*x[0] + 2*x[1]) + 4)**2,
                    (8.0/125.0)*(25*(ufl.sin(2*x[0] + 2*x[1]))**3 + 302*(ufl.sin(2*x[0] + 2*x[1]))**2 + 1216*ufl.sin(2*x[0] + 2*x[1]) + 1120)*ufl.cos(2*x[0] + 2*x[1])/(ufl.sin(2*x[0] + 2*x[1]) + 4)**2,
                    (8.0/625.0)*(175*(ufl.sin(2*x[0] + 2*x[1]))**4 + 4199*(ufl.sin(2*x[0] + 2*x[1]))**3 + 33588*(ufl.sin(2*x[0] + 2*x[1]))**2 + 112720*ufl.sin(2*x[0] + 2*x[1]) + 145600)*ufl.cos(2*x[0] + 2*x[1])/(ufl.sin(2*x[0] + 2*x[1]) + 4)**3]))

    uh = V.interpolate(gD)
    u = ufl.TrialFunction(V)
    v = ufl.TestFunction(V)

    bo = dg.CompressibleEulerOperator(mesh, V, dg.DGDirichletBC(ufl.ds, gD))
    residual = bo.generate_fem_formulation(u, v, ufl.dx, ufl.dS) - ufl.inner(f, v)*ufl.dx

    solverParameters =\
       {"newton.tolerance": 1e-8,
        "newton.linear.tolerance": 1e-12,
        "newton.linear.preconditioning.method": "ilu",
        "newton.linear.maxiterations":1000,
        "newton.verbose": True,
        "newton.linear.verbose": True}


    scheme = solutionScheme([residual == 0], solver="gmres", parameters=solverParameters)
    scheme.solve(target = uh)

    uh.plot()

    errorl2[run_count] = np.sqrt(integrate( mesh, ufl.dot(gD - uh, gD - uh),    order=V.order*2 ))
    hmax = 0.
    for e in mesh.elements:
        vol = np.sqrt(e.geometry.volume)
        hmax = max(hmax, vol)

    hsizes[run_count] = hmax

    run_count += 1

print(np.log(errorl2[0:-1]/errorl2[1:])/np.log(hsizes[0:-1]/hsizes[1:]))
