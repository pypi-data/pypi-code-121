
from peext.controller import CHPControlMultiEnergy, RegulatedG2PControlMultiEnergy, RegulatedP2GControlMultiEnergy
from peext.node import CHPNode, EmptyBusNode, EmptyJunctionNode, ExtGasGrid, ExtPowerGrid, G2PNode, P2GNode, PowerLoadNode, GeneratorNode, SGeneratorNode, SinkNode, SourceNode, RegulatableController, HeatExchangerNode
from peext.edge import CircPumpMassEdge, CircPumpPressureEdge, LineEdge, PipeEdge, TrafoEdge

import pandapower as ppower

POWER_NET = 'power'
GAS_NET = 'gas'
HEAT_NET = 'heat'
MULTI = 'multi'
NETS_ACCESS = 'nets'

class MENetwork:

    def __init__(self, nodes = None, edges = None, multinet=None, history_container=None) -> None:
        self.__nodes = nodes
        self.__edges = edges
        self.__multinet = multinet
        self.__history_container = history_container
        pass
    
    def add_history_table(self, network_name, table_name, table):
        if network_name not in self.__history_container:
            self.__history_container[network_name] = {}
        if table_name not in self.__history_container[network_name]:
            self.__history_container[network_name][table_name] = []

        self.__history_container[network_name][table_name].insert(0, table)

    @property
    def multinet(self):
        return self.__multinet

    @property
    def names(self):
        return self.__nodes.keys()

    @property
    def edges(self):
        all_edges = []
        for key in self.__edges.keys():
            all_edges += self.__edges[key]
        return all_edges

    @property
    def edges_as_dict(self):
        return self.__edges

    @property
    def nodes(self):
        all_nodes = []
        for key in self.__nodes.keys():
            all_nodes += self.__nodes[key]
        return all_nodes

    def power_nodes(self):
        return self.__nodes[POWER_NET]
    
    def power_balance(self):
        amount_gen = sum([node.active_power()*node.regulation_factor() for node in 
            list(filter(lambda node: isinstance(node, GeneratorNode), self.__nodes[POWER_NET]))])
        amount_load = sum([node.active_power()*node.regulation_factor() for node in
            list(filter(lambda node: isinstance(node, PowerLoadNode), self.__nodes[POWER_NET]))])
        return amount_gen - amount_load

def find_bus_junc_for_table(node_table, node_id, network_name):
    result = []
    for cross in ['bus', 'junction', 'to_junction', 'from_junction']:
        if cross in node_table:
            cross_id = node_table[cross][node_id]
            result.append((network_name, cross.replace('to_', '').replace('from_', ''), cross_id, cross.split('_')[0]))
    return result

def get_bus_junc(node):
    result = []
    if isinstance(node, RegulatableController):
        inner_nodes = node.controller.nodes
        for network_name, inner_node in inner_nodes.items():
            target_table = node.network[NETS_ACCESS][network_name][inner_node[0]]
            result += find_bus_junc_for_table(target_table, inner_node[1], network_name)
    elif isinstance(node, EmptyBusNode):
        result.append((node.network.name, 'bus', node.id))
    elif isinstance(node, EmptyJunctionNode):
        result.append((node.network.name, 'junction', node.id))
    else:
        node_table = node.network[node.component_type()]
        result += find_bus_junc_for_table(node_table, node.id, node.network.name)
    return result

def get_bus_junc_res_data(node):
    metadata_set = get_bus_junc(node)
    data_set = {}
    for network_name, cross, cross_id, _ in metadata_set:
        if network_name not in data_set:
            data_set[network_name] = []
        network = node.network
        if 'nets' in node.network:
            network = node.network['nets'][network_name]
        data_set[network_name] += [network['res_'+cross].iloc[cross_id]]
    return data_set

def find_edges_controller(edges, controller):
    all_edges = {}
    for key, value in controller.edges.items():
        edge_with_key = [(edge, value[edge.id][0], value[edge.id][2]) for edge in edges[key] if edge.id in value.keys() and value[edge.id][1] == edge.component_type()]
        all_edges[key] = edge_with_key
    return all_edges

def find_edges(edges, index, net, net_name, table, point_name):
    all_edges = {}
    cross = None
    if table in ['bus', 'junction']:
        cross = index
    else:
        cross = net[table][point_name][index]
    if 'junction' in point_name:
        for edge_type in ['pipe', 'pump', 'circ_pump_pressure', 'circ_pump_mass']:
            if edge_type not in net:
                continue 
            for i, row in net[edge_type].iterrows():
                to_junc = row['to_junction']
                from_junc = row['from_junction']
                if cross == to_junc or cross == from_junc:
                    key_to_from = 'to' if cross == to_junc else 'from'
                    if net_name not in all_edges:
                        all_edges[net_name] = []
                    all_edges[net_name].append(([edge for edge in edges[net_name] if edge.id == i and edge_type == edge.component_type()][0], key_to_from, point_name))
    elif point_name == 'bus':
        for edge_type in ['line', 'trafo']:
            for i, row in net[edge_type].iterrows():
                to_bus = row['lv_bus' if edge_type == 'trafo' else 'to_bus']
                from_bus = row['hv_bus' if edge_type == 'trafo' else 'from_bus']
                if cross == to_bus or cross == from_bus:
                    key_to_from = 'to' if cross == to_bus else 'from'
                    if net_name not in all_edges:
                        all_edges[net_name] = []
                    all_edges[net_name].append(([edge for edge in edges[net_name] if edge.id == i and edge_type == edge.component_type()][0], key_to_from, point_name))

    return all_edges

def post(node):
    for _, edges in node.edges.items():
        for edge in edges:
            edge[0].add_node(node, edge[1], edge[2])
    return node

def check_part_of_controller(multinet, comp_index, comp_type, network_name):
    found = False
    for _, row in multinet.controller.iterrows():
        controller = row.object
        if network_name in controller.nodes and comp_index == controller.nodes[network_name][1] and controller.nodes[network_name][0] == comp_type:
            found = True 
            break
    return found

def is_empty_bus(multinet, bus_id, network_name):
    connected_elements = ppower.get_connected_elements_dict(multinet[NETS_ACCESS][network_name], bus_id)
    # its about being connected to a 'productive' element
    for type in ['bus', 'line', 'trafo']:
        if type in connected_elements:
            del connected_elements[type]
    return len(connected_elements) == 0

def is_empty_junction(multinet, junction_id, network_name):
    for type in ['sink', 'source']:
        if type in multinet[NETS_ACCESS][network_name]:
            for _, row in multinet[NETS_ACCESS][network_name][type].iterrows():
                if row['junction'] == junction_id:
                    return False
    for type in ['heat_exchanger']:
        if type in multinet[NETS_ACCESS][network_name]:
            for _, row in multinet[NETS_ACCESS][network_name][type].iterrows():
                if row['from_junction'] == junction_id or row['to_junction'] == junction_id:
                    return False
    return True

def from_panda_multinet(multinet):
    power_net = multinet[NETS_ACCESS][POWER_NET]
    gas_net = multinet[NETS_ACCESS][GAS_NET]
    heat_net = multinet[NETS_ACCESS][HEAT_NET] if HEAT_NET in multinet[NETS_ACCESS] else None
    nodes = { GAS_NET: [], 
             POWER_NET: [],
             HEAT_NET: [],
             MULTI: [] }
    edges = { GAS_NET: [], 
             POWER_NET: [],
             HEAT_NET: [],
             MULTI: [] }
    history_container= {}

    #edges
    for i in range(len(power_net.line)):
        edges[POWER_NET].append(LineEdge(i, power_net, history_container=history_container))
    for i in range(len(power_net.trafo)):
        edges[POWER_NET].append(TrafoEdge(i, power_net, history_container=history_container))
    for i in range(len(gas_net.pipe)):
        edges[GAS_NET].append(PipeEdge(i, gas_net, history_container=history_container))

    if heat_net is not None:
        for i in range(len(heat_net.pipe)):
            edges[HEAT_NET].append(PipeEdge(i, heat_net, history_container=history_container))
        if 'circ_pump_pressure' in heat_net:
            for i in range(len(heat_net.circ_pump_pressure)):
                edges[HEAT_NET].append(CircPumpPressureEdge(i, heat_net, history_container=history_container))
        if 'circ_pump_mass' in heat_net:
            for i in range(len(heat_net.circ_pump_mass)):
                edges[HEAT_NET].append(CircPumpMassEdge(i, heat_net, history_container=history_container))

    # controller
    for i, row in multinet.controller.iterrows():
        controller = row.object

        if isinstance(controller, RegulatedP2GControlMultiEnergy):
            nodes[MULTI].append(post(P2GNode(i, multinet, find_edges_controller(edges, controller))))
        if isinstance(controller, RegulatedG2PControlMultiEnergy):
            nodes[MULTI].append(post(G2PNode(i, multinet, find_edges_controller(edges, controller))))
        if isinstance(controller, CHPControlMultiEnergy):
            nodes[MULTI].append(post(CHPNode(i, multinet, find_edges_controller(edges, controller))))

    # power
    for i in range(len(power_net.load)):
        if not check_part_of_controller(multinet, i, "load", POWER_NET):
            nodes[POWER_NET].append(post(PowerLoadNode(i, power_net, find_edges(edges, i, power_net, POWER_NET, 'load', 'bus'))))

    for i in range(len(power_net.gen)):
        if not check_part_of_controller(multinet, i, "gen", POWER_NET):
            nodes[POWER_NET].append(post(GeneratorNode(i, power_net, find_edges(edges, i, power_net, POWER_NET, 'gen', 'bus'))))

    for i in range(len(power_net.sgen)):
        if not check_part_of_controller(multinet, i, "sgen", POWER_NET):
            nodes[POWER_NET].append(post(SGeneratorNode(i, power_net, find_edges(edges, i, power_net, POWER_NET, 'sgen', 'bus'))))

    for i in range(len(power_net.ext_grid)):
        if not check_part_of_controller(multinet, i, "ext_grid", POWER_NET):
            nodes[POWER_NET].append(post(ExtPowerGrid(i, power_net, find_edges(edges, i, power_net, POWER_NET, 'ext_grid', 'bus'))))

    for i in range(len(power_net.bus)):
        if is_empty_bus(multinet, i, POWER_NET):
            nodes[POWER_NET].append(post(EmptyBusNode(i, power_net, find_edges(edges, i, power_net, POWER_NET, 'bus', 'bus'))))


    # gas
    for i in range(len(gas_net.sink)):
        if not check_part_of_controller(multinet, i, "sink", GAS_NET):
            nodes[GAS_NET].append(post(SinkNode(i, gas_net, find_edges(edges, i, gas_net, GAS_NET, 'sink', 'junction'))))

    for i in range(len(gas_net.source)):
        if not check_part_of_controller(multinet, i, "source", GAS_NET):
            nodes[GAS_NET].append(post(SourceNode(i, gas_net, find_edges(edges, i, gas_net, GAS_NET, 'source', 'junction'))))

    for i in range(len(gas_net.ext_grid)):
        if not check_part_of_controller(multinet, i, "ext_grid", GAS_NET):
            nodes[GAS_NET].append(post(ExtGasGrid(i, gas_net, find_edges(edges, i, gas_net, GAS_NET, 'ext_grid', 'junction'))))

    # heat
    if heat_net is not None:
        if 'sink' in heat_net:
            for i in range(len(heat_net.sink)):
                if not check_part_of_controller(multinet, i, "source", HEAT_NET):
                    nodes[HEAT_NET].append(post(SinkNode(i, heat_net, find_edges(edges, i, heat_net, HEAT_NET, 'sink', 'junction'))))

        # in heat networks you model a source as heat exchanger, therefore there is not necessarily a source
        if 'source' in heat_net:
            for i in range(len(heat_net.source)):
                if not check_part_of_controller(multinet, i, "source", HEAT_NET):
                    nodes[HEAT_NET].append(post(SourceNode(i, heat_net, find_edges(edges, i, heat_net, HEAT_NET, 'source', 'junction'))))

        for i in range(len(heat_net.junction)):
            if is_empty_junction(multinet, i, HEAT_NET):
                nodes[HEAT_NET].append(post(EmptyJunctionNode(i, heat_net, find_edges(edges, i, heat_net, HEAT_NET, 'junction', 'junction'))))
        
        if 'heat_exchanger' in heat_net:
            for i in range(len(heat_net.heat_exchanger)):
                if not check_part_of_controller(multinet, i, "heat_exchanger", HEAT_NET):
                    nodes[HEAT_NET].append(post(HeatExchangerNode(i, heat_net, {**find_edges(edges, i, heat_net, HEAT_NET, 'heat_exchanger', 'to_junction'), **find_edges(edges, i, heat_net, HEAT_NET, 'heat_exchanger', 'from_junction')})))

        for i in range(len(heat_net.ext_grid)):
            if not check_part_of_controller(multinet, i, "ext_grid", HEAT_NET):
                nodes[HEAT_NET].append(post(ExtGasGrid(i, heat_net, find_edges(edges, i, heat_net, HEAT_NET, 'ext_grid', 'junction'))))


    return MENetwork(nodes = nodes, edges = edges, multinet=multinet, history_container=history_container)