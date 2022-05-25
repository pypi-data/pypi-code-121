from __future__ import annotations

from typing import List, Optional, Type, cast

from sarus_data_spec.base import Referring
import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as st


class VariantConstraint(Referring[sp.VariantConstraint]):
    def __init__(self, protobuf: sp.VariantConstraint) -> None:
        self._referred = {protobuf.dataspec}
        super().__init__(protobuf=protobuf)

    def prototype(self) -> Type[sp.VariantConstraint]:
        """Return the type of the underlying protobuf."""
        return sp.VariantConstraint

    def constraint_kind(self) -> st.ConstraintKind:
        return st.ConstraintKind(self.protobuf().constraint_kind)

    def required_context(self) -> List[str]:
        return list(self.protobuf().required_context)

    def epsilon(self) -> Optional[float]:
        str_epsilon = self.protobuf().properties.get("epsilon", None)
        if str_epsilon:
            return float(str_epsilon)
        else:
            return None

    def dataspec(self) -> st.DataSpec:
        return cast(
            st.DataSpec, self.storage().referrable(self.protobuf().dataspec)
        )


def variant_constraint(
    constraint_kind: st.ConstraintKind,
    dataspec: st.DataSpec,
    required_context: List[str] = [],
    epsilon: Optional[float] = None,
) -> VariantConstraint:
    if epsilon:
        properties = {"epsilon": str(epsilon)}
    else:
        properties = dict()

    return VariantConstraint(
        sp.VariantConstraint(
            dataspec=dataspec.uuid(),
            constraint_kind=sp.ConstraintKind.Value(constraint_kind.name),
            properties=properties,
            required_context=required_context,
        )
    )


def dp_constraint(
    required_context: List[str],
    epsilon: float,
    dataspec: str,
) -> VariantConstraint:
    return VariantConstraint(
        sp.VariantConstraint(
            constraint_kind=sp.ConstraintKind.DP,
            required_context=required_context,
            properties={"epsilon": str(epsilon)},
            dataspec=dataspec,
        )
    )


def pep_constraint(
    required_context: List[str],
    epsilon: float,
    dataspec: str,
) -> VariantConstraint:
    return VariantConstraint(
        sp.VariantConstraint(
            constraint_kind=sp.ConstraintKind.PEP,
            required_context=required_context,
            properties={"epsilon": str(epsilon)},
            dataspec=dataspec,
        )
    )


def syn_constraint(
    required_context: List[str],
    dataspec: str,
) -> VariantConstraint:
    return VariantConstraint(
        sp.VariantConstraint(
            constraint_kind=sp.ConstraintKind.SYNTHETIC,
            required_context=required_context,
            dataspec=dataspec,
        )
    )
