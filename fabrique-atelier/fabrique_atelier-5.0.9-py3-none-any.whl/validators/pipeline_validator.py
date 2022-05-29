from fabrique_atelier.constants import VALID_ACTOR_TYPES, special_topics


def _rec_node_check(node_name, visited, nodes):
    if node_name == 'end':
        return ['end',]
    if node_name in visited:
        raise Exception(f"Not valid pipeline DAG, {node_name} in loop!")
    node = nodes[node_name]
    visited += ['node_name',]
    res = []
    for output in node['outputs']:
        if output == node_name:
            raise Exception(f"Not valid pipeline DAG, {node_name} refs to itself!")
        last = _rec_node_check(output, visited, nodes)
        res += last
    if not all((r == 'end' for r in res)):
        raise Exception("Some of DAG paths is not terminated by 'end'!")
    return res

def validate_pipeline(pipeline, VALID_ACTOR_TYPES=VALID_ACTOR_TYPES):
    #process nodes
    excluded_ids = ['begin', 'end']
    pipeline_nodes = {ID: pipeline.nodes[ID] for ID in pipeline.ids if ID not in excluded_ids}
    if not pipeline_nodes:
        raise Exception("No nodes in the pipeline")

    for node_name, node_cls in pipeline_nodes.items():
        if not node_cls:
            raise Exception(f"Node '{node_name}' wasn't assiged")

    nodes = {}          
    for node_id, node_cls in pipeline_nodes.items():
        node_outputs = node_cls._outputs
        actor_type = node_cls._actor_type
        if actor_type not in VALID_ACTOR_TYPES:
            raise Exception(f"Actor type '{actor_type}' is not in VALID_ACTOR_TYPES = {VALID_ACTOR_TYPES}")
        class_name = node_cls.__name__    
        if actor_type == 'dispatcher':
            if not node_outputs:
                raise Exception(f"No destinations in {class_name}.destinations") 
            outputs = list(node_outputs)
        elif actor_type == 'detector':
            outputs = []
        else:
            outputs = list(node_outputs)
            if not outputs:
                outputs = ['end',]

        nodes[node_id] = dict(class_name=class_name, 
                              actor_type=actor_type, 
                              outputs=outputs)    
    
    
    for node_id, node in nodes.items():
        for output in node['outputs']:
            if output in excluded_ids:
                continue

            if output not in pipeline.ids:
                class_name = node['class_name']
                bad_output_tpl = f"Transition in {class_name} references a node {output} that is not present in the node list"
                raise Exception(bad_output_tpl)
            if 'from' not in nodes[output]:
                nodes[output]['from'] = []

            nodes[output]['from'].append(node_id)

    #find start node
    start_node_name = None
    for node_name, node in nodes.items():
        if node['actor_type'] == 'detector':
            continue
        if not 'from' in node:
            if start_node_name:
                raise Exception(f"Mustn't have more than one start node {start_node_name} and {node_name}")
            node['from'] = ['begin',] #started terminal node
            start_node_name = node_name

    if not start_node_name:
        raise Exception("Start node wasn't found")
        
    _ = _rec_node_check(start_node_name, [], nodes)
    
    return nodes