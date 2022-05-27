import logging
from datetime import datetime
from time import sleep
from warnings import warn

import py2neo
from astropy.table import Table
from pathlib import Path
from py2neo import Graph as NeoGraph

import numpy as np
import pandas as pd
from weaveio.context import ContextMeta
from weaveio.writequery import CypherQuery

missing_types = {int:  np.inf, float: np.inf, str: '<MISSING>', type(None): np.inf, None: np.inf, bool: np.inf, datetime: datetime(1900, 1, 1, 0, 0)}
convert_types = {int:  int, float: float, str: str, type(None): float, None: float, bool: float,
                 datetime: lambda x: datetime(x.year, x.month, x.day, x.hour, x.minute, x.second),
                 list: list, tuple: tuple, np.ndarray: np.ndarray, pd.DataFrame: pd.DataFrame, pd.Series: pd.Series,
                 dict: dict, Table: Table,
                 np.int64: int, np.float64: float, np.float32: float, np.int32:int,
                 Path: str}

def is_null(x):
    try:
        return np.all(x != x)
    except TypeError:
        pass
    return x is None


def _convert_datatypes(x, nan2missing=True, none2missing=True, surrounding_type=None):
    if isinstance(x, (tuple, list)):
        types = set(convert_types[type(i)] for i in x if not is_null(i))
        if len(types) == 0:
            acceptable_type = str
        elif len(types) == 1:
            acceptable_type = types.pop()
        else:
            raise TypeError(f"Lists must be of homogeneous type")
        r = [_convert_datatypes(xi, nan2missing, none2missing, surrounding_type=acceptable_type) for xi in x]
        if isinstance(x, tuple):
            r = tuple(r)
        return r
    elif isinstance(x, dict):
        return {str(_convert_datatypes(k, nan2missing, none2missing)): _convert_datatypes(v, nan2missing, none2missing) for k, v in x.items()}
    elif isinstance(x, (pd.DataFrame, pd.Series)):
        return _convert_datatypes(pd.DataFrame(x).reset_index().to_dict('records'), nan2missing, none2missing)
    elif isinstance(x, Table):
        x = list(map(lambda row: {c: ri for c, ri in zip(x.colnames, row)}, x.iterrows()))
        return _convert_datatypes(pd.DataFrame(x).reset_index().to_dict('records'), nan2missing, none2missing)
    elif isinstance(x, np.ndarray):
        return _convert_datatypes(x.tolist(), nan2missing, none2missing)
    if not (none2missing or nan2missing):
        return x
    elif none2missing:
        if x is None:
            return missing_types[surrounding_type]
    if nan2missing:
        try:
            if np.isnan(x):
                return missing_types[surrounding_type]
        except TypeError:
            pass
    if surrounding_type is not None:
        return convert_types[surrounding_type](x)
    for from_type, to_type in convert_types.items():
        if from_type is not None:
            if isinstance(x, from_type):
                x = to_type(x)
    return x


class Graph(metaclass=ContextMeta):
    def __new__(cls, *args, **kwargs):
        # resolves the parent instance
        instance = super().__new__(cls)
        if kwargs.get("graph") is not None:
            instance._parent = kwargs.get("graph")
        else:
            instance._parent = cls.get_context(error_if_none=False)
        return instance

    def __init__(self, profile=None, name=None, **settings):
        self.write_allowed = settings.pop('write', False)
        self.neograph = NeoGraph(profile, name, **settings)

    def create_unique_constraint(self, label, key):
        try:
            self.neograph.schema.create_uniqueness_constraint(label, key)
        except py2neo.database.work.ClientError:
            pass

    def drop_unique_constraint(self, label, key):
        try:
            self.neograph.schema.drop_uniqueness_constraint(label, key)
        except py2neo.database.work.DatabaseError:
            pass

    def write(self, collision_manager):
        return CypherQuery(collision_manager)

    def _execute(self, cypher, parameters, backoff=1, limit=10):
        return self.neograph.auto(readonly=not self.write_allowed).run(cypher, parameters=parameters)
        # try:
        #     pass
        # except (ConnectionError) as e:
        #     logging.info(f'Connection possibly busy, waiting {backoff} seconds to retry. Actual error was {e}')
        #     if backoff >= limit:
        #         raise e
        #     sleep(backoff)
        #     backoff *= 2
        # except (RuntimeError, IndexError) as e:
        #     logging.info(f'Connection failed with an undefined py2neo error, waiting {backoff} seconds to retry. Actual error was {e}')
        #     if backoff >= limit:
        #         raise e
        #     backoff *= 2  # dont sleep retry immediately
        #     return self._execute(cypher, parameters, backoff, limit)

    def execute(self, cypher, **payload):
        d = _convert_datatypes(payload, nan2missing=True, none2missing=True)
        try:
            return self._execute(cypher, d)
        except IndexError:
            raise ConnectionResetError(f"Py2neo dropped the connection because it was taking too long. "
                                       f"Split up your query using batch_size=??")

    def output_for_debug(self,  silent=False, **payload):
        d = _convert_datatypes(payload, nan2missing=True, none2missing=True)
        if not silent:
            warn(f"When parameters are output for debug in the neo4j desktop, it cannot be guaranteed the data types will remain the same. "
                 f"For certain, infs/nans/None are converted to strings (to avoid this, run your query without using `output_for_debug`)")
        return f':params {d}'

Graph._context_class = Graph
