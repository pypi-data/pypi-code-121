import pathlib
from typing import Dict, List, Optional, Union

from reil.environments.session import Session
from reil.environments.task import Task
from reil.utils import ConfigParser, OutputWriter

# TODO: documentation


class SessionBuilder:
    def __init__(
            self, config_filenames: Dict[str, str],
            config_path: Optional[Union[pathlib.Path, str]],
            vars_dict: Optional[Dict[str, str]]) -> None:
        self._parser = ConfigParser(
            config_filenames=config_filenames, config_path=config_path,
            vars_dict=vars_dict)

    def create_task(
            self,
            task_name: str,
            parent_session_path: pathlib.PurePath = pathlib.PurePath('.')
    ) -> Task:
        components = self._parser.extract('tasks', task_name)

        name = components['name']
        path = components['path']
        agent_training_triggers = components['agent_training_triggers']

        start_iteration = components.get('start_iteration', 0)
        max_iterations = components.get('max_iterations', 1)
        save_iterations = components.get('save_iterations', True)

        temp = components.get(
            'writer',
            {'name': None, 'path': None, 'columns': None})
        writer = OutputWriter(
            filename=temp.get('name') or name,
            path=pathlib.PurePath(temp.get('path') or
                                  (parent_session_path / 'reports')),
            columns=temp.get('columns'))

        t = Task(
            name=name,
            path=pathlib.PurePath(parent_session_path, path),
            agent_training_triggers=agent_training_triggers,
            plan_name=components['plan_name'],
            start_iteration=start_iteration,
            max_iterations=max_iterations,
            writer=writer,
            save_iterations=save_iterations
        )

        return t

    def create_session(
            self,
            session_name: str,
            parent_session_path: Union[pathlib.PurePath, str] = '.'
    ) -> Session:

        try:
            session_info = self._parser.extract('sessions', session_name)
        except KeyError:
            raise ValueError(f'Session {session_name} not found.')

        components: Dict[str, List[Task]] = {
            'main_task': [],
            'tasks_before': [],
            'tasks_after': [],
            'tasks_before_iteration': [],
            'tasks_after_iteration': []
        }

        for component in components:
            if task_list := session_info.get(component):
                if component == 'main_task':
                    task_list = [task_list]
                for t in task_list:
                    if self._parser.contains('tasks', t):
                        temp = self.create_task(t, pathlib.PurePath(
                            session_info['path'], session_name))
                    # elif self._parser.contains('sessions', t):
                    #     temp = self.create_session(t, pathlib.PurePath(
                    #         session_info['path'], session_name))
                    else:
                        raise ValueError(f'Unknown name "{t}" in {component}.')

                    components[component].append(temp)

        if components['main_task']:
            main_task = components['main_task'][0]
        else:
            raise ValueError(
                f'main_task cannot be None for session {session_info}.')

        components.pop('main_task')

        plans = {
            name: self._parser.extract(
                'interaction_protocols', typ, as_object=True)
            for name, typ in (session_info.get('plans') or {}).items()
        }

        agents = {
            name: self._parser.extract('agents', typ, as_object=True)
            for name, typ in session_info['agents'].items()
        }

        subjects = {
            name: self._parser.extract('subjects', typ, as_object=True)
            for name, typ in session_info['subjects'].items()
        }

        demons = {
            name: self._parser.extract('demons', typ, as_object=True)
            for name, typ in (session_info.get('demons') or {}).items()
        }

        return Session(
            name=session_info['name'],
            path=pathlib.PurePath(
                parent_session_path or '.', session_info['path']),
            agents=agents, subjects=subjects,
            plans=plans, demons=demons,
            separate_process=session_info.get('separate_process'),
            process_type=session_info.get('process_type'),
            main_task=main_task,
            **components)
