import os
import json
import uuid
import numbers
import numpy as np

# from lhcb_ftcalib.Tagger import Tagger
from .Tagger import Tagger
from .printing import warning, raise_error
from .TaggerCollection import TaggerCollection
from .printing import info
from .PolynomialCalibration import PolynomialCalibration
from .NSplineCalibration import NSplineCalibration
from .BSplineCalibration import BSplineCalibration


def _serialize(OBJ):
    # returns dictionary of json-serialized objects (i.e. strings)
    serialized = {}
    if isinstance(OBJ, dict):
        for key, val in OBJ.items():
            if isinstance(val, dict):
                serialized[key] = _serialize(val)
            elif isinstance(val, numbers.Number):
                if isinstance(val, np.int64):
                    serialized[key] = int(val)
                else:
                    serialized[key] = val
            elif isinstance(val, (list, np.ndarray)):
                serialized[key] = [_serialize(v) for v in val]
            else:
                serialized[key] = val
    else:
        if isinstance(OBJ, dict):
            return _serialize(OBJ)
        elif isinstance(OBJ, numbers.Number):
            if isinstance(OBJ, np.int64):
                return int(OBJ)
            else:
                return OBJ
        elif isinstance(OBJ, (list, np.ndarray)):
            return [_serialize(v) for v in OBJ]
        else:
            return OBJ
    return serialized


def _save_function(tagger):
    if isinstance(tagger.func, PolynomialCalibration):
        return {
            "degree" : tagger.func.npar,
            "link"   : tagger.func.link.__name__,
            "basis"  : [_serialize(vec) for vec in tagger.func.basis]
        }
    elif isinstance(tagger.func, NSplineCalibration):
        return {
            "degree" : tagger.func.npar,
            "link"   : tagger.func.link.__name__,
            "nodes"  : _serialize(tagger.func.nodes),
            "basis"  : [_serialize(vec) for vec in tagger.func.basis]
        }
    elif isinstance(tagger.func, BSplineCalibration):
        return {
            "degree" : tagger.func.npar,
            "link"   : tagger.func.link.__name__,
            "nodes"  : _serialize(tagger.func.nodes)
        }


def save_calibration(taggers, title=None, indent=2):
    """ Writes calibrations of calibrated taggers to a file.

        :param taggers: Calibrated taggers
        :type taggers: TaggerCollection or list
        :param title: Title of calibration file. By default, filename will be assigned a uuid. If file exists, calibrations are appended.
        :type title: str
        :param indent: Number of indentation spaces to use in the calibration file
        :type indent: int
    """
    def write_calibration_dict(tagger):
        P = tagger.stats.params

        calib = {
            tagger.name : {
                tagger.func.__class__.__name__ : _save_function(tagger),
                "osc" : {
                    "DeltaM"     : tagger.DeltaM,
                    "DeltaGamma" : tagger.DeltaGamma,
                    "Aprod"      : tagger.Aprod,
                },
                "calibration" : {
                    "avg_eta" : tagger.stats.avg_eta,
                    "flavour_style" : {
                        "params" : [ (pn, n, s) for pn, n, s in zip(P.names_flavour, P.params_flavour, P.errors_flavour) ],
                        "cov"    : P.covariance_flavour,
                    },
                    "delta_style" : {
                        "params" : [ (pn, n, s) for pn, n, s in zip(P.names_delta, P.params_delta, P.errors_delta) ],
                        "cov"    : P.covariance_delta,
                    }
                },
                "stats" : {
                    "N"    : tagger.stats.N,
                    "Nt"   : tagger.stats.Nt,
                    "Neff" : tagger.stats.Neff,
                    "Nw"   : tagger.stats.Nw,
                    "Nwt"  : tagger.stats.Nwt,
                },
                "selected_stats" : {
                    "Ns"    : tagger.stats.Ns,
                    "Nts"   : tagger.stats.Nts,
                    "Neffs" : tagger.stats.Neffs,
                    "Nws"   : tagger.stats.Nws,
                    "Nwts"  : tagger.stats.Nwts,
                },
                "uncalibrated" : {
                    "selected" : {
                        "tag_efficiency"   : tagger.stats.tagging_efficiency(calibrated=False, inselection=True),
                        "mistag_rate"      : tagger.stats.mistag_rate(calibrated=False, inselection=True),
                        "effective_mistag" : tagger.stats.mistag_rate(calibrated=False, inselection=True),
                        "tagging_power"    : tagger.stats.tagging_power(calibrated=False, inselection=True)
                    },
                    "overall" : {
                        "tag_efficiency"   : tagger.stats.tagging_efficiency(calibrated=False, inselection=False),
                        "mistag_rate"      : tagger.stats.mistag_rate(calibrated=False, inselection=False),
                        "effective_mistag" : tagger.stats.mistag_rate(calibrated=False, inselection=False),
                        "tagging_power"    : tagger.stats.tagging_power(calibrated=False, inselection=False)
                    },
                },
                "calibrated" : {
                    "selected" : {
                        "Nts"              : tagger.stats.cal_Nts,
                        "Nwts"             : tagger.stats.cal_Nwts,
                        "tag_efficiency"   : tagger.stats.tagging_efficiency(calibrated=True, inselection=True),
                        "mistag_rate"      : tagger.stats.mistag_rate(calibrated=True, inselection=True),
                        "effective_mistag" : tagger.stats.mistag_rate(calibrated=True, inselection=True),
                        "tagging_power"    : tagger.stats.tagging_power(calibrated=True, inselection=True)
                    },
                    "overall" : {
                        "Nt"               : tagger.stats.cal_Nt,
                        "Nwt"              : tagger.stats.cal_Nwt,
                        "tag_efficiency"   : tagger.stats.tagging_efficiency(calibrated=True, inselection=False),
                        "mistag_rate"      : tagger.stats.mistag_rate(calibrated=True, inselection=False),
                        "effective_mistag" : tagger.stats.mistag_rate(calibrated=True, inselection=False),
                        "tagging_power"    : tagger.stats.tagging_power(calibrated=True, inselection=False)
                    },
                }
            }
        }
        return _serialize(calib)

    title = str(title) if title is not None else None  # Support pathlib et al

    if isinstance(taggers, (TaggerCollection, list)):
        calib = {}
        if title is None:
            warning("Calibration file has no specific title")
            title = "Calibration-" + str(uuid.uuid1())
        for tagger in taggers:
            calib.update(write_calibration_dict(tagger))
    elif isinstance(taggers, Tagger):
        title = title or taggers.name
        calib = write_calibration_dict(taggers)
    else:
        raise_error(False, "Tagger type unknown")

    filename = title + ".json" if not title.endswith(".json") else title

    if os.path.exists(filename):
        info(f"Calibration file {filename} exists: Appending calibrations")
        existing = json.load(open(filename, "r"))
        existing.update(calib)
        json.dump(existing, open(filename, "w"), indent=indent)
    else:
        json.dump(calib, open(filename, "w"), indent=indent)
