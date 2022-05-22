from typing import List, Optional

from .core import cpp_define

CPP_MACROS = \
{
   "VecUtils":
    """
    namespace VecUtils{
        template <typename T>
        std::vector<T> as_vector(const T* data, size_t size) {
            return std::vector<T>(data, data + size);
        }
    };
    """
}

def load_macro(macro_name:str):
    expression = CPP_MACROS.get(macro_name, None)
    if expression is None:
        raise ValueError(f"`{macro_name}` is not a built-in quickstats cpp macro."
                         " Available macros are: {}".format(",".join(list(CPP_MACROS))))
    cpp_define(expression, macro_name)

def load_macros(macro_names:Optional[List[str]]=None):
    if macro_names is None:
        macro_names = list(CPP_MACROS)
    for macro_name in macro_names:
        load_macro(macro_name)