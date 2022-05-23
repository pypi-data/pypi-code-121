"""Gapfilling functions. Mostly a meneco interface."""
from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable, cast

from clyngor.as_pyasp import Term, TermSet
from meneco.meneco import query

if TYPE_CHECKING:
    from ..core.model import Model

__all__ = [
    "model_to_termset",
    "name_to_term",
    "names_to_termset",
    "get_unproducible",
    "term_to_str",
    "termset_to_set",
    "get_termsets",
    "get_reconstructable_cpds",
    "get_essential_reactions",
    "get_minimal_solution",
    "gapfilling",
]


@dataclass
class Termsets:
    model: TermSet
    db: TermSet
    seeds: TermSet
    targets: TermSet


def model_to_termset(model: "Model", model_name: str) -> TermSet:
    model_terms = []
    for reaction in model.reactions.values():
        model_terms.append(Term("reaction", [f'"{reaction.id}"', f'"{model_name}"']))
        substrates, products = reaction.split_stoichiometries()
        for substrate in substrates:
            model_terms.append(
                Term(
                    "reactant",
                    [
                        f'"{substrate}"',
                        f'"{reaction.id}"',
                        f'"{model_name}"',
                    ],
                )
            )
        for product in products:
            model_terms.append(
                Term(
                    "product",
                    [
                        f'"{product}"',
                        f'"{reaction.id}"',
                        f'"{model_name}"',
                    ],
                )
            )
    return TermSet(model_terms)


def name_to_term(compound_type: str, compound_id: str) -> Term:
    return Term(compound_type, [f'"{compound_id}"'])


def names_to_termset(compound_type: str, compound_iterable: Iterable[str]) -> TermSet:
    terms = []
    for compound_id in compound_iterable:
        terms.append(name_to_term(compound_type, compound_id))
    return TermSet(terms)


def get_unproducible(model: TermSet, target: TermSet, seed: TermSet) -> set[str]:
    return set(
        i[0] for i in cast(dict, query.get_unproducible(model, target, seed)).get("unproducible_target", [])
    )


def term_to_str(term: Term) -> str:
    return term.arg(0).strip('"')  # type: ignore


def termset_to_set(ts: TermSet) -> set[str]:
    return {term_to_str(t) for t in ts}


def get_termsets(model: Model, db: Model, seeds: Iterable[str], targets: Iterable[str]) -> Termsets:
    return Termsets(
        model=model_to_termset(model, "draft"),
        db=model_to_termset(db, "repair"),
        seeds=names_to_termset("seed", seeds),
        targets=names_to_termset("target", targets),
    )


def get_reconstructable_cpds(
    ts: Termsets,
    verbose: bool,
) -> Termsets:
    unproducible_model = get_unproducible(ts.model, ts.targets, ts.seeds)
    non_reconstructible = get_unproducible(cast(TermSet, ts.model.union(ts.db)), ts.targets, ts.seeds)
    for target in non_reconstructible:
        warnings.warn(f"Cannot reproduce {target}")
    reconstructible = unproducible_model.difference(non_reconstructible)
    if verbose:
        print("Can reproduce {}".format(", ".join(sorted(reconstructible))))
    ts.targets = names_to_termset("target", reconstructible)
    return ts


def get_essential_reactions(
    ts: Termsets,
) -> set[str]:
    essential_reactions = set()
    for target in ts.targets:
        result = cast(
            dict[str, set[tuple[str, str]]],
            query.get_intersection_of_completions(ts.model, ts.db, ts.seeds, TermSet([target])),
        )
        if (rxns := result.get("xreaction")) is not None:
            essential_reactions |= {i[0] for i in rxns}
        else:
            warnings.warn(f"Could not find essential reactions for {term_to_str(target)}")
    return essential_reactions


def get_minimal_solution(ts: Termsets, essential_reactions: TermSet) -> set[str]:
    filled_model = cast(TermSet, ts.model.union(essential_reactions))
    min_models = cast(
        dict[str, set[tuple[str, str]]],
        query.get_minimal_completion_size(filled_model, ts.db, ts.seeds, ts.targets),
    )
    return {i[0] for i in min_models.get("xreaction", [])}


def gapfilling(
    model: "Model",
    db: "Model",
    seeds: Iterable[str],
    targets: Iterable[str],
    min_solution: bool = True,
    verbose: bool = False,
    include_weak_cofactors: bool = False,
) -> Iterable[str]:
    seeds = set(seeds)
    if include_weak_cofactors:
        seeds = seeds.union(set(db.get_weak_cofactor_duplications()))

    ts = get_termsets(model, db, seeds, targets)
    ts = get_reconstructable_cpds(ts, verbose)
    essential_reactions = get_essential_reactions(ts)
    if not min_solution:
        return essential_reactions
    return get_minimal_solution(ts, names_to_termset("draft", essential_reactions)).difference(
        model.reactions
    )
