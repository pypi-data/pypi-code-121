# -*- coding: utf-8 -*-
"""
Created on Fri May  8 00:12:49 2020

@author: msmsa
"""
import PFAS_SAT_InputData as psid


def check_inputdata(input_data_cls):
    model = input_data_cls()
    model.setup_MC()
    model.gen_MC()


def test_IncomFlowInput():
    check_inputdata(psid.IncomFlowInput)


def test_LandApp():
    check_inputdata(psid.LandAppInput)


def test_Comp():
    check_inputdata(psid.CompInput)


def test_Landfill():
    check_inputdata(psid.LandfillInput)


def test_WWT():
    check_inputdata(psid.WWTInput)


def test_Stab():
    check_inputdata(psid.StabInput)


def test_AdvWWT():
    check_inputdata(psid.AdvWWTInput)


def test_SCWO():
    check_inputdata(psid.SCWOInput)


def test_ThermalTreatment():
    check_inputdata(psid.ThermalTreatmentInput)


def test_AD():
    check_inputdata(psid.ADInput)


def test_SurfaceWaterRelease():
    check_inputdata(psid.SurfaceWaterReleaseInput)


def test_ThermalReactivation():
    check_inputdata(psid.ThermalReactivationInput)


def test_DeepWellInjection():
    check_inputdata(psid.DeepWellInjectionInput)
