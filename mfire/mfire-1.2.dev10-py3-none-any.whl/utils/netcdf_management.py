import xarray as xr
import numpy as np


def store_compress(da, fname, ctype="uint16", **kwargs):
    """
    Compress file before saving using xarray.
    The compression is performed using a dictionnary.
    The main principle is to decompose
    y = x * scale + offset
    with y the original dataArray (in float32 or float64) and x the stored
    dataArray (basically using uint16/uint8)

    Args:
        da (dataarray): The dataarray to save. This dataarray should have a name define.
        fname (str): The file to use to save. This file should not be previously open
        ctype (str, optional): The type in which we will save the dataArray using
            (scale,offset) algorithm. Defaults to "uint16".
    Kwargs :
        Other parameter that can be used in the encoding dictionnary

    """
    if not isinstance(da, xr.core.dataarray.DataArray):
        raise (
            ValueError("The input data should be a dataarray. Getting %s" % type(da))
        )
    if not hasattr(da, "name") or da.name is None:
        raise (
            ValueError(
                "The input dataArray should have a name. "
                "Please specify it using da.name = `xxxx`."
            )
        )

    # Determine the range of values
    mini = da.min().values
    maxi = da.max().values
    # Determine the offset
    offset = mini

    # Determine the scale based on the type
    if ctype.startswith(("i", "u")):
        scale = (maxi - mini) / np.iinfo(ctype).max * 1.2
        other_parameter = {"_FillValue": 9999}
        other_parameter.update(kwargs)
    else:
        scale = (maxi - mini) / np.finfo(ctype).max
        other_parameter = {}
        other_parameter.update(kwargs)
    # Create the dictionnary for encoding
    dict_encode_as_int = {}
    # Fill it for the desired variable
    dict_encode_as_int[da.name] = {
        "dtype": ctype,
        "add_offset": offset,
        "scale_factor": scale,
    }
    # update it with kwargs arguments and default argument for int/uint
    dict_encode_as_int[da.name].update(other_parameter)
    print("Dictionnary before storage %s" % dict_encode_as_int)
    da.to_netcdf(fname, encoding=dict_encode_as_int)
