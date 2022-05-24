"""Contains a number of multi energy network definitions.
"""
from numpy import random
from pandapower.timeseries.data_sources.frame_data import DFData

import pandapower as ppower
import pandapipes as ppipes
import pandapipes.multinet as ppm
import pandapower.networks as pandapowernetworks
import pandapipes.networks as pipesnetworks
import pandapipes.plotting as pipeplot
import pandapower.plotting as powerplot
import pandapower.control as powercontrol

import pandas as pd
import numpy as np
import math
import random

from peext.controller import CHPControlMultiEnergy, RegulatedG2PControlMultiEnergy, RegulatedP2GControlMultiEnergy

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

def create_big_multinet_gas_power():
    """Evaluation NET for big example with several controllers, which might act conflicting.
        Most of the components will use static data (load-data, schedules).
    """
    schutterwald_gas_net = pipesnetworks.schutterwald()
    mv_rhein_power_net = pandapowernetworks.mv_oberrhein()
    pipeplot.simple_plot(schutterwald_gas_net, plot_sinks=True, plot_sources=True)
    powerplot.simple_plot(mv_rhein_power_net, plot_loads=True, plot_sgens=True)

def generate_load_profiles(net_gas, net_power, net_heat, time_steps, with_heat, load_type, load_mul):
        # power loads
    TS_LEN = time_steps
    random_load_matr = np.random.normal(0.03 * load_mul, 0.01, (TS_LEN, len(net_power.load.index)))
    sink_matr = np.full((TS_LEN, len(net_gas.sink.index)), 0.8)
    heat_matr = None

    if with_heat:
        heat_matr = np.full((TS_LEN, len(net_heat.heat_exchanger.index)), 0.5)

    # sin curves for load/sinks in range 30 to 80
    if load_type == 'sin':
        for i in range(TS_LEN):
            random_load_matr[i, :] = (np.sin(i/10 + np.array([i for i in range(len(net_power.load.index))])) + 1) * load_mul + 20
            sink_matr[i, :] = (math.sin(i/10 + math.pi) + 1) * load_mul
            if with_heat:
                heat_matr[i, :] = (math.sin(i/10 + math.pi/2) + 1) * load_mul
    elif load_type == 'ssin':
        # load peaks in range 30 to 80
        for i in range(TS_LEN):
            sink_matr[i, :] = (math.sin(i/10 + math.pi) + 1) * load_mul
    elif load_type == 'ssin2':
        # load peaks in range 30 to 80
        for i in range(TS_LEN):
            random_load_matr[i, :] = (math.sin(i/10) + 1) * load_mul
    elif load_type == 'ext':
        # load peaks in range 30 to 80
        for i in range(30, TS_LEN-10):
            random_load_matr[i, :] *= random.randint(2, 6) * load_mul
            sink_matr[i, :] = sink_matr[0, 0] * random.randint(2, 4) * load_mul
            if with_heat:
                heat_matr[i, :] = heat_matr[0, 0] * random.randint(2, 4) * load_mul
    elif load_type == 'aext':
        # load peaks in range 30 to 80
        for i in range(30, TS_LEN-10):
            random_load_matr[i, :] *= -random.randint(2, 6) * load_mul
            sink_matr[i, :] = sink_matr[0, 0] * random.randint(2, 4) * load_mul
            if with_heat:
                heat_matr[i, :] = heat_matr[0, 0] * random.randint(2, 4) * load_mul
    elif load_type == 'aext2':
        # load peaks in range 30 to 80
        for i in range(30, TS_LEN-10):
            random_load_matr[i, :] *= random.randint(2, 6) * load_mul
            sink_matr[i, :] = sink_matr[0, 0] * -random.randint(2, 4) * load_mul
            if with_heat:
                heat_matr[i, :] = heat_matr[0, 0] * -random.randint(2, 4) * load_mul
    elif load_type == 'sext':
        # load peaks in range 30 to 80
        for i in range(30, TS_LEN-10):
            random_load_matr[i, :] *= random.randint(2, 6) * load_mul
            sink_matr[i, :] = sink_matr[0, 0] * load_mul
            if with_heat:
                heat_matr[i, :] = heat_matr[0, 0] * load_mul
    elif load_type == 'sext2':
        # load peaks in range 30 to 80
        for i in range(30, TS_LEN-10):
            random_load_matr[i, :] *=  load_mul
            sink_matr[i, :] = sink_matr[0, 0] * random.randint(2, 4) * load_mul
            if with_heat:
                heat_matr[i, :] = heat_matr[0, 0] * random.randint(2, 4) * load_mul

    return random_load_matr, heat_matr, sink_matr

def create_medium_multinet_gas_power(load_type=None, load_mul=1, time_steps=101, with_heat=False):
    """Evaluation NET for medium examples only consisting of generators and sinks.
    """
    # Setup power network
    net_power = pandapowernetworks.create_synthetic_voltage_control_lv_network("rural_1")
    net_power.name = 'power'

    # Setup L-Gas network
    REF_BAR = 60
    REF_TEMP = 290
    net_gas = ppipes.create_empty_network(name='gas', fluid="lgas")
    jun_id_ext = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k = REF_TEMP)
    jun_id = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k = REF_TEMP)
    jun_id2 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k = REF_TEMP)
    jun_id3 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k = REF_TEMP)
    jun_id4 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k = REF_TEMP)
    jun_id5 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k = REF_TEMP)
    jun_id6 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k = REF_TEMP)
    jun_id7 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k = REF_TEMP)
    jun_id8 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k = REF_TEMP)
    jun_id9 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k = REF_TEMP)
    jun_id10 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k = REF_TEMP)

    ppipes.create_pipe_from_parameters(net_gas, from_junction=jun_id6, to_junction=jun_id2, length_km=1.1, diameter_m=0.05, name="Pipe SI 6 SI 2")
    ppipes.create_pipe_from_parameters(net_gas, from_junction=jun_id6, to_junction=jun_id5, length_km=2.1, diameter_m=0.05, name="Pipe SI 6 SI 5")
    ppipes.create_pipe_from_parameters(net_gas, from_junction=jun_id6, to_junction=jun_id4, length_km=1.1, diameter_m=0.05, name="Pipe SI 6 SI 4")
    ppipes.create_pipe_from_parameters(net_gas, from_junction=jun_id5, to_junction=jun_id3, length_km=.5, diameter_m=0.05, name="Pipe SI 5 SI 3")
    ppipes.create_pipe_from_parameters(net_gas, from_junction=jun_id2, to_junction=jun_id, length_km=1.1, diameter_m=0.05, name="Pipe SI 2 SI 1")
    ppipes.create_pipe_from_parameters(net_gas, from_junction=jun_id7, to_junction=jun_id6, length_km=3.1, diameter_m=0.05, name="Pipe SI 7 SI 6")

    ppipes.create_pipe_from_parameters(net_gas, from_junction=jun_id_ext, to_junction=jun_id9, length_km=1.1, diameter_m=0.08, name="Pipe EXT SO 2")
    ppipes.create_pipe_from_parameters(net_gas, from_junction=jun_id8, to_junction=jun_id6, length_km=3.1, diameter_m=0.05, name="Pipe SO 1 SI 7")
    ppipes.create_pipe_from_parameters(net_gas, from_junction=jun_id9, to_junction=jun_id6, length_km=1.1, diameter_m=0.05, name="Pipe SO 2 SI 6")
    ppipes.create_pipe_from_parameters(net_gas, from_junction=jun_id10, to_junction=jun_id6, length_km=1.1, diameter_m=0.05, name="Pipe SO 2 SI 6")

    g_si_1 = ppipes.create_sink(net_gas, junction=jun_id, mdot_kg_per_s=0.02, name="BSink 1")
    g_si_2 = ppipes.create_sink(net_gas, junction=jun_id2, mdot_kg_per_s=0.045, name="SSink 2")
    ppipes.create_sink(net_gas, junction=jun_id3, mdot_kg_per_s=0.0085, name="SSink 3")
    ppipes.create_sink(net_gas, junction=jun_id4, mdot_kg_per_s=0.008, name="MSink 4")
    ppipes.create_sink(net_gas, junction=jun_id5, mdot_kg_per_s=0.0085, name="SSink 5")
    ppipes.create_sink(net_gas, junction=jun_id6, mdot_kg_per_s=0.00085, name="SSink 6")
    ppipes.create_sink(net_gas, junction=jun_id7, mdot_kg_per_s=0.008, name="MSink 7")

    g_s_1 = ppipes.create_source(net_gas, junction=jun_id8, mdot_kg_per_s=0.0285, name="BSource 1")
    g_s_2 = ppipes.create_source(net_gas, junction=jun_id9, mdot_kg_per_s=0.0285, name="BSource 2")
    ppipes.create_source(net_gas, junction=jun_id10, mdot_kg_per_s=0.01885, name="BSource 3")
    ppipes.create_ext_grid(net_gas, junction=jun_id_ext, p_bar=REF_BAR, t_k=REF_TEMP, name="Grid Connection Gas")

    # COUPLINGS
    mn = ppm.create_empty_multinet()
    ppm.add_net_to_multinet(mn, net_gas, net_name="gas")
    ppm.add_net_to_multinet(mn, net_power, net_name="power")

    # Setup Heat network
    net_heat = None
    if with_heat:
        HEAT_BAR = 5
        HEAT_TEMP = 363.15
        net_heat = ppipes.create_empty_network('heat', fluid="water")
        jun_id_heat = ppipes.create_junction(net_heat, pn_bar=HEAT_BAR, tfluid_k = HEAT_TEMP)
        jun_id2_heat = ppipes.create_junction(net_heat, pn_bar=HEAT_BAR, tfluid_k = HEAT_TEMP)
        jun_id3_heat = ppipes.create_junction(net_heat, pn_bar=HEAT_BAR, tfluid_k = HEAT_TEMP)
        jun_id4_heat = ppipes.create_junction(net_heat, pn_bar=HEAT_BAR, tfluid_k = HEAT_TEMP)
        jun_id5_heat = ppipes.create_junction(net_heat, pn_bar=HEAT_BAR, tfluid_k = HEAT_TEMP)
        jun_id6_heat = ppipes.create_junction(net_heat, pn_bar=HEAT_BAR, tfluid_k = HEAT_TEMP)
        chp_heat_feed_in = ppipes.create_heat_exchanger(net_heat, from_junction=jun_id_heat, to_junction=jun_id2_heat, diameter_m=0.075, qext_w=-0.1)
        ppipes.create_heat_exchanger(net_heat, from_junction=jun_id4_heat, to_junction=jun_id5_heat, diameter_m=0.075, qext_w=0.1)
        ppipes.create_heat_exchanger(net_heat, from_junction=jun_id5_heat, to_junction=jun_id6_heat, diameter_m=0.075, qext_w=0.1)
        ppipes.create_pipe_from_parameters(net_heat, from_junction=jun_id3_heat, to_junction=jun_id4_heat, length_km=0.1,
                                diameter_m=0.075, k_mm=.025, alpha_w_per_m2k=100, sections = 5, text_k=HEAT_TEMP, name="Heat Pipe 1")  
        ppipes.create_pipe_from_parameters(net_heat, from_junction=jun_id2_heat, to_junction=jun_id3_heat, length_km=0.1,
                                diameter_m=0.075, k_mm=.025, alpha_w_per_m2k=100, sections = 5, text_k=HEAT_TEMP, name="Heat Pipe 1")
        ppipes.create_pipe_from_parameters(net_heat, from_junction=jun_id6_heat, to_junction=jun_id_heat, length_km=0.1,
                                diameter_m=0.075, k_mm=.025, alpha_w_per_m2k=100, sections = 5, text_k=HEAT_TEMP, name="Heat Pipe 2")
        ppipes.create_ext_grid(net_heat, junction=jun_id6_heat, p_bar=HEAT_BAR, t_k=HEAT_TEMP, name="Grid Connection Heat")
        ppm.add_net_to_multinet(mn, net_heat, net_name='heat')

    random_load_matr, heat_matr, sink_matr = generate_load_profiles(net_gas, net_power, net_heat, time_steps, with_heat, load_type, load_mul)

    # P2G load exception
    random_load_matr[:, 2] = 0.18
    random_load_matr[:, 3] = 0.18
    sink_matr[:, g_si_1] = 0.8
    sink_matr[:, g_si_2] = 0.8

    if with_heat:
        heat_matr[:, chp_heat_feed_in] = -0.5

    df = pd.DataFrame(random_load_matr,
                    index=list(range(time_steps)), columns=net_power.load.index) * net_power.load.p_mw.values
    ds = DFData(df)
    powercontrol.ConstControl(net_power, element='load', element_index=net_power.load.index,
                                    variable='p_mw', data_source=ds, profile_name=net_power.load.index)

    # gas loads
    df = pd.DataFrame(sink_matr,
                    index=list(range(time_steps)), columns=net_gas.sink.index) * net_gas.sink.mdot_kg_per_s.values
    ds = DFData(df)
    powercontrol.ConstControl(net_gas, element='sink', element_index=net_gas.sink.index,
                                    variable='mdot_kg_per_s', data_source=ds, profile_name=net_gas.sink.index)

    if with_heat:
        # gas loads
        df = pd.DataFrame(heat_matr,
                        index=list(range(time_steps)), columns=net_heat.heat_exchanger.index) * net_heat.heat_exchanger.qext_w.values
        ds = DFData(df)
        powercontrol.ConstControl(net_heat, element='heat_exchanger', element_index=net_heat.heat_exchanger.index,
                                        variable='qext_w', data_source=ds, profile_name=net_heat.heat_exchanger.index)
            
        CHPControlMultiEnergy(mn, 0, g_si_1, chp_heat_feed_in, 0.8, 300, "CHP1", ambient_temperature=282.5, element_type_power='sgen')
        CHPControlMultiEnergy(mn, 1, g_si_2, chp_heat_feed_in, 0.8, 300, "CHP1", ambient_temperature=282.5, element_type_power='sgen')
    else:
        RegulatedG2PControlMultiEnergy(mn, 0, g_si_1, efficiency = 0.9, name="ANg2p2 0 0", element_type_power='sgen')
        RegulatedG2PControlMultiEnergy(mn, 1, g_si_2, efficiency = 0.85, name="ANg2p3 1 1", element_type_power='sgen')


    # partially overwrite constcontrol
    RegulatedP2GControlMultiEnergy(mn, 2, g_s_1, efficiency = 0.78, name="ANp2g1 1 0", element_type_power='gen')
    RegulatedP2GControlMultiEnergy(mn, 3, g_s_2, efficiency = 0.94, name="ANp2g2 2 1", element_type_power='gen')

    return mn

def create_big_multinet_gas_power(load_type=None, load_mul=1, time_steps=101, with_heat=False):
    """Evaluation NET for medium examples only consisting of generators and sinks.
    """
    # Setup power network
    net_power = pandapowernetworks.create_synthetic_voltage_control_lv_network("rural_1")
    net_power.name = 'power'

    # Setup L-Gas network
    REF_BAR = 60
    REF_TEMP = 290
    net_gas = ppipes.create_empty_network(name='gas', fluid="lgas")
    jun_id_ext = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k = REF_TEMP)
    jun_id = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k = REF_TEMP)
    jun_id2 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k = REF_TEMP)
    jun_id3 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k = REF_TEMP)
    jun_id4 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k = REF_TEMP)
    jun_id5 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k = REF_TEMP)
    jun_id6 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k = REF_TEMP)
    jun_id7 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k = REF_TEMP)
    jun_id8 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k = REF_TEMP)
    jun_id9 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k = REF_TEMP)
    jun_id10 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k = REF_TEMP)

    ppipes.create_pipe_from_parameters(net_gas, from_junction=jun_id6, to_junction=jun_id2, length_km=1.1, diameter_m=0.05, name="Pipe SI 6 SI 2")
    ppipes.create_pipe_from_parameters(net_gas, from_junction=jun_id6, to_junction=jun_id5, length_km=2.1, diameter_m=0.05, name="Pipe SI 6 SI 5")
    ppipes.create_pipe_from_parameters(net_gas, from_junction=jun_id6, to_junction=jun_id4, length_km=1.1, diameter_m=0.05, name="Pipe SI 6 SI 4")
    ppipes.create_pipe_from_parameters(net_gas, from_junction=jun_id5, to_junction=jun_id3, length_km=.5, diameter_m=0.05, name="Pipe SI 5 SI 3")
    ppipes.create_pipe_from_parameters(net_gas, from_junction=jun_id2, to_junction=jun_id, length_km=1.1, diameter_m=0.05, name="Pipe SI 2 SI 1")
    ppipes.create_pipe_from_parameters(net_gas, from_junction=jun_id7, to_junction=jun_id6, length_km=3.1, diameter_m=0.05, name="Pipe SI 7 SI 6")

    ppipes.create_pipe_from_parameters(net_gas, from_junction=jun_id_ext, to_junction=jun_id9, length_km=1.1, diameter_m=0.08, name="Pipe EXT SO 2")
    ppipes.create_pipe_from_parameters(net_gas, from_junction=jun_id8, to_junction=jun_id6, length_km=3.1, diameter_m=0.05, name="Pipe SO 1 SI 7")
    ppipes.create_pipe_from_parameters(net_gas, from_junction=jun_id9, to_junction=jun_id6, length_km=1.1, diameter_m=0.05, name="Pipe SO 2 SI 6")
    ppipes.create_pipe_from_parameters(net_gas, from_junction=jun_id10, to_junction=jun_id6, length_km=1.1, diameter_m=0.05, name="Pipe SO 2 SI 6")

    g_si_1 = ppipes.create_sink(net_gas, junction=jun_id, mdot_kg_per_s=0.02, name="BSink 1")
    g_si_2 = ppipes.create_sink(net_gas, junction=jun_id2, mdot_kg_per_s=0.045, name="SSink 2")
    ppipes.create_sink(net_gas, junction=jun_id3, mdot_kg_per_s=0.0085, name="SSink 3")
    ppipes.create_sink(net_gas, junction=jun_id4, mdot_kg_per_s=0.008, name="MSink 4")
    ppipes.create_sink(net_gas, junction=jun_id5, mdot_kg_per_s=0.0085, name="SSink 5")
    ppipes.create_sink(net_gas, junction=jun_id6, mdot_kg_per_s=0.00085, name="SSink 6")
    ppipes.create_sink(net_gas, junction=jun_id7, mdot_kg_per_s=0.008, name="MSink 7")

    g_s_1 = ppipes.create_source(net_gas, junction=jun_id8, mdot_kg_per_s=0.0285, name="BSource 1")
    g_s_2 = ppipes.create_source(net_gas, junction=jun_id9, mdot_kg_per_s=0.0285, name="BSource 2")
    ppipes.create_source(net_gas, junction=jun_id10, mdot_kg_per_s=0.01885, name="BSource 3")
    ppipes.create_ext_grid(net_gas, junction=jun_id_ext, p_bar=REF_BAR, t_k=REF_TEMP, name="Grid Connection Gas")

    # COUPLINGS
    mn = ppm.create_empty_multinet()
    ppm.add_net_to_multinet(mn, net_gas, net_name="gas")
    ppm.add_net_to_multinet(mn, net_power, net_name="power")

    #EXT
    jun_id11 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k = REF_TEMP)
    jun_id12 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k = REF_TEMP)
    jun_id13 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k = REF_TEMP)
    jun_id14 = ppipes.create_junction(net_gas, pn_bar=REF_BAR, tfluid_k = REF_TEMP)
    ppipes.create_pipe_from_parameters(net_gas, from_junction=jun_id3, to_junction=jun_id11, length_km=1.1, diameter_m=0.05, name="Pipe SI 6 SI 2")
    ppipes.create_pipe_from_parameters(net_gas, from_junction=jun_id5, to_junction=jun_id12, length_km=2.1, diameter_m=0.05, name="Pipe SI 6 SI 5")
    ppipes.create_pipe_from_parameters(net_gas, from_junction=jun_id10, to_junction=jun_id13, length_km=1.1, diameter_m=0.05, name="Pipe SI 6 SI 4")
    ppipes.create_pipe_from_parameters(net_gas, from_junction=jun_id4, to_junction=jun_id14, length_km=.5, diameter_m=0.05, name="Pipe SI 5 SI 3")
    g_si_3 = ppipes.create_sink(net_gas, junction=jun_id11, mdot_kg_per_s=0.008, name="MSink 4")
    g_si_4 = ppipes.create_sink(net_gas, junction=jun_id12, mdot_kg_per_s=0.0085, name="SSink 5")
    g_si_5 = ppipes.create_sink(net_gas, junction=jun_id13, mdot_kg_per_s=0.00085, name="SSink 6")
    g_si_6 = ppipes.create_sink(net_gas, junction=jun_id14, mdot_kg_per_s=0.008, name="MSink 7")

    ext_gen = ppower.create_sgen(net_power, 20, p_mw = 0.1, name="Torgenerator2")
    ext_gen2 = ppower.create_sgen(net_power, 13, p_mw = 0.105, name="Torgenerator3")
    ext_gen3 = ppower.create_sgen(net_power, 16, p_mw = 0.1, name="Torgenerator4")
    ext_gen4 = ppower.create_sgen(net_power, 17, p_mw = 0.52, name="Torgenerator5")

    RegulatedG2PControlMultiEnergy(mn, ext_gen, g_si_3, efficiency = 0.88, name="ANp2g1 1 0", element_type_power='sgen')
    RegulatedG2PControlMultiEnergy(mn, ext_gen2, g_si_4, efficiency = 0.90, name="ANp2g2 2 1", element_type_power='sgen')
    RegulatedG2PControlMultiEnergy(mn, ext_gen3, g_si_5, efficiency = 0.85, name="ANp2g1 1 0", element_type_power='sgen')
    RegulatedG2PControlMultiEnergy(mn, ext_gen4, g_si_6, efficiency = 0.91, name="ANp2g2 2 1", element_type_power='sgen')

    # Setup Heat network
    net_heat = None
    if with_heat:
        HEAT_BAR = 5
        HEAT_TEMP = 363.15
        net_heat = ppipes.create_empty_network('heat', fluid="water")
        jun_id_heat = ppipes.create_junction(net_heat, pn_bar=HEAT_BAR, tfluid_k = HEAT_TEMP)
        jun_id2_heat = ppipes.create_junction(net_heat, pn_bar=HEAT_BAR, tfluid_k = HEAT_TEMP)
        jun_id3_heat = ppipes.create_junction(net_heat, pn_bar=HEAT_BAR, tfluid_k = HEAT_TEMP)
        jun_id4_heat = ppipes.create_junction(net_heat, pn_bar=HEAT_BAR, tfluid_k = HEAT_TEMP)
        jun_id5_heat = ppipes.create_junction(net_heat, pn_bar=HEAT_BAR, tfluid_k = HEAT_TEMP)
        jun_id6_heat = ppipes.create_junction(net_heat, pn_bar=HEAT_BAR, tfluid_k = HEAT_TEMP)
        chp_heat_feed_in = ppipes.create_heat_exchanger(net_heat, from_junction=jun_id_heat, to_junction=jun_id2_heat, diameter_m=0.075, qext_w=-0.1)
        ppipes.create_heat_exchanger(net_heat, from_junction=jun_id4_heat, to_junction=jun_id5_heat, diameter_m=0.075, qext_w=0.1)
        ppipes.create_heat_exchanger(net_heat, from_junction=jun_id5_heat, to_junction=jun_id6_heat, diameter_m=0.075, qext_w=0.1)
        ppipes.create_pipe_from_parameters(net_heat, from_junction=jun_id3_heat, to_junction=jun_id4_heat, length_km=0.1,
                                diameter_m=0.075, k_mm=.025, alpha_w_per_m2k=100, sections = 5, text_k=HEAT_TEMP, name="Heat Pipe 1")  
        ppipes.create_pipe_from_parameters(net_heat, from_junction=jun_id2_heat, to_junction=jun_id3_heat, length_km=0.1,
                                diameter_m=0.075, k_mm=.025, alpha_w_per_m2k=100, sections = 5, text_k=HEAT_TEMP, name="Heat Pipe 1")
        ppipes.create_pipe_from_parameters(net_heat, from_junction=jun_id6_heat, to_junction=jun_id_heat, length_km=0.1,
                                diameter_m=0.075, k_mm=.025, alpha_w_per_m2k=100, sections = 5, text_k=HEAT_TEMP, name="Heat Pipe 2")
        ppipes.create_ext_grid(net_heat, junction=jun_id6_heat, p_bar=HEAT_BAR, t_k=HEAT_TEMP, name="Grid Connection Heat")
        ppm.add_net_to_multinet(mn, net_heat, net_name='heat')

    # power loads
    random_load_matr, heat_matr, sink_matr = generate_load_profiles(net_gas, net_power, net_heat, time_steps, with_heat, load_type, load_mul)
    
    # P2G load exception
    random_load_matr[:, 2] = 0.18
    random_load_matr[:, 3] = 0.18
    sink_matr[:, g_si_3] = 0.8
    sink_matr[:, g_si_4] = 0.8
    sink_matr[:, g_si_5] = 0.8
    sink_matr[:, g_si_6] = 0.8

    if with_heat:
        heat_matr[:, chp_heat_feed_in] = -0.5

    df = pd.DataFrame(random_load_matr,
                    index=list(range(time_steps)), columns=net_power.load.index) * net_power.load.p_mw.values
    ds = DFData(df)
    powercontrol.ConstControl(net_power, element='load', element_index=net_power.load.index,
                                    variable='p_mw', data_source=ds, profile_name=net_power.load.index)

    # gas loads
    df = pd.DataFrame(sink_matr,
                    index=list(range(time_steps)), columns=net_gas.sink.index) * net_gas.sink.mdot_kg_per_s.values
    ds = DFData(df)
    powercontrol.ConstControl(net_gas, element='sink', element_index=net_gas.sink.index,
                                    variable='mdot_kg_per_s', data_source=ds, profile_name=net_gas.sink.index)

    if with_heat:
        # gas loads
        df = pd.DataFrame(heat_matr,
                        index=list(range(time_steps)), columns=net_heat.heat_exchanger.index) * net_heat.heat_exchanger.qext_w.values
        ds = DFData(df)
        powercontrol.ConstControl(net_heat, element='heat_exchanger', element_index=net_heat.heat_exchanger.index,
                                        variable='qext_w', data_source=ds, profile_name=net_heat.heat_exchanger.index)
            
        CHPControlMultiEnergy(mn, 0, g_si_1, chp_heat_feed_in, 0.8, 300, "CHP1", ambient_temperature=282.5, element_type_power='sgen')
        CHPControlMultiEnergy(mn, 1, g_si_2, chp_heat_feed_in, 0.8, 300, "CHP1", ambient_temperature=282.5, element_type_power='sgen')
    else:
        RegulatedG2PControlMultiEnergy(mn, 0, g_si_1, efficiency = 0.9, name="ANg2p2 0 0", element_type_power='sgen')
        RegulatedG2PControlMultiEnergy(mn, 1, g_si_2, efficiency = 0.85, name="ANg2p3 1 1", element_type_power='sgen')


    # partially overwrite constcontrol
    RegulatedP2GControlMultiEnergy(mn, 2, g_s_1, efficiency = 0.78, name="ANp2g1 1 0", element_type_power='gen')
    RegulatedP2GControlMultiEnergy(mn, 3, g_s_2, efficiency = 0.94, name="ANp2g2 2 1", element_type_power='gen')

    return mn
