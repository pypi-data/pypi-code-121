import networkx as nx


def reduce_computational_theme(graph: nx.DiGraph):
    graph = graph.copy()

    change = True
    while change:
        change = False
        remove_vertices = []
        for vertex_ref in graph.nodes:
            if vertex_ref in remove_vertices:
                continue

            for vertex_oth in graph.nodes:
                if vertex_oth in remove_vertices or vertex_ref == vertex_oth:
                    continue

                set_in_ref = set(graph.predecessors(vertex_ref))
                set_in_oth = set(graph.predecessors(vertex_oth))
                set_out_ref = set(graph.neighbors(vertex_ref))
                set_out_oth = set(graph.neighbors(vertex_oth))

                """print(set_in_ref)
                print(set_in_oth)
                print(set_out_ref)
                print(set_out_oth)
                print()"""
                if set_in_ref == set_in_oth and set_out_ref == set_out_oth:
                    # Combine equivalent vertices
                    remove_vertices.append(vertex_oth)
                    change = True

        #print("Removing", remove_vertices)
        graph.remove_nodes_from(remove_vertices)

    return graph


def is_isomorphic_theme(graph_ref, graph_other):
    return nx.is_isomorphic(reduce_computational_theme(graph_ref), reduce_computational_theme(graph_other))
