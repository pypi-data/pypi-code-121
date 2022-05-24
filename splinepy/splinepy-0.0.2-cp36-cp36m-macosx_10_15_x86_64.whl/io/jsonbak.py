"""
Export splines in custom json format
"""

import base64
import json
import logging
import numpy as np


def load(fname):
    """
    Loads splines from json file. Returns dict-splines

    Parameters
    -----------
    fname: str

    Returns
    --------
    spline_list: list
    """
    def unpack_spline(raw_dict):
        """try to unpack spline properties"""
        unpacked = dict()
        splinekeys = ["degrees", "knot_vectors", "control_points", "weights"]

        for sk in splinekeys:
            prop = raw_dict.get(sk, None)

            if prop is not None:
                unpacked.update({sk : prop})

        return unpacked

    # Import data from file into dict format
    jsonbz = json.load(open(fname, "r"))

    spline_list = []
    base64encoding = jsonbz["Base64Encoding"]
    for jbz in jsonbz["SplineList"]:
    
        # Convert Base64 str into np array
        if base64encoding:
            jbz["control_points"] = np.frombuffer(
                base64.b64decode(
                    jbz["control_points"].encode('ascii')
                ), dtype=np.float64
            ).reshape(-1, jbz["dim"])

            if "knot_vectors" in jbz:
                jbz["knot_vectors"] = \
                    np.frombuffer(
                      base64.b64decode(
                        jbz["knot_vectors"].encode('ascii')
                      ), dtype=np.float
                    ).reshape((-1,jbz["dim"]))
                    
    logging.warning("Found unknown spline-type: " + str(jbz))

    logging.debug("Imported " + str(len(spline_list)) + " splines from file.")
    return spline_list

def export_splines(
        fname,
        spline_list,
        list_name=None,
        base64encoding=False
):
    """
    Exports a list of arbitrary splines in json-format


    Parameters
    ----------
    fname : str
      Export Filename
    spline_list: list or Spline
      List of arbitrary Spline-Types or a single spline
    list_name: str
      Default is None and "SplineGroup" will be assigned. Used to define name.
    base64encoding: bool
      Default is False. If True, encodes float type spline properties before
      saving.


    Returns
    -------
    output_dict : dict
    """
    if list_name == None:
        list_name = "SplineGroup"

    if not isinstance(spline_list, list):
        # duck test
        allowed = ["Bezier", "BSpline", "NURBS"]
        whatami = spline_list.whatami
        oneofus = False

        for a in allowed:
            if whatami.startswith(a):
                oneofus = True

        if not oneofus:
            raise TypeError("Invalid input for spline export!")

        spline_list = [spline_list]

    # Number of splines in group
    n_splines = len(spline_list)

    # top level keywords
    output_dict = {
        "Name" : list_name,
        "NumberOfSplines" : n_splines,
        "Base64Encoding" : base64encoding
    }

    # Append all splines to a dictionary
    spline_dictonary_list = []
    for i_spline in spline_list:
        # Create Dictionary
        i_spline_dict = i_spline.todict()
        # Append para_dim and dim
        i_spline_dict["dim"] = i_spline.dim
        i_spline_dict["para_dim"] = i_spline.para_dim
        i_spline_dict["SplineType"] = type(i_spline).__qualname__

        if base64encoding:
            i_spline_dict["control_points"] = base64.b64encode(
                np.array(i_spline_dict["control_points"])
            ).decode('utf-8')

            # each knot vector can have different len. so save it as str
            if "knot_vectors" in i_spline_dict:
                i_spline_dict["knot_vectors"] = base64.b64encode(
                    np.
                )

          
        spline_dictonary_list.append(i_spline_dict)

    output_dict["SplineList"] = spline_dictonary_list

    with open(fname, 'w') as file_pointer:
        file_pointer.write(json.dumps(output_dict, indent=4))

    return output_dict


#def export(spline, fname):
#  """
#  Pass Information to export_splines routin
#
#  Parameters
#  ----------
#  spline : spline
#    arbitrary spline-type
#  fname : str
#    filename
#
#  Returns
#  -------
#  None
#  """
#  export_splines(fname, [spline])

