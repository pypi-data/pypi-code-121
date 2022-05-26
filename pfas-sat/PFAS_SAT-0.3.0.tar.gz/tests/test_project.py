# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 21:16:00 2020

@author: msmsa
"""
import PFAS_SAT as ps
import PFAS_SAT_ProcessModels as pspm
import PFAS_SAT_InputData as psid


def check_project(feed, n):
    InventoryObject = pspm.Inventory()

    CommonDataObject = psid.CommonData()

    InputFlow = pspm.IncomFlow()

    InputFlow.set_flow(feed, 1000)

    demo = ps.Project(InventoryObject, CommonDataObject, ProcessModels=None)
    ProcessSet = demo.get_process_set(InputFlow.Inc_flow)
    demo.set_process_set(ProcessSet[0])
    FlowParams = demo.get_flow_params()
    demo.set_flow_params(FlowParams)
    demo.setup_network()
    demo.Inventory.Inv

    demo.setup_MC(InputFlow)
    demo.MC_Next()
    demo.Inventory.Inv

    results = demo.MC_Run(n)

    MC_results = ps.MCResults(results)
    MC_results.to_df()
    MC_results.plot_corr(MC_results.results_df.columns[2])
    MC_results.plot_data(MC_results.results_df.columns[2], MC_results.results_df.columns[8])
    MC_results.plot_dist(param=MC_results.results_df.columns[2])


def test_project_foodwaste():
    check_project('FoodWaste', 20)


def test_project_MSW():
    check_project('MSW', 50)


def test_project_AFFF_Sulfonate():
    check_project('AFFF_Sulfonate', 20)


def test_project_LFLeachate():
    check_project('LFLeachate', 20)


def test_project_WWTEffluent():
    check_project('WWTEffluent', 20)


def test_project_ROConcentrate():
    check_project('ROConcentrate', 20)
