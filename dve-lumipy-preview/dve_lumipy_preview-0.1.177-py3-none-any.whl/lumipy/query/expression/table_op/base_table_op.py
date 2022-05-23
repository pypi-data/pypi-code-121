from abc import abstractmethod
from typing import List, Union, Optional

import networkx as nx
from pandas import DataFrame

from lumipy.client import Client
from lumipy.query.expression.base_expression import BaseExpression
from lumipy.query.expression.column.column_base import BaseColumnExpression
from lumipy.query.expression.table.base_table import BaseTable
from lumipy.query.expression.variable.base_variable import BaseVariable
from lumipy.query.query_job import QueryJob
from lumipy.query.expression.column_op.binary_op import RandomUniformFloat


class BaseTableExpression(BaseTable):
    """Base class for all expression that represent an operation on a whole table that resolves to another table
    such as 'select' or 'where' and resolves to valid SQL that can be sent off to Luminesce using the .go() method.

    Each table expression will manifest the columns it contains as public members as it inherits from BaseTable.

    All table expressions are built to support building up SQL table ops via method chaining. The design is that one
    starts with a source table (inheritor of BaseSourceTable class) and then chains table operation expressions
    (BaseTableExpression) of it and later child table operation expressions.
    Each table expression needs to pass along the source table it relates back to, the web client, the select type of
    the initial select statement (distinct or not) and it's immediate table expression ancestor (parent).

    Inheritors must implement the following methods:
        get_table_sql(self) -> str: function that builds the SQL string that the table expression resolves to
        (but not the @/@@ var assignment SQL)
        make_copy_with_auto_alias_cols(self) -> type(self): function that creates a version of the table expression
        where the columns that are functions of columns are automatically aliased. This is for when the expression is
        converted to an @ var (table variable).

    """

    @abstractmethod
    def __init__(
            self,
            columns: List[BaseColumnExpression],
            client: Client,
            table_op_name: str,
            select_type: Union[str, None],
            source_table: 'BaseSourceTable',
            parent_arg: BaseExpression,
            *args: BaseExpression
    ):
        """__init__ method of the BaseTableExpression class.
        
        Args:
            columns (List[BaseColumnExpression]): list of columns that are members of the table expression
            client (Client): web api client for sending query requests off to.
            table_op_name (str): name labelling the table op this class represents.
            select_type (str): the select type of the expression (whether select/select distinct is in the lineage)
            source_table (BaseSourceTable): source table of the table expression chain.
            parent_arg (BaseExpression): main parent expression of this table expresion (e.g. select passed into a where
            expression: source_table.select('*').where(...))
            *args (BaseExpression): other expression arguments for the table expression.
        """
        self._source_table = source_table
        self._parent = parent_arg
        self._select_type = select_type

        super().__init__(
            self._source_table.validate_source_columns(columns),
            client,
            table_op_name,
            parent_arg,
            *args
        )

    def get_select_type(self) -> str:
        """Get the select type string ('select' or 'select distinct')

        Returns:
            str: the select type
        """
        return self._select_type

    @abstractmethod
    def get_table_sql(self) -> str:
        """Get the SQL string for the table expression only. Not including the @/@@ var assignments.

        Returns:
            str: the table SQL string.
        """
        raise NotImplementedError

    def variable_sql(self) -> str:
        """Construct the SQL string that does the assignment of Luminesce @/@@ variables.

        Returns:
            str: the assignment SQL string for all of the @/@@ vars this expression depends on.
        """
        if self.get_at_var_dependencies() is not None and len(self.get_at_var_dependencies()) > 0:
            # Sort the dependencies by whether they depend on another
            dependencies = self._resolve_at_var_dependency_order()
            return '\n\n'.join(s.get_assignment_sql() for s in dependencies) + '\n\n'
        else:
            return ''

    def get_sql(self) -> str:
        """Return the SQL string that this expression resolves to.

        Returns:
            str: the SQL string.
        """
        return f"{self.variable_sql()}{self.get_table_sql()}"

    def print_sql(self):
        """Print the SQL that this expression resolves to.

        """
        print(self.get_sql())

    def _resolve_at_var_dependency_order(self) -> List[BaseVariable]:
        """Resolve the dependency order of the @/@@ variables that this table expression requires.

        Table expressions can depend on @/@@ variables that in turn depend on @/@@ variables and so on. An @ variable
        that depends on another can't be above the one it depends on in the final SQL query string to Luminesce. This
        method constructs a directed acyclic graph in networkx (a graph analytics package) that represents these
        dependencies. Functionality in networkx is then used to count how many descendents each @/@@ var has and
        then the vars are returned as a list ordered by this number. The ones with most descendents are the ones with
        the most dependencies and they can be put at the top, and so on.

        Returns:
            List[BaseVariable]: list of @/@@ variable expressions ordered by dependency.
        """

        # Construct the DAG
        at_var_to_label = {at_var: i for i, at_var in enumerate(self.get_at_var_dependencies())}
        dag = nx.DiGraph()
        for at_var, i in at_var_to_label.items():
            dag.add_node(i, at_var=at_var)

        for at_var in at_var_to_label.keys():
            for dep in at_var.get_at_var_dependencies():
                u = at_var_to_label[dep]
                v = at_var_to_label[at_var]
                dag.add_edge(u, v)

        dag = nx.relabel.relabel_nodes(dag, {i: at_var.get_sql() for at_var, i in at_var_to_label.items()})

        # Count descendents and create sorted list
        def count_dependencies(n):
            return len(nx.algorithms.dag.descendants(dag, n))

        n_descendants = {n: count_dependencies(n) for n in dag.nodes}
        dependencies = []
        for k in sorted(n_descendants, key=n_descendants.get, reverse=True):
            dependencies.append(dag.nodes[k]['at_var'])

        return dependencies

    def to_scalar_var(self, var_name: Optional[str] = None) -> 'ScalarVariable':
        """Build a scalar variable (@@variable) expression from this table expression.

        Args:
            var_name (str): name to give to the scalar variable. Names that conflict with SQL keywords are not allowed
            and will raise an error.

        Returns:
            ScalarVariable: the scalar variable expression built from this table expression.
        """
        from lumipy.query.expression.variable.scalar_variable import ScalarVariable
        if var_name is None:
            var_name = f'sv_{str(hash(self))[1:]}'
        return ScalarVariable(var_name, self)

    def to_table_var(self, var_name: Optional[str] = None) -> 'TableVariable':
        """Build a table variable (@variable) expression from this table expression.

        Args:
            var_name: name to give to the table variable. Names that conflict with SQL keywords are not allowed
            and will raise an error.

        Returns:
            TableVariable: the table variable expression built from this table expression.

        """
        from lumipy.query.expression.variable.table_variable import TableVariable
        if var_name is None:
            var_name = f'tv_{str(hash(self))[1:]}'
        return TableVariable(var_name, self)

    def get_source_table(self) -> 'BaseSourceTable':
        """Get the source table expression object that this table expression depends on.

        Returns:
            BaseSourceTable: the source table of this table expression.
        """
        return self._source_table

    def go(self, fetch_page_size=100000) -> DataFrame:
        """Send query off to Luminesce, monitor progress and then get the result back as a pandas dataframe.

        Returns:
            DataFrame: the result of the query as a pandas dataframe.
        """
        job = self.go_async()
        job.interactive_monitor()
        result = job.get_result(fetch_page_size)
        return result

    def go_async(self) -> QueryJob:
        """Just send the query to luminesce. Don't monitor progress or fetch result.

        Returns:
            QueryJob: a job instance representing the query.
        """
        sql = self.get_sql()
        ex_id = self._client.start_query(f"-- built with fluent syntax\n{sql}")
        return QueryJob(ex_id, self.get_client())

    def to_drive(self, file_path) -> 'DriveSave':
        """Add an expression to the query that saves the result to drive.

        Args:
            file_path: the file path to the save location including the file format. File format is inferred from the
            file_path string (i.e. /A/B/C/file.csv will save as a csv at directory /A/B/C)

        Returns:
            DriveSave: DriveSave instance representing the save to drive expression.
        """

        drive_path = "/".join(file_path.split('/')[:-1]) + '/'
        name = file_path.split('/')[-1].split('.')[0]
        file_type = file_path.split('.')[-1]
        input_tv = self.to_table_var()

        from lumipy.query.expression.direct_provider.save import DriveSave
        return DriveSave(
            drive_path=drive_path,
            client=self.get_client(),
            drive_file_type=file_type,
            **{name: input_tv}
        )

    def setup_view(self, provider_name: str) -> 'View':
        """Register this query as a view (like a virtual data provider). Once the query is run it will be
        available as a data provider in the atlas.

        Args:
            provider_name (str): name of the view provider that will be created/modified. Must be just alphanumerics and '.', '_'.

        Returns:
            View: View instance representing the query passed to the `Sys.Admin.SetupView` provider.
        """

        from lumipy.query.expression.direct_provider.view import View
        return View(provider_name, self)

    def sample(self, n: Optional[int] = None, frac: Optional[float] = None):
        """Build a random sample of a table expression result as another table variable.

        Args:
            n (Optional[int]): number of rows to sample and return
            frac (Optional[float]): fraction of the table to sample and return.

        Returns:
            TableVariable: table variable representing the table that results from the sampling.
        """

        if (n is None and frac is None) or (n is not None and frac is not None):
            raise ValueError("You must specify either n or frac but not both!")

        if n is not None and (not isinstance(n, int) or n < 1):
            raise ValueError("n must be an integer that is greater than 1. Did you mean to use frac=?")

        if frac is not None and (frac < 0 or frac > 1):
            raise ValueError("Frac must be a value between 0 and 1.")

        tv = self.to_table_var()

        if frac is not None:
            return tv.select('*').where(
                RandomUniformFloat(0, 1) < frac
            ).to_table_var()

        if n is not None:
            return tv.select('*').order_by(
                RandomUniformFloat(0, 1).ascending()
            ).limit(n).to_table_var()
