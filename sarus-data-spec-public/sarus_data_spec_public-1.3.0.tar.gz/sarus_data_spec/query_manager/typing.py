from typing import Collection, List, Optional, Protocol

from sarus_data_spec.storage.typing import Storage
import sarus_data_spec.typing as st


class QueryManager(Protocol):
    def storage(self) -> Storage:
        ...

    def is_compliant(
        self,
        dataspec: st.DataSpec,
        kind: st.ConstraintKind,
        public_context: List[str],
        epsilon: Optional[float],
    ) -> bool:
        ...

    def variant(
        self,
        dataspec: st.DataSpec,
        kind: st.ConstraintKind,
        public_context: List[str],
        epsilon: Optional[float],
    ) -> Optional[st.DataSpec]:
        ...

    def variants(self, dataspec: st.DataSpec) -> Collection[st.DataSpec]:
        ...

    def variant_constraint(
        self, dataspec: st.DataSpec
    ) -> Optional[st.VariantConstraint]:
        ...

    def transform_equivalent(
        self, transform: st.Transform, dp: bool
    ) -> Optional[st.Transform]:
        ...

    def is_pe_preserving(self, transform: st.Transform) -> bool:
        ...

    def is_differentially_private(self, transform: st.Transform) -> bool:
        ...

    def verifies(
        self,
        variant_constraint: st.VariantConstraint,
        kind: st.ConstraintKind,
        public_context: Collection[str],
        epsilon: Optional[float],
    ) -> bool:
        ...
