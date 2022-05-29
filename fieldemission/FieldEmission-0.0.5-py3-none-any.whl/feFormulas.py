from logging import exception
import random
from FieldEmission.dataManager import DataProvider as dPrvdr
import numpy as np
import math
import scipy.constants as sciConst


def FowlerNordheim(DatMgr: dPrvdr, ColumnU, ColumnI, distance_m):
    # Create copys of U and I (also for predefining correct array-size)
    fnX = abs(DatMgr.GetColumn(ColumnU))  # Here still U!
    fnY = abs(DatMgr.GetColumn(ColumnI))  # Here still I!

    for iRow in range(len(fnX)):
        fnX[iRow] = distance_m / fnX[iRow]  # Convert d/U = 1/E
        fnY[iRow] = math.log(fnY[iRow] * math.pow(fnX[iRow], 2))  # Convert I -> fnY

    return np.transpose([fnX, fnY])


def IdealFowlerNordheim(uVector_V, fieldEnhancment=np.double, distance_d_m=50e-6, workFunc_phi=4.8, area_S_cmSquare=1e-12, noiseLevel=1e-12):
    vType = type(uVector_V)
    if not vType == range and not vType == list and not vType == np.ndarray:
        raise ('Error: voltagesU is not type "range", "list" or "numpy.ndarray"')

    if vType == range:
        vList = list(uVector_V)
    else:
        vList = uVector_V

    if vType == list or vType == range:
        U = np.array(vList)
    else:
        U = uVector_V

    # Constants for getting I [A]: E [MV/m], S [cm²], phi [eV]
    _A = 154  # A * e * V * V^-2 | Combines all constants together
    _B = 6830  # eV^3/2 * V / m | Combines all power-constants together

    # "Map" parameters
    _beta = fieldEnhancment
    _d_µm = distance_d_m * (10**6)
    _phi = workFunc_phi
    _S = area_S_cmSquare
    _nL = noiseLevel
    _n = 0.5e-12

    # Build E-Field-Vector in MegaVolt/Meter
    E = U / _d_μm  # Build MV/m (== V/µm)
    ETip = E * _beta  # Build enhanced field

    const = (_A * _S) / (_phi)
    expConst = -_B * (_phi**1.5)

    numVals = const * (ETip**2)
    expVals = expConst / ETip
    expMul = np.exp(expVals)
    fnI = np.multiply(numVals, expMul)

    for index in range(U.__len__()):
        if abs(fnI[index]) < _nL:
            rVal = random.random() - 0.5
            fnI[index] = _nL * rVal

    data = np.array([U, fnI])
    rProvider = dPrvdr(["U", "I"], np.transpose(data))
    return rProvider
