from typing import Final

from sarus_data_spec.attribute import Attribute
from sarus_data_spec.context import push_global_context
from sarus_data_spec.dataset import Dataset
from sarus_data_spec.scalar import Scalar
from sarus_data_spec.status import Status
from sarus_data_spec.transform import Transform
from sarus_data_spec.variant_constraint import VariantConstraint

"""A library to manage Sarus datasets"""
# pylint: disable=unused-variable

PACKAGE_NAME: Final[str] = 'sarus_data_spec'
VERSION: Final[str] = '1.3.1.dev3'

try:
    # The local context is absent from the public release
    import sarus_data_spec.context.local as sc

    push_global_context(sc.Local())
except ModuleNotFoundError:
    pass
