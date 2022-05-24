import os
import os.path
from copy import deepcopy
from collections import OrderedDict
import shutil
import argparse
import json
import yaml
from pathlib import Path
import random
ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) 
wconfig = {}
dag_file = 'rdag_10.yaml'
graph_order = 10
randomlist_size = int(graph_order / 10)

randomlist = []
i = 0
while i < randomlist_size:
    n = random.randint(1, graph_order)
    i +=1
    if n not in randomlist:
        randomlist.append(n)
    else:
        i -=1    
print(randomlist)


with open(dag_file) as input_stream:
    random_dag = yaml.load(input_stream, Loader=yaml.Loader)
graph_edges = random_dag['graph']['edges']
graph_nodes = random_dag['graph']['nodes']
num_nodes = len(random_dag['graph']['nodes'])
num_nodes +=1 # Last node- target node only for nodes without target  
graph_nodes.append({'id': str(num_nodes)})
wconfig = {}
nodes_wconfig = []
no_output_nodes = []
for node_graph in graph_nodes:
    node = {}
    node['tasks']= []
    node['name'] = 'node_id'+ node_graph['id']
    node['id'] = int(node_graph['id'])
    task = {}
    task['func'] = []
    task['inputs'] = []
    task['outputs'] = []
    task['func'].append('my_function')    
    task['func'].append('weighted_sleep')
    for edge in graph_edges:
        if edge['source'] == node_graph['id']:              
            task['outputs'].append('link_'+ edge['source']+'_to_'+ edge['target']) 
        elif edge['target'] == node_graph['id']:
            task['inputs'].append('link_' + edge['source']+'_to_'+ edge['target'])
    if (len(graph_edges) == 0 or len(task['outputs']) == 0) and node_graph['id'] != str(num_nodes):
        task['outputs'].append('link_'+ node_graph['id']+'_to_'+ str(num_nodes))
        no_output_nodes.append(node_graph['id'])
    if node_graph['id'] == str(num_nodes):
        for source in no_output_nodes:
            task['inputs'].append('link_' + str(source)+ '_to_' +  node_graph['id'])
    task['kwargs'] = {}
    if int(node_graph['id']) in randomlist:
        task['kwargs'] = { 'len_output' : len(task['outputs']), 'sleep_time': 100, 'id': int(node_graph['id'])}
    else:
        task['kwargs'] = { 'len_output' : len(task['outputs']), 'sleep_time': 10, 'id': int(node_graph['id'])}
    node['tasks'].append(task)
    nodes_wconfig.append(node)


workflow_name = str('node_') + str(len(graph_nodes))+ '_' + str(len(graph_edges))
wconfig = {'workflow_name': workflow_name, 'nodes': nodes_wconfig }
noalias_dumper = yaml.dumper.SafeDumper
noalias_dumper.ignore_aliases = lambda self, data: True
with open('wconfig_unbalanced.yaml', 'w') as output_stream:
    yaml.dump(wconfig, output_stream)      

