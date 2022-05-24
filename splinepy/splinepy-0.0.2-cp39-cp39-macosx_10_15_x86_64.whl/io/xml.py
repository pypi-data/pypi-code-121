import xml.etree.ElementTree as ElementTree

import numpy as np

keywords = dict(
    entries="SplineEntry",
    cps="cntrlPntVars",
    cpkeys=["x", "y", "z"]
    ws="wght",
    ds="deg",
    kvs="kntVecs",
    kv="kntVec",
    dim="spaceDim",
    para_dim="splDim",
)


def load(fname):
    """
    Loads xml files based on keywords

    Parameters
    -----------
    fname: str

    Returns
    --------
    loaded_splines: list
    """
    kw = keywords

    et = ElementTree.parse(fname)
    root = et.getroot()

    loaded_splines = []
    for sp in root.findall(kw["entries"]):
        # ds
        strds = " ".join(sp.find(kw["ds"]).text.split())
        ds = np.fromstring(strds, dtype=np.int32, sep=" ")

        # kvs
        kvs = []
        for kvec in sp.find(kw["kvs"]).findall(kw["kv"]):
            kvstr = kvec.text.split() # list of string
            kv = [float(k) for k in kvstr]
            kvs.append(kv)

        # cps
        strcps = " ".join(sp.find(kw["cps"]).text.split())
        cps = np.fromstring(strcps, dtype=np.double, sep=" ")
        cps = cps.reshape(-1, int(sp.get(kw["dim"])))

        # ws
        strws = " ".join(sp.find(kw["ws"]).text.split())
        ws = np.fromstring(strws, dtype=np.double, sep=" ")
        ws = ws.reshape(-1, 1)

        tmpspline = dict(
            degrees=ds,
            knot_vectors=kvs,
            control_points=cps,
        )
        if ws.size > 0:
            tmpspline.update(weights=ws)

        loaded_splines.append(tmpspline)

    return loaded_splines


def export(fname, splines):
    """
    Exports xml files based on keywords

    """
