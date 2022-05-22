# -*- coding: utf-8 -*-
from math import*
"""
Created on Mon Aug 31 14:14:16 2020

@author: VG6075
"""
"""
' Validity ranges are the following :
'   - Dry temperature [-20°C to 100°C[
'   - Pressure  [80 000 to 150 000 Pa]
'   - Relative Humidity ]0; 100%] (0% excluded)
   
   
' *******************************************************
' **************** GENERAL FUNCTIONS ********************
' *******************************************************


' FUNCTION Psv - Saturation vapor pressure [Pa] as a function of dry bulb temperature
' Input:    Dry bulb temperature           [°C]
' Output:   Saturation vapor pressure      [Pa]
"""

       


"""
'ASHRAE Fundamentals handbood (2005) p 6.2, equation 5 and 6 - Valid from -100C to 200 C
'Constants
"""
def Psv(Tdb):
    C1 = -5.6745359 * 10 ** (3)
    C2 = 6.3925247
    C3 = -9.677843 * 10 ** (-3)
    C4 = 6.2215701 * 10 ** (-7)
    C5 = 2.0747825 * 10 ** (-9)
    C6 = -9.484024 * 10 ** (-13)
    C7 = 4.1635019 * 10 ** (0)
    C8 = -5.8002206 * 10 ** (3)
    C9 = 1.3914993 * 10 ** (0)
    C10 = -4.8640239 * 10 ** (-2)
    C11 = 4.1764768 * 10 ** (-5)
    C12 = -1.4452093 * 10 ** (-8)
    C13 = 6.5459673 * 10 ** (0)
    
    """Temperature in Kelvin"""
    TK= Tdb + 273.15
    
    """Saturation vapor pressure"""
    if TK <= 273.15:
        Psv = exp(C1 / TK + C2 + C3 * TK + C4 * TK ** 2 + C5 * TK ** 3 + C6 * TK ** 4 + C7 * log(TK))
    else:
        Psv = exp(C8 / TK + C9 + C10 * TK + C11 * TK ** 2 + C12 * TK ** 3 + C13 * log(TK))
    return Psv

"""
FUNCTION H_a - Moist air specific enthalpy [kJ/kg dry air] as a function of dry bulb temperature and humidity ratio
' Input:    Dry bulb temperature           [°C]
'           Humidity ratio                 [kg H2O / kg dry air]
' Output:   Saturation vapor pressure      [Pa]

"""

def H_a(Tdb,w):
    """Calculations from 2005 ASHRAE Handbook - Fundamentals - SI P6.9 eqn 32'"""
    H_a = 1.006 * Tdb + w * (2501 + 1.86 * Tdb)
    return H_a

    
"""
' **********************************************************
' **************** FUNCTIONS Tdb, Twb, P *******************
' **********************************************************


' FUNCTION Air1_RH - Air relative humidity [0 ; 1] as a function of dry bulb temperature, wet bulb temperature and pressure
' Input :    Dry bulb temperature         [°C]
'            Wet bulb temperature         [°C]
'            Pressure                     [Pa]
' Output :   Relative humidity            [0 ; 1]
"""
def Air1_RH(Tdb, Twb , P):
    
    """ Specific humidity [kg H2O/kg dry air]"""
    w = Air1_w(Tdb, Twb, P)
    
    """Relative humidity [0 ; 1]"""
    Air1_RH = P / Psv(Tdb) * w / (0.62198 + w)
    return Air1_RH
"""
_______________________________________________________________________________________________
' FUNCTION Air1_Tdp - Dew point temperature (°C) as a function of dry bulb temperature, wet bulb temperature and pressure
' Input :    Dry bulb temperature   [°C]
'            Wet bulb temperature   [°C]
'            Pressure               [Pa]
' Output :   Dew point temperature  [°C]
"""
def Air1_Tdp(Tdb, Twb, P):
    
    """' Relative humidity"""
    RH = Air1_RH(Tdb, Twb, P)
    """ dew point temperature"""
    Air1_Tdp = Air2_Tdp(Tdb, RH, P)
    
    return Air1_Tdp
"""
_______________________________________________________________________________________________
' FUNCTION Air1_w - Air specific humidity as a function of dry bulb temperature, wet bulb temperature and pressure
' Input :    Dry bulb temperature         [°C]
'            Wet bulb temperature         [°C]
'            Pressure                     [Pa]
' Output :   Specific humidity at Tdb     [kgH2O/kg dry air]
"""
def Air1_w(Tdb, Twb, P):
    """ ASHRAE Fundamentals handbood (2005)

Saturation vapor pressure [Pa] and specific humidity at wet bulb temperature [kgH2O/kg dry air]
    ' Saturation vapor pressure at wet bulb t°"""
    Pws = Psv(Twb)
    """ Specific humidity at wet bulb temperature"""
    Ws = 0.62198 * Pws / (P - Pws) 
    if Tdb >= 0:
        Air1_w = ((2501 - 2.326 * Twb) * Ws - 1.006 * (Tdb - Twb)) / (2501 + 1.86 * Tdb - 4.186 * Twb)
    else :
        Air1_w = ((2830 - 0.24 * Twb) * Ws - 1.006 * (Tdb - Twb)) / (2830 + 1.86 * Tdb - 2.1 * Twb) 
        
    return Air1_w
"""
_______________________________________________________________________________________________
' FUNCTION Air1_xH2O - Water molar fraction as a function of dry bulb temperature, wet bulb temperature and pressure
' Input :    Dry bulb temperature       [°C]
'            Wet bulb temperature       [°C]
'            Pressure                   [Pa]
' Output :   Water molar fraction       [0 ; 1]
"""
def Air1_xH2O(Tdb, RH, P):
    
    """Specific humidity [kgH2O/kg dry air]y"""
    w = Air1_w(Tdb, RH, P)
    """H2O molar fraction"""
    Air1_xH2O = w / (w + 0.62198)
    return Air1_xH2O
"""
_______________________________________________________________________________________________
' FUNCTION Air1_Hs - Specific enthalpy kJ/kg dry air) as a function of dry bulb temperature, wet bulb temperature and pressure
' Input :    Dry bulb temperature   [°C]
'            Wet bulb temperature   [°C]
'            Pressure               [Pa]
' Output :   Specific enthalpy      [kJ/kg dry air]
"""
def Air1_Hs(Tdb , Twb , P ):
    
    """Specific humidity [kgH2O/kg dry air]"""
    w = Air1_w(Tdb, Twb, P)
    
    """Specific enthalpy [kJ/kg dry air]"""
    Air1_Hs = H_a(Tdb, w)
    return Air1_Hs
"""
_______________________________________________________________________________________________
' FUNCTION Air1_Mv - Moist air density (kg/m3) as a function of dry bulb temperature, wet bulb temperature and pressure
' Input :    Dry bulb temperature   [°C]
'            Wet bulb temperature   [°C]
'            Pressure               [Pa]
' Output :   Density                [kg/m3]
"""
def Air1_Mv(Tdb , Twb, P):

    """Standard volumic mass of dry air [kg/Nm3] and relative humidity"""
    Mv0 = 1.2922
    """Relative humidity"""
    RH = Air1_RH(Tdb, Twb, P)
    """Moist air density [kg/m3]"""
    Air1_Mv = Mv0 * 273.15 / (273.15 + Tdb) * (P - (1 - 0.62198) * RH * Psv(Tdb)) / 101325
    return Air1_Mv
"""
______________________________________________________________________________________________
' FUNCTION Air1_Vs - Air specific volume (m3/kg dry air) as a function of dry bulb temperature, wet bulb temperature and pressure
' Input :    Dry bulb temperature   [°C]
'            Wet bulb temperature   [°C]
'            Pressure               [Pa]
' Output :   Air specific volume    [m3/kg dry air]
"""
def Air1_Vs(Tdb, Twb, P):
    
    """Air specific volume [m3/kg dry air]"""
    Air1_Vs = (1 + Air1_w(Tdb, Twb, P)) / Air1_Mv(Tdb, Twb, P)
    
    return Air1_Vs
"""
______________________________________________________________________________________________
' **********************************************************
' **************** FUNCTIONS Tdb, RH, P ********************
' **********************************************************

' FUNCTION Air2_w - Specific humidity (humidity ratio) as a function of dry bulb temperature, relative humidity and pressure
' Input :    Dry bulb temperature       [°C]
'            Relative humidity          [ 0 ; 1]
'            Pressure                   [Pa]
' Output :   Specific humidity          [kgH2O/kg dry air]
"""

def Air2_w(Tdb,RH, P):
    
    """Vapor partial pressure"""
    Pv = RH * Psv(Tdb)
    """Specific humidity - Humidity ratio [kgH2O/kg dry air]"""
    Air2_w = 0.62198 * Pv / (P - Pv)

    return Air2_w

"""
______________________________________________________________________________________________
' FUNCTION Air2_xH2O - Water molar fraction as a function of dry bulb temperature, relative humidity and pressure
' Input :    Dry bulb temperature       [°C]
'            Relative humidity          [ 0 ; 1]
'            Pressure                   [Pa]
' Output :   Water molar fraction       [0 ; 1]
"""
def Air2_xH2O(Tdb, RH , P):
    
    """Specific humidity [kgH2O/kg dry air]"""
    w = Air2_w(Tdb, RH, P)
    """H2O molar fraction"""
    Air2_xH2O = w / (w + 0.62198)
    return Air2_xH2O
"""
______________________________________________________________________________________________
' FUNCTION Air2_Twb - Wet bulb temperature (°C) as a function of dry bulb temperature, relative humidity and pressure
' Input :    Dry bulb temperature   [°C]
'            Relative humidity      [ 0 ; 1]
'            Pressure               [Pa]
' Output :   Wet bulb temperature   [°C]
"""
def Air2_Twb(Tdb, RH, P):
   
    """ Uses Newton-Rhapson iteration for quick convergence"""
    """ Vapor pressure[Pa]"""

    """ Vapor pressure in moist air [Pa]"""
    Pv = RH * Psv(Tdb)
    """Humidity ratio [kgH2O/kg dry air]"""
    Wa = 0.62198 * Pv / (P - Pv)
    """CALCULATION"""
    Twb = Tdb
    """Solve to within 0.001% accuracy using Newton-Rhapson"""
    Ws = Air1_w(Tdb, Twb, P)
    while True:
            Ws2 = Air1_w(Tdb, Twb - 0.001, P)
            dw_dt = (Ws - Ws2) / 0.001
            Twb = Twb - (Ws - Wa) / dw_dt
            Ws = Air1_w(Tdb, Twb, P)
            if abs((Ws - Wa) / Wa) <= 0.00001:
                break
    """Wet bulb temperature"""
    Air2_Twb = Twb
    return Air2_Twb
"""
_____________________________________________________________________________________________
' FUNCTION Air2_Tdp - dew point temperature (°C) as a function of dry bulb temperature, relative humidity and pressure
' Input :    Dry bulb temperature   [°C]
'            Relative humidity      [ 0 ; 1]
'            Pressure               [Pa]
' Output :   dew point temperature  [°C]
"""
def Air2_Tdp(Tdb, RH, P):
    """Uses Newton-Rhapson iteration for quick convergence
    ' Vapor pressure[Pa]
        Dim Pv As Double
    ' Specific humidity at Tdb and at dew point Tdp - [kgH2O/kg dry air]
        Dim Wa As Double, Ws As Double, Ws2 As Double
    ' Intermediate
        Dim dw_dt As Double
    ' dew point temperature [°C]
        Dim Tdp As Double
    
    ' Vapor pressure in moist air [Pa]
    """
    Pv = RH * Psv(Tdb)
    """Humidity ratio [kgH2O/kg dry air]"""
    Wa = 0.62198 * Pv / (P - Pv)
    """CALCULATION"""
    Tdp = Tdb
    """Solve to within 0.001% accuracy using Newton-Rhapson"""
    Ws = Air2_w(Tdp, 1, P)
    while True:
            Ws2 = Air2_w(Tdp - 0.001, 1, P)
            dw_dt = (Ws - Ws2) / 0.001
            Tdp = Tdp - (Ws - Wa) / dw_dt
            Ws = Air2_w(Tdp, 1, P)
            if abs((Ws - Wa) / Wa) <= 0.00001:
                break
    """Wet bulb temperature"""
    Air2_Tdp = Tdp
    return Air2_Tdp
"""
_____________________________________________________________________________________________
' FUNCTION Air2_Hs - Specific enthalpy kJ/kg dry air) as a function of dry bulb temperature, relative humidity and pressure
' Input :    Dry bulb temperature   [°C]
'            Relative humidity      [ 0 ; 1]
'            Pressure               [Pa]
' Output :   Specific enthalpy      [kJ/kg dry air]
"""
def Air2_Hs(Tdb, RH, P):
    """
    Specific humidity [kgH2O/kg dry air]
        Dim w As Double
    
    Specific humidity [kgH2O/kg dry air]
    """
    w = Air2_w(Tdb, RH, P)

    """Specific enthalpy [kJ/kg dry air]"""
    Air2_Hs = H_a(Tdb, w)
    return Air2_Hs 
"""
_____________________________________________________________________________________________
' FUNCTION Air2_Mv - Moist air density (kg/m3) as a function of dry bulb temperature, relative humidity and pressure
' Input :    Dry bulb temperature   [°C]
'            Relative humidity      [ 0 ; 1]
'            Pressure               [Pa]
' Output :   Density                [kg/m3]
"""
def Air2_Mv(Tdb, RH,  P):
    """Standard volumic mass of dry air [kg/Nm3]
    Dim Mv0 As Double

    ' Standard volumic mass of dry air [kg/Nm3]"""
    Mv0 = 1.2922
    """Moist air density [kg/m3]"""
    Air2_Mv = Mv0 * 273.15 / (273.15 + Tdb) * (P - (1 - 0.62198) * RH * Psv(Tdb)) / 101325
    return Air2_Mv 
"""
___________________________________________________________________________________________
' FUNCTION Air2_Vs - Air specific volume (m3/kg dry air) as a function of dry bulb temperature, relative humidity and pressure
' Input :    Dry bulb temperature   [°C]
'            Relative humidity      [ 0 ; 1]
'            Pressure               [Pa]
' Output :   Air specific volume    [m3/kg dry air]
"""
def Air2_Vs(Tdb , RH , P ):
    
    """Air specific volume [m3/kg dry air]"""
    Air2_Vs = (1 + Air2_w(Tdb, RH, P)) / Air2_Mv(Tdb, RH, P)
    return Air2_Vs
"""
_____________________________________________________________________________________________
' **********************************************************
' **************** FUNCTIONS w, P, Hs **********************
' **********************************************************

' FUNCTION Air3_Tdb - Air dry bulb temperature (°C) as a function of specific humidity, pressure and specific enthalpy
' Input :    Specific humidity            [kgH2O/kg dry air]
'            Pressure                     [Pa]
'            Specific enthalpy            [kJ/kg dry air]
' Output :   Dry bulb temperature         [°C]
"""
def Air3_Tdb(w, P , H): 
    
    """Dry bulb temperature [°C]"""
    Air3_Tdb = (H - w * 2501) / (1.006 + w * 1.86)
    return Air3_Tdb
"""
_____________________________________________________________________________________________
' FUNCTION Air3_RH - Air relative humidity [0 ; 1] as a function of specific humidity, pressure and specific enthalpy
' Input :    Specific humidity            [kgH2O/kg dry air]
'            Pressure                     [Pa]
'            Specific enthalpy            [kJ/kg dry air]
' Output :   Relative humidity            [0 ; 1]
"""
def Air3_RH(w , P , H ):

    """ Dry bulb temperature
    Dim Tdb As Double

    ' Dry bulb temperature [°C]"""
    Tdb = Air3_Tdb(w, P, H)
    """' Relative humidity [0 ; 1]"""
    Air3_RH = P / Psv(Tdb) * w / (0.62198 + w)
    return Air3_RH
"""
_____________________________________________________________________________________________
' FUNCTION Air3_Twb - Wet bulb temperature (°C) as a function of specific humidity, pressure and specific enthalpy
' Input :    Specific humidity            [kgH2O/kg dry air]
'            Pressure                     [Pa]
'            Specific enthalpy            [kJ/kg dry air]
' Output :   Wet bulb temperature         [°C]
"""
def Air3_Twb(w , P , H ):
    """' Dry bulb temperature [°C]
        Dim Tdb As Double
    ' Relative humidity
        Dim RH As Double
    
    ' Dry bulb temperature [°C]"""
    Tdb = Air3_Tdb(w, P, H)
    """"' Relative humidity [0 ; 1]"""
    RH = P / Psv(Tdb) * w / (0.62198 + w)
    """' Wet bulb temperature [°C]"""
    Air3_Twb = Air2_Twb(Tdb, RH, P)
    return Air3_Twb
"""
_____________________________________________________________________________________________
' FUNCTION Air3_Tdp - Dew point temperature (°C) as a function of specific humidity, pressure and specific enthalpy
' Input :    Specific humidity            [kgH2O/kg dry air]
'            Pressure                     [Pa]
'            Specific enthalpy            [kJ/kg dry air]
' Output :   dew point temperature        [°C]
"""
def Air3_Tdp(w , P , H ):

    """' 
    Dry bulb temperature [°C]
        Dim Tdb As Double
    ' Relative humidity
        Dim RH As Double
    
    ' Dry bulb temperature [°C]"""
    Tdb = Air3_Tdb(w, P, H)
    """' Relative humidity [0 ; 1]"""
    RH = P / Psv(Tdb) * w / (0.62198 + w)
    """"' Dew point temperature"""
    Air3_Tdp = Air2_Tdp(Tdb, RH, P)
    return Air3_Tdp
"""
_____________________________________________________________________________________________

' FUNCTION Air3_xH2O - Water molar fraction as a function of specific humidity, pressure and specific enthalpy
' Input :    Specific humidity            [kgH2O/kg dry air]
'            Pressure                     [Pa]
'            Specific enthalpy            [kJ/kg dry air]
' Output :   Water molar fraction         [0 ; 1]
"""
def Air3_xH2O(w , P , H ):

    """' H2O molar fraction"""
    Air3_xH2O = w / (w + 0.62198)
    return Air3_xH2O
"""
' FUNCTION Air3_Mv - Moist air density (kg/m3) as a function of specific humidity, pressure and specific enthalpy
' Input :    Specific humidity            [kgH2O/kg dry air]
'            Pressure                     [Pa]
'            Specific enthalpy            [kJ/kg dry air]
' Output :   Density                      [kg/m3]
"""
def Air3_Mv(w , P ,H ):
    """' Standard volumic mass of dry air [kg/Nm3]
        Dim Mv0 As Double
    ' Dry bulb temperature [°C]
        Dim Tdb As Double
    ' Relative humidity
        Dim RH As Double
    
    ' Dry bulb temperature [°C]"""
    Tdb = Air3_Tdb(w, P, H)
    """' Relative humidity [0 ; 1]"""
    RH = P / Psv(Tdb) * w / (0.62198 + w)
    """' Standard volumic mass of dry air [kg/Nm3]"""
    Mv0 = 1.2922
    """' Moist air density [kg/m3]"""
    Air3_Mv = Mv0 * 273.15 / (273.15 + Tdb) * (P - (1 - 0.62198) * RH * Psv(Tdb)) / 101325
    return Air3_Mv

"""
_____________________________________________________________________________________________
' FUNCTION Air3_Vs - Air specific volume (m3/kg dry air) as a function of specific humidity, pressure and specific enthalpy
' Input :    Specific humidity            [kgH2O/kg dry air]
'            Pressure                     [Pa]
'            Specific enthalpy            [kJ/kg dry air]
' Output :   Air specific volume          [m3/kg dry air]
"""
def Air3_Vs(w , P , H ):

    """'Air specific volume [m3/kg dry air]"""
    Air3_Vs = (1 + w) / Air3_Mv(w, P, H)
    return Air3_Vs

"""
_____________________________________________________________________________________________

' **********************************************************
' **************** FUNCTIONS Tdb, P, w *********************
' **********************************************************

"""
"""_____________________________________________________________________________________________
' FUNCTION Air4_Hs - Specific enthalpy [kJ/kg dry air] as a finction of dry bulb temperature, pressure and specific humidity
' Input :    Dry bulb temperature          [°C]
'            Pressure                      [Pa]
'            Specific humidity             [kgH2O/kg dry air]
' Output :   Specific enthalpy             [kJ/kg dry air]
"""
def Air4_Hs(Tdb , P , w ) :

    """'Specific enthalpy [kJ/kg dry air]"""
    Air4_Hs = H_a(Tdb, w)
    return Air4_Hs

"""
_____________________________________________________________________________________________
' FUNCTION Air4_RH - Air relative humidity s a function of dry bulb temperature, pressure and specific humidity
' Input :    Dry bulb temperature          [°C]
'            Pressure                      [Pa]
'            Specific humidity             [kgH2O/kg dry air]
' Output :   Relative humidity             [0 ; 1]
"""
def Air4_RH(Tdb , P , w ):

    """' Relative humidity [0 ; 1]"""
    Air4_RH = P / Psv(Tdb) * w / (0.62198 + w)
    return Air4_RH
"""
_____________________________________________________________________________________________
' FUNCTION Air4_Twb - Wet bulb temperature (°C) as a function of dry bulb temperature, pressure and specific humidity
' Input :    Dry bulb temperature          [°C]
'            Pressure                      [Pa]
'            Specific humidity             [kgH2O/kg dry air]
' Output :   Wet bulb temperature         [°C]
"""

def Air4_Twb(Tdb , P , w ): 

    """' Relative humidity
    Dim RH As Double

    ' Relative humidity [0 ; 1]"""
    RH = P / Psv(Tdb) * w / (0.62198 + w)
    """' Wet bulb temperature [°C]"""
    Air4_Twb = Air2_Twb(Tdb, RH, P)
    return Air4_Twb

"""
_____________________________________________________________________________________________
' FUNCTION Air4_Tdp - dew point temperature (°C) as a function of dry bulb temperature, pressure and specific humidity
' Input :    Dry bulb temperature          [°C]
'            Pressure                      [Pa]
'            Specific humidity             [kgH2O/kg dry air]
' Output :   dew point temperature         [°C]
"""
def Air4_Tdp(Tdb , P , w ):

    """' Relative humidity
        Dim RH As Double
    
    ' Relative humidity [0 ; 1]"""
    RH = P / Psv(Tdb) * w / (0.62198 + w)
    """' Dew point temperature"""
    Air4_Tdp = Air2_Tdp(Tdb, RH, P)
    return Air4_Tdp 
"""
_____________________________________________________________________________________________
' FUNCTION Air4_xH2O - Water molar fraction as a function of dry bulb temperature, pressure and specific humidity
' Input :    Dry bulb temperature          [°C]
'            Pressure                      [Pa]
'            Specific humidity             [kgH2O/kg dry air]
' Output :   Water molar fraction          [0 ; 1]
"""
def Air4_xH2O(Tdb, P , w ):
    """' H2O molar fraction"""
    Air4_xH2O = w / (w + 0.62198)
    return Air4_xH2O
"""
___________________________________________________________________________________________

' FUNCTION Air4_Mv - Moist air density (kg/m3) as a function of dry bulb temperature, pressure and specific humidity
' Input :    Dry bulb temperature          [°C]
'            Pressure                      [Pa]
'            Specific humidity             [kgH2O/kg dry air]
' Output :   Density                       [kg/m3]
"""
def Air4_Mv(Tdb , P , w ):

    """' Standard volumic mass of dry air [kg/Nm3]
        Dim Mv0 As Double
    ' Relative humidity
        Dim RH As Double
    
    ' Relative humidity [0 ; 1]"""
    RH = P / Psv(Tdb) * w / (0.62198 + w)
    """' Standard volumic mass of dry air [kg/Nm3]"""
    Mv0 = 1.2922
    """' Moist air density [kg/m3]"""
    Air4_Mv = Mv0 * 273.15 / (273.15 + Tdb) * (P - (1 - 0.62198) * RH * Psv(Tdb)) / 101325
    return Air4_Mv
"""
_____________________________________________________________________________________________
' FUNCTION Air4_Vs - Air specific volume (m3/kg dry air) as a function of dry bulb temperature, pressure and specific humidity
' Input :    Dry bulb temperature          [°C]
'            Pressure                      [Pa]
'            Specific humidity             [kgH2O/kg dry air]
' Output :   Air specific volume           [m3/kg dry air]
"""
def Air4_Vs(Tdb , P , w) : 

    """ Air specific volume [m3/kg dry air]"""
    Air4_Vs = (1 + w) / Air4_Mv(Tdb, P, w)
    return Air4_Vs

"""
_____________________________________________________________________________________________
' FUNCTION Air5_Tdb - Dry bulb temperature as a function of relative humidity, pressure and specific enthalpy
' Input :    Relative humidity            [%]
'            Pressure                     [Pa]
'            Specific enthalpy            [kJ/kg dry air]
' Output :   Dry bulb temperature         [°c]
"""
def Air5_Tdb(RH , P , H ):
    """
    ' Uses Newton-Rhapson iteration for quick convergence
    
    ' Specific humidity - [kgH2O/kg dry air]
        Dim Ws As Double, Ws2 As Double
    ' Intermediate
        Dim dH_dt As Double, Hs As Double, Hs2 As Double
    ' Dry bulb temperature [°C]
        Dim Tdb As Double
    
    ' CALCULATION
    ' Dry bulb temperature [°C] - start"""
    Tdb = 10
    """' Humidity ratio [kgH2O/kg dry air]"""
    Ws = Air2_w(Tdb, RH, P)
    """' Enthalpy"""
    Hs = H_a(Tdb, Ws)
    """' Solve to within 0.001 accuracy using Newton-Rhapson"""
    while True:
            Ws2 = Air2_w(Tdb - 0.001, RH, P)
            Hs2 = H_a(Tdb - 0.001, Ws2)
            dH_dt = (Hs - Hs2) / 0.001
            Tdb = Tdb - (Hs - H) / dH_dt
            Ws = Air2_w(Tdb, RH, P)
            Hs = H_a(Tdb, Ws)
            if abs(H - Hs) <= 0.0001:
                break

    """' Dry bulb temperature [°C]"""
    Air5_Tdb = Tdb
    return Air5_Tdb

"""
_____________________________________________________________________________________________
' FUNCTION Air6_Tdb - Dry bulb temperature as a function of relative humidity, pressure and wet bulb temperature
' Input :    Relative humidity            [%]
'            Pressure                     [Pa]
'            Wet bulb temperature         [°C]
' Output :   Dry bulb temperature         [°c]
"""
def Air6_Tdb(RH , P , Twb ):

    """' Uses Newton-Rhapson iteration for quick convergence
    
    ' Specific humidity - [kgH2O/kg dry air]
        Dim Ws As Double, Ws2 As Double
    ' Intermediate
        Dim dTw_dt As Double, Twbs As Double, Twbs2 As Double
        Dim n As Integer
    ' Dry bulb temperature [°C]
        Dim Tdb As Double
    
    ' CALCULATION
    ' Dry bulb temperature [°C] - start"""
    Tdb = Twb
    """' Wet bulb temperature"""
    Twbs = Air2_Twb(Tdb, RH, P)
    n = 0
    """' Solve to within 0.001 accuracy using Newton-Rhapson"""
    while True:
            Twbs2 = Air2_Twb(Tdb - 0.001, RH, P)
            dTw_dt = (Twbs - Twbs2) / 0.001
            Tdb = Tdb - (Twbs - Twb) / dTw_dt
            Twbs = Air2_Twb(Tdb, RH, P)
            n = n + 1
            if abs(Twb - Twbs) <= 0.00001:
                break
            
    """' Dry bulb temperature [°C]"""
    Air6_Tdb = Tdb
    return Air6_Tdb


# """
# ______________________________________________________________________
# Tracer graphique
# """
# import numpy as np
# from matplotlib.patches import Rectangle
# import matplotlib.pyplot as plt
# import matplotlib.colors as mcolors
# P= 101325
# HR_1=[0.02,0.04,0.06,0.08,0.1,0.15,0.2,0.25,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1]
# T_1=[-20,-15,-10,-5,0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80]



# row=len(HR_1)
# lines=len(T_1)
# R_H=np.ones((lines,row*3))

# """Définition du tableau Humidité_relative__________________________________"""
# j=0
# for i in range(lines):
#     for k in range(row):
#         j=(k)*3
#         R_H[i][j]=Air2_w(T_1[i],HR_1[k],P)*1000
#         R_H[i][j+1]=Air2_Hs(T_1[i],HR_1[k],P)
#         R_H[i][j+2]=Air2_Vs(T_1[i],HR_1[k],P)

# """
# Définition tableau température bulbe humide________________________________________________"""
    
# T1=[-19,-15,-10,-5,0,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]
# T2=[25,26,27,28,29,30,31,32,33,34,35,36]
# HR_2=[0.00001,0.3,1]
# HR_3=[0.05,0.3,1]            
# row1=len(T1)
# row2=len(T2)  
# line1=len(HR_2)
# line2=len(HR_3)
# Twb_HR=np.zeros((line1,(row1+row2)*2))     
# cpt=0
# k=0  
        
# """Première partie du tableau"""
# for i in range(line1):
#     for k in range(row1):
#             j=k*2
#             Twb_HR[i,j]=Air6_Tdb(HR_2[i],P,T1[k])
#             Twb_HR[i,j+1]=1000*Air2_w(Twb_HR[i,j],HR_2[i],P)

# """Seconde partie du tableau"""            
# for i in range(line1): 
#     for k in range(row1,row1+row2):
#             j=k*2
#             Twb_HR[i,j]=Air6_Tdb(HR_3[i],P,T2[k-25])
#             Twb_HR[i,j+1]=1000*Air2_w(Twb_HR[i,j],HR_3[i],P)
                        
# """Définition tableau température bulbe sèche________________________________________________"""
# H=[-15,-10,-5,0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135]
# HR_4=[0.00001,1]
# HR_5=[0.00001,0.2,0.5,1]        
# HR_6=[0.00001,1]  
# HR_7=[0.00001,0.93]
# HR_8=[0.00001,0.72] 
# HR_9=[0.00001,0.56]
# HR_10=[0.00001,0.44]
# HR_11=[0.00001,0.35]
# HR_12=[0.00001,0.28]       


# TdB_HR=np.zeros((len(HR_5),len(H)*2))

# for i in range(len(HR_4)):
#     for k in range(H.index(40)+1):
#             j=k*2
#             TdB_HR[i,j]=Air5_Tdb(HR_4[i],P,H[k])
#             TdB_HR[i,j+1]=1000*Air2_w(TdB_HR[i,j],HR_4[i],P)
     
# for i in range(len(HR_5)):
#     for k in range(H.index(45),H.index(95)+1):
#             j=k*2
#             TdB_HR[i,j]=Air5_Tdb(HR_5[i],P,H[k])
#             TdB_HR[i,j+1]=1000*Air2_w(TdB_HR[i,j],HR_5[i],P)

# for i in range(len(HR_6)):
#     for k in range(H.index(100),H.index(105)+1):
#             j=k*2
#             TdB_HR[i,j]=Air5_Tdb(HR_6[i],P,H[k])
#             TdB_HR[i,j+1]=1000*Air2_w(TdB_HR[i,j],HR_6[i],P)

# for i in range(len(HR_7)):
#     for k in range(H.index(110),H.index(110)+1):
#             j=k*2
#             TdB_HR[i,j]=Air5_Tdb(HR_7[i],P,H[k])
#             TdB_HR[i,j+1]=1000*Air2_w(TdB_HR[i,j],HR_7[i],P)

# for i in range(len(HR_8)):
#     for k in range(H.index(115),H.index(115)+1):
#             j=k*2
#             TdB_HR[i,j]=Air5_Tdb(HR_8[i],P,H[k])
#             TdB_HR[i,j+1]=1000*Air2_w(TdB_HR[i,j],HR_8[i],P)

# for i in range(len(HR_9)):
#     for k in range(H.index(120),H.index(120)+1):
#             j=k*2
#             TdB_HR[i,j]=Air5_Tdb(HR_9[i],P,H[k])
#             TdB_HR[i,j+1]=1000*Air2_w(TdB_HR[i,j],HR_9[i],P)            
            
# for i in range(len(HR_10)):
#     for k in range(H.index(125),H.index(125)+1):
#             j=k*2
#             TdB_HR[i,j]=Air5_Tdb(HR_9[i],P,H[k])
#             TdB_HR[i,j+1]=1000*Air2_w(TdB_HR[i,j],HR_9[i],P)            
                        
# for i in range(len(HR_11)):
#     for k in range(H.index(130),H.index(130)+1):
#             j=k*2
#             TdB_HR[i,j]=Air5_Tdb(HR_9[i],P,H[k])
#             TdB_HR[i,j+1]=1000*Air2_w(TdB_HR[i,j],HR_9[i],P)            
                        
# for i in range(len(HR_12)):
#     for k in range(H.index(135),H.index(135)+1):
#             j=k*2
#             TdB_HR[i,j]=Air5_Tdb(HR_9[i],P,H[k])
#             TdB_HR[i,j+1]=1000*Air2_w(TdB_HR[i,j],HR_9[i],P)               

# """Définition tableau température bulbe humide________________________________________________"""
# from pylab import *
# """Taille du graphique"""
# figure(figsize=(15,10),dpi=200)   

# ylabel('Humidity Ratio - grams moisture /kg of dry air',fontsize=20)
# xlabel('Dry Bulb Temperature - °C',fontsize=20)


# """Limites axes x et y___________________________________________________________________"""
# xlim(-20,60)
# ylim(0,30)

# """Graduation axes x et y_____________________________________________________________"""
# xticks(linspace(-20,60,17,endpoint=True),fontsize=18)

# yticks(np.linspace(0,30,7,endpoint=True),fontsize=18)

# grid() 

# """Courbes HR en Noir pointillés__________________________________________________________________________"""
# for i in range(0,(HR_1.index(0.1))*3,3):
#     plot(T_1[T_1.index(35):],R_H[T_1.index(35):,i],'k--')
#     k=int(i/3)
#     if i==0:
#         text(T_1[T_1.index(45)]+3,R_H[T_1.index(50),i]-1,'Relative humidity ='+str(int(HR_1[k]*100))+' %',fontsize=8,rotation=5,fontweight='light')
#     else:
#         text(T_1[T_1.index(55)],R_H[T_1.index(55),i]-1,str(int(HR_1[k]*100))+' %',fontsize=8,rotation=30,fontweight='light')
         
# for i in range((HR_1.index(0.1))*3,(HR_1.index(0.4))*3,6):
#     plot(T_1[T_1.index(0):],R_H[T_1.index(0):,i],'k--')

# text(25,R_H[T_1.index(25),HR_1.index(0.1)*3]-0.5,'10 %',fontsize=8,rotation=20,fontweight='light')
# text(25,R_H[T_1.index(25),HR_1.index(0.2)*3]-0.5,'20 %',fontsize=8,rotation=20,fontweight='light')
# text(25,R_H[T_1.index(25),HR_1.index(0.3)*3]-0.5,'30 %',fontsize=8,rotation=30,fontweight='light')


    
# for i in range((HR_1.index(0.6))*3,(HR_1.index(0.9)+1)*3,3):
#     plot(T_1[T_1.index(0):],R_H[T_1.index(0):,i],'k--')
#     k=int(i/3)
#     text(T_1[T_1.index(25)],R_H[T_1.index(25),i]-0.5,str(int(HR_1[k]*100))+' %',fontsize=8,rotation=65,fontweight='light')
    
# for i in range((HR_1.index(0.15))*3,(HR_1.index(0.25)+1)*3,6):
#     plot(T_1[T_1.index(20):],R_H[T_1.index(20):,i],'k--')
    
# plot(T_1[T_1.index(0):],R_H[T_1.index(0):,HR_1.index(0.4)*3],'k--')
# text(25,R_H[T_1.index(25),HR_1.index(0.4)*3]-0.5,'40 %',fontsize=11,rotation=35,fontweight='light') 

# plot(T_1[T_1.index(-20):],R_H[T_1.index(-20):,HR_1.index(0.5)*3],'k--')   
# text(25,R_H[T_1.index(25),HR_1.index(0.5)*3]-0.5,'50 %',fontsize=11,rotation=40,fontweight='light') 

# plot(T_1[T_1.index(-20):],R_H[T_1.index(-20):,HR_1.index(1)*3],'k--')
# text(25,R_H[T_1.index(25),HR_1.index(1)*3]-0.5,'100 %',fontsize=8,rotation=65,fontweight='light') 
      
# """Courbes bulbe humide en ROUGE__________________________________________________________________________"""

# for i in range(0,len(T1)*2,2):
#     plot(Twb_HR[:,i],Twb_HR[:,i+1],'r-')    
   
# # for i in range(0,T1.index(5)+1):
# #     k=i*2
# #     text(Twb_HR[2,k],Twb_HR[2,k+1],str(int(T1[i]))+' °C',fontsize=8,rotation=-40,fontweight='bold')


# for i in range(0,len(T2)*2,2):
#     plot(Twb_HR[:,i+len(T1)*2],Twb_HR[:,i+len(T1)*2+1],'r--')    
    
# """Courbes enthalpie en VERT__________________________________________________________________________"""    
    
# for i in range(0,(H.index(40)+1)*2,2):
#     plot(TdB_HR[0:2,i],TdB_HR[0:2,i+1],'g--') 

# for i in range(0,(H.index(40)+1)):
#     k=i*2
#     text(TdB_HR[1,k],TdB_HR[1,k+1],str(int(H[i]))+' kJ/kgda ',horizontalalignment = 'right',color = 'green',fontsize=5,rotation=-20,fontweight='light')
    
# for i in range(H.index(45)*2,(H.index(95)+1)*2,2):
#     plot(TdB_HR[0:4,i],TdB_HR[0:4,i+1],'g--')

# for i in range(H.index(45),(H.index(95)+1)):
#     k=i*2
#     text(TdB_HR[3,k],TdB_HR[3,k+1],str(int(H[i]))+' kJ/kgda ',horizontalalignment = 'right',color = 'green',fontsize=5,rotation=-20,fontweight='light')
    
# for i in range(H.index(100)*2,(H.index(135)+1)*2,2):
#     plot(TdB_HR[0:2,i],TdB_HR[0:2,i+1],'g--')

# for i in range(H.index(100),(H.index(110))):
#     k=i*2
#     text(TdB_HR[1,k],TdB_HR[1,k+1],str(int(H[i]))+' kJ/kgda ',horizontalalignment = 'right',color = 'green',fontsize=5,rotation=-20,fontweight='light')
        

# for i in range(H.index(110),(H.index(120))):
#     k=i*2
#     text(TdB_HR[1,k]+2,TdB_HR[1,k+1]-1,str(int(H[i]))+' kJ/kgda ',horizontalalignment = 'left',color = 'green',fontsize=5,rotation=-35,fontweight='light')
        
# for i in range(H.index(110),(H.index(120))):
#     k=i*2
#     text(TdB_HR[1,k]+2,TdB_HR[1,k+1]-1,str(int(H[i]))+' kJ/kgda ',horizontalalignment = 'left',color = 'green',fontsize=5,rotation=-35,fontweight='light')

# j=0    
# for i in range(H.index(120),(H.index(135)+1)):
#     k=i*2
#     l=j*5
#     text(46+l,29,str(int(H[i]))+' kJ/kgda ',horizontalalignment = 'right',color = 'green',fontsize=5,rotation=-35,fontweight='light')
#     j=j+1
    