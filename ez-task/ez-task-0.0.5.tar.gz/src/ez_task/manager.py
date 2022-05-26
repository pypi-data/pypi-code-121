from typing import Callable, List, Tuple

from .types.health_check import HealthCheck
from .task import Task

class TaskManager():

    def __init__(self, daemon=True, use_gatherer=True) -> None:
        self._task_list: List[Task] = []
        self.daemon: bool = daemon
        self.use_gatherer: bool = use_gatherer

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        try:
            self.terminate_tasks()
        except Exception as e:
            print(e)
            return

    def define_task(self, target: Callable) -> Task:
        """
        Creates a managed instance of the Task object.

        A Task will call the target parameter whenever Task.run is invoked

        Parameters
        ----------
        target : Callable
            Any top level python function or callable class attribute

        Returns
        -------
        Task
            An instance of ez_task.task.Task 

        """
        task = self._add_task(target)
        return task

    def define_task_set(self, *targets: Tuple[Callable]) -> List[Task]:
        """
        Creates multiple managed instances of the Task object and sends a dummy health check to ready the pipe.
        Preferable if Tasks need to be available in the future with low latency

        A Task will call the target parameter whenever Task.run is invoked

        Parameters
        ----------
        targets : Tuple[Callable]
            A list of any top level python function or callable class attribute

        Returns
        -------
        Tuple[Task]
            An instance of ez_task.task.Task 

        """
        tasks: List[Task] = []
        for target in targets:
            task = self._add_task(target)
            tasks.append(task)
        
        return (*tasks,)

    def terminate_tasks(self) -> None:
        """
        Terminates all managed Task instances along with their respective resources.
        Returns
        -------
        None
        """
        for task in self._task_list:
            task.terminate()

    def _add_task(self, target: Callable) -> Task:
        """
        <Private> Initializes task and adds it to manager self._task_list

        Parameters
        ----------
        target : Callable
            Any top level python function or callable class attribute

        Returns
        -------
        Task
            An instance of ez_task.task.Task 

        """
        task: Task = Task(target, daemon=self.daemon, manager=self, use_gatherer=self.use_gatherer)
        self._task_list.append(task)
        task._blocking_health_check()
        task.run(HealthCheck())
        task.get_result()
        return task

        




    



