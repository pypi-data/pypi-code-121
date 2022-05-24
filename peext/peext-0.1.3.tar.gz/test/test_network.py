
import pandapower as ppower
import pandapipes as ppipes
import pandapipes.multinet as ppm

from peext.controller import CHPControlMultiEnergy, RegulatedP2GControlMultiEnergy

import peext.network as network

def create_small_test_multinet():
    """Factory for the panda-multinet.

    :return: multinet
    :rtype: pandapower/pipes multinet
    """

    # Setup power network
    net_power = ppower.create_empty_network('power')
    bus_id = ppower.create_bus(net_power, vn_kv = 1, name = "bus_el")
    bus_id2 = ppower.create_bus(net_power, vn_kv = 1, name = "bus_el2")
    bus_id3 = ppower.create_bus(net_power, vn_kv = 1, name = "bus_el3")
    bus_id4 = ppower.create_bus(net_power, vn_kv = 1, name = "bus_el4")
    ppower.create_line_from_parameters(net_power, from_bus=bus_id, to_bus=bus_id2, length_km=10, r_ohm_per_km=1, x_ohm_per_km=1, c_nf_per_km=20, max_i_ka=20, name="PHLine")
    ppower.create_line_from_parameters(net_power, from_bus=bus_id, to_bus=bus_id3, length_km=10, r_ohm_per_km=1, x_ohm_per_km=1, c_nf_per_km=20, max_i_ka=20, name="TWLine")
    ppower.create_line_from_parameters(net_power, from_bus=bus_id2, to_bus=bus_id4, length_km=1, r_ohm_per_km=1, x_ohm_per_km=1, c_nf_per_km=20, max_i_ka=20, name="ASLine")
    ppower.create_ext_grid(net_power, bus = bus_id, vm_pu = 10)
    ppower.create_gen(net_power, bus_id3, p_mw = 1, vm_pu = 10, name="Torgenerator")
    ppower.create_load(net_power, bus = bus_id4, p_mw = 0.1, name='ALoad')
    

    # Setup L-Gas network
    net_gas = ppipes.create_empty_network('gas', fluid="lgas")
    jun_id = ppipes.create_junction(net_gas, pn_bar=20, tfluid_k = 290)
    jun_id2 = ppipes.create_junction(net_gas, pn_bar=20, tfluid_k = 290)
    jun_id3 = ppipes.create_junction(net_gas, pn_bar=20, tfluid_k = 290)
    jun_id4 = ppipes.create_junction(net_gas, pn_bar=20, tfluid_k = 290)
    ppipes.create_pipe_from_parameters(net_gas, from_junction=jun_id, to_junction=jun_id2, length_km=1.1, diameter_m=0.05, name="Pipe 1")
    ppipes.create_pipe_from_parameters(net_gas, from_junction=jun_id2, to_junction=jun_id3, length_km=1.1, diameter_m=0.15, name="Pipe 2")
    ppipes.create_pipe_from_parameters(net_gas, from_junction=jun_id3, to_junction=jun_id4, length_km=1.1, diameter_m=0.15, name="Pipe 3")
    ppipes.create_sink(net_gas, junction=jun_id3, mdot_kg_per_s=0.085, name="Sink 2")
    ppipes.create_ext_grid(net_gas, junction=jun_id, p_bar=5.2, t_k=293.15, name="Grid Connection")

    
    # Setup Heat network
    net_heat = ppipes.create_empty_network('heat', fluid="water")
    jun_id_heat = ppipes.create_junction(net_heat, pn_bar=5, tfluid_k = 308)
    jun_id2_heat = ppipes.create_junction(net_heat, pn_bar=5, tfluid_k = 293)
    jun_id3_heat = ppipes.create_junction(net_heat, pn_bar=5, tfluid_k = 293)
    jun_id4_heat = ppipes.create_junction(net_heat, pn_bar=5, tfluid_k = 293)
    ppipes.create_circ_pump_const_mass_flow(net_heat, from_junction=jun_id3_heat, to_junction=jun_id4_heat, p_bar=5, mdot_kg_per_s=20, t_k=273.15+35)
    ppipes.create_pipe_from_parameters(net_heat, from_junction=jun_id2_heat, to_junction=jun_id3_heat, length_km=1,
                               diameter_m=200e-3, k_mm=.1, alpha_w_per_m2k=10, sections = 5, text_k=283, name="Heat Pipe 1")
    ppipes.create_pipe_from_parameters(net_heat, from_junction=jun_id4_heat, to_junction=jun_id_heat, length_km=1,
                               diameter_m=200e-3, k_mm=.1, alpha_w_per_m2k=10, sections = 5, text_k=283, name="Heat Pipe 2")
    
    # Multinet for coupling of those networks
    mn = ppm.create_empty_multinet('multi')
    ppm.add_net_to_multinet(mn, net_gas, net_name="gas")
    ppm.add_net_to_multinet(mn, net_power, net_name="power")
    ppm.add_net_to_multinet(mn, net_heat, net_name="heat")

    # Create coupling point chp    
    chp_gen = ppower.create_gen(net_power, bus_id3, p_mw = 1, vm_pu = 10, name="CHPTorgenerator")
    chp_sink = ppipes.create_sink(net_gas, junction=jun_id3, mdot_kg_per_s=0.085, name="CHP Sink")
    chp_heat_feed_in = ppipes.create_heat_exchanger(net_heat, from_junction=jun_id_heat, to_junction=jun_id2_heat, diameter_m=200e-3, qext_w=-10000)
    CHPControlMultiEnergy(mn, chp_gen, chp_sink, chp_heat_feed_in, 0.8, 300, "CHP1", ambient_temperature=282.5)
    
    # Create coupling point power2gas
    p2g_id_el = ppower.create_load(net_power, bus = bus_id2, p_mw = 1, name='ALoad')
    p2g_id_gas = ppipes.create_source(net_gas, junction = jun_id2, mdot_kg_per_s = 0.5, name='ASource')
    ppipes.create_source(net_gas, junction = jun_id4, mdot_kg_per_s = 0.2, name='A2Source')
    RegulatedP2GControlMultiEnergy(mn, p2g_id_el, p2g_id_gas, efficiency = 0.8, name="ANp2g")

    #run_timeseries(net_heat, time_steps=range(10), output_writers=create_output_writers(net_heat, 3), mode='all')
    #plot.simple_plot(net_heat, plot_sinks=True, plot_sources=True)
    #plot.simple_plot(net_gas, plot_sinks=True, plot_sources=True)
    return mn

def test_from_pandapipes():
    # GIVEN
    test_network = create_small_test_multinet()

    # WHEN
    me_network = network.from_panda_multinet(test_network)

    # THEN
    assert len(me_network.nodes) == 10
    assert len(me_network.edges) == 9
    assert len(me_network.nodes[8].edges) == 3
    assert me_network.nodes[8].edges['power'][0][1] == 'to'
    assert me_network.nodes[8].edges['power'][0][0]._id == 1
    assert me_network.nodes[8].edges['gas'][0][1] == 'to'
    assert me_network.nodes[8].edges['gas'][0][0]._id == 1
    assert me_network.nodes[8].edges['heat'][0][1] == 'from'
    assert me_network.nodes[8].edges['heat'][0][0]._id == 0
    
