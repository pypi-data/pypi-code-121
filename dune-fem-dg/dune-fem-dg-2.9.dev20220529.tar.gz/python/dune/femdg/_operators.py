from __future__ import absolute_import, division, print_function, unicode_literals

import sys, hashlib
import logging
logger = logging.getLogger(__name__)
from io import StringIO

from dune.typeregistry import generateTypeName
from dune.generator import Constructor, Method
from dune.generator.importclass import load as classLoad
from dune.common.hashit import hashIt
from dune.fem.operator import load
from dune.fem import parameter as parameterReader
import dune.fem

from dune.ufl import Constant
from dune.ufl.tensors import ExprTensor
from dune.ufl.codegen import generateCode, generateMethodBody, generateMethod

from dune.source.cplusplus import assign, construct, TypeAlias, Declaration, Variable,\
        UnformattedBlock, UnformattedExpression, Struct, return_,\
        SwitchStatement
from dune.source.cplusplus import Method as clsMethod
from dune.source.cplusplus import SourceWriter, ListWriter, StringWriter

from ufl import SpatialCoordinate,TestFunction,TrialFunction,Coefficient,\
        as_vector, as_matrix,dx,ds,grad,inner,zero,FacetNormal,dot
from ufl.algorithms.analysis import extract_arguments_and_coefficients as coeff
from ufl.differentiation import Grad


# limiter can be ScalingLimiter or FV based limiter with FV type reconstructions for troubled cells
def createLimiter(domainSpace, rangeSpace=None, bounds = [1e-12,1.], limiter='scaling'):
    if rangeSpace is None:
        rangeSpace = domainSpace

    domainSpaceType = domainSpace.cppTypeName
    rangeSpaceType = rangeSpace.cppTypeName

    _, domainFunctionIncludes, domainFunctionType, _, _, _ = domainSpace.storage
    _, rangeFunctionIncludes, rangeFunctionType, _, _, _ = rangeSpace.storage

    includes = ["dune/fem-dg/operator/limiter/limiter.hh"]
    includes += domainSpace.cppIncludes + domainFunctionIncludes
    includes += rangeSpace.cppIncludes + rangeFunctionIncludes

    typeName = 'Dune::Fem::ScalingLimiter< ' + domainFunctionType + ', ' + rangeFunctionType + ' >'
    # FV type limiter where FV based reconstructions are done
    if limiter == 'fv':
        typeName = 'Dune::Fem::Limiter< ' + domainFunctionType + ', ' + rangeFunctionType + ' >'

    constructor = Constructor(['const '+domainSpaceType + ' &dSpace, const '+rangeSpaceType + ' &rSpace, double lower,double upper'],
                              ['return new ' + typeName + '(dSpace,rSpace,lower,upper );'],
                              ['"dSpace"_a', '"rSpace"_a', '"lower"_a', '"upper"_a',
                               'pybind11::keep_alive< 1, 2 >()', 'pybind11::keep_alive< 1, 3 >()'])

    # add method activated to inspect limited cells.
    activated = Method('activated', '&'+typeName+'::activated')

    return load(includes, typeName, constructor, activated).Operator( domainSpace, rangeSpace, bounds[0], bounds[1] )

# new method name, only is kept for convenience
def limiter(domainSpace, rangeSpace=None, bounds = [1e-12,1.], limiter='scaling'):
    return createLimiter( domainSpace, rangeSpace, bounds, limiter )

def createOrderRedcution(domainSpace):

    domainSpaceType = domainSpace.cppTypeName

    _, domainFunctionIncludes, domainFunctionType, _, _, _ = domainSpace.storage

    includes = ["dune/fem-dg/operator/common/orderreduction.hh"]
    includes += domainSpace.cppIncludes + domainFunctionIncludes

    typeName = 'Dune::Fem::OrderReduction< ' + domainFunctionType + ' >'

    constructor = Constructor(['const '+domainSpaceType + ' &dSpace'],
                              ['return new ' + typeName + '(dSpace);'],
                              ['"dSpace"_a','pybind11::keep_alive< 1, 2 >()'])

    # add method maxRelevantOrder to get max order that is relevant per cell
    # maxRelevantOrder = Method('maxRelevantOrder', '&'+typeName+'::maxRelevantOrder')

    # return load(includes, typeName, constructor, maxRelevantOrder).Operator( domainSpace )
    return load(includes, typeName, constructor).Operator( domainSpace )

#####################################################
## fem-dg models
#####################################################
from dune.femdg.patch import transform
def femDGModels(Model, space, initialTime=0):

    u = TrialFunction(space)
    v = TestFunction(space)
    n = FacetNormal(space.cell())
    x = SpatialCoordinate(space.cell())
    t = Constant(initialTime,"time")

    hasAdvFlux = hasattr(Model,"F_c")
    if hasAdvFlux:
        advModel = inner(Model.F_c(t,x,u),grad(v))*dx   # -div F_c v
    else:
        advModel = inner(t*grad(u-u),grad(v))*dx    # TODO: make a better empty model
    hasNonStiffSource = hasattr(Model,"S_e")
    if hasNonStiffSource:
        advModel += inner(as_vector(Model.S_e(t,x,u,grad(u))),v)*dx   # (-div F_v + S_e) * v
    else:
        hasNonStiffSource = hasattr(Model,"S_ns")
        if hasNonStiffSource:
           advModel += inner(as_vector(Model.S_ns(t,x,u,grad(u))),v)*dx   # (-div F_v + S_ns) * v
           print("Model.S_ns is deprecated. Use S_e instead!")

    hasDiffFlux = hasattr(Model,"F_v")
    if hasDiffFlux:
        diffModel = inner(Model.F_v(t,x,u,grad(u)),grad(v))*dx
    else:
        diffModel = inner(t*grad(u-u),grad(v))*dx   # TODO: make a better empty model

    hasStiffSource = hasattr(Model,"S_i")
    if hasStiffSource:
        diffModel += inner(as_vector(Model.S_i(t,x,u,grad(u))),v)*dx
    else:
        hasStiffSource = hasattr(Model,"S_s")
        if hasStiffSource:
            diffModel += inner(as_vector(Model.S_impl(t,x,u,grad(u))),v)*dx
            print("Model.S_s is deprecated. Use S_i instead!")

    from dune.fem.model import conservationlaw
    #from dune.fem.model import integrands as conservationlaw
    virtualize = False

    advModel  = conservationlaw(space.gridView, advModel,
                                modelPatch=transform(Model,space,t,"Adv"),
                                virtualize=virtualize)

    diffModel = conservationlaw(space.gridView, diffModel,
                                modelPatch=transform(Model,space,t,"Diff"),
                                virtualize=virtualize)

    Model._ufl = {"u":u,"v":v,"n":n,"x":x,"t":t}

    return [Model,advModel,diffModel]

#####################################################
## fem-dg Operator
#####################################################
# create DG operator + solver (limiter = none,default,minmod,vanleer,superbee,lp,scaling),
# (diffusionScheme = cdg2,cdg,br2,ip,nipg,bo)
def femDGOperator(Model, space,
        limiter="default",
        advectionFlux="default",
        diffusionScheme = "cdg2",
        threading="default",
        defaultQuadrature=True,
        codegen=True,
        initialTime=0.0, parameters=None):
    """ create DG operator + ODE solver

    Args:
        Model: analytical model describing the PDE and auxiliary functionality
        space: discrete function space (DG space)
        limiter: choice of limiter stabilization, possible values are
                 none,default,minmod,vanleer,superbee,lp,scaling
        advectionFlux: choice of numerical flux for advective parts
                    default is local Lax-Friedrichs
        diffusionScheme: choice of numerical flux for diffusive parts
                possible choices are cdg2(default),cdg,br2,ip,nipg,bo
        threading: enable shared memory parallelization - default is that
                threading is turned on if `dune.fem.threading.use>1`
        defaultQuadrature: use quadratures that generically fit to the space
        codegen: enable optimized code for evaluation and interpolation
        initialTime: T_0, default is 0.0
        parameters: Additional parameter passed to the DG operator, limiter and ODE solvers
    Returns:
        DGOperator
    """

    includes = []

    # obtain information about limiter interface before Model
    # is augmented with default implementations
    hasScalingInterface = hasattr(Model,"lowerBound") or hasattr(Model,"upperBound") or hasattr(Model,"physical")
    hasLimiterInterface = (hasattr(Model,"jump") and hasattr(Model,"velocity")) or hasattr(Model,"physical")

    if threading == "default":
        threading = dune.fem.threading.use>1

    if type(Model)==list or type(Model)==tuple:
        advModel = Model[1]
        diffModel = Model[2]
        Model = Model[0]
    else:
        Model, advModel, diffModel = femDGModels(Model,space,initialTime)

    hasAdvFlux = hasattr(Model,"F_c")
    hasDiffFlux = hasattr(Model,"F_v")
    hasStiffSource = hasattr(Model,"S_i") or hasattr(Model,"S_s")
    hasNonStiffSource = hasattr(Model,"S_e") or hasattr(Model,"S_ns")

    virtualize = False

    defaultLimiter = limiter == "default"

    if limiter is None or limiter is False:
        limiter = "unlimited"

    if type(limiter) in [list,tuple]:
        limiterIndicator = limiter[1]
        limiter = limiter[0]
    else:
        limiterIndicator = None

    limiterstr = limiter
    if limiter.lower() == "default":
        # check for limiter interface implementation
        if not hasLimiterInterface:
            print("\nfemDGOperator: Limiter selected but limiter interface (jump,velocity,physical) missing in Model!", flush=True)
            print("femDGOperator: Falling back to unlimited!\n", flush=True)
            limiter = "unlimited"
        else:
            # default is minmod which can be either lp-minmod or muscl-minmod
            limiter = "minmod"
            limiterstr = limiter if space.gridView.type.isSimplex else "lp"
            # force default values for how reconstruction is done
            if parameters is None:
                parameterReader.append({"femdg.limiter.admissiblefunctions":"default"})
            else:
                parameters["femdg.limiter.admissiblefunctions"] = "default"

    if limiter.lower() == "lp":
        limiter = "minmod"
        # force default values for how reconstruction is done
        if parameters is None:
            parameterReader.append({"femdg.limiter.admissiblefunctions":"lp"})
        else:
            parameters["femdg.limiter.admissiblefunctions"] = "lp"

    if limiter.lower() == "scaling":
        # check for scaling limiter interface
        if not hasScalingInterface:
            raise KeyError(\
              "femDGOperator: ScalingLimiter selected but scaling limiter interface (lowerBound,upperBound,physical) missing in Model!\n")
    elif limiter.lower() != "unlimited":
        # check for limiter interface
        if not hasLimiterInterface:
            raise KeyError(\
              "femDGOperator: MUSCL type stabilization selected but limiter interface (jump,velocity,physical) missing in Model!\n")

    if space.gridView.comm.rank == 0:
        limiterstr = "default(" + limiterstr + ")" if defaultLimiter else limiterstr
        print("femDGOperator: Limiter =",limiterstr)

    # TODO: does this make sense - if there is no diffusion then it doesn't
    # matter and with diffusion using 'none' seems a bad idea?
    if diffusionScheme is None or diffusionScheme is False:
        diffusionScheme = "none"

    spaceType = space.cppTypeName

    if virtualize:
        modelType = "DiffusionModel< " +\
              "typename " + spaceType + "::GridPartType, " +\
              spaceType + "::dimRange, " +\
              spaceType + "::dimRange, " +\
              "typename " + spaceType + "::RangeFieldType >"
        advModelType  = modelType
        diffModelType = modelType
    else:
        advModelType  = advModel.cppTypeName # modelType
        diffModelType = diffModel.cppTypeName # modelType

    _, destinationIncludes, destinationType, _, _, _ = space.storage

    ###'###############################################
    ### extra methods for limiter and time step control
    ###################################################
    ## choose details of discretization (i.e. fluxes)
    ## default settings:
    solverId     = "Dune::Fem::Solver::Enum::fem"
    formId       = "Dune::Fem::Formulation::Enum::primal"
    limiterId    = "Dune::Fem::AdvectionLimiter::Enum::limited"
    limiterFctId = "Dune::Fem::AdvectionLimiterFunction::Enum::minmod"
    advFluxId    = "Dune::Fem::AdvectionFlux::Enum::none"
    diffFluxId   = "Dune::Fem::DiffusionFlux::Enum::none"

    if hasDiffFlux:
        diffFluxId = "Dune::Fem::DiffusionFlux::Enum::"+diffusionScheme

    if hasattr(Model,"NumericalF_c") and advectionFlux=="default":
        advectionFlux = Model.NumericalF_c

    advectionFluxIsCallable = False
    if hasAdvFlux:
        # default value is LLF
        advFluxId  = "Dune::Fem::AdvectionFlux::Enum::llf"
        # if flux choice is default check parameters
        if callable(advectionFlux):
            advFluxId  = "Dune::Fem::AdvectionFlux::Enum::userdefined"
            advectionFluxIsCallable = True
            # wrong model class used here - EllipticModel with no Traits
            # at the moment this is always the same type (depending on
            # model.cppTypeName) so could be done by only providing the header
            # file in the dg operator construction method
            clsName,includes = generateTypeName("Dune::Fem::DGAdvectionFlux",advModel.cppTypeName,"Dune::Fem::AdvectionFlux::Enum::userdefined")
            advectionFlux = advectionFlux(advModel,clsName,includes)
            includes += advectionFlux.cppIncludes
        elif hasattr(advectionFlux,"_typeName"):
            advFluxId  = "Dune::Fem::AdvectionFlux::Enum::userdefined"
            advectionFluxIsCallable = True
            includes += advectionFlux.cppIncludes
        else:
            # if dgadvectionflux.method has been selected, then use general flux,
            # otherwise default to LLF flux
            if advectionFlux == "default":
                key = 'dgadvectionflux.method'
                if parameters is not None and key in parameters.keys():
                    advectionFlux = parameters["dgadvectionflux.method"]

                    # set parameter in dune-fem parameter container
                    # parameterReader.append( { key: value } )
                    if advectionFlux.upper().find( 'LLF' ) >= 0:
                        advFluxId  = "Dune::Fem::AdvectionFlux::Enum::llf"
                    else:
                        if advectionFlux.upper().find( 'EULER' ) >= 0:
                            advFluxId  = "Dune::Fem::AdvectionFlux::Enum::euler_general"
                            includes += [ "dune/fem-dg/operator/fluxes/euler/fluxes.hh" ]
                        elif advectionFlux.upper().find( 'MHD' ) >= 0:
                            advFluxId  = "Dune::Fem::AdvectionFlux::Enum::mhd_general"
                            includes += [ "dune/fem-dg/operator/fluxes/mhd/mhdfluxes.hh" ]
                        else:
                            advFluxId  = "Dune::Fem::AdvectionFlux::Enum::general"
            else:
                advFluxId = advectionFlux
                # raise KeyError("wrong value "+advectionFlux+" for 'advectionFlux' parameter")

    if limiter.lower() == "unlimited" or limiter.lower() == "none":
        limiterId = "Dune::Fem::AdvectionLimiter::Enum::unlimited"
    elif limiter.lower() == "scaling":
        limiterFctId = "Dune::Fem::AdvectionLimiterFunction::Enum::none"
        limiterId = "Dune::Fem::AdvectionLimiter::Enum::scalinglimited"
    # check for different limiter functions (default is minmod)
    elif limiter.lower() == "superbee":
        limiterFctId = "Dune::Fem::AdvectionLimiterFunction::Enum::superbee"
    elif limiter.lower() == "vanleer":
        limiterFctId = "Dune::Fem::AdvectionLimiterFunction::Enum::vanleer"
    elif limiter.lower() != "minmod":
        raise ValueError("limiter "+limiter+" not recognised")

    signature = (advFluxId,diffusionScheme,threading,solverId,formId,
                 limiterId,limiterFctId,advFluxId,diffFluxId,str(defaultQuadrature))
    additionalClass = "Additional_"+hashIt(str(signature))
    struct = Struct(additionalClass, targs=['class FunctionSpace'])
    struct.append(TypeAlias('DomainType','typename FunctionSpace::DomainType'))
    struct.append(TypeAlias('RangeType','typename FunctionSpace::RangeType'))
    struct.append(TypeAlias('JacobianRangeType','typename FunctionSpace::JacobianRangeType'))
    struct.append(TypeAlias('HessianRangeType','typename FunctionSpace::HessianRangeType'))

    ##################################
    ## limiter modification size
    limiterModifiedDict = getattr(Model,"limitedRange",None)
    if limiterModifiedDict is None:
        limiterModified = {}
        limitedDimRange = "FunctionSpace :: dimRange"
    else:
        limiterModified = {}
        count = len( limiterModifiedDict.items() )
        limitedDimRange = str(count)
    struct.append([Declaration(
        Variable("const int", "limitedDimRange = " + limitedDimRange),
        static=True)])
    ##################################
    ## Add 'has*' properties for model
    struct.append([Declaration(
        Variable("const bool", "hasAdvection"), initializer=hasAdvFlux or hasNonStiffSource,
        static=True)])
    struct.append([Declaration(
        Variable("const bool", "hasDiffusion"), initializer=hasDiffFlux,
        static=True)])
    struct.append([Declaration(
        Variable("const bool", "hasStiffSource"), initializer=hasStiffSource,
        static=True)])
    struct.append([Declaration(
        Variable("const bool", "hasNonStiffSource"), initializer=hasNonStiffSource,
        static=True)])
    struct.append([Declaration(
        Variable("const bool", "hasFlux"), initializer=hasAdvFlux or hasDiffFlux,
        static=True)])
    struct.append([Declaration(
        Variable("const bool", "threading"), initializer=threading,
        static=True)])

    struct.append([Declaration(
        Variable("const Dune::Fem::Solver::Enum", "solverId = " + solverId),
        static=True)])
    struct.append([Declaration(
        Variable("const Dune::Fem::Formulation::Enum", "formId = " + formId),
        static=True)])
    struct.append([Declaration(
        Variable("const Dune::Fem::AdvectionLimiter::Enum", "limiterId = " + limiterId),
        static=True)])
    struct.append([Declaration(
        Variable("const Dune::Fem::AdvectionLimiterFunction::Enum", "limiterFunctionId = " + limiterFctId),
        static=True)])
    struct.append([Declaration(
        Variable("const Dune::Fem::AdvectionFlux::Enum", "advFluxId = " + advFluxId),
        static=True)])
    struct.append([Declaration(
        Variable("const Dune::Fem::DiffusionFlux::Enum", "diffFluxId = " + diffFluxId),
        static=True)])
    struct.append([Declaration(
        Variable("const bool", "defaultQuadrature"), initializer=defaultQuadrature,
        static=True)])

    writer = SourceWriter(StringWriter())
    writer.emit([struct])

    # print("#################################")
    # print(writer.writer.getvalue())
    # print("#################################")

    ################################################################
    ### Construct DuneType, includes, and extra methods/constructors
    includes += ["dune/fem-dg/python/operator.hh"]
    includes += ["dune/fem-dg/operator/dg/dgpyoperator.hh"]
    includes += space.cppIncludes + destinationIncludes
    includes += ["dune/fem/schemes/conservationlawmodel.hh", "dune/fempy/parameter.hh"]
    includes += advModel.cppIncludes + diffModel.cppIncludes

    additionalType = additionalClass + '< typename ' + spaceType + '::FunctionSpaceType >'

    typeName = 'Dune::Fem::DGOperator< ' +\
            destinationType + ', ' +\
            advModelType + ', ' + diffModelType + ', ' + additionalType +\
            " >"

    _, domainFunctionIncludes, domainFunctionType, _, _, _ = space.storage
    base = 'Dune::Fem::SpaceOperatorInterface< ' + domainFunctionType + '>'

    estimateMark = Method('estimateMark', '''[]( DuneType &self, const typename DuneType::DestinationType &u, const double dt) { self.estimateMark(u, dt); }''' )

    includes += ["dune/fem-dg/operator/limiter/indicatorbase.hh"]
    setIndicator = Method('setTroubledCellIndicator',
            args=['DuneType &self, typename DuneType::TroubledCellIndicatorType indicator'],
            body=['self.setTroubledCellIndicator(indicator);'],
            extra=['pybind11::keep_alive<0,1>()'])
    gridSizeInterior = Method('gridSizeInterior', '&DuneType::gridSizeInterior')

    order = space.order
    if codegen:
        codegen = [space,range(2,2*order+2),range(2,2*order+2)]
    else:
        codegen = None

    if parameters is not None:
        if advectionFluxIsCallable:
            op = load(includes, typeName, estimateMark, setIndicator, gridSizeInterior,
                     baseClasses=[base],
                     codegen=codegen,
                     preamble=writer.writer.getvalue()).\
                     Operator( space, advModel, diffModel, advectionFlux, parameters=parameters )
        else:
            op = load(includes, typeName, estimateMark, setIndicator, gridSizeInterior,
                     baseClasses = [base],
                     codegen=codegen,
                     preamble=writer.writer.getvalue()).\
                     Operator( space, advModel, diffModel, parameters=parameters )
    else:
        if advectionFluxIsCallable:
            op = load(includes, typeName, estimateMark, setIndicator, gridSizeInterior,
                     baseClasses = [base],
                     codegen=codegen,
                     preamble=writer.writer.getvalue()).\
                     Operator( space, advModel, diffModel, advectionFlux )
        else:
            op = load(includes, typeName, estimateMark, setIndicator, gridSizeInterior,
                     baseClasses = [base],
                     codegen=codegen,
                     preamble=writer.writer.getvalue()).\
                     Operator( space, advModel, diffModel )

    op._t = Model._ufl["t"]
    op.time = Model._ufl["t"].value
    op.models = [advModel,diffModel]
    op.space = space
    def setTime(self,time):
        self._t.value = time
        self.time = time
        self._setTime(self.time)
    op.setTime = setTime.__get__(op)
    # def addToTime(self,dt):
    #     self.setTime(self,self.time+dt)
    # op.addToTime = addToTime.__get__(op)
    def stepTime(self,c,dt):
        self.setTime(self.time+c*dt)
    op.stepTime  = stepTime.__get__(op)
    op._hasAdvFlux = hasAdvFlux
    op._hasDiffFlux = hasDiffFlux
    if limiterIndicator is not None:
        op.setTroubledCellIndicator(limiterIndicator)

    return op

def smoothnessIndicator(clsName, includes, u_h, ctorArgs=None):
    if ctorArgs is None: ctorArgs=[]
    baseName,_ = generateTypeName("Dune::Fem::TroubledCellIndicatorBase",u_h)
    return classLoad(clsName, includes,*ctorArgs, baseClasses=[baseName],
                              holder="std::shared_ptr")
def advectionNumericalFlux(clsName ,includes, advModel, additionalArgs=None):
    if additionalArgs is None: additionalArgs=[]
    code = '''
namespace Dune
{
  namespace Fem
  {
    template <>
    struct DGAdvectionFlux< XXXADV_MODELXXX, AdvectionFlux::Enum::userdefined >
    : public XXXIMPL_MODELXXX
    {
      template< class ... Args>
      DGAdvectionFlux( Args&&... args )
      : XXXIMPL_MODELXXX( std::forward<Args>(args)... ) {}
      std::string name() const {return "user defined flux";}
    };
  }
}
'''
    code = code.replace("XXXADV_MODELXXX",advModel.cppTypeName)
    code = code.replace("XXXIMPL_MODELXXX",clsName)
    clsName,includesA = generateTypeName("Dune::Fem::DGAdvectionFlux",advModel,
                                         "Dune::Fem::AdvectionFlux::Enum::userdefined")
    return classLoad(clsName, includes+includesA+[StringIO(code)], advModel, *additionalArgs)

# RungeKutta solvers
def rungeKuttaSolver( fullOperator, imex='EX', butchertable=None, parameters={} ):

    space = fullOperator.domainSpace
    spaceType = space.cppTypeName

    # only need space includes since we use basic operator type
    includes = ["dune/fem-dg/solver/rungekuttasolver.hh"] # , "dune/fem-dg/misc/algorithmcreatorselector.hh"]
    #includes += fullOperator.cppIncludes
    includes += space.cppIncludes

    _, domainFunctionIncludes, domainFunctionType, _, _, _ = space.storage

    baseOperatorType = 'Dune::Fem::SpaceOperatorInterface< ' + domainFunctionType + '>'
    fullOperatorType = baseOperatorType
    explOperatorType = baseOperatorType
    implOperatorType = baseOperatorType

    typeName = 'Dune::Fem::SimpleRungeKuttaSolver< ' + domainFunctionType + '>'

    imexId = 0 # == 'EX'
    if imex == 'IM':
        imexId = 1
    elif imex == 'IMEX':
        imexId = 2

    # TODO: move this to header file in dune/fem-dg/python
    constructor = Constructor([fullOperatorType + ' &op',
                               explOperatorType + ' &explOp',
                               implOperatorType + ' &implOp',
                               'const int imexId',
                               'const pybind11::dict &parameters'],
                              ['return new ' + typeName + '(op, explOp, implOp, imexId, Dune::FemPy::pyParameter( parameters, std::make_shared< std::string >() ));'],
                              ['"op"_a', '"explOp"_a', '"implOp"_a', '"imexId"_a', '"parameters"_a', 'pybind11::keep_alive< 1, 2 >()', 'pybind11::keep_alive< 1, 3 >()','pybind11::keep_alive< 1, 4 >()','pybind11::keep_alive< 1, 6>()' ])

    solve = Method('solve', '''[]( DuneType &self, typename DuneType::DestinationType &u) { self.solve(u); }''' )
    setTimeStepSize = Method('setTimeStepSize', '&DuneType::setTimeStepSize')
    deltaT = Method('deltaT', '&DuneType::deltaT')

    return load(includes, typeName,
                constructor, solve, setTimeStepSize, deltaT,
                codegen=fullOperator.codegen).\
            Operator( fullOperator.fullOperator,
                      fullOperator.explicitOperator,
                      fullOperator.implicitOperator,
                      imexId,
                      parameters=parameters )


# return DGHelmholtzInverseOperator to be used in RungeKutta solvers
def dgHelmholtzInverseOperator( op, u = None, parameters = {} ):
    """

    Parameters
    ----------
    op : Operator
         Operator describing the spatial operator L, has to be of
         type molGalerkin or similar.

    u  : DiscreteFunction
         DiscreteFunction describing type of argument and target of op.

    parameters : dict
         Parameters handed down to the nonlinear solver.

    Returns
    -------
    Operator (DGHelmholtzInverseOperator on C++ side).

    """

    if u is None:
        u = op.space.function("u_tmp")

    destType    = u.cppTypeName

    # in case a wrapper was passed
    if not hasattr(op, "cppTypeName"):
        op = op._op

    spaceOpType = op.cppTypeName
    # for DGOperator from femDGOperator we need to use SpaceOperatorInterface here
    if 'DGOperator' in spaceOpType:
        spaceOpType = 'Dune::Fem::SpaceOperatorInterface< ' + destType + '>'

    includes = ["dune/fem-dg/solver/dghelmholtzinverse.hh","dune/fempy/parameter.hh"]
    includes += op.cppIncludes
    includes += u.cppIncludes

    typeName = 'Dune::Fem::DGHelmholtzInverseOperator< ' + spaceOpType + ', ' + destType + ' >'

    # constructor for operator
    constructor = Constructor([spaceOpType + ' &spaceOp, const pybind11::dict& parameters'],
                              ['return new ' + typeName + '( spaceOp, Dune::FemPy::pyParameter( "fem.solver.", parameters, std::make_shared< std::string >() ) );'],
                              ['"spaceOp"_a', '"parameters"_a',
                               'pybind11::keep_alive< 1, 2 >()'])

    # add method setLambda to modify lambda stored internally
    setLambda = Method('setLambda', '''[]( DuneType &self, const double lambda) { self.setLambda(lambda); }''' )

    # add method solve, combining setLambda and __call__ for efficiency. Also,
    # here some solver diagnostics can be returned
    solve = Method('_solve', '''[]( DuneType &self, const typename DuneType::DestinationType &rhs, typename DuneType::DestinationType &u, const double lambda, const double tol)
                                 {
                                   self.setTolerance( tol );
                                   auto info = self.solve(rhs, u, lambda);
                                   pybind11::dict ret;
                                   ret["converged"]  = pybind11::cast(info.converged);
                                   ret["iterations"] = pybind11::cast(info.nonlinearIterations);
                                   ret["linear_iterations"] = pybind11::cast(info.linearIterations);
                                   return ret;
                                 }''' )
    # add method solve, combining setLambda and __call__ for efficiency. Also,
    # here some solver diagnostics can be returned
    preCondSolve = Method('_preconditionedSolve', '''[]( DuneType &self,
                                                        const typename DuneType::PreconditionerType& p,
                                                        const typename DuneType::UpdatePreconditionerType& up,
                                                        const typename DuneType::DestinationType &rhs,
                                                        typename DuneType::DestinationType &u, const double lambda,
                                                        const double tol )
                                 {
                                   self.setTolerance( tol );
                                   auto info = self.preconditionedSolve(p, up, rhs, u, lambda);
                                   pybind11::dict ret;
                                   ret["converged"]  = pybind11::cast(info.converged);
                                   ret["iterations"] = pybind11::cast(info.nonlinearIterations);
                                   ret["linear_iterations"] = pybind11::cast(info.linearIterations);
                                   return ret;
                                 }''' )


    op = load(includes, typeName, constructor, setLambda, solve, preCondSolve).Operator( op, parameters )

    # add method solve with default parameter for tolerance
    def solve(rhs, u, lmbda, tol = 1e-8 ):
        return op._solve(rhs, u, lmbda, tol )
    op.solve = solve
    def preconditionedSolve(p, up, rhs, u, lmbda, tol = 1e-8 ):
        return op._preconditionedSolve(p, up, rhs, u, lmbda, tol )
    op.preconditionedSolve = preconditionedSolve
    return op
