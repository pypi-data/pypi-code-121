from math import sqrt
from dune.femdg import femDGOperator, rungeKuttaSolver, dgHelmholtzInverseOperator

class FemDGStepper:
    def __init__(self,op,parameters):
        if parameters is None:
            self.rkScheme = rungeKuttaSolver( op )
        else:
            self.rkScheme = rungeKuttaSolver( op, parameters=parameters )
    def __call__(self,u,dt=None):
        if dt is not None:
            self.rkScheme.setTimeStepSize(dt)
        self.rkScheme.solve(u)
        return self.rkScheme.deltaT()
    @property
    def deltaT(self):
        return self.rkScheme.deltaT()
    @deltaT.setter
    def deltaT(self,dt):
        self.rkScheme.setTimeStepSize(dt)

def femdgStepper(*,order=None,rkType=None,operator=None,cfl=0.45,parameters=True):
    if parameters is True: parameters = {}
    elif parameters is False: parameters = None
    if rkType == "default": rkType = None
    def _femdgStepper(op,cfl=None):
        if parameters is not None:
            if not "fem.timeprovider.factor" in parameters:
                if cfl is not None:
                    parameters["fem.timeprovider.factor"] = cfl
                else:
                    parameters["fem.timeprovider.factor"] = 0.45
            if not "fem.ode.odesolver" in parameters:
                if rkType is not None:
                    parameters["fem.ode.odesolver"] = rkType
                elif op._hasAdvFlux and op._hasDiffFlux:
                    parameters["fem.ode.odesolver"] = "IMEX"
                elif op._hasAdvFlux:
                    parameters["fem.ode.odesolver"] = "EX"
                else:
                    parameters["fem.ode.odesolver"] = "IM"
            if not "fem.ode.order" in parameters:
                assert order is not None, "need to pass the order of the rk method to the 'femDGStepper' as argument or set it in the parameters"
                parameters["fem.ode.order"] = order
            if not "fem.ode.maxiterations" in parameters:
                parameters["fem.ode.maxiterations"] = 100 # the default (16) seems to lead to very small time steps
        return FemDGStepper(op,parameters)
    if operator is None:
        return _femdgStepper
    else:
        return _femdgStepper(operator,cfl)

# Set up problem: L[baru+a*k] - k = 0
class HelmholtzButcher:
    def __init__(self, op, parameters = {}, useScipy = False ):
        self.op = op
        self._alpha = None
        self.arg = op.space.interpolate(op.space.dimRange*[0],name="HelmholtzButcher::arg")
        self._invOp = None
        if useScipy:
            self.res = op.space.interpolate(op.space.dimRange*[0],name="HelmholtzButcher::res")
            def f(x_coeff):
                """
                Implements: L[baru+a*k] - k = 0
                """
                # interpret x_coeff as discrete function
                k = self.op.space.function("HelmholtzButcher::f::k", dofVector=x_coeff)
                self.arg.assign( self.baru )
                self.arg.axpy( self.alpha, k )
                self.op(self.arg, self.res)
                self.res -= k
                return self.res.as_numpy
            self.f = f
        else:
            self._invOp = dgHelmholtzInverseOperator( self.op._op, self.arg, parameters )

        self.counter = 0
        self.inner_counter = 0
    @property
    def alpha(self):
        return self._alpha
    @alpha.setter
    def alpha(self,value):
        self._alpha = value

    def dot(self, x_coeff, y_coeff):
        # convert to discrete functions
        x = self.op.space.function("dot::x", dofVector=x_coeff)
        y = self.op.space.function("dot::y", dofVector=y_coeff)
        return x.scalarProductDofs( y )

    def nrm2(self, x ):
        x = self.op.space.function("nrm2::x", dofVector=x_coeff)
        return x.scalarProductDofs( x )

    def solve(self, baru, target):
        if self._invOp:
            # prepare right hand side
            self.op( baru, self.arg )
            info = self._invOp.solve( self.arg, target, self.alpha )
            self.counter = info["iterations"]
            self.inner_counter = info["linear_iterations"]
        else:
            from scipy.optimize import newton_krylov
            counter = 0
            inner_counter = 0
            def callb(x,Fx): nonlocal counter;       counter+=1
            def icallb(rk):  nonlocal inner_counter; inner_counter+=1
            self.baru = baru

            sol_coeff = target.as_numpy
            sol_coeff[:] = newton_krylov(self.f, sol_coeff,
                                         verbose=False,
                                         callback=callb, inner_callback=icallb)
            self.counter = counter
            self.inner_counter = inner_counter # linear iterations not correct


# Set up problem: rhs + a*L[y] - y = 0
class HelmholtzShuOsher:
    def __init__(self,op, parameters={}, useScipy = False ):
        self.op = op
        self._alpha = None
        self._nonlinsolve = None
        self.res = op.space.interpolate(op.space.dimRange*[0],name="HelmholtzShuOsher::res")
        self._invOp = None
        if useScipy:
            def f(x_coeff):
                # interpret x_coeff as discrete function
                xtmp = self.op.space.function("x_tmp", dofVector=x_coeff)
                # apply operator
                self.op(xtmp, self.res)
                # compute alpha*res -x + rhs (by calling routines on discrete functions)
                self.res *= self.alpha
                self.res -= xtmp
                self.res += self.rhs
                return self.res.as_numpy
            self.f = f
        else:
            self._invOp = dgHelmholtzInverseOperator( self.op, self.res, parameters )
            # not needed anymore
            del self.res
            self.res = None

        self.counter = 0
        self.inner_counter = 0
    @property
    def alpha(self):
        return self._alpha
    @alpha.setter
    def alpha(self,value):
        self._alpha = value

    def solve(self,rhs,target):
        if self._invOp:
            # dummy preconditioner doing nothing
            #def pre(u,v):
            #    # print("Pre: ", u.name, v.name )
            #    v.assign( u )
            #    return
            # dummy updatePreconditioner doing nothing
            #def updatePre( ubar ):
            #    print("Update pre: ", ubar.name)
            #    return
            #info = self._invOp.preconditionedSolve( pre, updatePre, rhs, target, self.alpha )

            # tol = 1e-5
            info = self._invOp.solve( rhs, target, self.alpha ) #, tol )
            self.counter = info["iterations"]
            self.inner_counter = info["linear_iterations"]
        else:
            from scipy.optimize import newton_krylov
            counter = 0
            inner_counter = 0
            def callb(x,Fx): nonlocal counter;       counter+=1
            def icallb(rk):  nonlocal inner_counter; inner_counter+=1
            self.rhs = rhs

            sol_coeff = target.as_numpy
            sol_coeff[:] = newton_krylov(self.f, sol_coeff,
                        verbose=False,
                        callback=callb, inner_callback=icallb)
            self.counter = counter
            self.inner_counter = inner_counter # linear iterations not correct

class RungeKutta:
    def __init__(self,op,cfl, A, b, c, *args, **kwargs ):
        self.op = op
        self.A = A
        self.b = b
        self.c = c
        self.stages = len(b)
        self.cfl = cfl
        self.dt = None
        self.k = self.stages*[None]
        for i in range(self.stages):
            self.k[i] = op.space.interpolate(op.space.dimRange*[0],name="k")
        self.tmp = op.space.interpolate(op.space.dimRange*[0],name="tmp")
        self.explicit = all([abs(A[i][i])<1e-15 for i in range(self.stages)])
        self.computeStages = self.explicitStages if self.explicit else self.implicitStages
        if not self.explicit:
            self.helmholtz = HelmholtzButcher(self.op, *args, **kwargs)

    def explicitStages(self,u,dt=None):
        assert self.explicit, "call method was setup wrong"

        assert abs(self.c[0])<1e-15
        self.op.stepTime(0,0)
        self.op(u,self.k[0])
        if dt is None and self.dt is None:
            dt = self.op.localTimeStepEstimate[0]*self.cfl
        elif dt is None:
            dt = self.dt
        self.dt = 1e10
        for i in range(1,self.stages):
            self.tmp.assign(u)
            for j in range(i):
                self.tmp.axpy(dt*self.A[i][j],self.k[j])
            self.op.stepTime(self.c[i],dt)
            self.op(self.tmp,self.k[i])
            self.dt = min(self.dt, self.op.localTimeStepEstimate[0]*self.cfl)

    def implicitStages(self,u,dt=None):
        assert not self.explicit, "call method was setup wrong"
        if dt is None and self.dt is None:
            self.op.stepTime(0,0)
            self.op(u,self.k[0])
            dt = self.op.localTimeStepEstimate[0]*self.cfl
        elif dt is None:
            dt = self.dt
        self.dt = 1e10
        for i in range(0,self.stages):
            self.tmp.assign(u)
            for j in range(i):
                self.tmp.axpy(dt*self.A[i][j],self.k[j])
            self.op.stepTime(self.c[i],dt)
            self.op(self.tmp,self.k[i]) # this seems like a good initial guess for dt small
            self.dt = min(self.dt, self.op.localTimeStepEstimate[0]*self.cfl)
            self.helmholtz.alpha = dt*self.A[i][i]
            self.helmholtz.solve(baru=self.tmp,target=self.k[i])

    def __call__(self,u,dt=None):
        # compute stages
        self.computeStages(u,dt)

        for i in range(self.stages):
            u.axpy(dt*self.b[i],self.k[i])
        self.op.applyLimiter( u )
        self.op.stepTime(0,0)
        return self.op.space.gridView.comm.min(dt)

class Heun(RungeKutta):
    def __init__(self, op, cfl=None):
        A = [[0,0],
             [1,0]]
        b = [0.5,0.5]
        c = [0,1]
        cfl = 0.45 if cfl is None else cfl
        RungeKutta.__init__(self,op,cfl,A,b,c)
# The following seems an inefficient implementation in the sense that it
# converges very slowly - there is a better implementation below using a
# Shu-Osher form of the method - the dune-fem implementation of DIRK also
# uses some transformation of the Butcher tableau which could be
# reimplemented here.
# A lot about DIRK - worth looking into more closely
# https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/20160005923.pdf

class ExplEuler(RungeKutta):
    def __init__(self, op, cfl=None, *args, **kwargs):
        A = [[0.]]
        b = [1.]
        c = [0.]
        cfl = 0.45 if cfl is None else cfl
        RungeKutta.__init__(self,op,cfl,A,b,c, *args, **kwargs)
class ImplEuler(RungeKutta):
    def __init__(self, op, cfl=None, *args, **kwargs):
        A = [[1.]]
        b = [1]
        c = [1.]
        cfl = 0.45 if cfl is None else cfl
        RungeKutta.__init__(self,op,cfl,A,b,c, *args, **kwargs)


def euler(explicit=True):
    if explicit:
        return lambda op,cfl=None, *args, **kwargs: ExplEuler(op,cfl, *args, **kwargs)
    else:
        return lambda op,cfl=None, *args, **kwargs: ImplEuler(op,cfl, *args, **kwargs)



######################################################################
##
## Explicit/Implicit SSP-2
##
######################################################################
# Implemented using ImplSSP2 with s=1
#class Midpoint(RungeKutta):
#    def __init__(self, op, cfl=None):
#        A = [[0.5]]
#        b = [1]
#        c = [0.5]
#        cfl = 0.45 if cfl is None else cfl
#        RungeKutta.__init__(self,op,cfl,A,b,c)


class ImplSSP2: # with stages=1 same as above - increasing stages does not improve anything
    def __init__(self,stages,op,cfl=None, *args, **kwargs):

        self.stages = stages
        self.op     = op

        self.mu11   = 1/(2*stages)
        self.mu21   = 1/(2*stages)
        self.musps  = 1/(2*stages)
        self.lamsps = 1

        self.q2     = op.space.interpolate(op.space.dimRange*[0],name="q2")
        self.tmp    = self.q2.copy()
        self.cfl    = 0.45 if cfl is None else cfl
        self.dt     = None
        self.helmholtz = HelmholtzShuOsher(self.op, *args, **kwargs)
    def c(self,i):
        return i/(2*self.stages)
    def __call__(self,u,dt=None):
        if dt is None and self.dt is None:
            self.op.stepTime(0,0)
            self.op(u, self.tmp)
            dt = self.op.localTimeStepEstimate[0]*self.cfl
        elif dt is None:
            dt = self.dt
        self.dt = 1e10
        self.helmholtz.alpha = dt*self.mu11

        self.q2.assign(u)
        self.op.stepTime(self.c(1),dt)
        self.helmholtz.solve(u,self.q2) # first stage
        for i in range(2,self.stages+1):
            self.op.stepTime(self.c(i),dt)
            self.op(self.q2, self.tmp)
            self.dt = min(self.dt, self.op.localTimeStepEstimate[0]*self.cfl)
            self.q2.axpy(dt*self.mu21, self.tmp)
            self.helmholtz.solve(self.q2,self.tmp)
            self.q2.assign(self.tmp)
        u *= (1-self.lamsps)
        u.axpy(self.lamsps, self.q2)
        self.op(self.q2, self.tmp)
        self.dt = min(self.dt, self.op.localTimeStepEstimate[0]*self.cfl)
        u.axpy(dt*self.musps, self.tmp)
        self.op.applyLimiter( u )
        self.op.stepTime(0,0)
        return self.op.space.gridView.comm.min(dt)

class ExplSSP2:
    def __init__(self,stages,op,cfl=None, *args, **kwargs):
        self.op     = op
        self.stages = stages
        self.q2     = op.space.interpolate(op.space.dimRange*[0],name="q2")
        self.tmp    = self.q2.copy()
        self.cfl    = 0.45 * (stages-1)
        self.dt     = None
    def c(self,i):
        return (i-1)/(self.stages-1)
    def __call__(self,u,dt=None):
        if dt is None and self.dt is None:
            self.op.stepTime(0,0)
            self.op(u, self.tmp)
            dt = self.op.localTimeStepEstimate[0]*self.cfl
        elif dt is None:
            dt = self.dt
        self.dt = 1e10
        fac = dt/(self.stages-1)
        self.q2.assign(u)
        for i in range(1,self.stages):
            self.op.stepTime(self.c(i),dt)
            self.op(u,self.tmp)
            self.dt = min(self.dt, self.op.localTimeStepEstimate[0]*self.cfl)
            u.axpy(fac, self.tmp)
        self.op.stepTime(self.c(i),dt)
        self.op(u,self.tmp)
        self.dt = min(self.dt, self.op.localTimeStepEstimate[0]*self.cfl)
        u *= (self.stages-1)/self.stages
        u.axpy(dt/self.stages, self.tmp)
        u.axpy(1/self.stages, self.q2)
        self.op.applyLimiter( u )
        self.op.stepTime(0,0)
        return self.op.space.gridView.comm.min(dt)


def ssp2(stages,explicit=True):
    if explicit:
        return lambda op,cfl=None, *args, **kwargs: ExplSSP2(stages,op,cfl, *args, **kwargs)
    else:
        return lambda op,cfl=None, *args, **kwargs: ImplSSP2(stages,op,cfl, *args, **kwargs)

# MidPoint rule using ImplSSP2 with s=1
class Midpoint(ImplSSP2):
    def __init__(self, op, cfl=None, *args, **kwargs):
        # create ImplSSP2 with stages s=1
        super().__init__(1, op, cfl=cfl, *args, **kwargs)


######################################################################
##
## Explicit/Implicit SSP-3
##
######################################################################
# optimal low storage methods:
# http://www.sspsite.org
# https://arxiv.org/pdf/1605.02429.pdf
# https://openaccess.leidenuniv.nl/bitstream/handle/1887/3295/02.pdf?sequence=7
# https://epubs.siam.org/doi/10.1137/07070485X
# implicit: https://www.sciencedirect.com/science/article/abs/pii/S0168927408000688
class ExplSSP3:
    def __init__(self,stages,op,cfl=None, *args, **kwargs):
        self.op     = op
        self.n      = int(sqrt(stages))
        self.stages = self.n*self.n
        assert self.stages == stages, "doesn't work if sqrt(s) is not integer"
        self.r      = self.stages-self.n
        self.q2     = op.space.interpolate(op.space.dimRange*[0],name="q2")
        self.tmp    = self.q2.copy()
        self.cfl    = 0.45 * stages*(1-1/self.n) if cfl is None else cfl
        self.dt     = None
    def c(self,i):
        return (i-1)/(self.n*self.n-self.n) \
               if i<=(self.n+2)*(self.n-1)/2+1 \
               else (i-self.n-1)/(self.n*self.n-self.n)
    def __call__(self,u,dt=None):
        if dt is None and self.dt is None:
            self.op.stepTime(0,0)
            self.op(u, self.tmp)
            dt = self.op.localTimeStepEstimate[0]*self.cfl
        elif dt is None:
            dt = self.dt
        self.dt = 1e10
        fac = dt/self.r
        i = 1
        while i <= (self.n-1)*(self.n-2)/2:
            self.op.stepTime(self.c(i),dt)
            self.op(u,self.tmp)
            self.dt = min(self.dt, self.op.localTimeStepEstimate[0]*self.cfl)
            u.axpy(fac, self.tmp)
            i += 1
        self.q2.assign(u)
        while i <= self.n*(self.n+1)/2:
            self.op.stepTime(self.c(i),dt)
            self.op(u,self.tmp)
            self.dt = min(self.dt, self.op.localTimeStepEstimate[0]*self.cfl)
            u.axpy(fac, self.tmp)
            i += 1
        u *= (self.n-1)/(2*self.n-1)
        u.axpy(self.n/(2*self.n-1), self.q2)
        while i <= self.stages:
            self.op.stepTime(self.c(i),dt)
            self.op(u,self.tmp)
            self.dt = min(self.dt, self.op.localTimeStepEstimate[0]*self.cfl)
            u.axpy(fac, self.tmp)
            i += 1
        self.op.applyLimiter( u )
        self.op.stepTime(0,0)
        return self.op.space.gridView.comm.min(dt)


class ImplSSP3:
    def __init__(self,stages,op,cfl=None, *args, **kwargs):
        self.stages = stages
        self.op     = op

        self.mu11   = 0.5*( 1 - sqrt( (stages-1)/(stages+1) ) )
        self.mu21   = 0.5*( sqrt( (stages+1)/(stages-1) ) - 1 )
        q           = stages*(stages+1+sqrt(stages*stages-1))
        self.musps  = (stages+1)/q
        self.lamsps = (stages+1)/q*(stages-1+sqrt(stages*stages-1))

        self.q2     = op.space.interpolate(op.space.dimRange*[0],name="q2")
        self.tmp    = self.q2.copy()
        self.cfl    = 0.45 * (stages-1+sqrt(stages*stages-1)) if cfl is None else cfl
        self.dt     = None
        self.helmholtz = HelmholtzShuOsher(self.op, *args, **kwargs)
    def c(self,i):
        assert False, "not yet implemented"
    def __call__(self,u,dt=None):
        # y_1 = u + dt mu_{i,i-1}L[y_{i-1}]
        # y_i = y_{i-1} + dt mu_{i,i-1}L[y_{i-1}] + dt mu_{i,i}L[y_i]   i>1
        # or
        # (1 - dt mu_{ii} L)y_1 = u
        # (1 - dt mu_{ii} L)y_i = (1 + dt * mu_{i,i-1} L)y_{i-1}        i>1
        # and u = (1-lamsps)u + (lamsps + dt musps L)y_s

        if dt is None and self.dt is None:
            # self.op.stepTime(0,0)
            self.op(u, self.tmp)
            dt = self.op.localTimeStepEstimate[0]*self.cfl
        elif dt is None:
            dt = self.dt
        self.dt = 1e10
        self.helmholtz.alpha = dt*self.mu11

        # self.op.stepTime(self.c(1),dt)
        self.helmholtz.solve(u,self.q2) # first stage
        for i in range(2,self.stages+1):
            # self.op.stepTime(self.c(i),dt)
            self.op(self.q2, self.tmp)
            self.dt = min(self.dt, self.op.localTimeStepEstimate[0]*self.cfl)
            self.q2.axpy(dt*self.mu21, self.tmp)
            self.helmholtz.solve(self.q2,self.tmp)
            self.q2.assign(self.tmp)
        u *= (1-self.lamsps)
        u.axpy(self.lamsps, self.q2)
        self.op(self.q2, self.tmp)
        self.dt = min(self.dt, self.op.localTimeStepEstimate[0]*self.cfl)
        u.axpy(dt*self.musps, self.tmp)
        self.op.applyLimiter( u )
        self.op.stepTime(0,0)
        return self.op.space.gridView.comm.min(dt)


def ssp3(stages,explicit=True):
    if explicit:
        return lambda op,cfl=None, *args, **kwargs: ExplSSP3(stages,op,cfl, *args, **kwargs)
    else:
        return lambda op,cfl=None, *args, **kwargs: ImplSSP3(stages,op,cfl, *args, **kwargs)

######################################################################
##
## Explicit SSP-4-10
##
######################################################################
class ExplSSP4_10:
    def __init__(self, op,cfl=None, *args, **kwargs):
        self.op     = op
        self.stages = 10
        self.q2     = op.space.interpolate(op.space.dimRange*[0],name="q2")
        self.tmp    = self.q2.copy()
        self.cfl    = 0.45 * self.stages*0.6 if cfl is None else cfl
        self.dt     = None
    def c(self,i):
        return (i-1)/6 if i<=5 else (i-4)/6
    def __call__(self,u,dt=None):
        if dt is None and self.dt is None:
            self.op.stepTime(0,0)
            self.op(u, self.tmp)
            dt = self.op.localTimeStepEstimate[0]*self.cfl
        elif dt is None:
            dt = self.dt
        self.dt = 1e10

        i = 1
        self.q2.assign(u)
        while i <= 5:
            self.op.stepTime(self.c(i), dt)
            self.op(u, self.tmp)
            self.dt = min(self.dt, self.op.localTimeStepEstimate[0]*self.cfl)
            u.axpy(dt/6, self.tmp)
            i += 1

        self.q2 *= 1/25
        self.q2.axpy(9/25, u)
        u *= -5
        u.axpy(15, self.q2)

        while i <= 9:
            self.op.stepTime(self.c(i), dt)
            self.op(u, self.tmp)
            self.dt = min(self.dt, self.op.localTimeStepEstimate[0]*self.cfl)
            u.axpy(dt/6, self.tmp)
            i += 1

        self.op.stepTime(self.c(i), dt)
        self.op(u, self.tmp)
        self.dt = min(self.dt, self.op.localTimeStepEstimate[0]*self.cfl)
        u *= 3/5
        u.axpy(1, self.q2)
        u.axpy(dt/10, self.tmp)
        self.op.applyLimiter( u )
        self.op.stepTime(0,0)
        return self.op.space.gridView.comm.min(dt)
