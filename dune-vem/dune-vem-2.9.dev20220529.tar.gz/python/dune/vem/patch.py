from __future__ import division, print_function, unicode_literals

from dune.ufl.codegen import generateMethod
from ufl import SpatialCoordinate, Coefficient, replace, diff, as_vector, MaxCellEdgeLength
from ufl.core.expr import Expr
from ufl.tensors import ListTensor
from dune.source.cplusplus import Variable, UnformattedExpression, AccessModifier, maxEdgeLength
from ufl.algorithms import expand_compounds, expand_derivatives, expand_indices, expand_derivatives

def codeVEM(self, name, targs):
    code = self._code(name,targs)

    u = self.trialFunction
    ubar = Coefficient(u.ufl_function_space())
    mStab = self.mStab
    if isinstance(mStab,Expr):
        try:
            mStab = expand_indices(expand_derivatives(expand_compounds(mStab)))
        except:
            pass
        dmStab = replace(
                   expand_derivatives( diff(replace(mStab,{u:ubar}),ubar) ),
                   {ubar:u} )
        if mStab.ufl_shape == ():
            mStab = as_vector([mStab])
        try:
            mStab = expand_indices(expand_derivatives(expand_compounds(mStab)))
        except:
            pass
        assert mStab.ufl_shape == u.ufl_shape
        dmStab = as_vector([
                    replace(
                      expand_derivatives( diff(replace(mStab,{u:ubar}),ubar) )[i,i],
                    {ubar:u} )
                 for i in range(u.ufl_shape[0]) ])
    else:
        dmStab = None

    gStab = self.gStab
    if isinstance(gStab,Expr):
        if gStab.ufl_shape == ():
            gStab = as_vector([gStab])
        try:
            gStab = expand_indices(expand_derivatives(expand_compounds(gStab)))
        except:
            pass
        assert gStab.ufl_shape == u.ufl_shape
        dgStab = as_vector([
                    replace(
                      expand_derivatives( diff(replace(gStab,{u:ubar}),ubar) )[i,i],
                    {ubar:u} )
                 for i in range(u.ufl_shape[0]) ])
    else:
        dgStab = None

    hStab = self.hStab
    if isinstance(hStab,Expr):
        if hStab.ufl_shape == ():
            hStab = as_vector([hStab])
        try:
            hStab = expand_indices(expand_derivatives(expand_compounds(hStab)))
        except:
            pass
        assert hStab.ufl_shape == u.ufl_shape
        dhStab = as_vector([
                    replace(
                      expand_derivatives( diff(replace(hStab,{u:ubar}),ubar) )[i,i],
                    {ubar:u} )
                 for i in range(u.ufl_shape[0]) ])
    else:
        dhStab = None

    code.append(AccessModifier("public"))
    x = SpatialCoordinate(self.space.cell())
    maxCellEdgeLength = MaxCellEdgeLength(self.space.cell())
    predefined = {}
    self.predefineCoefficients(predefined, False)
    spatial = Variable('const auto', 'y')
    predefined[x] = UnformattedExpression('auto', 'entity().geometry().global( Dune::Fem::coordinate( x ) )')
    predefined[maxCellEdgeLength] = maxEdgeLength(self.cellGeometry())
    self.predefineCoefficients(predefined)
    generateMethod(code, hStab,
            'RRangeType', 'hessStabilization',
            args=['const Point &x',
                  'const DRangeType &u'],
            targs=['class Point','class DRangeType'], static=False, const=True,
            predefined=predefined)
    generateMethod(code, dhStab,
            'RRangeType', 'linHessStabilization',
            args=['const Point &x',
                  'const DRangeType &u'],
            targs=['class Point','class DRangeType'], static=False, const=True,
            predefined=predefined)
    generateMethod(code, gStab,
            'RRangeType', 'gradStabilization',
            args=['const Point &x',
                  'const DRangeType &u'],
            targs=['class Point','class DRangeType'], static=False, const=True,
            predefined=predefined)
    generateMethod(code, dgStab,
            'RRangeType', 'linGradStabilization',
            args=['const Point &x',
                  'const DRangeType &u'],
            targs=['class Point','class DRangeType'], static=False, const=True,
            predefined=predefined)
    generateMethod(code, mStab,
            'RRangeType', 'massStabilization',
            args=['const Point &x',
                  'const DRangeType &u'],
            targs=['class Point','class DRangeType'], static=False, const=True,
            predefined=predefined)
    generateMethod(code, dmStab,
            'RRangeType', 'linMassStabilization',
            args=['const Point &x',
                  'const DRangeType &u'],
            targs=['class Point','class DRangeType'], static=False, const=True,
            predefined=predefined)
    return code

def transform(space,hStab,gStab,mStab):
    if not type(hStab) in [list,tuple,ListTensor]: # note __getitem__ exists for any ufl expressions
        hStab = [hStab]
    if not type(gStab) in [list,tuple,ListTensor]: # note __getitem__ exists for any ufl expressions
        gStab = [gStab]
    if not type(mStab) in [list,tuple,ListTensor]: # note __getitem__ exists for any ufl expressions
        mStab = [mStab]
    exprs = []
    baseSignature = []
    if mStab[0] is not None:
        baseSignature += [["mass",mStab]]
        exprs += [x for x in mStab if not type(x) in [int,float]]
    if gStab[0] is not None:
        baseSignature += [["grad",gStab]]
        exprs += [x for x in gStab if not type(x) in [int,float]]
    if hStab[0] is not None:
        baseSignature += [["hess",hStab]]
        exprs += [x for x in hStab if not type(x) in [int,float]]
    def transform_(model):
        model.baseSignature = baseSignature
        if model.baseName == "vemintegrands":
            return
        model._code = model.code
        model.code  = lambda *args,**kwargs: codeVEM(model,*args,**kwargs)
        model.space = space
        model.hStab = hStab
        model.gStab = gStab
        model.mStab = mStab
        model.baseName = "vemintegrands"
    return [transform_, exprs]
