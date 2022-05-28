import logging
import pathlib
import random
from typing import Dict, List, Optional, Union

from reil.agents.agent_demon import AgentDemon
from reil.datatypes.dataclasses import Entity, InteractionProtocol
from reil.datatypes.feature_array_dumper import FeatureSetDumper
from reil.environments.single import Single
from reil.environments.task import Task
from reil.subjects.subject import Subject
from reil.subjects.subject_demon import SubjectDemon
from reil.utils.argument_parser import ConfigParser
from reil.utils.instance_generator import InstanceGenerator


class Trajectory:
    def __init__(
            self,
            env_filename: str,
            env_path: Optional[Union[pathlib.Path, str]],
            parser: Optional[ConfigParser] = None,
            state_dumper: Optional[FeatureSetDumper] = None,
            agent_entity: Optional[Entity] = None,
            subject_entity: Optional[Entity] = None,
            demons: Optional[
                Dict[str, Union[AgentDemon, SubjectDemon, str]]] = None,
            state_name: Optional[str] = None,
            action_name: Optional[str] = None):
        self._parser = parser
        self._env_filename = env_filename
        self._env_path = env_path

        self._state_dumper = state_dumper
        self._agent_entity = agent_entity
        self._subject_entity = subject_entity
        self._demons = demons
        self._state_name = state_name
        self._action_name = action_name

    def run(  # noqa: C901
            self,
            trajectory_subjects: Union[InstanceGenerator[Subject], str],
            iteration: int,
            subject_list: Optional[List[str]] = None,
            subject_save_path: str = '.',
            state_dumper: Optional[FeatureSetDumper] = None,
            agent_entity: Optional[Entity] = None,
            subject_entity: Optional[Entity] = None,
            demons: Optional[
                Dict[str, Union[AgentDemon, SubjectDemon, str]]] = None,
            state_name: Optional[str] = None,
            action_name: Optional[str] = None) -> None:

        subjects: InstanceGenerator[Subject]
        dumper = state_dumper or self._state_dumper
        if isinstance(trajectory_subjects, str):
            if self._parser is None:
                raise ValueError('parser not found.')

            s = self._parser.extract(
                'subjects', trajectory_subjects, True)
        else:
            s = trajectory_subjects

        if isinstance(s, InstanceGenerator):
            subjects = s
            if dumper:
                subjects._state_dumper = dumper
                subjects._object.state._dumper = dumper

            if subject_list is not None:
                logging.warning(
                    'The parsed subject is an `InstanceGenerator`. '
                    'subject_list will not be used.'
                )
        else:
            if subject_list is None:
                raise ValueError(
                    'subject_list should be provided when '
                    'trajectory_subjects is of type str.')

            subjects = InstanceGenerator[Subject].from_instance_list(
                s, (subject_list,), save_instances=True,
                save_path=subject_save_path,
                state_dumper=dumper)

        if (_agent_entity := agent_entity or self._agent_entity) is None:
            raise TypeError('agent_entity is not specified.')

        if (_subject_entity := subject_entity or self._subject_entity) is None:
            raise TypeError('subject_entity is not specified.')

        if (_state_name := state_name or self._state_name) is None:
            raise TypeError('state_name is not specified.')

        if (_action_name := action_name or self._action_name) is None:
            raise TypeError('action_name is not specified.')

        env = Single.from_pickle(
            filename=self._env_filename, path=self._env_path)
        if (_demons := demons or self._demons):
            env.add_demons(_demons)
        env.add_entities({_subject_entity.name: subjects})

        while (plan_name := str(random.random())) in env._plans:
            pass

        env.add_plans({
            plan_name:
                InteractionProtocol(
                    agent=_agent_entity,
                    subject=_subject_entity,
                    state_name=_state_name,
                    action_name=_action_name,
                    reward_name='no_reward',
                    n=1, unit='iteration')})

        t = Task(
            name='trajectory',
            path='../experiments/trajectories',
            agent_training_triggers={_agent_entity.name: 'none'},
            plan_name=plan_name,
        )

        t.run_env(env, iteration)
