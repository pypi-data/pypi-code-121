"""Pandapipes/power controller used to couple different networks.
"""
from peext.storage import EnergyStorage
from pandapipes.multinet.control.controller.multinet_control import G2PControlMultiEnergy, P2GControlMultiEnergy
from overrides import overrides
from pandapower.control.basic_controller import Controller

NETS_ACCESS = 'nets'
P_MW = 'p_mw'

def find_for_junction(net, key, junction_id, connect_point):
    """Searches for all objects connected to a junction. Return the obj id + the direction.

    :param net: the network
    :type net: pandapipes network
    :param junction_id: id of the junction
    :type junction_id: int
    :return: Dictionary will all obj (obj_id, direction in ['to', 'from'])
    :rtype: Dict
    """
    obj = {}
    for index, row in net[key].iterrows():
        if row['from_junction'] == junction_id:
            obj[index] = ('from', key, connect_point)
        if row['to_junction'] == junction_id:
            obj[index] = ('to', key, connect_point)
    return obj

def find_pipes_for_junction(net, junction_id, connect_point=''):
    """Searches for all pipes connected to a junction. Return the pipe id + the direction.

    :param net: the network
    :type net: pandapipes network
    :param junction_id: id of the junction
    :type junction_id: int
    :return: Dictionary will all pipes (pipe_id, direction in ['to', 'from'])
    :rtype: Dict
    """
    pipes = find_for_junction(net, 'pipe', junction_id, connect_point)

    # if no pipe directly connected, look for connected pump and their pipes
    if len(pipes) == 0:
        for key in ['pump', 'circ_pump_pressure', 'circ_pump_mass']:
            if key in net:
                pump = find_for_junction(net, key, junction_id, connect_point)
                pipes.update(pump)

    return pipes

def find_lines_for_bus(net, bus_id, connect_point=''):
    """Searches for all lines connected to a bus. Return the bus id + the direction.

    :param net: the network
    :type net: pandapower network
    :param bus_id: id of the junction
    :type bus_id: int
    :return: Dictionary will all lines (line_id, direction in ['to', 'from'])
    :rtype: Dict
    """
    lines = {}
    for index, row in net.line.iterrows():
        if row['from_bus'] == bus_id:
            lines[index] = ('from', 'line', connect_point)
        if row['to_bus'] == bus_id:
            lines[index] = ('to', 'line', connect_point)
    return lines

class RoleListController(Controller):
    """Interface to the pandapipes/power controller system to overcome the need to have
    a mango agent. Useful for time-series simulations without the need of communication
    between real agents.
    """
    def __init__(self, multinet, names, roles, in_service=True, order=0,
                 level=0, drop_same_existing_ctrl=False, initial_run=True,
                 calc_gas_from_power=False, **kwargs):
        super().__init__(multinet, in_service, order, level,
                        drop_same_existing_ctrl=drop_same_existing_ctrl, initial_run=initial_run,
                        **kwargs)

        self._names = names
        self._roles = roles

    def initialize_control(self, multinet):
        self.applied = False

    def get_all_net_names(self):
        return self._names

    def time_step(self, net, time):
        if time > 0:
            self.applied = False

            for role in self._roles:
                if time % (role.time_pause() + 1) == 0:
                    role.control()

    def control_step(self, multinet):
        self.applied = True

    def is_converged(self, multinet):
        return self.applied


class CHPControlMultiEnergy(G2PControlMultiEnergy):
    """Coupling controller representing a CHP unit without boiler. The heat energy will directly be injected to the heat-network via heat-exchanger and
    its efficiency. 

    :param G2PControlMultiEnergy: [description]
    :type G2PControlMultiEnergy: [type]
    """

    def __init__(self, multinet, element_index_power, element_index_gas, heat_exchanger_id, efficiency, set_point_temp_out, name,
                 name_power_net='power', name_gas_net='gas', name_heat_net='heat', element_type_power="gen", initial_heat_regulation=0.001,
                 storage_cap=1000, storage_charge_eff=0.81 , storage_discharge_eff=0.81,
                 in_service=True, order=0,
                 level=0, drop_same_existing_ctrl=False, initial_run=True,
                 calc_gas_from_power=False, ambient_temperature=24, **kwargs):

        super().__init__(multinet, element_index_power, element_index_gas, efficiency, name_power_net=name_power_net,
            name_gas_net=name_gas_net, element_type_power=element_type_power,
            in_service=in_service, order=order, level=level, drop_same_existing_ctrl=drop_same_existing_ctrl, initial_run=initial_run, 
            calc_gas_from_power=calc_gas_from_power, **kwargs)

        self.name = name
        self.__load_regulation_multiplier = 1
        self.__heat_regulation_multiplier = initial_heat_regulation
        self.__ambient_temperature_in_k = ambient_temperature
        self.__name_heat_net = name_heat_net
        self.__heat_exchanger_id = heat_exchanger_id
        self.__storage_builder = EnergyStorage.builder() \
                .step_size(1) \
                .load(0) \
                .capacity(storage_cap) \
                .self_discharge(0) \
                .charge_efficiency(storage_charge_eff) \
                .discharge_efficiency(storage_discharge_eff)
        self.storage = None
        self.heat_energy = 0
        self.power_gen = 0
        
        heat_net = multinet['nets'][self.__name_heat_net]
        power_net = multinet['nets'][self.name_net_power]
        gas_net = multinet['nets'][self.name_net_gas]

        from_heat_junc = heat_net.heat_exchanger.loc[self.__heat_exchanger_id, 'from_junction']
        to_heat_junc = heat_net.heat_exchanger.loc[self.__heat_exchanger_id, 'to_junction']
        bus_gen = power_net[self.elm_type_power].loc[self.elm_idx_power, 'bus']
        junction_sink = gas_net.sink.loc[self.elm_idx_gas, 'junction']

        self._pipes_heat = dict(find_pipes_for_junction(heat_net, from_heat_junc, 'from_junction'))
        self._pipes_heat.update(find_pipes_for_junction(heat_net, to_heat_junc, 'to_junction'))
        self._line_power = find_lines_for_bus(power_net, bus_gen)
        self._pipes_gas = find_pipes_for_junction(gas_net, junction_sink)
    
    def get_gas_consume(self, multinet):
        try:
            gas_sink = multinet['nets'][self.name_net_gas].sink.at[self.elm_idx_gas,
                                                                'mdot_kg_per_s']
        except (ValueError, TypeError):
            gas_sink = multinet['nets'][self.name_net_gas].sink.loc[self.elm_idx_gas,
                                                                'mdot_kg_per_s'].values[:]
        return gas_sink

    def get_power_production(self, multinet):
        try:
            power_gen = multinet['nets'][self.name_net_power][self.elm_type_power].at[
                self.elm_idx_power, 'p_mw']
        except (ValueError, TypeError):
            power_gen = multinet['nets'][self.name_net_power][self.elm_type_power].loc[
                            self.elm_idx_power, 'p_mw'].values[:]
        return power_gen

    def time_step(self, multinet, time):
        if time == 0:
            self.ref_gas_consume = self.get_gas_consume(multinet)
            self.ref_power_production = self.get_power_production(multinet)

        gas_flow = 0

        if self.el_power_led:
            try:
                power_gen = multinet['nets'][self.name_net_power][self.elm_type_power].at[
                    self.elm_idx_power, 'p_mw']
            except (ValueError, TypeError):
                power_gen = multinet['nets'][self.name_net_power][self.elm_type_power].loc[
                                self.elm_idx_power, 'p_mw'].values[:]

            self.gas_cons = gas_flow = (power_gen / (self.conversion_factor_kgps_to_mw() * self.efficiency)) * self.__load_regulation_multiplier
            self.power_gen = self.ref_power_production * self.__load_regulation_multiplier

        else:
            try:
                gas_sink = gas_flow = multinet['nets'][self.name_net_gas].sink.at[self.elm_idx_gas,
                                                                       'mdot_kg_per_s'] * self.__load_regulation_multiplier
            except (ValueError, TypeError):
                gas_sink = gas_flow = multinet['nets'][self.name_net_gas].sink.loc[self.elm_idx_gas,
                                                                        'mdot_kg_per_s'].values[:] * self.__load_regulation_multiplier
            self.gas_cons = self.ref_gas_consume * self.__load_regulation_multiplier
            self.power_gen = gas_sink * self.conversion_factor_kgps_to_mw() * self.efficiency

        heat_energy_overall = (gas_flow * self.conversion_factor_kgps_to_mw() * (0.000028 * self.__ambient_temperature_in_k \
            + 273.3567) + 2.1609 * self.__ambient_temperature_in_k + 339.714)
        self.heat_energy = heat_energy_overall * self.heat_regulation 
        self.heat_save_energy = heat_energy_overall * (1 - self.heat_regulation)
        self.storage = self.__storage_builder.build()
        self.storage.charge(self.heat_save_energy)
        self.write_to_net(multinet)

    def control_step(self, _):
        self.applied = True

    @overrides
    def get_all_net_names(self):
        return [self.name_net_gas, self.name_net_power, self.__name_heat_net]

    def write_to_net(self, multinet):
        try:
            multinet['nets'][self.name_net_gas].sink.at[self.elm_idx_gas,
                                                        'mdot_kg_per_s'] = self.gas_cons
        except (ValueError, TypeError):
            multinet['nets'][self.name_net_gas].sink.loc[self.elm_idx_gas,
                                                            'mdot_kg_per_s'] = self.gas_cons
        try:
            multinet['nets'][self.name_net_power][self.elm_type_power].at[
                self.elm_idx_power, 'p_mw'] = self.power_gen
        except (ValueError, TypeError):
            multinet['nets'][self.name_net_power][self.elm_type_power].loc[
                self.elm_idx_power, 'p_mw'] = self.power_gen

        try:
            multinet['nets'][self.__name_heat_net].heat_exchanger.at[self.__heat_exchanger_id, 'qext_w'] = -self.heat_energy
        except (ValueError, TypeError):
            multinet['nets'][self.__name_heat_net].heat_exchanger.loc[self.__heat_exchanger_id, 'qext_w'].values[:] = -self.heat_energy

    @property
    def edges(self):
        """Return all edges connected to the CHP unit.

        :return: dict, energy-network-name -> edges
        :rtype: Dict
        """
        
        return {self.name_net_power: self._line_power, 
                self.name_net_gas: self._pipes_gas, 
                self.__name_heat_net: self._pipes_heat}

    @property
    def nodes(self):
        return {self.name_net_power: (self.elm_type_power, self.elm_idx_power), 
                self.name_net_gas: ('sink', self.elm_idx_gas),
                self.__name_heat_net: ('heat_exchanger', self.__heat_exchanger_id)}
    @property
    def regulation(self):
        return self.__load_regulation_multiplier

    @property
    def heat_regulation(self):
        return self.__heat_regulation_multiplier

    @regulation.setter
    def regulation(self, new_value):
        self.__load_regulation_multiplier = new_value

    @heat_regulation.setter
    def heat_regulation(self, new_value):
        self.__heat_regulation_multiplier = new_value

    @property
    def storage_load(self):
        return self.storage.load

    def state_as_dict(self):
        return {'regulation': self.regulation, 'heat_regulation': self.heat_regulation, 'storage_load': self.storage_load}


class RegulatedG2PControlMultiEnergy(G2PControlMultiEnergy):
    """Models a regulatable g2p coupling point.
    """

    def __init__(self, multinet, element_index_power, element_index_gas, efficiency, name,
                 name_power_net='power', name_gas_net='gas', element_type_power='sgen', desync_mode=False,
                 in_service=True, order=0, level=0,
                 drop_same_existing_ctrl=False, initial_run=True, **kwargs):
        super().__init__(multinet, element_index_power, element_index_gas, efficiency, name_power_net=name_power_net, element_type_power=element_type_power,
                         name_gas_net=name_gas_net, in_service=in_service, order=order, level=level, 
                         drop_same_existing_ctrl=drop_same_existing_ctrl, initial_run=initial_run, **kwargs)

        self.__load_regulation_multiplier = 1
        self.name = name
        self.power_gen = 0
        self._desync = desync_mode

        
        power_net = multinet['nets'][self.name_net_power]
        gas_net = multinet['nets'][self.name_net_gas]

        bus_gen = power_net[self.elm_type_power].loc[self.elm_idx_power, 'bus']
        junction_sink = gas_net.sink.loc[self.elm_idx_gas, 'junction']

        self._line_power = find_lines_for_bus(power_net, bus_gen) 
        self._pipes_gas = find_pipes_for_junction(gas_net, junction_sink)

    def get_gas_consume(self, multinet):
        try:
            gas_sink = multinet['nets'][self.name_net_gas].sink.at[self.elm_idx_gas,
                                                                'mdot_kg_per_s']
        except (ValueError, TypeError):
            gas_sink = multinet['nets'][self.name_net_gas].sink.loc[self.elm_idx_gas,
                                                                'mdot_kg_per_s'].values[:]
        return gas_sink

    def get_power_production(self, multinet):
        try:
            power_gen = multinet['nets'][self.name_net_power][self.elm_type_power].at[
                self.elm_idx_power, 'p_mw']
        except (ValueError, TypeError):
            power_gen = multinet['nets'][self.name_net_power][self.elm_type_power].loc[
                            self.elm_idx_power, 'p_mw'].values[:]
        return power_gen


    def time_step(self, multinet, time):
        if time == 0:
            self.ref_gas_consume = self.get_gas_consume(multinet)
            self.ref_power_production = self.get_power_production(multinet)
        
        if self.el_power_led:
            self.gas_cons = (self.get_power_production(multinet)*self.__load_regulation_multiplier) / (self.conversion_factor_kgps_to_mw() * self.efficiency)
            self.power_gen = self.ref_power_production * self.__load_regulation_multiplier
        else:
            self.power_gen = self.__load_regulation_multiplier * self.get_gas_consume(multinet) * self.conversion_factor_kgps_to_mw() * self.efficiency
            self.gas_cons = self.ref_gas_consume * self.__load_regulation_multiplier

        self.write_to_net(multinet)

    def write_to_net(self, multinet):  
        # we always have to write both values, as the regulation can change the static one.
        try:
            multinet['nets'][self.name_net_gas].sink.at[self.elm_idx_gas,
                                                        'mdot_kg_per_s'] = self.gas_cons
        except (ValueError, TypeError):
            multinet['nets'][self.name_net_gas].sink.loc[self.elm_idx_gas,
                                                            'mdot_kg_per_s'] = self.gas_cons
        try:
            multinet['nets'][self.name_net_power][self.elm_type_power].at[
                self.elm_idx_power, 'p_mw'] = self.power_gen
        except (ValueError, TypeError):
            multinet['nets'][self.name_net_power][self.elm_type_power].loc[
                self.elm_idx_power, 'p_mw'] = self.power_gen


    def control_step(self, multinet):
        self.applied = True
    
    @property
    def nodes(self):
        return {self.name_net_power: (self.elm_type_power, self.elm_idx_power), 
                self.name_net_gas: ('sink', self.elm_idx_gas)}

    @property
    def edges(self):
        return {self.name_net_power: self._line_power, self.name_net_gas: self._pipes_gas}

    @property
    def regulation(self):
        return self.__load_regulation_multiplier

    @regulation.setter
    def regulation(self, new_value):
        self.__load_regulation_multiplier = new_value

class RegulatedP2GControlMultiEnergy(P2GControlMultiEnergy):
    """Models a regulatable p2g coupling point.
    """

    def __init__(self, multinet, element_index_power, element_index_gas, efficiency, name, desync_mode=False,
                 name_power_net='power', name_gas_net='gas', in_service=True, order=0, level=0,
                 drop_same_existing_ctrl=False, initial_run=True, **kwargs):
        super().__init__(multinet, element_index_power, element_index_gas, efficiency, name_power_net=name_power_net, 
                         name_gas_net=name_gas_net, in_service=in_service, order=order, level=level, 
                         drop_same_existing_ctrl=drop_same_existing_ctrl, initial_run=initial_run, **kwargs)

        self.__load_regulation_multiplier = 1
        self.name = name
        self._desync = desync_mode
        power_net = multinet['nets'][self.name_net_power]
        gas_net = multinet['nets'][self.name_net_gas]

        bus_gen = power_net.load.loc[self.elm_idx_power, 'bus']
        junction_sink = gas_net.source.loc[self.elm_idx_gas, 'junction']

        self._line_power = find_lines_for_bus(power_net, bus_gen) 
        self._pipes_gas = find_pipes_for_junction(gas_net, junction_sink)

    def get_power_load(self, multinet):
        try:
            power_load = multinet[NETS_ACCESS][self.name_net_power].load.at[self.elm_idx_power, P_MW]
        except (ValueError, TypeError):
            power_load = multinet[NETS_ACCESS][self.name_net_power].load.loc[self.elm_idx_power, P_MW].values[:]
        return power_load

    def get_source_production(self, multinet):
        try:
            prod = multinet[NETS_ACCESS][self.name_net_gas].source.at[self.elm_idx_gas, 'mdot_kg_per_s']
        except (ValueError, TypeError):
            prod = multinet[NETS_ACCESS][self.name_net_gas].source.loc[self.elm_idx_gas, 'mdot_kg_per_s'].values[:]
        return prod

    def time_step(self, multinet, time):
        if time == 0:
            self.ref_power_load = self.get_power_load(multinet)
        
        self.mdot_kg_per_s = self.__load_regulation_multiplier * self.get_power_load(multinet) * self.conversion_factor_mw_to_kgps()[0] * self.efficiency
        self.power_load = self.ref_power_load * self.__load_regulation_multiplier
        self.write_to_net(multinet)

    def write_to_net(self, multinet):
        try:
            multinet[NETS_ACCESS][self.name_net_gas].source.at[self.elm_idx_gas, 'mdot_kg_per_s'] \
                = self.mdot_kg_per_s
        except (ValueError, TypeError):
            multinet[NETS_ACCESS][self.name_net_gas].source.loc[self.elm_idx_gas,
                                                           'mdot_kg_per_s'].values[:] = self.mdot_kg_per_s
        try:
            multinet[NETS_ACCESS][self.name_net_power].load.at[self.elm_idx_power, P_MW] = self.power_load
        except (ValueError, TypeError):
            multinet[NETS_ACCESS][self.name_net_power].load.loc[self.elm_idx_power, P_MW].values[:] = self.power_load

    def control_step(self, _):
        self.applied = True    
    
    @property
    def nodes(self):
        return {self.name_net_power: ('load', self.elm_idx_power), 
                self.name_net_gas: ('source', self.elm_idx_gas)}

    @property
    def edges(self):
        
        return {self.name_net_power: self._line_power, self.name_net_gas: self._pipes_gas}

    @property
    def regulation(self):
        return self.__load_regulation_multiplier

    @regulation.setter
    def regulation(self, new_value):
        self.__load_regulation_multiplier = new_value


class HistoryController(Controller):
    """Interface to the controller system of pandapower/pipes. Collect the data at each time step an shows 
    live updating graphs.
    """
    def __init__(self, multinet, names, me_network, network_to_collect_types, in_service=True, order=0,
                 level=0, drop_same_existing_ctrl=False, initial_run=True, **kwargs):
        super().__init__(multinet, in_service, order, level,
                        drop_same_existing_ctrl=drop_same_existing_ctrl, initial_run=initial_run,
                        **kwargs)

        self._names = names
        self._me_network = me_network
        self._network_to_collect_types = network_to_collect_types

    def initialize_control(self, multinet):
        self.applied = False

    def get_all_net_names(self):
        return self._names

    def time_step(self, net, time):
        if time > 0:
            for net_name, types in self._network_to_collect_types.items():
                if net_name in net[NETS_ACCESS]:
                    for t in types:
                        self._me_network.add_history_table(net_name, t, net[NETS_ACCESS][net_name][f'res_{t}'])

    def control_step(self, multinet):
        self.applied = True

    def is_converged(self, multinet):
        return self.applied