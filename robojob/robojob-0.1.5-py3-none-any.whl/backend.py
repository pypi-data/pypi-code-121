
class NoBackend:
    def __init__(self):
        self.next_job_execution_id = 1
        self.next_task_execution_id = 1

    def before_job_execution(self, job_execution):
        job_execution.id = self.next_job_execution_id
        self.next_job_execution_id += 1

    def before_task_execution(self, job_execution, task_execution):
        task_execution.id = self.next_task_execution_id
        self.next_task_execution_id += 1

    def after_task_execution(self, job_execution, task_execution):
        pass

    def after_job_execution(self, job_execution):
        pass

    def close(self):
        pass

class SqlServerBackend:
    def __init__(self, connection):
        self.connection = connection

    def before_job_execution(self, job_execution):
        cursor = self.connection.execute(_JOB_EXECUTION_INSERT,
                                         job_execution.environment_name,
                                         job_execution.job_name,
                                         job_execution.status
                                         )
        ((job_execution.id,),) = cursor.execute("SELECT @@IDENTITY AS JobExecutionID")

    def before_task_execution(self, job_execution, task_execution):
        cursor = self.connection.execute(_TASK_EXECUTION_INSERT,
                                         job_execution.id,
                                         task_execution.__class__.__name__,
                                         task_execution.name,
                                         task_execution.status,
                                         )
        ((task_execution.id,),) = cursor.execute("SELECT @@IDENTITY AS TaskExecutionID")
        
        for name, value in sorted(task_execution.parameters.items()):
            if name.lower().endswith("password"):
                value = "[secret]"
            cursor.execute("INSERT INTO dbo.TaskExecutionParameter (TaskExecutionID, ParameterName, ParameterValue) VALUES (?, ?, ?);",
                            task_execution.id,
                            name,
                            str(value))

    def after_task_execution(self, job_execution, task_execution):
        self.connection.execute(_TASK_EXECUTION_UPDATE,
                                task_execution.status,
                                task_execution.error_message,
                                task_execution.id)

    def after_job_execution(self, job_execution):
        self.connection.execute(_JOB_EXECUTION_UPDATE,
                                job_execution.status,
                                job_execution.error_message,
                                job_execution.id)

    def close(self):
        self.connection.commit()
        self.connection.close()


_JOB_EXECUTION_INSERT = """
INSERT INTO dbo.JobExecution (
    EnvironmentName
  , JobName
  , StartedOn
  , Status
  )
VALUES (
    ? -- EnvironmentName
  , ? -- JobName
  , SYSUTCDATETIME() -- StartedOn
  , ? -- Status
  );
"""

_JOB_EXECUTION_UPDATE = """
UPDATE dbo.JobExecution
SET CompletedOn = SYSUTCDATETIME()
  , Status = ?
  , ErrorMessage = ?
WHERE JobExecutionID = ?;
"""

_TASK_EXECUTION_INSERT = """
INSERT INTO dbo.TaskExecution (
    JobExecutionID
  , TaskTypeName
  , TaskName
  , StartedOn
  , Status
  )
VALUES (
    ? -- JobExecutionID
  , ? -- TaskTypeName
  , ? -- TaskName
  , SYSUTCDATETIME() -- StartedOn
  , ? -- Status
)
"""

_TASK_EXECUTION_UPDATE = """
UPDATE dbo.TaskExecution
SET CompletedOn = SYSUTCDATETIME()
  , Status = ?
  , ErrorMessage = ?
WHERE TaskExecutionID = ?;
"""
