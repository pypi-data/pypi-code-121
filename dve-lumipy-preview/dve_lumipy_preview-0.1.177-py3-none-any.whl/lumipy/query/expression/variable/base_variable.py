from abc import abstractmethod


class BaseVariable:
    """Base class for Luminesce variable expressions. All @/@@ variables must inherit from this class so they can be
    tracked in the BaseExpression class' dependency resolution.

    """

    @abstractmethod
    def __init__(self, at_prefix: str, var_name: str, sql_def: str):
        """__init__ method of the BaseVariable class.

        Args:
            at_prefix (str): luminesce variable prefix syntax string. Valid values are @ (table) @@ (scalar)
            var_name (str): name of the variable. Must not conflict with SQL keywords.
            sql_def (str): SQL string that defines the variable's content.
        """
        if any(var_name.lower() == pn for pn in protected_names):
            raise ValueError(f"Variable name was equal to a protected sql string: {var_name}.")
        self._at_prefix = at_prefix
        self._var_name = var_name
        self._sql_def = sql_def

    def get_assignment_sql(self) -> str:
        """Get the assignment SQL string of the variable.

        Returns:
            str: assignment string.
        """
        return f"{self._at_prefix}{self._var_name} = {self._sql_def};"

    def get_sql(self) -> str:
        """Get the SQL string that the variable resolves to when used in other expressions. This will be it's name
        prefixed by the @s.

        Returns:
            str: teh variable's SQL string value.
        """
        return f"{self._at_prefix}{self._var_name}"

    def get_at_var_name(self) -> str:
        """Get the name of the variable.

        Returns:
            str: the variable's name.
        """
        return self._var_name

    def __hash__(self):
        return hash(self.get_assignment_sql())


protected_names = [
    'select', 'distinct', 'where',
    'order', 'by', 'group',
    'from', 'limit', 'as',
    'union', 'all'
]
