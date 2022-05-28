# -*- coding: utf-8 -*-
'''
Environment class
==================

The base class of all learning environments in which one or more `agents` act
on one or more `subjects`.
'''
import inspect
from collections import defaultdict
from typing import Any, Callable, Dict, Generator, NamedTuple, Optional, Tuple, Union

import pandas as pd
from reil import stateful
from reil.agents.agent_base import AgentBase
from reil.agents.agent_demon import AgentDemon
from reil.datatypes.dataclasses import InteractionProtocol
from reil.datatypes.feature import FeatureSet
from reil.subjects.subject import Subject
from reil.subjects.subject_demon import SubjectDemon
from reil.utils.instance_generator import InstanceGenerator
from reil.utils.instance_generator_v2 import InstanceGeneratorV2

AgentSubjectTuple = Tuple[str, str]
EntityType = Union[AgentBase, Subject]
EntityGenType = Union[
    InstanceGenerator[AgentBase],
    InstanceGenerator[AgentDemon],
    InstanceGenerator[Subject],
    InstanceGenerator[SubjectDemon],  # type: ignore
    InstanceGeneratorV2[AgentBase],
    InstanceGeneratorV2[AgentDemon],
    InstanceGeneratorV2[Subject],
    InstanceGeneratorV2[SubjectDemon],  # type: ignore
]


class Plan(NamedTuple):
    name: Optional[str] = None
    plan: Optional[Any] = None


class Environment(stateful.Stateful):
    '''
    Provide an interaction and learning environment for `agents` and
    `subjects`.

    Notes
    -----
    `Agents` act on `subjects` and receive the reward of their action and
    the new state of those `subjects`. Then `agents` learn based on this
    information to improve their actions.

    `Pass`: visiting all protocols in the interaction sequence, once.

    `iteration`: For each subject, an iteration is one time reaching its
    terminal state. If the subject is an instance generator, then
    the generator should reach to terminal state, not just its
    current instance.
    '''

    def __init__(
            self,
            entity_dict: Optional[Dict[str, Union[
                EntityType, EntityGenType, str]]] = None,
            demon_dict: Optional[Dict[str, Union[
                AgentDemon, SubjectDemon, str]]] = None,
            interaction_plans: Optional[Dict[str, Any]] = None,
            stopping_criteria: Optional[
                Callable[[Dict[str, float], Optional[Any]], bool]] = None,
            **kwargs: Any):
        '''
        Arguments
        ---------
        entity_dict:
            a dictionary that contains `agents`, `subjects`, and
            `generators`.
        '''
        super().__init__(**kwargs)

        self._agents: Dict[str, AgentBase] = {}
        self._subjects: Dict[str, Subject] = {}
        self._agent_demons: Dict[str, AgentDemon] = {}
        self._subject_demons: Dict[str, SubjectDemon] = {}
        self._instance_generators: Dict[str, EntityGenType] = {}
        self._assignment_list: Dict[
            AgentSubjectTuple,
            Tuple[Union[int, None], Union[int, None]]] = \
            defaultdict(lambda: (None, None))
        self._iterations: Dict[str, int] = defaultdict(int)
        self._agent_observers: Dict[
            Tuple[str, str],
            Generator[Union[FeatureSet, None], Any, None]] = {}
        self._plans: Dict[str, Any] = {}
        self._active_plan: Plan = Plan()

        self._stopping_criteria = stopping_criteria

        if entity_dict:
            self.add_entities(entity_dict)

        if demon_dict:
            self.add_demons(demon_dict)

        if interaction_plans:
            self.add_plans(interaction_plans)

        if len(self._plans) == 1:
            self._active_plan = Plan(
                *next(iter(self._plans.items())))

    def add_entities(
            self,
            entity_dict: Dict[str, Union[
                EntityType, EntityGenType, str]]) -> None:
        '''
        Add `agents` and `subjects` to the environment.

        Arguments
        ---------
        entity_dict:
            a dictionary consist of `agent`/ `subject` name and the
            respective entity. Names should be unique, otherwise overwritten.
            To assign one entity to multiple names, use the name in the
            first assignment as the value of the dict for other assignments.
            For example:
            >>> env.add_entities({'agent_1': Agent(), 'agent_2': 'agent_1'})

            When using name as value, the name is being looked up first in
            instance generators, then agents, and finally subjects. Whichever
            contains the name first, the entity corresponding to that instance
            is being used.

        Notes
        -----
        Reusing an `InstanceGenerator` produces unintended consequences.

        Raises
        ------
        ValueError
            An entity is being reused without being defined first.

        TypeError
            The entity is niether an `agent` [generator] nor a `subject`
            [generator].
        '''
        for name, obj in entity_dict.items():
            if isinstance(obj, str):
                _obj = self._instance_generators.get(
                    obj, self._agents.get(
                        obj, self._subjects.get(obj)))
                if _obj is None:
                    raise ValueError(
                        f'entity {obj} defined for {name} is '
                        'not in the list of agents, subjects, and generators.')
            else:
                _obj = obj

            if isinstance(_obj, (InstanceGenerator, InstanceGeneratorV2)):
                self._instance_generators.update({name: _obj})

                _, instance = next(_obj)
                if isinstance(instance, AgentBase):
                    self._agents.update({name: instance})  # type: ignore
                elif isinstance(instance, Subject):
                    self._subjects.update({name: instance})
                else:
                    raise TypeError(
                        f'entity {name} is niether an agent generator nor a '
                        'subject generator.')

            elif isinstance(_obj, AgentBase):
                self._agents.update({name: _obj})
            elif isinstance(_obj, Subject):  # type: ignore
                self._subjects.update({name: _obj})
            else:
                raise TypeError(
                    f'entity {name} is niether an agent nor a subject.')

    def remove_entity(self, entity_names: Tuple[str, ...]) -> None:
        '''
        Remove `agents`, `subjects`, or `instance_generators` from
        the environment.

        Arguments
        ---------
        entity_names:
            A list of `agent`/ `subject` names to be deleted.

        Notes
        -----
        This method removes the item from both `agents` and `subjects`
        lists. Hence, it is not recommended to use the same name for both
        an `agent` and a `subject`.
        '''
        for name in entity_names:
            if name in self._agents:
                del self._agents[name]
            if name in self._subjects:
                del self._subjects[name]
            if name in self._instance_generators:
                del self._instance_generators[name]

    def add_demons(
            self,
            demon_dict: Dict[str, Union[
                AgentDemon, SubjectDemon, str]]) -> None:
        '''
        Add `AgentDemon`s and `SubjectDemon`s to the environment.

        Arguments
        ---------
        demon_dict:
            a dictionary consist of `AgentDemon`/ `SubjectDemon` name and the
            respective entity. Names should be unique, otherwise overwritten.
            To assign one entity to multiple names, use the name in the
            first assignment as the value of the dict for other assignments.
            For example:
            >>> env.add_demons({'agent_demon_1': AgentDemon(),
                                'agent_demon_2': 'agent_demon_1'})

            When using name as value, the name is being looked up first in
            agent demons, and then subject demons. Whichever
            contains the name first, the demon corresponding to that instance
            is being used.

        Raises
        ------
        ValueError
            A demon is being reused without being defined first.

        TypeError
            The demon is niether an `AgentDemon` nor a `SubjectDemon`.
        '''
        for name, obj in demon_dict.items():
            if isinstance(obj, str):
                _obj = self._agent_demons.get(
                    obj, self._subject_demons.get(obj))
                if _obj is None:
                    raise ValueError(
                        f'entity {obj} defined for {name} is '
                        'not in the list of agent demons, and subject demons.')
            else:
                _obj = obj
            if isinstance(_obj, AgentDemon):
                self._agent_demons.update({name: _obj})
            elif isinstance(_obj, SubjectDemon):  # type: ignore
                self._subject_demons.update({name: _obj})
            else:
                raise TypeError(
                    f'entity {name} is niether an agent demon nor '
                    'a subject demon.')

    def remove_demon(self, demon_names: Tuple[str, ...]) -> None:
        '''
        Remove `agent demons` or `subject demons` from
        the environment.

        Arguments
        ---------
        demon_names:
            A list of demon names to be deleted.

        Notes
        -----
        This method removes the item from both `agent_demons` and
        `subject_demons` lists.
        Hence, it is not recommended to use the same name for both
        an `agent demon` and a `subject demon`.
        '''
        for name in demon_names:
            if name in self._agent_demons:
                del self._agent_demons[name]
            if name in self._subject_demons:
                del self._subject_demons[name]

    def add_plans(self, interaction_plans: Dict[str, Any]) -> None:
        for name, plan in interaction_plans.items():
            if name in self._plans:
                raise ValueError(f'plan {name} already exists.')
            self._plans[name] = plan

    def remove_plans(self, plan_names: Tuple[str, ...]) -> None:
        for name in plan_names:
            del self._plans[name]

    def activate_plan(self, plan_name: str) -> None:
        if plan_name not in self._plans:
            raise ValueError(f'Plan {plan_name} not found.')
        self._active_plan = Plan(plan_name, self._plans[plan_name])

    def simulate_pass(self, n: int = 1) -> None:
        '''
        Go through the interaction sequence for a number of passes and
        simulate interactions accordingly.

        Arguments
        ---------
        n:
            The number of passes that simulation should go.
        '''
        raise NotImplementedError

    def simulate_to_termination(self) -> None:
        '''
        Go through the interaction sequence and simulate interactions
        accordingly, until all `subjects` are terminated.

        Notes
        -----
        To avoid possible infinite loops caused by normal `subjects`,
        this method is only available if all `subjects` are generated
        by `instance generators`.

        Raises
        ------
        TypeError:
            Attempt to call this method will normal subjects in the interaction
            sequence.
        '''
        raise NotImplementedError

    @classmethod
    def interact(
            cls,
            agent_id: int,
            agent_observer: Generator[Union[FeatureSet, None], Any, None],
            subject_instance: Union[Subject, SubjectDemon],
            state_name: str,
            action_name: str,
            reward_name: str,
            iteration: int,
            times: int = 1) -> None:
        '''
        Allow `agent` and `subject` to interact at most `times` times.

        Attributes
        ----------
        agent_id:
            Agent's ID by which it is registered at the subject.

        subject_id:
            Subject's ID by which it is registered at the `agent`.

        agent_instance:
            An instance of an `agent` that takes the action.

        subject_instance:
            An instance of a `subject` that computes reward, determines
            possible actions, and takes the action.

        state_name:
            A string that specifies the state definition.

        action_name:
            A string that specifies the action definition.

        reward_name:
            A string that specifies the reward function definition.

        iteration:
            The iteration of of the current run. This value is used by the
            `agent` to determine the action.

        times:
            The number of times the `agent` and the `subject` should interact.

        Returns
        -------
        :
            A list of subject's reward and state before taking an action
            and agent's action.

        Notes
        -----
        If subject is terminated before "times" iterations, the result will
        be truncated and returned. In other words, the output will not
        necessarily have a lenght of "times".
        '''
        for _ in range(times):
            reward = subject_instance.reward(
                name=reward_name, _id=agent_id)
            # When dealing with multiple agents, the first agent enables the
            # reward. Hence, other agent observers cannot get `None` to start.
            # In such cases, we have to manually feed the generator with a
            # `None`.
            try:
                agent_observer.send(
                    None if reward is None else {'reward': reward})
            except TypeError:
                agent_observer.send(None)

            state = subject_instance.state(name=state_name, _id=agent_id)
            possible_actions = subject_instance.possible_actions(
                name=action_name, _id=agent_id)
            if possible_actions:
                try:
                    next(possible_actions)
                except TypeError:
                    pass
                action = agent_observer.send(
                    {'state': state,
                     'actions': possible_actions,
                     'iteration': iteration})
                action_taken = subject_instance.take_effect(
                    action, agent_id)  # type: ignore
                agent_observer.send({'action_taken': action_taken})
                try:
                    possible_actions.close()
                except AttributeError:
                    pass

    @classmethod
    def interact_while(
            cls,
            agent_id: int,
            agent_observer: Generator[
                Union[FeatureSet, None], Any, None],
            subject_instance: Union[Subject, SubjectDemon],
            state_name: str,
            action_name: str,
            reward_name: str,
            iteration: int) -> None:
        '''
        Allow `agent` and `subject` to interact until `subject` is terminated.

        Attributes
        ----------
        agent_id:
            Agent's ID by which it is registered at the subject.

        agent_instance:
            An instance of an agent that takes the action.

        subject_instance:
            An instance of a subject that computes reward,
            determines possible actions, and takes the action.

        state_name:
            A string that specifies the state definition.

        action_name:
            A string that specifies the action definition.

        reward_name:
            A string that specifies the reward function definition.

        iteration:
            The iteration of of the current run. This value is used by the
            agent to determine the action.

        Returns
        -------
        :
            A list of subject's reward and state before taking an action and
            agent's action.

        Notes
        -----
        For `instance generators`, only the current
        instance is run to termination, not the whole generator.
        '''
        while not subject_instance.is_terminated(agent_id):
            cls.interact(
                agent_id, agent_observer, subject_instance,
                state_name, action_name, reward_name, iteration)

    def assert_protocol(self, protocol: InteractionProtocol) -> None:
        '''
        Check whether the given protocol:

        * contains only entities that are known to the `environment`.

        * unit is one of the possible values.

        Arguments
        ---------
        protocol:
            An interaction protocol.

        Raises
        ------
        ValueError
            `agent`, `agent demon`, `subject`, or `subject demon` is not
            defined.

        ValueError
            `unit` is not one of `interaction`, `instance`, or `iteration`.
        '''
        agent_name = protocol.agent.name
        agent_demon_name = protocol.agent.demon_name
        subject_name = protocol.subject.name
        subject_demon_name = protocol.subject.demon_name
        unit = protocol.unit

        if agent_name not in self._agents:
            raise ValueError(f'Unknown agent name: {agent_name}.')
        if (agent_demon_name is not None
                and agent_demon_name not in self._agent_demons):
            raise ValueError(
                f'Unknown agent demon name: {agent_demon_name}.')
        if subject_name not in self._subjects:
            raise ValueError(f'Unknown subject name: {subject_name}.')
        if (subject_demon_name is not None
                and subject_demon_name not in self._subject_demons):
            raise ValueError(
                f'Unknown subject demon name: {subject_demon_name}.')
        if unit not in ('interaction', 'instance', 'iteration'):
            raise ValueError(
                f'Unknown unit: {unit}. '
                'It should be one of interaction, instance, or iteration. '
                'For subjects of non-instance generator, iteration and '
                'instance are equivalent.')

    def register_protocol(
            self,
            interaction_protocol: InteractionProtocol,
            get_agent_observer: bool = False) -> None:
        '''
        Register the `agent` and `subject` of an interaction protocol.

        Arguments
        ---------
        interaction_protocol:
            The protocol whose `agent` and `subject` should be registered.

        get_agent_observer:
            If `True`, the method calls the `observe` method of the `agent`
            with `subject_id`, and adds the resulting generator to the list
            of observers.

        Notes
        -----
        When registration happens for the first time, agents and subjects
        get any ID that the counterpart provides. However, in the follow up
        registrations, `entities` attempt to register with the same ID to
        have access to the same information.
        '''
        a_name = interaction_protocol.agent.name
        a_demon_name = interaction_protocol.agent.demon_name
        a_stat = interaction_protocol.agent.statistic_name
        s_name = interaction_protocol.subject.name
        s_demon_name = interaction_protocol.subject.demon_name
        a_s_name = (a_name, s_name)

        if s_demon_name is None:
            subject_instance = self._subjects[s_name]
        else:
            subject_instance = \
                self._subject_demons[s_demon_name](self._subjects[s_name])

        if a_demon_name is None:
            agent_instance = self._agents[a_name]
        else:
            agent_instance = \
                self._agent_demons[a_demon_name](self._agents[a_name])

        a_id, s_id = self._assignment_list[a_s_name]
        a_id = subject_instance.register(entity_name=a_name, _id=a_id)
        s_id = agent_instance.register(entity_name=s_name, _id=s_id)

        self._assignment_list[a_s_name] = (a_id, s_id)

        if get_agent_observer:
            self._agent_observers[a_s_name] = \
                agent_instance.observe(s_id, a_stat)

    def close_agent_observer(
            self, protocol: InteractionProtocol) -> Dict[str, float]:
        '''
        Close an `agent_observer` corresponding to `protocol`.

        Before closing the observer, the final `reward` and `state` of the
        system are passed on to the observer.

        Attributes
        -----------
        protocol:
            The protocol whose `agent_observer` should be closed.

        Returns
        -------
        :
            A dictionary of metrics and losses.

        Notes
        -----
        This method should only be used if a `subject` is terminated.
        Otherwise, the `agent_observer` might be expecting to receive different
        values, and it will corrupt the training data for the `agent`.
        '''
        agent_name = protocol.agent.name
        subject_name = protocol.subject.name
        r_func_name = protocol.reward_name
        state_name = protocol.state_name
        a_s_names = (agent_name, subject_name)
        s_demon_name = protocol.subject.demon_name

        if s_demon_name is None:
            subject_instance = self._subjects[subject_name]
        else:
            subject_instance = \
                self._subject_demons[s_demon_name](
                    self._subjects[subject_name])

        if inspect.getgeneratorstate(
                self._agent_observers[a_s_names]) != inspect.GEN_SUSPENDED:
            return {}

        a_id, _ = self._assignment_list[a_s_names]
        reward = subject_instance.reward(name=r_func_name, _id=a_id)
        state = subject_instance.state(name=state_name, _id=a_id)

        self._agent_observers[a_s_names].send({'reward': reward})
        self._agent_observers[a_s_names].send(
            {'state': state, 'actions': None, 'iteration': None})

        self._agent_observers[a_s_names].close()

        return self._agents[agent_name]._metrics

    def reset_subject(self, subject_name: str) -> bool:
        '''
        When a `subject` is terminated for all interacting `agents`, this
        function is called to reset the `subject`.

        If the `subject` is an `InstanceGenerator`, a new instance is created.
        If reset is successful, `iteration` is incremented by one.

        Attributes
        ----------
        subject_name:
            Name of the `subject` that is terminated.

        Returns
        -------
        :
            `True` if the `instance_generator` for the `subject` is still
            active, `False` if it hit `StopIteration`.

        Notes
        -----
        `Environment.reset_subject` only resets the `subject`. It does not
        get the statistics for that `subject`.
        '''
        if subject_name in self._instance_generators:
            # get a new instance if possible,
            # if not instance generator returns StopIteration.
            # So, increment iteration by 1, then if the generator is not
            # terminated, get a new instance.
            # If the generator is terminated, check if it is finite. If
            # infinite, call it again to get a subject. If not, disable reward
            # for the current subject, so that agent_observer does not raise
            # exception.
            try:
                _, self._subjects[subject_name] = next(  # type: ignore
                    self._instance_generators[subject_name])

            except StopIteration:
                self._iterations[subject_name] += 1
                if self._instance_generators[subject_name].is_terminated():
                    self._subjects[subject_name].reward.disable()
                else:
                    _, self._subjects[subject_name] = next(  # type: ignore
                        self._instance_generators[subject_name])
                return False
        else:
            self._iterations[subject_name] += 1
            self._subjects[subject_name].reset()

        return True

    def report_statistics(
            self,
            unstack: bool = True,
            reset_history: bool = True,
    ) -> Dict[Tuple[str, str], pd.DataFrame]:
        '''Generate statistics for agents and subjects.

        Parameters
        ----------
        unstack:
            Whether to unstack the resulting pivottable or not.

        reset_history:
            Whether to clear up the history after computing stats.

        Returns
        -------
        :
            A dictionary with state-subject pairs as keys and dataframes as
            values.
        '''
        raise NotImplementedError

    def __repr__(self) -> str:
        try:
            return (
                (sup_repr := super().__repr__()) + '\n' + '=' * len(sup_repr) +
                '\n'.join((
                    f'\n{name}\n{"-"*len(name)}\n' + '\n'.join(
                        (f'- {k}: {v.__repr__()}'
                         for k, v in entity.items())))
                    for name, entity in (
                        ('Agents', self._agents),
                        ('Subjects', self._subjects),
                        ('Agent Demons', self._agent_demons),
                        ('Subject Demons', self._subject_demons))))
        except AttributeError:
            return super().__repr__()

    def __getstate__(self):
        open_observers = set(
            a_s_names
            for a_s_names in self._agent_observers
            if inspect.getgeneratorstate(self._agent_observers[a_s_names])
            not in [inspect.GEN_CREATED or inspect.GEN_CLOSED]
        )

        if open_observers:
            raise RuntimeError(
                'Cannot save an environment in the middle of a simulation. '
                'These agent/subject interactions are still underway:\n'
                f'{open_observers}'
            )

        state = super().__getstate__()

        state['_agent_observers'] = {}

        return state
