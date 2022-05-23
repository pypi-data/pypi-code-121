import numpy as np
try:
    from osgeo import gdal, osr
except ImportError:
    gdal = None


numpy_types_to_gdal = {}

if gdal is not None:
    numpy_types_to_gdal.update({
        np.dtype(np.uint8): gdal.GDT_Byte,
        np.dtype(np.uint16): gdal.GDT_UInt16,
        np.dtype(np.uint32): gdal.GDT_UInt32,
        np.dtype(np.int16): gdal.GDT_Int16,
        np.dtype(np.int32): gdal.GDT_Int32,
        np.dtype(np.float32): gdal.GDT_Float32,
        np.dtype(np.float64): gdal.GDT_Float64,
        np.dtype(np.complex64): gdal.GDT_CFloat32,
        np.dtype(np.complex128): gdal.GDT_Float64
    })


def lookup_dtype(dtype):
    try:
        d = np.dtype(dtype)
        return numpy_types_to_gdal[d]
    except (KeyError, TypeError):
        if dtype in list(numpy_types_to_gdal.values()):
            return dtype
    raise ValueError(f"invalid dtype '{dtype}'")


def get_spatial_reference(epsg_or_sr):
    cd = 0
    if isinstance(epsg_or_sr, osr.SpatialReference):
        return epsg_or_sr
    try:
        cd = int(epsg_or_sr.split(':')[-1])
        sr = osr.SpatialReference()
        sr.ImportFromEPSG(cd)
        return sr
    except AttributeError:
        sr = osr.SpatialReference()
        sr.ImportFromEPSG(epsg_or_sr)
        return sr
    raise ValueError(f"invalid spatial reference '{epsg_or_sr}'")
