import networkx as nx
import pyomo.core as pyo


def mds(graph: nx.Graph) -> pyo.ConcreteModel:
    model = pyo.ConcreteModel()
    model.x = pyo.Var(graph.nodes, domain=pyo.Binary)

    @model.Constraint(graph.nodes)
    def dominating_rule(model, idx):
        sum_of_neighbors = sum(model.x[neighbor] for neighbor in graph.neighbors(idx))
        return model.x[idx] + sum_of_neighbors >= 1

    model.cost = pyo.Objective(expr=sum(model.x.values()), sense=pyo.minimize)

    return model
