import numpy
from dune.ufl import cell
from ufl import *
from dune.common import FieldVector
from dune.grid import reader, cartesianDomain
from dune.fem.function import gridFunction

def model(problem, dim=2, mu=0.001, **kwargs):
    cmpE = dim+1
    class Model:
        gamma = 1.4
        dimRange = dim+2
        Pr = 0.72
        Re = 1.
        # helper function
        def toPrim(U):
            v = as_vector( [U[i]/U[0] for i in range(1,dim+1)] )
            kin = dot(v,v) * U[0] / 2
            pressure = (Model.gamma-1)*(U[cmpE]-kin)
            return U[0], v, pressure
        def toCons(V):
            m = as_vector( [V[i]*V[0] for i in range(1,dim+1)] )
            kin = dot(m,m) / V[0] / 2
            rE = V[cmpE]/(Model.gamma-1) + kin
            return as_vector( [V[0],*m,rE] )

        # interface methods for model
        def F_c(t,x,U):
            rho, v, p = Model.toPrim(U)
            v = numpy.array(v)
            res = numpy.vstack([ rho*v,
                                 rho*numpy.outer(v,v) + p*numpy.eye(dim),
                                 (U[cmpE]+p)*v ])
            return as_matrix(res)
        def F_v(t,x, U, DU):
            rho  = U[0]
            rhou = as_vector([U[i] for i in range(1,dim+1)])
            rhoE = U[cmpE]
            grad_rho = DU[0, :]
            grad_rhou = as_matrix([[DU[j,:] for j in range(1, dim+1)]])[0]
            grad_rhoE = DU[cmpE,:]

            grad_u = as_matrix([[(grad_rhou[j,:]*rho - rhou[j]*grad_rho)/rho**2 for j in range(dim)]])[0]
            grad_E = (grad_rhoE*rho - rhoE*grad_rho)/rho**2

            tau = mu*(grad_u + grad_u.T - 2.0/3.0*tr(grad_u)*Identity(2))
            K_grad_T = mu*Model.gamma/Model.Pr*(grad_E - dot(rhou, grad_u)/rho)

            taum = numpy.vstack([ [*tau[i,:]] for i in range(dim)])

            return as_matrix([  [0.0]*dim,
                               *[ [*tau[i,:]] for i in range(dim) ],
                                [ dot(tau[i,:], rhou)/rho + K_grad_T[i] for i in range(dim)]
                             ])

        # interface method needed for LLF and time step control
        def maxWaveSpeed(t,x,U,n):
            rho, v, p = Model.toPrim(U)
            return abs(dot(v,n)) + sqrt(Model.gamma*p/rho)

        # interface method for viscosity time step control
        def maxDiffusion(t,x,U):
            rho, v, p = Model.toPrim(U)
            alpha = pow( Model.gamma, 1.5 ) /(Model.Re * Model.Pr)
            return mu * alpha / ( rho * 0.25 )

        def velocity(t,x,U):
            _, v ,_ = Model.toPrim(U)
            return v
        def physical(t,x,U):
            rho, _, p = Model.toPrim(U)
            return conditional( rho>1e-8, conditional( p>1e-8 , 1, 0 ), 0 )
        def jump(t,x,U,V):
            _,_, pU = Model.toPrim(U)
            _,_, pV = Model.toPrim(V)
            return (pU - pV)/(0.5*(pU + pV))

        class Indicator:
            def eta(t,x,U):
                _,_, p = Model.toPrim(U)
                return U[0]*ln(p/U[0]**Model.gamma)
            def F(t,x,U,DU):
                s = Model.Indicator.eta(t,x,U)
                _,v,_ = Model.toPrim(U)
                return v*s
            def S(t,x,U,DU):
                return 0


    x = SpatialCoordinate(cell(dim))

    if problem == "KH":
        w0    = 0.1
        sigma = 0.05/sqrt(2)
        rho   = conditional( abs(x[1]-0.5)<0.25,2,1)
        u     = conditional( abs(x[1]-0.5)<0.25,0.5,-0.5)
        v     = w0*sin(4*pi*x[0])*( exp(-(x[1]-0.25)**2/(2*sigma**2))+
                                    exp(-(x[1]-0.75)**2/(2*sigma**2)) )
        pres  = 2.5
        Model.U0 = Model.toCons([rho,u,v,pres])
        def reflect(U,n):
            n = as_vector(n)
            m = as_vector([U[1],U[2]])
            mref = m - 2*dot(m,n)*n
            return as_vector([U[0],*mref,U[3]])
        Model.boundary = {3: lambda t,x,U: reflect(U,[0,-1]),
                          4: lambda t,x,U: reflect(U,[0,1])}
        Model.domain = (reader.dgf, "kh.dgf")
        Model.endTime = 1.5

    elif problem == "SB" or problem == "SBR":
        center = 0.5
        R2 = 0.2*0.2
        gam = 1.4
        # shock
        pinf = 5
        rinf = ( 1-gam + (gam+1)*pinf )/( (gam+1) + (gam-1)*pinf )
        vinf = (1.0/sqrt(gam)) * (pinf - 1.)/ sqrt( 0.5*((gam+1)/gam) * pinf + 0.5*(gam-1)/gam);
        U_m = Model.toCons( [rinf,vinf]+(dim-1)*[0]+[pinf] )
        U_p = Model.toCons( [1]+dim*[0]+[1] )
        # vortex
        vortex = Model.toCons( [0.1]+dim*[0]+[1] )
        Model.U0 = conditional( x[0]<-0.25, U_m, conditional( dot(x,x)<R2, vortex, U_p) )

        def noFlowFlux(u,n):
            _, _, p = Model.toPrim(u)
            return as_vector([0]+[p*c for c in n]+[0])
        def rotateForth(u, n):
            if dim == 1:
                return [ u[0], n[0]*u[1], u[2] ]
            elif dim == 2:
                return [ u[0], n[0]*u[1] + n[1]*u[2], -n[1]*u[1] + n[0]*u[2], u[3] ]
            elif dim == 3:
                d = sqrt( n[0]*n[0]+n[1]*n[1] )
                d_1 = 1./d
                return [ u[0],
                         conditional(d>1e-9, n[0]*u[1] + n[1]*u[2] + n[2]*u[3], n[2] * u[3]),
                         conditional(d>1e-9,-n[1] * d_1 * u[1] + n[0] * d_1 * u[2], u[2]),
                         conditional(d>1e-9,- n[0] * n[2] * d_1 * u[1] - n[1] * n[2] * d_1 * u[2] + d * u[3], -n[2] * u[1]),
                         u[4] ]
        def rotateBack(u, n):
            if dim == 1:
                return [ u[0], n[0]*u[1], u[2] ]
            elif dim == 2:
                return [ u[0], n[0]*u[1] - n[1]*u[2],  n[1]*u[1] + n[0]*u[2], u[3] ]
            elif dim == 3: # assumption n[0]==0
                d = sqrt( n[0]*n[0]+n[1]*n[1] )
                d_1 = 1./d
                return [ u[0],
                         conditional(d>1e-9, n[0] * u[1] - n[1]*d_1 * u[2] - n[0]*n[2]*d_1 * u[3], -n[2]*u[3]),
                         conditional(d>1e-9, n[1] * u[1] + n[0]*d_1 * u[2] - n[1]*n[2]*d_1 * u[3], u[2]),
                         conditional(d>1e-9, n[2] * u[1] + d * u[3], n[2]*u[1]),
                         u[4] ]
        def reflect(u,n):
            uRot = rotateForth(u, n)
            uRot[ 1 ] = -uRot[ 1 ]
            return as_vector( rotateBack(uRot, n) )

        Model.boundary = {1: lambda t,x,u: U_m,
                          2: lambda t,x,u: U_p,
                          3: lambda t,x,u,n,k: reflect(u,n)}

        if problem == "SBR":
            def source(t,x,U,DU):
                _, v, p = Model.toPrim(U)
                return as_vector([ - U[0]   *v[1]/x[1],
                                   - U[1]   *v[1]/x[1],
                                   - U[2]   *v[1]/x[1],
                                   -(U[3]+p)*v[1]/x[1] ])
            Model.S_e = source
            def indicatorSource(t,x,U,DU):
                s = Model.Indicator.eta(t,x,U)
                _,v,_ = Model.toPrim(U)
                return - s * v[1]/x[1]
            Model.Indicator.S = indicatorSource

        Model.domain = (reader.dgf, "shockvortex"+str(dim)+"d.dgf")
        Model.endTime = 0.5

    elif problem == "RP":
        Vl = kwargs["Vl"]
        Vr = kwargs["Vr"]
        Model.endTime = kwargs["endTime"]
        x0 = 0.5
        def riemanProblem(Model,x,x0,VL,VR):
          return Model.toCons( conditional(x<x0,as_vector(VL),as_vector(VR)) )
        Model.domain=(reader.dgf, "unitsquare.dgf")
        Model.U0=riemanProblem( Model, x[0], x0, Vl, Vr)
        def rotateForth(u, n):
            return [ u[0], n[0]*u[1] + n[1]*u[2], -n[1]*u[1] + n[0]*u[2], u[3] ]
        def rotateBack(u, n):
            return [ u[0], n[0]*u[1] - n[1]*u[2],  n[1]*u[1] + n[0]*u[2], u[3] ]
        def reflect(t,x,u,n,k):
            uRot = rotateForth(u, n)
            uRot[ 1 ] = -uRot[ 1 ]
            return as_vector( rotateBack(uRot, n) )
        Model.boundary = {range(5): lambda t,x,u,n,k: conditional(x[0]<1e-5,Model.toCons(Vl),
                                      conditional(x[0]>1-1e-5,Model.toCons(Vr),
                                        reflect(t,x,u,n,k) )) }
        def chorin(gv,t):
            gf = gv.function("chorin","chorin.hh", Vl,Vr,Model.gamma,x0,t,name="chorin")
            lgf = gf.localFunction()
            @gridFunction(gv,"sod",3)
            def lf(e,x):
               lgf.bind(e)
               return FieldVector( Model.toCons(lgf(x)) )
            return lf
        Model.exact = lambda gv,t: chorin(gv,t)

    return Model
