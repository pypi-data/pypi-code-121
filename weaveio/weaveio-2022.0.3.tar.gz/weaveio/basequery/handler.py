from typing import Dict, Set

from .actions import TraversalPath
from .hierarchy import *
from .tree import BranchHandler


class Handler:
    def __init__(self, data: 'Data'):
        self.data = data
        self.branch_handler = data.branch_handler  # type: BranchHandler

    def begin_with_heterogeneous(self):
        return HeterogeneousHierarchyFrozenQuery(self, self.branch_handler.entry)

    def hierarchy_from_neo4j_identity(self, htype, identity):
        begin = self.branch_handler.begin(htype.__name__)
        new = begin.add_data(identity)
        identifier_var = new.current_variables[0]
        branch = new.filter('id({h}) = {identifier}', h=begin.current_hierarchy, identifier=identifier_var)
        return DefiniteHierarchyFrozenQuery(self, branch, htype, branch.current_hierarchy, [], None)

    def paths2factor(self, factor_name: str,  plural: bool,
                     start: Type[Hierarchy] = None) -> Tuple[Dict[Type[Hierarchy], Set[TraversalPath]], Type[Hierarchy], bool, str]:
        """
        returns a dictionary of hierarchy: [path,...] and a shared hierarchy
        """
        factor_name = self.data.singular_name(factor_name)
        if start is None:
            starts = set(self.data.factor_hierarchies[factor_name])
            if len(starts) > 1:
                raise AmbiguousPathError(f"{factor_name} could refer to any of {starts}. Please traverse to the parent object first.")
            start = starts.pop()
        pathsetdict, base, factor_name = self.data.find_factor_paths(start, factor_name, plural)
        is_product = factor_name in base.products.keys()
        if len(pathsetdict) > 1:
            names = [i.__name__.lower() for i in pathsetdict.keys()]
            plural = self.data.plural_name(factor_name)
            warn(f"This query for {factor_name} is ambiguous and will return all {plural} "
                 f"for each of the following:\n {', '.join(names)}.\n"
                 f"If this is not what you intended, you can use `.{names[0]}` before `{factor_name}` to choose only {plural} from {names[0]}",
                 SyntaxWarning)
        return pathsetdict, base, is_product, factor_name


    def paths2hierarchy(self, hierarchy_name, plural,
                        start: Type[Hierarchy] = None) -> Tuple[List[TraversalPath], List[Type[Hierarchy]], Type[Hierarchy], Type[Hierarchy]]:
        """
        Returns:
            list of possible paths
            list of hierarchies those paths end with
            the shared start hierarchy
            the shared end hierarchy
        """
        if start is None:
            end = self.data.singular_hierarchies[self.data.singular_name(hierarchy_name)]
            return [], [end], None, end
        return self.data.find_hierarchy_paths(start, self.data.singular_hierarchies[self.data.singular_name(hierarchy_name)], plural)
