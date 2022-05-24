import sympy as sp
from sympy.vector import CoordSys3D
from sympy.parsing.sympy_parser import parse_expr


def parse_vector(value, coord_sys=CoordSys3D("N")):
    if isinstance(value, (str, int, float)):
        value = parse_expr(str(value))

        # create a mapping e.g. sp.Symbol("i") -> coord_sys.i
        vec_map = {
            sp.Symbol(vec._name.split(".")[1]): vec for vec in coord_sys._base_vectors
        }

        components = sp.collect(value, vec_map.keys(), evaluate=False)
        
        if set.intersection(set(vec_map.keys()), set(components.keys())):
            value = 0*coord_sys._base_vectors[0]
            for k,v in components.items():
                value += v*vec_map.get(k, k)

    return value
