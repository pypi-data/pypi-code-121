import pyomo.core
import sympy
from pyomo.core.expr.logical_expr import EqualityExpression

from classiq.interface.pyomo_extension import (
    equality_expression,
    inequality_expression,
    set_pprint,
)

pyomo.core.expr.logical_expr.InequalityExpression.getname = (
    inequality_expression.getname
)

pyomo.core.expr.logical_expr.EqualityExpression.getname = equality_expression.getname

pyomo.core.base.set.Set._pprint_members = staticmethod(set_pprint.pprint_members)

pyomo.core.expr.sympy_tools._operatorMap.update({sympy.LessThan: lambda x, y: x <= y})
pyomo.core.expr.sympy_tools._operatorMap.update(
    {sympy.GreaterThan: lambda x, y: x >= y}
)
pyomo.core.expr.sympy_tools._pyomo_operator_map.update({EqualityExpression: sympy.Eq})
