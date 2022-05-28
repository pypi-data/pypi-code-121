# from __future__ import annotations

import multiprocessing
import pathlib
from multiprocessing.context import BaseContext
from typing import Any, Dict, List, Literal, Optional, Union

from reil.agents.agent import Agent
from reil.agents.agent_demon import AgentDemon
from reil.environments.single import Single
from reil.environments.task import Task
from reil.subjects.subject import Subject
from reil.subjects.subject_demon import SubjectDemon

# TODO: Documentation


class Session:
    def __init__(
            self, name: str, path: Union[pathlib.PurePath, str],
            main_task: Task,
            agents: Dict[str, Union[Agent[Any, Any], str]],
            subjects: Dict[str, Union[Subject, str]],
            plans: Dict[str, Any],
            demons: Optional[Dict[
                str, Union[AgentDemon, SubjectDemon, str]]] = None,
            tasks_before: Optional[List[Task]] = None,
            tasks_after: Optional[List[Task]] = None,
            tasks_before_iteration: Optional[List[Task]] = None,
            tasks_after_iteration: Optional[List[Task]] = None,
            separate_process: Optional[List[Literal[
                'tasks_before',
                'tasks_after',
                'tasks_before_iteration',
                'tasks_after_iteration']]] = None,
            process_type: Optional[Literal[
                'spawn', 'fork', 'forkserver']] = None):

        self._environment = Single(
            name=name, path=pathlib.PurePath(path),
            demon_dict=demons or {})
        self._environment.add_entities(agents)  # type: ignore
        self._environment.add_entities(subjects)  # type: ignore
        self._environment.add_plans(plans)

        self._main_task = main_task
        self._tasks_before = tasks_before
        self._tasks_after = tasks_after
        self._tasks_before_iteration = tasks_before_iteration
        self._tasks_after_iteration = tasks_after_iteration

        self._separate_process = separate_process or []
        if separate_process:
            self._process_type = process_type or 'spawn'
        else:
            self._process_type = None

    @staticmethod
    def _run_tasks(
            task_list: Optional[List[Task]],
            environment: Single,
            iteration: int, separate_process: bool,
            context: Optional[BaseContext] = None):
        path = environment._path / environment._name
        p = None
        if task_list:
            for t in task_list:
                filename = f'{t._name}_{str(iteration)}'
                if separate_process and context:
                    environment.save(
                        filename=filename, path=path)
                    p = context.Process(
                        target=t.run_file, args=(filename, path, iteration))
                    p.start()
                else:
                    t.run_env(environment, iteration)

    def run(self):
        '''Run the session'''
        context = (multiprocessing.get_context(self._process_type)
                   if self._separate_process else None)

        self._run_tasks(
            task_list=self._tasks_before,
            environment=self._environment,
            iteration=0,
            separate_process='tasks_before' in self._separate_process,
            context=context)

        itr = 0
        for itr in range(itr, self._main_task.max_iterations):
            self._run_tasks(
                task_list=self._tasks_before_iteration,
                environment=self._environment,
                iteration=itr,
                separate_process=(
                    'tasks_before_iteration' in self._separate_process),
                context=context)

            # path = self._environment._path / self._environment._name
            # filename = f'{self._environment._name}_{str(itr)}'
            # self._environment.save(
            #     filename=filename, path=path)
            self._environment = self._main_task.run_env(
                self._environment, itr)

            self._run_tasks(
                task_list=self._tasks_after_iteration,
                environment=self._environment,
                iteration=itr,
                separate_process=(
                    'tasks_after_iteration' in self._separate_process),
                context=context)

        self._run_tasks(
            task_list=self._tasks_after,
            environment=self._environment,
            iteration=itr + 1,
            separate_process='tasks_after' in self._separate_process,
            context=context)

        path = self._environment._path / self._environment._name
        filename = (f'{self._environment._name}_'
                    + str(self._main_task.max_iterations))
        self._environment.save(
            filename=filename, path=path)
