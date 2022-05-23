from .task_execution import TaskExecution


class StoredProcedureExecution(TaskExecution):
    def __init__(self, connection, schema_name, procedure_name):
        super().__init__(name=f"{schema_name}.{procedure_name}")
        self.connection = connection
        self.schema_name = schema_name
        self.procedure_name = procedure_name

    def bind_parameters(self, context_parameters):
        for (name,) in self.connection.execute(
                """
                SELECT PARAMETER_NAME
                FROM INFORMATION_SCHEMA.PARAMETERS
                WHERE SPECIFIC_SCHEMA = ? AND SPECIFIC_NAME = ?
                ORDER BY ORDINAL_POSITION
                """, self.schema_name, self.procedure_name):
            self.parameters[name] = context_parameters.get(name)

    def execute(self):
        parameter_names = list()
        parameter_values = list()
        for name, value in self.parameters.items():
            parameter_names.append(name)
            parameter_values.append(value)
        sql_parameter_list = ", ".join(f"{key} = ?" for key in parameter_names)
        execute_query = f"EXEC [{self.schema_name}].[{self.procedure_name}] {sql_parameter_list}"
        cursor = self.connection.cursor()
        cursor.execute(execute_query, parameter_values)
