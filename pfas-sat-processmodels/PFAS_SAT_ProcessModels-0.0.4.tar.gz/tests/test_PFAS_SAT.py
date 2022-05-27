# -*- coding: utf-8 -*-
"""
Created on Fri May  8 00:12:49 2020

@author: msmsa
"""
import PFAS_SAT_ProcessModels as pspm
from PFAS_SAT_ProcessModels import ProcessModelsMetaData


def check_processmodel(process_model_cls, feed):
    Input = pspm.IncomFlow()
    if feed in Input.WasteMaterials:
        Input.set_flow(feed, 1000)
        Input.calc()
        model = process_model_cls()
        model.calc(Input.Inc_flow)
        A = model.report()
        if abs(A.sum().sum() - sum(Input.Inc_flow.PFAS)) > 0.01 * sum(Input.Inc_flow.PFAS):
            raise Exception(f'Error in PFAS mass Balance. Process: {model.Name}, Feed: {feed}')
        if A.min().min() < 0:
            raise Exception(f'Negative PFAS flow in the report. Process = {model.Name}')
        model.report(normalized=True)
        model.setup_MC()
        model.MC_Next()
        model.calc(Input.Inc_flow)
        model.MC_Next()
        model.MC_Next()
        model.MC_Next()
        model.MC_Next()
        model.report()


def test_LandApp():
    for flow in ProcessModelsMetaData['LandApp']['InputType']:
        check_processmodel(pspm.LandApp, flow)


def test_Comp():
    for flow in ProcessModelsMetaData['Comp']['InputType']:
        check_processmodel(pspm.Comp, flow)


def test_Landfill():
    for flow in ProcessModelsMetaData['Landfill']['InputType']:
        check_processmodel(pspm.Landfill, flow)


def test_WWT():
    for flow in ProcessModelsMetaData['WWT']['InputType']:
        check_processmodel(pspm.WWT, flow)


def test_Stab():
    for flow in ProcessModelsMetaData['Stab']['InputType']:
        check_processmodel(pspm.Stab, flow)


def test_AdvWWT():
    for flow in ProcessModelsMetaData['AdvWWT']['InputType']:
        check_processmodel(pspm.AdvWWT, flow)


def test_SCWO():
    for flow in ProcessModelsMetaData['SCWO']['InputType']:
        check_processmodel(pspm.SCWO, flow)


def test_ThermalTreatment():
    for flow in ProcessModelsMetaData['ThermalTreatment']['InputType']:
        check_processmodel(pspm.ThermalTreatment, flow)


def test_AD():
    for flow in ProcessModelsMetaData['AD']['InputType']:
        check_processmodel(pspm.AD, flow)


def test_SurfaceWaterRelease():
    for flow in ProcessModelsMetaData['SurfaceWaterRelease']['InputType']:
        check_processmodel(pspm.SurfaceWaterRelease, flow)


def test_ThermalReactivation():
    for flow in ProcessModelsMetaData['ThermalReactivation']['InputType']:
        check_processmodel(pspm.ThermalReactivation, flow)


def test_DeepWellInjection():
    for flow in ProcessModelsMetaData['DeepWellInjection']['InputType']:
        check_processmodel(pspm.DeepWellInjection, flow)
