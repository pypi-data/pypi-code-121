import math
from typing import Dict, Tuple

import networkx as nx
import pyomo.core as pyo

Node = int
Edge = Tuple[Node, Node]
Pubo = Dict[Tuple[Edge, ...], float]


def build_mht_pyomo_model(
    pubo: Pubo, scenario_graph: nx.DiGraph, has_constraints: bool = True
) -> pyo.ConcreteModel:
    model = pyo.ConcreteModel()
    model.Nodes = pyo.Set(initialize=list(scenario_graph.nodes))
    model.Arcs = pyo.Set(initialize=list(scenario_graph.edges))
    model.x = pyo.Var(model.Arcs, domain=pyo.Binary)

    _DECIMALS = 3

    if has_constraints:

        @model.Constraint(model.Nodes)
        def out_edges_rule(model, idx):
            out_nodes = [
                node_id for node_id in model.Nodes if [idx, node_id] in model.Arcs
            ]
            if len(out_nodes) >= 2:
                return sum(model.x[idx, node_id] for node_id in out_nodes) <= 1
            else:
                return pyo.Constraint.Feasible

        @model.Constraint(model.Nodes)
        def in_edges_rule(model, idx):
            in_nodes = [
                node_id for node_id in model.Nodes if [node_id, idx] in model.Arcs
            ]
            if len(in_nodes) >= 2:
                return sum(model.x[node_id, idx] for node_id in in_nodes) <= 1
            else:
                return pyo.Constraint.Feasible

    def obj_expression(model):
        return sum(
            round(pubo_energy, _DECIMALS)
            * math.prod(model.x[edge] for edge in pubo_edges)
            for pubo_edges, pubo_energy in pubo.items()
        )

    model.cost = pyo.Objective(rule=obj_expression, sense=pyo.minimize)

    return model
