#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import os
import traceback
from pathlib import Path


def get_ontology_name(ontology_name: object = None) -> list:
    """ Consistent Retrieval of Ontology Name
        https://github.com/grafflr/graffl-core/issues/135 """

    if ontology_name is None:

        # function copied from 'EnvIO.as_list(...)'
        if 'GRAFFL_ONTOLOGIES' in os.environ:
            values = [x.strip()
                      for x in os.environ['GRAFFL_ONTOLOGIES'].split(',')]
            return [x for x in values if x and len(x)]

        raise ValueError('No Ontology Name Specified')

    else:

        ontology_name_type = type(ontology_name)

        if ontology_name_type == str:
            return [ontology_name]

        elif ontology_name_type == list:
            return ontology_name

        raise ValueError(f"Unrecognized Data Type: {ontology_name_type}")


def odds_of(odds: int) -> bool:
    """ Help randomize decisions
        odds_of(20) gives a 20% chance of being True

    Returns:
        True: if a True value is selected
    """
    from random import randint

    MIN = 1
    MAX = 100

    if odds >= MAX:
        return True
    if odds <= MIN:
        return False

    return randint(MIN, MAX) <= odds


def prov_stack():
    """ Returns an Execution Stack Trace """

    stack = [str(x) for x in traceback.extract_stack()]

    stack = [[y for y in x.split(' ') if '.py' in y][0]
             for x in stack]  # reduce to python file only

    stack = [Path(x).name for x in stack]  # filename only

    stack = [x.replace(',', '') for x in stack]  # remove trailing commas

    stack = [x for x in stack if x != 'stack_utils.py']  # remove this call

    # remove duplicates without changing the order
    stack2 = []
    for x in stack:
        if x not in stack2:
            stack2.append(x)

    return stack2
