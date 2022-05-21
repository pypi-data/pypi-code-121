from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict, Counter
from dataclasses import dataclass, replace
from itertools import chain
from typing import List, Dict, Iterable, Tuple, Optional, cast, DefaultDict, Union, Any, TypeVar, Protocol, Generic, Set

from pkm.api.versions.version import Version, StandardVersion
from pkm.api.versions.version_specifiers import VersionSpecifier, VersionMatch, AllowAllVersions, \
    RestrictAllVersions
from pkm.resolution.resolution_monitor import DependencyResolutionIterationEvent, \
    DependencyResolutionConclusionEvent, DependencyResolutionMonitoredOp
from pkm.utils.iterators import find_first
from pkm.utils.sequences import argmax


class PKG(Protocol):
    def __hash__(self): ...

    def __eq__(self, other): ...

    def __str__(self): ...

    def __lt__(self, other): ...


PKG_T = TypeVar('PKG_T', bound=PKG)


class UnsolvableProblemException(Exception):
    def __init__(self, incompatibility: "Incompatibility"):
        super().__init__(f'Dependency Versions Resolution Failed\n{incompatibility.report()}')
        self.incompatibility = incompatibility


class MalformedPackageException(Exception):
    ...


@dataclass(frozen=True)
class Term:
    package: PKG
    constraint: VersionSpecifier

    def negate(self) -> "Term":
        return Term(self.package, self.constraint.inverse())

    def intersect(self, other: "Term") -> "Term":
        assert self.package == other.package, 'cannot intersect terms of different packages'
        return Term(self.package, self.constraint.intersect_with(other.constraint))

    def satisfies(self, constraint: VersionSpecifier) -> bool:
        """self ⊆ term"""
        return constraint.allows_all(self.constraint)

    @classmethod
    def join(cls, package: PKG, terms: Iterable["Term"]) -> "Term":
        terms_iter = iter(terms)
        first_term = next(terms_iter, None)

        if not first_term:
            return Term.create(package, "*")

        next_term = next(terms_iter, None)
        if not next_term:
            return first_term

        package = first_term.package
        constraint = first_term.constraint

        while next_term is not None:
            constraint = constraint.intersect_with(next_term.constraint)
            next_term = next(terms_iter, None)

        return cls(package, constraint)

    def __repr__(self):
        return f"[{self.package} {self.constraint}]"

    @classmethod
    def create(cls, package: PKG, constraint: str) -> "Term":
        return cls(package, VersionSpecifier.parse(constraint))


@dataclass
class Assignment:
    term: Term
    decision_level: int
    order_index: int
    cause: Optional["Incompatibility"]
    accumulated: VersionSpecifier

    def is_decision(self) -> bool:
        return self.cause is None

    def __repr__(self):
        return f"A({self.term}, dlevel={self.decision_level}, cause={self.cause})"


class PartialSolution:
    def __init__(self, root_package: PKG = 'root'):
        self._root_package = root_package
        self._assignments_by_order: List[Assignment] = []
        self.assignments_by_package: DefaultDict[PKG, List[Assignment]] = defaultdict(list)
        self._required_packages: Dict[PKG, int] = {}
        self._decisions: Dict[PKG, Assignment] = {}

    def notify_state(self, current_package: PKG, monitor: DependencyResolutionMonitoredOp):
        # noinspection PyTypeChecker
        DependencyResolutionIterationEvent(self._decisions.keys(), self._required_packages.keys(), current_package) \
            .notify(monitor)

    def undecided_packages(self) -> List[PKG]:
        return [req for req in self._required_packages if req not in self._decisions]

    def requirement_decision_level(self, package: PKG) -> int:
        """
        returns the decision level in which the given `package` was required
        :param package: the package to check
        :return: the decision level if the package is required, otherwise -1
        """
        return self._required_packages.get(package) or -1

    @property
    def _decision_level(self) -> int:
        return max(0, len(self._decisions) - 1)

    def requiering_decision(self, package: PKG):
        decision_level = self._required_packages[package]
        return next(acc for acc in self._decisions.values()
                    if acc.decision_level == decision_level)

    def backtrack(self, decision_level: int):
        # print(f"backtrack to decision_level: {decision_level}")

        def filtered(lst: List[Assignment]) -> Iterable[Assignment]:
            return (ass for ass in lst if ass.decision_level <= decision_level)

        self._assignments_by_order = list(filtered(self._assignments_by_order))

        assignments_by_package = defaultdict(list)
        for package, assignments in self.assignments_by_package.items():
            assignments_by_package[package].extend(filtered(assignments))

        self.assignments_by_package = assignments_by_package

        self._required_packages = {
            package: req_decision_level
            for package, req_decision_level in self._required_packages.items()
            if req_decision_level <= decision_level
        }

        self._decisions = {
            package: decision
            for package, decision in self._decisions.items()
            if decision.decision_level <= decision_level
        }

    def require(self, packages: Iterable[PKG]):
        required_packages = self._required_packages
        for package in packages:
            if package not in required_packages:
                required_packages[package] = self._decision_level

    def requires(self, package: PKG) -> bool:
        return package in self._required_packages

    def make_assignment(self, assignment_value: Term, cause: Optional["Incompatibility"] = None):
        package_assignments = self.assignments_by_package[assignment_value.package]

        accumulated_constraint = assignment_value.constraint
        if package_assignments:
            accumulated_constraint = package_assignments[-1].accumulated.intersect_with(accumulated_constraint)

        dlevel = self._decision_level

        if cause is None and assignment_value.package != self._root_package:
            dlevel += 1

        return Assignment(assignment_value, dlevel, len(self._assignments_by_order), cause, accumulated_constraint)

    def assign(self, assignment_value: Union[Term, Assignment], cause: Optional["Incompatibility"] = None):
        assignment = self.make_assignment(assignment_value, cause) \
            if not isinstance(assignment_value, Assignment) else assignment_value

        self.assignments_by_package[assignment.term.package].append(assignment)
        self._assignments_by_order.append(assignment)

        if assignment.is_decision():
            # print(f"decided: {assignment}")
            self._decisions[assignment.term.package] = assignment
        else:
            # print(f"derrived: {assignment}")
            ...

    def __repr__(self):
        return f"PartialSolution({self._assignments_by_order})"

    def decisions(self) -> Dict[PKG, Version]:
        return {package: cast(VersionMatch, ass.term.constraint).version for package, ass in self._decisions.items()}


@dataclass
class IncompatibilitySatisfaction:
    incompatibility: "Incompatibility"
    satisfier: Optional[Assignment] = None
    prev_satisfier: Optional[Assignment] = None
    undecided_term: Optional[Term] = None

    def is_full(self) -> bool:
        return bool(self.satisfier)

    def is_almost_full(self) -> bool:
        return bool(self.undecided_term)

    def __str__(self):
        if self.is_full():
            return f"fully-satisfied: sat={self.satisfier}, pre-sat={self.prev_satisfier}"
        if self.is_almost_full():
            return f"almost-fully-satisfied: undecided={self.undecided_term}"
        return "not-satisfied"

    @staticmethod
    def find_satisfier(
            solution: "PartialSolution", term: Term, next_satisfier: Optional[Assignment] = None
    ) -> Optional[Assignment]:

        if package_assignments := solution.assignments_by_package[term.package]:
            if term.constraint.allows_all(package_assignments[-1].accumulated):
                for assignment in package_assignments:
                    if assignment is next_satisfier:
                        return None

                    acc = assignment.accumulated
                    if next_satisfier:
                        if term.constraint.allows_all(acc.intersect_with(next_satisfier.term.constraint)):
                            return assignment
                    elif term.constraint.allows_all(acc):
                        return assignment
        return None

    @classmethod
    def create_unsatisfied(cls, incompatibility: Incompatibility) -> IncompatibilitySatisfaction:
        return cls(incompatibility)

    @classmethod
    def create_almost_full(cls, incompatibility: Incompatibility, undecided_term: Term) -> IncompatibilitySatisfaction:
        return cls(incompatibility, undecided_term=undecided_term)

    @classmethod
    def create_full(
            cls, incompatibility: Incompatibility, solution: PartialSolution, satisfiers: List[Assignment]
    ) -> IncompatibilitySatisfaction:
        satisfier_index = argmax(satisfiers, key=lambda s: s.order_index)
        satisfier = satisfiers.pop(satisfier_index)

        for term in incompatibility.terms:
            if solution.requires(term.package):
                satisfiers.append(solution.requiering_decision(term.package))

            if term.package == satisfier.term.package:
                if prev_satisfier := cls.find_satisfier(solution, term, satisfier):
                    satisfiers.append(prev_satisfier)

        prev_satisfier_index = argmax(satisfiers, key=lambda s: s.order_index) if satisfiers else None

        return cls(
            incompatibility, satisfier=satisfier,
            prev_satisfier=satisfiers[prev_satisfier_index] if prev_satisfier_index is not None else None)


class Incompatibility:
    def __init__(self, terms: Tuple[Term, ...], internal_cause: Optional[Tuple["Incompatibility", "Incompatibility"]],
                 external_cause: Optional[str]):
        assert not internal_cause or internal_cause[0] != internal_cause[1], "duplicated internal cause"

        self.terms = terms
        self.internal_cause = internal_cause
        self.external_cause = external_cause

    def is_simple(self):
        if self.internal_cause:
            ic1, ic2 = self.internal_cause
            return ic1.external_cause and ic2.external_cause

        return False

    def term_for(self, package: PKG) -> Optional[Term]:
        return next((term for term in self.terms if term.package == package), None)

    def check_satisfaction(self, solution: "PartialSolution") -> IncompatibilitySatisfaction:
        assignments = solution.assignments_by_package
        undecided_term: Optional[Term] = None
        satisfiers: List[Assignment] = []

        for term in self.terms:
            package_assignments = assignments[term.package]
            if package_assignments and package_assignments[-1].accumulated is RestrictAllVersions:
                return IncompatibilitySatisfaction.create_unsatisfied(self)

        for term in self.terms:
            satisfier = IncompatibilitySatisfaction.find_satisfier(solution, term)
            if not satisfier and (assignments := solution.assignments_by_package[term.package]) \
                    and not assignments[-1].accumulated.allows_any(term.constraint):
                return IncompatibilitySatisfaction.create_unsatisfied(self)

            if not satisfier:
                if not undecided_term:
                    undecided_term = term
                else:
                    return IncompatibilitySatisfaction.create_unsatisfied(self)
            else:
                satisfiers.append(satisfier)

        if undecided_term:
            return IncompatibilitySatisfaction.create_almost_full(self, undecided_term)

        return IncompatibilitySatisfaction.create_full(self, solution, satisfiers)

    def is_empty(self) -> bool:
        return not self.terms

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Incompatibility) and o.terms == self.terms

    def __hash__(self):
        return hash(self.terms)

    def __str__(self):
        if self.external_cause:
            return self.external_cause

        terms = self.terms
        if len(terms) == 1:
            if terms[0].constraint is AllowAllVersions:
                return f"{terms[0].package} cannot be resolved"
            return f"{terms[0].package} must be {terms[0].constraint.inverse()}"

        return f"{terms}"

    def __repr__(self):

        if self.external_cause:
            return f"EXI'{str(self)}'"
        else:
            return f"INI'{str(self)}'"

    def report(self):
        report: Dict[Any, Tuple[int, str]] = {}

        def write(key: Any, text: str):
            report[key] = len(report), text

        def generate(incompatability: Incompatibility):
            if incompatability.external_cause:
                write(incompatability, incompatability.external_cause)
                return

            ic1, ic2 = incompatability.internal_cause
            if ic1.internal_cause and ic2.internal_cause:
                l1, l2 = report.get(ic1), report.get(ic2)

                if l1 and l2:
                    write(incompatability, f"Because {ic1} ({l1[0]}) and {ic2} ({l2[0]}), {incompatability}")
                elif l1:
                    generate(ic2)
                    write(incompatability, f"And because {ic1} ({l1[0]}), {incompatability}")
                elif l2:
                    generate(ic1)
                    write(incompatability, f"And because {ic2} ({l2[1]}), {incompatability}")
                elif ic1.is_simple():
                    generate(ic2)
                    generate(ic1)
                    write(incompatability, f"Thus, {incompatability}")
                elif ic2.is_simple():
                    generate(ic1)
                    generate(ic2)
                    write(incompatability, f"Thus, {incompatability}")
                else:
                    generate(ic1)
                    write(len(report), '')
                    generate(ic2)
                    write(len(report), '')
                    write(incompatability,
                          f"So, because {ic1} ({report[ic1][0]}) and {ic2} ({report[ic2][0]}), {incompatability}")
            elif ic1.internal_cause or ic2.internal_cause:
                dr = ic1 if ic1.internal_cause else ic2
                ex = ic1 if ic2 is dr else ic2

                dl, el = report.get(dr), report.get(ex)
                if dl:
                    write(incompatability, f"Because {ex} and {dr} ({dl[0]}), {incompatability}")
                elif bool(dr.internal_cause[0].internal_cause) ^ bool(dr.internal_cause[1].internal_cause):
                    prior_dr = dr.internal_cause[0] if dr.internal_cause[0].internal_cause else dr.internal_cause[1]
                    prior_ex = dr.internal_cause[0] if prior_dr is dr.internal_cause[1] else dr.internal_cause[1]
                    generate(prior_dr)
                    write(incompatability, f"And because {prior_ex} and {ex}, {incompatability}")
                else:
                    generate(dr)
                    write(incompatability, f"And because {ex}, {incompatability}")
            else:
                if ic2.external_cause.startswith("Compatible version for"):
                    write(incompatability, f"Because {ic1} which is unresolved, {incompatability}")
                else:
                    write(incompatability, f"Because {ic1} and {ic2}, {incompatability}")

        generate(self)
        lines = sorted(report.values(), key=lambda x: x[0])
        return '\n'.join(f"{line}) {text}" for line, text in lines)

    @classmethod
    def create(cls, terms: Iterable[Term],
               internal_cause: Optional[Tuple["Incompatibility", "Incompatibility"]] = None,
               external_cause: Optional[str] = None) -> "Incompatibility":

        grouped_terms: Dict[PKG, List[Term]] = defaultdict(list)
        for term in terms:
            grouped_terms[term.package].append(term)

        normalized_terms = [Term.join(package, terms)
                            for package, terms in grouped_terms.items()]

        sorted_terms = sorted(normalized_terms, key=lambda x: str(x.package))
        return cls(tuple(sorted_terms), internal_cause, external_cause)

    def update_inavailability(self, new_constraint: VersionSpecifier):
        assert len(self.terms) == 1, 'attempting to update terms for non inavailability incompatability'
        self.terms = (replace(self.terms[0], constraint=new_constraint),)
        self.external_cause = f'Compatible version for {self.terms[0]} not found'


class DependencyIncompatibility(Incompatibility):
    def __init__(self, dependant: Term, dependency: Term):
        super().__init__(
            tuple(sorted([dependency.negate(), dependant], key=lambda x: str(x.package))), None,
            f"{dependant} depends on {dependency}")

        self.dependant = dependant
        self.dependency = dependency
        self.added = False

    def check_satisfaction(self, solution: "PartialSolution") -> IncompatibilitySatisfaction:
        if dependant_assignments := solution.assignments_by_package[self.dependant.package]:
            dependant_assignment = dependant_assignments[-1]
            acc = dependant_assignment.accumulated

            if acc.allows_any(self.dependant.constraint) or \
                    (acc is not RestrictAllVersions and self.dependant.constraint.allows_all(acc)):
                return super().check_satisfaction(solution)

        return IncompatibilitySatisfaction.create_unsatisfied(self)

    def update_dependant(self, new_dependant: Term):
        package = str(new_dependant.package)
        assert package == str(self.dependant.package), \
            "attempting to update dependency incompatibility with a term that does not belongs to it"

        self.dependant = new_dependant
        self.terms = tuple(sorted([self.dependency.negate(), new_dependant], key=lambda x: str(x.package)))
        self.external_cause = f"{new_dependant} depends on {self.dependency}"


@dataclass
class _PackageVersion:
    term: Term
    # the effective range of this version (v2.0.0 -> range >=1.7.3, <1.0.1)
    effective_constraint_range: VersionSpecifier = AllowAllVersions
    dependencies: Optional[Dict[PKG, "PackageDependency"]] = None
    next: Optional["_PackageVersion"] = None

    @property
    def version(self) -> Version:
        return cast(VersionMatch, self.term.constraint).version

    def fetch_dependencies_info(self, problem: Problem):
        if not self.dependencies:
            version_dependencies = problem.get_dependencies(self.term.package, self.version)
            self.dependencies = {
                d.package: PackageDependency(d)
                for d in version_dependencies}

    def compute_incompatibilities(self) -> List[Incompatibility]:
        result: List[Incompatibility] = []
        for dependency in self.dependencies.values():
            last_requiring = self

            while last_requiring.next:
                nxt = last_requiring.next
                nxt_deps = nxt.dependencies
                if not nxt_deps:
                    break

                nxt_dep = nxt_deps.get(dependency.term.package)
                if not nxt_dep or nxt_dep.term.constraint != dependency.term.constraint:
                    break

                last_requiring = nxt

            if last_requiring is not self:
                incompatibility = last_requiring.dependencies[dependency.term.package].incompatibility
                if incompatibility:
                    result.append(incompatibility)
                    incompatibility.update_dependant(
                        Term(self.term.package,
                             incompatibility.dependant.constraint.union_with(self.effective_constraint_range)))
                    continue

            nt = Term(self.term.package, self.effective_constraint_range)
            dependency.incompatibility = DependencyIncompatibility(nt, dependency.term)
            result.append(dependency.incompatibility)

        return result

    def __repr__(self):
        return f"V({self.term})"


@dataclass
class PackageDependency:
    term: Term
    incompatibility: Optional[DependencyIncompatibility] = None


class Problem(ABC):
    """
    represents the input for the pubgrub algorithm = the problem it attempts to solve.
    """

    @abstractmethod
    def get_dependencies(self, package: PKG, version: Version) -> List[Term]:
        """
        :param package: the package name to get dependencies to
        :param version: the required version of the `package`
        :return: list of dependencies for the given `package` and `version`
        """

    @abstractmethod
    def get_versions(self, package: PKG) -> List[StandardVersion]:
        """
        get the available (standard) versions of the given package in importance order
         (first is more important than last)
        :param package: the package name to look for version in
        :return: versions of the package ordered by importance
        """

    @abstractmethod
    def has_version(self, package: PKG, version: Version) -> bool:
        """
        checks for the existence of the given `version`
        :param package: the package to check
        :param version: the version to check
        :return: True if the given package and version pair could be found, False otherwise
        """


class Solver(Generic[PKG_T]):

    def __init__(self, problem: Problem, root_package: PKG_T = 'root'):
        self._root_package = root_package
        self._problem = problem
        self._solution = PartialSolution(root_package)
        self._package_versions: Dict[PKG, List[_PackageVersion]] = {}
        self._package_availability_incompatibilities: Dict[PKG, Incompatibility] = {}
        self._package_trouble_level: Counter[PKG] = Counter()

        # incompatibilities by package
        self._incompatibilities: DefaultDict[PKG, List[Incompatibility]] = defaultdict(list)

    def _add_incompatibility(self, incompatibility: Incompatibility):
        if isinstance(incompatibility, DependencyIncompatibility):
            if incompatibility.added:
                return True
            incompatibility.added = True

        # print(f'adding incompatibility: {incompatibility}')
        for term in incompatibility.terms:
            term_incompatibilities = self._incompatibilities[term.package]
            if incompatibility not in term_incompatibilities:
                term_incompatibilities.append(incompatibility)

    def solve(self) -> Dict[PKG_T, Version]:
        with DependencyResolutionMonitoredOp() as mop:
            root_term = self.package_versions(self._root_package)[0].term
            self._add_incompatibility(
                Incompatibility.create([root_term.negate()], external_cause='Root Project'))

            self._solution.require([root_term.package])

            next_package = root_term.package
            while next_package is not None:
                self._solution.notify_state(next_package, mop)
                # print(f"trying to solve for {next_package}, already decided on: {self._solution.decisions()}")
                self._propagate(next_package)
                next_package = self._make_next_decision()

            # print(f"reached into conclusion: {self._solution.decisions()}")
            DependencyResolutionConclusionEvent(self._solution.decisions()).notify(mop)
            return self._solution.decisions()

    def _propagate(self, next_package: PKG):

        # print("#### unit propagation ####")
        changed = {next_package}

        while changed:
            package = changed.pop()

            for incompatibility in list(reversed(self._incompatibilities[package])):
                satisfaction: IncompatibilitySatisfaction = incompatibility.check_satisfaction(self._solution)
                if satisfaction.is_full():
                    # print(f"incompatibility: {incompatibility} satisfied, entering conflict resolution")
                    changed.add(self._resolve_conflict(incompatibility, satisfaction))

                elif satisfaction.is_almost_full():
                    term = satisfaction.undecided_term
                    # print(f"incompatibility {incompatibility} is almost full, undecided_term is {term}")
                    self._solution.assign(term.negate(), incompatibility)
                    changed.add(term.package)

    def _is_tautology(self, incompatibility: Incompatibility) -> bool:
        return not (terms := incompatibility.terms) or \
               (len(terms) == 1 and terms[0].package == self._root_package)

    def _resolve_conflict(
            self, incompatibility: Incompatibility, satisfaction: IncompatibilitySatisfaction) -> PKG:

        # print("#### conflict resolution ####")
        original_incompatibility = incompatibility

        while True:
            # print(f"enter conflict resolution loop with {incompatibility}")
            for term in incompatibility.terms:
                self._package_trouble_level[term.package] += 1

            if self._is_tautology(incompatibility):
                raise UnsolvableProblemException(incompatibility)

            satisfier = satisfaction.satisfier
            term = incompatibility.term_for(satisfier.term.package)

            prev_satisfier = satisfaction.prev_satisfier
            prev_satisfier_level = prev_satisfier.decision_level if prev_satisfier else 0
            # print(f"satisfier: {satisfier}, prev_satisfier: {prev_satisfier}")

            if satisfier.is_decision() or prev_satisfier_level < satisfier.decision_level:
                self._solution.backtrack(prev_satisfier_level)
                if incompatibility is not original_incompatibility:
                    self._add_incompatibility(incompatibility)

                satisfaction = incompatibility.check_satisfaction(self._solution)
                assert satisfaction.is_almost_full(), \
                    "new incompatibility resulted after conflict resolution is not almost satisfied"

                term = satisfaction.undecided_term
                # print(f"conflict happened because {term}, rejecting this assignment from now on")
                self._solution.assign(term.negate(), incompatibility)
                return term.package

            prior_cause_terms: Set[Term] = {
                term for term in chain(incompatibility.terms, satisfier.cause.terms)
                if term.package != satisfier.term.package}

            assert satisfier.cause != incompatibility  # this massup the error reporting...
            if not satisfier.term.satisfies(term.constraint) or not prior_cause_terms:
                prior_cause_terms.add(
                    Term(satisfier.term.package,
                         # satisfier.term.constraint.difference_from(term.constraint).inverse()))
                         satisfier.accumulated.difference_from(term.constraint).inverse()))

            prev_incompatibility = incompatibility
            incompatibility = Incompatibility.create(
                list(prior_cause_terms), internal_cause=(satisfier.cause, incompatibility))

            if len(prior_cause_terms) == 0:
                self._solution.backtrack(0)
                self._solution.assign(Term(term.package, RestrictAllVersions), cause=incompatibility)
                return term.package

            # print(f"root cause: {incompatibility}")

            if not self._is_tautology(incompatibility):
                satisfaction = incompatibility.check_satisfaction(self._solution)
                assert satisfaction.is_full(), \
                    f"incompatibility: {prev_incompatibility} resulted in " \
                    f"root cause: {incompatibility} that is not satisfied"

    def package_versions(self, package: PKG) -> List[_PackageVersion]:
        versions = self._package_versions.get(package)
        if not versions:
            versions = self._package_versions[package] = [
                _PackageVersion(Term(package, VersionMatch(ver)))
                for ver in self._problem.get_versions(package)]

            sorted_versions = sorted(versions, key=lambda v: v.version)

            for i in range(len(versions) - 1):
                sorted_versions[i].next = sorted_versions[i + 1]

            if len(sorted_versions) == 1:
                sorted_versions[0].effective_constraint_range = AllowAllVersions
            elif sorted_versions:
                for i in range(1, len(versions) - 1):
                    sorted_versions[i].effective_constraint_range = VersionSpecifier.create_range(
                        min_=cast(StandardVersion, sorted_versions[i - 1].version),
                        max_=cast(StandardVersion, sorted_versions[i].version), includes_max=True)

                sorted_versions[0].effective_constraint_range = VersionSpecifier.create_range(
                    max_=cast(StandardVersion, sorted_versions[0].version), includes_max=True)
                sorted_versions[-1].effective_constraint_range = VersionSpecifier.create_range(
                    min_=cast(StandardVersion, sorted_versions[-2].version))

        return versions

    def _attempt_minor_adjustments(self, package: PKG, conflicts: List[Incompatibility]) -> bool:
        # attempt the minor adjustment heuristic: the idea is that if this package cannot be selected
        # because we previously chose incompatible version of one of its dependencies then we check
        # what was the actual limitation of this dependency when we chose its version, if the limitation allows
        # the required version, we backtrack to remove this assignment and instead assign this package version
        # which will cause the dependency to be adjusted and chosen correctly

        minor_adjustment_dlevel = -1
        for conflict in conflicts:
            dependency: Term = find_first(conflict.terms, lambda it: it.package != package)
            dependency_assignments = self._solution.assignments_by_package[dependency.package]
            dependency_requirement = dependency.constraint.inverse()
            if len(dependency_assignments) > 1 and dependency_assignments[-1].is_decision():
                actual_limitation = dependency_assignments[-2].accumulated
                if actual_limitation.allows_any(dependency_requirement):
                    # print(f"{package} is conflicting with {dependency.package}, it requires that ", end='')
                    # print(f"{dependency_requirement} but it actual limitation in solution is '{actual_limitation}'")
                    dlevel = dependency_assignments[-1].decision_level - 1
                    minor_adjustment_dlevel = dlevel if minor_adjustment_dlevel == -1 \
                        else min(dlevel, minor_adjustment_dlevel)
                else:
                    minor_adjustment_dlevel = -1
                    break

        if minor_adjustment_dlevel >= 0 \
                and self._solution.requirement_decision_level(package) <= minor_adjustment_dlevel:
            # print(f"applying minor adjusments heuristic - backtracking to {minor_adjustment_dlevel}")
            self._solution.backtrack(minor_adjustment_dlevel)
            return True

        return False

    def _make_next_decision(self) -> Optional[PKG]:
        # print("#### decision ####")
        undecided_packages = self._solution.undecided_packages()
        if not undecided_packages:
            return None

        # print(f"undecided packages: {undecided_packages}")
        package_matching_versions: Dict[PKG, List[_PackageVersion]] = {}
        for package in undecided_packages:
            acc_assignment = self._solution.assignments_by_package[package][-1].accumulated

            if isinstance(acc_assignment, VersionMatch) and acc_assignment.allow and \
                    not isinstance(acc_assignment.version, StandardVersion):

                if self._problem.has_version(package, acc_assignment.version):
                    package_matching_versions[package] = [
                        _PackageVersion(Term(package, acc_assignment), acc_assignment)]
                else:
                    package_matching_versions[package] = []
            else:
                versions = self.package_versions(package)
                package_matching_versions[package] = [pver for pver in versions if
                                                      acc_assignment.allows_version(pver.version)]

        package = min(undecided_packages,
                      key=lambda pack: (-self._package_trouble_level[pack], len(package_matching_versions[pack])))

        # print(f"choosing to try and assign {package} with constraint: ", end='')
        # print(f"{self._solution.assignments_by_package[package][-1].accumulated}")
        versions = list(package_matching_versions[package])  # defensive copy because we might change it

        while True:
            if not versions:
                acc_assignment = self._solution.assignments_by_package[package][-1].accumulated

                if ic := self._package_availability_incompatibilities.get(package):
                    ic.update_inavailability(ic.terms[0].constraint.union_with(acc_assignment))
                else:
                    # print(f"could not find version that match {acc_assignment}")
                    ic = Incompatibility.create(
                        [Term(package, acc_assignment)],
                        external_cause=f'Compatible version for [{package} {acc_assignment}] not found')
                    self._package_availability_incompatibilities[package] = ic
                    self._add_incompatibility(ic)
                return package

            version = versions.pop(0)
            # print(f"version: {version} match our term")

            try:
                version.fetch_dependencies_info(self._problem)
            except MalformedPackageException:
                import traceback
                traceback.print_exc()
                print(f"version: {version} discovered to be malformed")
                continue  # retry with another version
            break

        incompatibilities = self._add_dependency_incompatibilities(version)

        assignment: Assignment = self._solution.make_assignment(Term(package, VersionMatch(version.version)), None)
        assignments = self._solution.assignments_by_package
        assignments[package].append(assignment)
        # print(f"checking if we can still assign {version} after the new incompatibilities: {incompatibilities}")
        conflicts = list(filter(lambda it: it.check_satisfaction(self._solution).is_full(), incompatibilities))
        assignments[package].pop()

        if conflicts and self._attempt_minor_adjustments(package, conflicts):
            conflicts = []

        if not conflicts:
            # print("we can!")
            self._solution.assign(assignment)
            self._solution.require(version.dependencies.keys())
        else:
            # print(f"we cant.. ({conflicts})")
            ...

        return package

    def _add_dependency_incompatibilities(self, version: _PackageVersion) -> List[Incompatibility]:
        incompatibilities = version.compute_incompatibilities()
        for incompatibility in incompatibilities:
            self._add_incompatibility(incompatibility)

        return incompatibilities
