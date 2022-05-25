# This file is part of PyCosmo, a multipurpose cosmology calculation tool in Python.
#
# Copyright (C) 2013-2021 ETH Zurich, Institute for Particle and Astrophysics and SIS
# ID.
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.

import inspect
import types
import warnings

import six


def prototype(func):
    func._is_prototype = True
    return func


class ClassContractMeta(object):
    def __new__(self, name, bases, d, **kwargs):
        cls = type(name, bases, d, **kwargs)
        prototypes = {
            name: method
            for name, method in d.items()
            if getattr(method, "_is_prototype", False)
        }
        cls._prototypes = prototypes
        return cls


def check_protypes(clz):
    for name, method in clz._prototypes.items():
        if name not in clz.__dict__:
            raise RuntimeError(
                "class {} implements no method for prototype {}.".format(clz, name)
            )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            spec_tobe = inspect.getargspec(method)
            spec_is = inspect.getargspec(clz.__dict__[name])
            if spec_tobe != spec_is:
                # fix when decorated with @profile:
                closure = clz.__dict__[name].__closure__
                if closure:
                    for cell in closure:
                        if isinstance(cell.cell_contents, types.FunctionType):
                            spec_is = inspect.getargspec(cell.cell_contents)
                            break
                    else:
                        raise RuntimeError(
                            "can not inspect if {}.{} is compliant to protype".format(
                                clz.__name__, name
                            )
                        )
                if spec_tobe != spec_is:
                    raise RuntimeError(
                        "implementation of {} in {} has wrong API. Should be {} "
                        "but is {}.".format(name, clz, spec_tobe, spec_is)
                    )


@six.add_metaclass(ClassContractMeta)
class NonLinearPerturbationBase(object):
    def __new__(clz, *a, **kw):
        check_protypes(clz)
        return super(NonLinearPerturbationBase, clz).__new__(clz)

    @prototype
    def powerspec_a_k(self, a=1.0, k=0.1, diag_only=False):
        pass
