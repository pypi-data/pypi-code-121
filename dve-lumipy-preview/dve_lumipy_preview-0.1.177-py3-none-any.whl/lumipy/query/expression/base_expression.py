from lumipy.common.string_utils import prettify_tree, connector, indent_str
from termcolor import colored
from lumipy.common.lockable import Lockable
from lumipy.atlas.field_metadata import FieldMetadata
from lumipy.atlas.base.base_provider_factory import BaseProviderFactory
from abc import abstractmethod
from typing import Callable, Union, List, Tuple, Set, Dict
import lumipy.query.expression.sql_value_type as svt


class BaseExpression(Lockable):
    """Base class for all Lumipy query expression classes.

    An expression is a node in a directed acyclic graph that represents the operations that build up a SQL query to
    Luminesce.

    The function of this class is to implement the basic functionality around labelling
    the expression classes, checking their input types, declaring output type, handling their hashes/string
    representation and keeping track of the expression graph (each expression must track and declare its parent inputs).

    An expression can have arbitrarily many inputs, but must only have one output. That one output can be a value
    that's made up of other values such as an array or a table.
    """

    @abstractmethod
    def __init__(
            self, op_name: str,
            type_check_fn: Callable,
            return_type_fn: Callable,
            *values: Union['BaseExpression', BaseProviderFactory, FieldMetadata]
    ):
        """__init__ method for the BaseExpression class.

        Args:
            op_name (str): name for the operation this class represents (e.g. 'add' or 'select').
            type_check_fn (Callable): function that checks the sql value types of the parents.
            return_type_fn (Callable): function that determines the output sql value type of this expression.
            *values (Union['BaseExpression', ProviderDefinition, FieldDefinition]): input values to the expression
        """

        if len(values) == 0:
            raise ValueError("Expression supplies nothing to *values in BaseExpression ctor.")

        if not callable(type_check_fn):
            raise ValueError("Value supplied to type_check_fn arg is not a callable.")

        if not callable(return_type_fn):
            raise ValueError("Value supplied to return_type_fn arg is not a callable.")

        def type_check_failure(t):
            return not issubclass(t, BaseExpression) and t != FieldMetadata and not issubclass(t, BaseProviderFactory)

        if any(type_check_failure(type(v)) for v in values):
            raise TypeError(
                f"Input types to {type(self).__name__} must be FieldDescription, ProviderDescription, "
                f"or BaseExpression subclass. Were {', '.join(type(v).__name__ for v in values)}."
            )

        if not type_check_fn(*[v.get_type() for v in values]):
            types = ', '.join(v.get_type().name for v in values)
            raise TypeError(f"Input types invalid for expression '{op_name}'. Types: ({types})")

        self._op_name = op_name
        self._type = return_type_fn(*[v.get_type() for v in values])
        self._lineage = values
        self._validate()
        self._gather_dependencies()
        super().__init__()

    def __str__(self):
        def parent_str(p):
            if issubclass(type(p), BaseExpression):
                return str(p)
            elif isinstance(p, FieldMetadata):
                return f"{p.table_name}: {p.field_name}"
            else:
                return str(p)

        parents = indent_str('\n'.join(map(parent_str, self._lineage)), n=3)
        out_str = ''
        out_str += f"{connector}{self._type.name}\n"
        out_str += indent_str(f"{connector}[{colored(self._op_name.upper(), 'blue')}]\n{parents}")

        return prettify_tree(out_str)

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(sum(hash(p) for p in self._lineage)+hash(self._op_name))

    def get_lineage(self) -> Tuple[Union['BaseExpression', BaseProviderFactory, FieldMetadata]]:
        """Return the parent values input to this expression.

        Returns:
            Tuple[Union['BaseExpression', ProviderDefinition, FieldDefinition]]: parent values.

        """
        return self._lineage

    def get_op_name(self) -> str:
        """Get the name that labels this operation.

        Returns:
            str: op name string.
        """
        return self._op_name

    def get_type(self) -> svt.SqlValType:
        """Get the SQL value type that this expression resolves to.

        Returns:
            SqlValType: enum denoting the SQL value type returned.

        """
        return self._type

    def hash_equals(self, other):
        """Compare to another object via hash value. The '==' operator is expected to be overloaded.

        Args:
            other: other object to compare to.

        Returns:
            bool: whether their hashes match.
        """
        return hash(self) == hash(other)

    # noinspection PyArgumentList
    def _gather_dependencies(self):
        """Check the lineage of this expression and its parents for dependencies on @/@@ vars
        and source columns. If present, carry them along so they're available for the child expressions
        of this expression.

        """

        # Dependency tracking:
        # @ and @@ variable dependencies
        from lumipy.query.expression.variable.base_variable import BaseVariable
        # Get the at var dependencies of this expression
        at_var_dependencies = [p for p in self._lineage if issubclass(type(p), BaseVariable)]
        # Then add the dependencies of the parents too
        for parent in self._lineage:
            if not issubclass(type(parent), BaseExpression):
                # Skip literals
                continue

            for parent_dep in parent.get_at_var_dependencies():
                if not any(parent_dep.hash_equals(c) for c in at_var_dependencies):
                    at_var_dependencies.append(parent_dep)
        self._at_var_dependencies = at_var_dependencies

        # Column dependencies
        from lumipy.query.expression.column.source_column import SourceColumn
        # Get the col dependencies of this expression
        col_dependencies = [p for p in self._lineage if type(p) == SourceColumn]
        # Then add the dependencies of the parents too
        for parent in self._lineage:
            if not issubclass(type(parent), BaseExpression):
                # Skip literals
                continue

            for parent_dep in parent.get_col_dependencies():
                if not any(parent_dep.hash_equals(c) for c in col_dependencies):
                    col_dependencies.append(parent_dep)

        self._col_dependencies = col_dependencies

    def _validate(self):
        """Check that the information contained in the expression is valid.

        Every expression should have a valid lineage and a valid expression value type.
        """

        if self._lineage is None or len(self._lineage) == 0:
            raise ValueError(
                "Expression has no lineage: all inheritors of BaseExpression must declare their lineage. "
                "Recommended way is to call the __init__() of BaseExpression"
            )
        if not isinstance(self._type, svt.SqlValType):
            raise TypeError(
                "Expression type field is not an ArgType: all expression must declare their "
                "return type using the ArgType enum."
            )

    # noinspection PyUnresolvedReferences
    # import will cause circular reference
    def get_col_dependencies(self) -> List['SourceColumn']:
        """Get the source table columns that this expression depends on somewhere in its lineage.

        Returns:
            Set[SourceColumn]: list of source column dependencies.
        """
        return self._col_dependencies

    # noinspection PyUnresolvedReferences
    # import will cause circular reference
    def get_at_var_dependencies(self) -> List['BaseVariable']:
        """Get the @/@@ variables that this expression depends on somewhere in its lineage.

        Returns:
            List[BaseVariable]: List of @ or @@ variable dependencies.
        """
        return self._at_var_dependencies

    def get_decomposition(self, truncate_variables: bool = False) -> Dict['BaseExpression', List[int]]:
        """Get decomposition of expression into a dictionary its component parts and their parent hash values.

        Args:
            truncate_variables (bool): whether to truncate table or scalar variables from the graph.

        Returns:
            Dict[BaseExpression, List[int]]: the decomposition dictionary.
        """

        from lumipy.query.expression.variable.base_variable import BaseVariable
        decomposition = {}

        def flatten(x):
            if issubclass(type(x), BaseExpression) and not (truncate_variables and issubclass(type(x), BaseVariable)):

                if hash(x) not in [hash(k) for k in decomposition.keys()]:
                    decomposition[x] = [hash(p) for p in x.get_lineage()]
                for p in x.get_lineage():
                    flatten(p)

        flatten(self)
        return decomposition
