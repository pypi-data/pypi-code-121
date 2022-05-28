def sort_models(items):
    """
    Производит топологическую сортировку django-моделей
    """

    def add_node(graph, node):
        graph.setdefault(node, [0])

    def add_arc(graph, fromnode, tonode):
        graph[fromnode].append(tonode)
        graph[tonode][0] += 1

    graph = {}

    for v in items:
        add_node(graph, v)

    for a in items:

        for field in a._meta.get_fields():
            if field.concrete:
                if field.many_to_many or field.many_to_one:
                    add_arc(graph, field.related_model, a)

    roots = [node for (node, nodeinfo) in graph.items() if nodeinfo[0] == 0]

    sorted = []
    while roots:
        root = roots.pop()
        sorted.append(root)
        for child in graph[root][1:]:
            graph[child][0] = graph[child][0] - 1
            if graph[child][0] == 0:
                roots.append(child)
        del graph[root]

    if len(graph.items()) != 0:
        raise CircularReferenceException

    return sorted


class CircularReferenceException(Exception):
    pass
