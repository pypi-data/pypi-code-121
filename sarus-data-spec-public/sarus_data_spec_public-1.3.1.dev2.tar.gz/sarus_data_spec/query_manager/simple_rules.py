from typing import Collection, Dict, List, Optional, Tuple, cast

from sarus_data_spec.attribute import attach_properties
from sarus_data_spec.dataset import transformed
from sarus_data_spec.query_manager.typing import QueryManager
from sarus_data_spec.transform import synthetic
from sarus_data_spec.variant_constraint import variant_constraint
import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as st

ArgStruct = Tuple[List[int], List[str]]


def flatten_args(
    args: List[st.DataSpec], kwargs: Dict[str, st.DataSpec]
) -> Tuple[List[st.Dataset], List[st.Scalar], ArgStruct]:
    """Split args and kwargs into Datasets and Scalars."""
    flat_args = args + list(kwargs.values())
    ds_args = [
        cast(st.Dataset, arg)
        for arg in flat_args
        if arg.prototype() == sp.Dataset
    ]
    sc_args = [
        cast(st.Scalar, arg)
        for arg in flat_args
        if arg.prototype() == sp.Scalar
    ]

    ds_idx = [
        i for i, arg in enumerate(flat_args) if arg.prototype() == sp.Dataset
    ]
    sc_idx = [
        i for i, arg in enumerate(flat_args) if arg.prototype() == sp.Scalar
    ]
    idx = ds_idx + sc_idx
    struct = (idx, list(kwargs.keys()))

    return ds_args, sc_args, struct


def nest_args(
    ds_args: List[st.DataSpec],
    sc_args: List[st.DataSpec],
    struct: ArgStruct,
) -> Tuple[List[st.DataSpec], Dict[str, st.DataSpec]]:
    """Nest Datasets and Scalars into args and kwargs."""
    idx, keys = struct
    all_args = ds_args + sc_args
    flat_args = [all_args[idx.index(i)] for i in range(len(idx))]
    n_args = len(flat_args) - len(keys)
    args = flat_args[:n_args]
    kwargs = {key: val for key, val in zip(keys, flat_args[n_args:])}
    return args, kwargs


def attach_variant(
    original: st.DataSpec,
    variant: st.DataSpec,
    kind: st.ConstraintKind,
) -> None:
    sp_kind = sp.ConstraintKind.Value(kind.name)
    attach_properties(
        original, properties={sp.ConstraintKind.Name(sp_kind): variant.uuid()}
    )


def verifies(
    query_manager: QueryManager,
    variant_constraint: st.VariantConstraint,
    kind: st.ConstraintKind,
    public_context: Collection[str],
    epsilon: Optional[float],
) -> bool:
    if kind == st.ConstraintKind.PUBLIC:
        return verifies_public(variant_constraint=variant_constraint)

    elif kind == st.ConstraintKind.SYNTHETIC:
        return verifies_synthetic(variant_constraint=variant_constraint)

    elif kind == st.ConstraintKind.DP:
        raise NotImplementedError("DP verification")

    else:  # kind == st.ConstraintKind.PEP:
        raise NotImplementedError("PEP verification")


def verifies_public(variant_constraint: st.VariantConstraint) -> bool:
    return variant_constraint.constraint_kind() == st.ConstraintKind.PUBLIC


def verifies_synthetic(variant_constraint: st.VariantConstraint) -> bool:
    return variant_constraint.constraint_kind() in [
        st.ConstraintKind.PUBLIC,
        st.ConstraintKind.SYNTHETIC,
    ]


def compile(
    query_manager: QueryManager,
    dataspec: st.DataSpec,
    kind: st.ConstraintKind,
    public_context: List[str],
    epsilon: Optional[float],
) -> Optional[st.DataSpec]:
    """Returns a compliant Node or None."""

    if kind == st.ConstraintKind.SYNTHETIC:
        variant, _ = compile_synthetic(
            query_manager,
            dataspec,
            public_context,
        )
        return variant

    if not epsilon:
        raise ValueError("epsilon must be defined for PEP or DP to compile.")

    if kind == st.ConstraintKind.DP:
        raise NotImplementedError("DP compilation")

    elif kind == st.ConstraintKind.PEP:
        raise NotImplementedError("PEP compilation")

    else:
        raise ValueError(
            f"Privacy policy {kind} compilation " "not implemented yet"
        )


def compile_synthetic(
    query_manager: QueryManager,
    dataspec: st.DataSpec,
    public_context: Collection[str],
) -> Tuple[st.DataSpec, Collection[str]]:
    # Caching mechanisms
    if dataspec.verifies(
        kind=st.ConstraintKind.SYNTHETIC,
        public_context=public_context,
        epsilon=None,
    ):
        return dataspec, public_context

    for variant in dataspec.variants():
        if variant.verifies(
            kind=st.ConstraintKind.SYNTHETIC,
            public_context=public_context,
            epsilon=None,
        ):
            return variant, public_context

    if dataspec.prototype() == sp.Dataset:
        dataset = cast(st.Dataset, dataspec)
        # TODO remove this constraint once we have the whole
        # graph for a remote DataSpec
        if not dataspec.is_remote() and dataset.is_synthetic():
            variant_constraint(
                constraint_kind=st.ConstraintKind.SYNTHETIC,
                dataspec=dataspec,
            )
            return dataset, list(public_context)

    if not dataspec.is_remote() and dataspec.is_transformed():
        transform = dataspec.transform()
        args, kwargs = dataspec.parents()
        ds_args, sc_args, struct = flatten_args(args, kwargs)
        ds_syn_args_context = [
            compile_synthetic(query_manager, parent, public_context)
            for parent in ds_args
        ]
        sc_syn_args_context = [
            compile_synthetic(query_manager, parent, public_context)
            for parent in sc_args
        ]

        if len(ds_syn_args_context) > 0:
            ds_syn_args, ds_contexts = zip(*ds_syn_args_context)
        else:
            ds_syn_args, ds_contexts = [], ([],)
        if len(sc_syn_args_context) > 0:
            sc_syn_args, sc_contexts = zip(*sc_syn_args_context)
        else:
            sc_syn_args, sc_contexts = [], ([],)
        new_context = list(set(sum(ds_contexts + sc_contexts, [])))
        args, kwargs = nest_args(
            cast(List[st.DataSpec], list(ds_syn_args)),
            cast(List[st.DataSpec], list(sc_syn_args)),
            struct,
        )
        syn_variant = cast(
            st.DataSpec,
            transformed(
                transform,
                *args,
                dataspec_type=sp.type_name(dataspec.prototype()),
                dataspec_name=None,
                **kwargs,
            ),
        )
        variant_constraint(
            constraint_kind=st.ConstraintKind.SYNTHETIC,
            dataspec=syn_variant,
        )
        attach_variant(dataspec, syn_variant, kind=st.ConstraintKind.SYNTHETIC)
        return syn_variant, new_context

    # Source (non transformed) dataset
    if dataspec.prototype() == sp.Dataset:
        dataset = cast(st.Dataset, dataspec)
        syn_dataset = cast(st.Dataset, synthetic()(dataset))
        variant_constraint(
            constraint_kind=st.ConstraintKind.SYNTHETIC,
            dataspec=syn_dataset,
        )
        attach_variant(dataset, syn_dataset, kind=st.ConstraintKind.SYNTHETIC)
        new_context = list(public_context) + [syn_dataset.uuid()]
        return syn_dataset, new_context

    elif dataspec.prototype() == sp.Scalar:
        scalar = cast(st.Scalar, dataspec)
        assert scalar.is_model()
        new_context = list(public_context) + [scalar.uuid()]
        variant_constraint(
            constraint_kind=st.ConstraintKind.PUBLIC,
            dataspec=scalar,
        )
        return scalar, new_context

    raise ValueError("Uncaught compilation case.")


def is_public(dataspec: st.DataSpec) -> bool:
    if dataspec.prototype() == sp.Scalar:
        scalar = cast(st.Scalar, dataspec)
        if scalar.is_model():
            return True

    # Returns true if the DataSpec derives only from public
    if dataspec.is_transformed():
        args_parents, kwargs_parents = dataspec.parents()
        return all(
            [is_public(ds) for ds in args_parents]
            + [is_public(ds) for ds in kwargs_parents.values()]
        )

    # Default case
    return False
