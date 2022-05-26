# Copyright 2021 AIPlan4EU project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from typing import Dict, List, Tuple
import unified_planning as up
import pyperplan # type: ignore


def _change_notation(name: str) -> str:
    '''This function takes a name with a lisp-like notation, for example "(at robot Trento)" and returns
    the string "at_robot_Trento".
    '''
    return("_".join(name[1:len(name)-1].split(" ")))

def _get_fresh_name(new_problem: 'up.model.Problem', name: str) -> str:
    '''This method gets always a fresh name for the problem'''
    new_name = name
    count = 0
    while(new_problem.has_name(new_name)):
        new_name = f'{name}_{str(count)}'
        count += 1
    return new_name

def _get_original_action_and_parameters_name(name: str) -> Tuple[str, List[str]]:
    '''From a name in lisp-like notation, return the action name.
    For example: "(move l1 l2)" returns tuple("move", ["l1", "l2"])'''
    names = name[1:len(name)-1].split(" ")
    return (names[0], names[1:])

def rewrite_back_task(task: 'pyperplan.task.Task', original_problem: 'up.model.Problem') -> Tuple['up.model.Problem', Dict['up.model.Action', Tuple['up.model.Action', List['up.model.FNode']]]]:
    #parse facts etc, init and goals. All are set of strings, so we need a way to parse fluents from objects.
    #facts are all the fluents applied to all the objects, in lisp notation, therefore a fluent "at" that takes a robot
    # and a location, with r1, r2, l1, l2 is represented as 4 facts called "(at r1 l1) (at r1 l2) (at r2 l1) (at r2 l2)"
    # those 4 facts will be our fluents after we remove "()" and change blank spaces " " with underscores "_".
    grounded_problem = up.model.Problem(task.name, original_problem.env)
    rewrite_back_map: Dict['up.model.Action', Tuple['up.model.Action', List['up.model.FNode']]] = {}
    #map from names in the task domain to fluents of the grounded problem
    vars_to_fluent_map: Dict[str, 'up.model.Fluent'] = {}
    for fact in task.facts:
        fluent = up.model.Fluent(_get_fresh_name(grounded_problem, _change_notation(fact)))
        vars_to_fluent_map[fact] = fluent
        grounded_problem.add_fluent(fluent, default_initial_value=False)
    for init in task.initial_state:
        grounded_problem.set_initial_value(vars_to_fluent_map[init], True)
    for goal in task.goals:
        grounded_problem.add_goal(vars_to_fluent_map[goal])
    for operator in task.operators:
        new_action = up.model.InstantaneousAction(_get_fresh_name(grounded_problem, _change_notation(operator.name)))
        original_action_name, parameters_names = _get_original_action_and_parameters_name(operator.name)
        for prec in operator.preconditions:
            new_action.add_precondition(vars_to_fluent_map[prec])
        for fluent_to_add in operator.add_effects:
            new_action.add_effect(vars_to_fluent_map[fluent_to_add], True)
        for fluent_to_del in operator.del_effects:
            new_action.add_effect(vars_to_fluent_map[fluent_to_del], False)
        grounded_problem.add_action(new_action)
        parameters: List['up.model.Object'] = []
        for parameter_name in parameters_names:
            parameters.append(original_problem.object(parameter_name))
        rewrite_back_map[new_action] = (original_problem.action(original_action_name), original_problem.env.expression_manager.auto_promote(parameters))
    return (grounded_problem, rewrite_back_map)
