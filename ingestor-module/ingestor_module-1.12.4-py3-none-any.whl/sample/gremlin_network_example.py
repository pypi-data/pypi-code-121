from graphdb import GraphDbConnection, GraphDb
import networkx as nx

connection_uri = (
    "ws://dev-neptune-240353578.ap-southeast-1.elb.amazonaws.com:8182/gremlin"
)

if __name__ == '__main__':

    cls = GraphDb.from_connection(GraphDbConnection.from_uri(connection_uri))

    query = cls.custom_query(f'''
    g.V().hasLabel('no_pay_tv_content').outE().subgraph('sg').cap('sg').next()
    ''', payload={
        'no_pay_tv_content': 'no_pay_tv_content'
    })

    di_graph = nx.DiGraph()

    for e in query[0][0]['@value']['edges']:
        di_graph.add_edge(e.outV.id, e.inV.id, elabel=e.label)

    print(di_graph.nodes())

    print(di_graph.edges())
