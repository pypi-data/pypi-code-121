import os
import numpy as np
from copy import deepcopy
import xml.etree.ElementTree as et

import lhcb_ftcalib as ft


class MinimizerOverride:
    """ Fake minimizer used for transferring calibrations during testing """
    def __init__(self, values, errors, cov):
        self.p = ft.CalParameters.CalParameters(len(values) // 2)
        self.p.set_calibration_delta(values, cov)

        self.values = values
        self.errors = errors
        self.covariance = cov
        self.accurate = True

    def convert_params(self):
        self.values     = self.p.params_flavour
        self.covariance = self.p.covariance_flavour
        self.errors     = self.p.errors_flavour


def force_calibration(tagger, func, calibration):
    # Fake a ftcalib calibration by overwriting minimizer
    # and triggering computation of calibrated statistics
    minimizer = MinimizerOverride(
        values = calibration["p_nom"],
        errors = calibration["p_err"],
        cov    = calibration["cov"])
    minimizer.convert_params()
    tagger.set_calibration(func)

    if isinstance(func, ft.PolynomialCalibration):
        tagger.func.set_basis(basis=calibration["basis"])
    elif isinstance(func, ft.NSplineCalibration):
        tagger.func.set_basis(basis=calibration["basis"], nodes=calibration["nodes"])
    elif isinstance(func, ft.BSplineCalibration):
        tagger.func.set_basis(nodes=calibration["nodes"])

    warning = tagger.stats._compute_calibrated_statistics(tagger.func, minimizer)
    if warning != []:
        print(tagger.name, warning[0])
    tagger._calibrated = True


def get_xml_content(xmlfile, tagger):
    # Read EPM xml file and extract calibration results
    xmlfile = str(xmlfile)
    calibration_xml = et.parse(xmlfile)
    root = calibration_xml.getroot()

    calib = root.find(f'{tagger}_Calibration').find('TypicalCalibration')
    funcinfo = root.find(f'{tagger}_Calibration').find('func')

    summary = {}
    degree = int(calib.find('coeffs').find('n').text)
    covariance = -999 * np.ones((2 * degree, 2 * degree))
    # Extract p0 & p1
    ps = calib.find('coeffs').find('vector_data')
    for i in range(degree):
        summary['p' + str(i)] = np.float64(ps[i].text)

    # Extract Δp0 & Δp1
    delta_ps = calib.find('delta_coeffs').find('vector_data')
    for i in range(degree):
        summary['Dp' + str(i)] = np.float64(delta_ps[i].text)

    # Extract p0-p1 covariance matrix
    cov_ps = calib.find('covariance').find('matrix_data')
    i = 0
    for r in range(degree):
        for c in range(degree):
            if c == r:
                summary['p{}_err'.format(c)] = np.sqrt(np.float64(cov_ps[i].text))
            # summary['p_cov_{0}{1}'.format(r, c)] = np.float64(cov_ps[i].text)
            covariance[r][c] = np.float64(cov_ps[i].text)
            i += 1

    # Extract Δp0-Δp1 covariance matrix
    cov_Dps = calib.find('delta_covariance').find('matrix_data')
    i = 0
    for r in range(degree):
        for c in range(degree):
            if c == r:
                summary['Dp{}_err'.format(c)] = np.sqrt(np.float64(cov_Dps[i].text))
            # summary['Dp_cov_{0}{1}'.format(r, c)] = np.float64(cov_Dps[i].text)
            covariance[r + degree][c + degree] = np.float64(cov_Dps[i].text)
            i += 1

    # Extract cross covariance matrix
    cov_cross = calib.find('cross_covariance').find('matrix_data')
    i = 0
    for r in range(degree):
        for c in range(degree):
            # summary['cross_cov_{0}{1}'.format(r, c)] = np.float64(cov_cross[i].text)
            covariance[r][c + degree] = np.float64(cov_cross[i].text)
            covariance[r + degree][c] = np.float64(cov_cross[i].text)
            i += 1

    # Extract calibration basis
    basis = funcinfo.find('glm').find('tx').find('basis')
    if basis is not None:
        basis = basis.find('matrix_data')
    nodes = funcinfo.find('glm').find('tx').find('nodes')

    if nodes is not None:
        summary["nodes"] = []
        nodecount = np.int32(nodes.find("count").text)
        for i in range(2, nodecount + 2):
            summary["nodes"].append(np.float64(nodes[i].text))

    if basis is not None:
        i = 0
        summary["basis"] = []
        for r in range(degree):
            for c in range(degree):
                if c == 0 and r == 1:
                    summary['eta'] = -np.float64(basis[i].text)
                    summary['basis'].append(np.float64(basis[i].text))
                else:
                    # summary['basis_{0}{1}'.format(r, c)] = np.float64(basis[i].text)
                    summary['basis'].append(np.float64(basis[i].text))
                i += 1

    summary["cov"] = covariance

    return summary


def delete_file(F):
    if os.path.exists(F):
        os.remove(F)
        print("Removed", F)


class DataIntegrity:
    # Make deep copies of TaggingData so that we can test whether basic tagging
    # statistics that should remain constant during calibration actually remain
    # constant
    def __init__(self, taggers):
        self.taggers_reference = taggers
        self.checkpoints = [deepcopy(tagger.stats) for tagger in taggers]
        self.funcs = [deepcopy(tagger.func) for tagger in taggers]

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        # These data fields contain the underlying input data which should always remain untouched
        basic_datafields_full_frame = [
            "eta", "dec", "decay_flav", "selected", "tau", "tau_err",
            "weight", "overflow", "underflow", "tagged", "tagged_sel",
            "prod_flav", "wrong_tags", "correct_tags"
        ]
        isconst = True

        for func, tagger in zip(self.funcs, self.taggers_reference):
            isconst &= func == tagger.func

        assert isconst, "Calibration function basis changes during minimization, this is not allowed"

        for checkpoint, tagger in zip(self.checkpoints, self.taggers_reference):
            for column in basic_datafields_full_frame:
                if column in tagger.stats._full_data:
                    # Compare ids because just in case
                    assert id(checkpoint._full_data[column]) != id(tagger.stats._full_data[column]), "deepcopy failed"
                    assert id(checkpoint._tagdata[column]) != id(tagger.stats._tagdata[column]), "deepcopy failed"
                    isconst &= checkpoint._full_data[column].equals(tagger.stats._full_data[column])
                    isconst &= checkpoint._tagdata[column].equals(tagger.stats._tagdata[column])
                    isconst &= checkpoint.N         == tagger.stats.N
                    isconst &= checkpoint.Ns        == tagger.stats.Ns
                    isconst &= checkpoint.Nt        == tagger.stats.Nt
                    isconst &= checkpoint.Nts       == tagger.stats.Nts
                    isconst &= checkpoint.Nw        == tagger.stats.Nw
                    isconst &= checkpoint.Nwt       == tagger.stats.Nwt
                    isconst &= checkpoint.Nws       == tagger.stats.Nws
                    isconst &= checkpoint.Neffs     == tagger.stats.Neffs
                    isconst &= checkpoint.Nwts      == tagger.stats.Nwts
                    isconst &= checkpoint.Noverflow == tagger.stats.Noverflow
                    isconst &= checkpoint.avg_eta   == tagger.stats.avg_eta

        assert isconst, "Basic tagging data has been altered during minimization, this is not allowed"


def compare_tuples(taggername, title, ftc, epm, rtol, atol=1e-5, sep='±'):
    # Compare two tuples with numerical elements. If values are not matching
    # within a set relative tolerance and absolute difference is larger than
    # atol, returns False. else true
    if not len(ftc) == len(epm):
        print(ftc)
        print(epm)
        raise RuntimeError("Cannot compare datasets of unequal length")

    print(f"\033[1m{taggername}: Testing {title} ... \033[0m", end='', flush=True)

    def relative_tolerance_ok(t1, t2, rtol):
        return all(np.isclose(a, b, rtol=rtol) for a, b in zip(t1, t2))

    def absolute_tolerance_ok(t1, t2, atol):
        return all(np.isclose(a, b, atol=atol) for a, b in zip(t1, t2))

    if relative_tolerance_ok(epm, ftc, rtol):
        print("\033[32;1m PASS \033[0m")
        isgood = True
    elif absolute_tolerance_ok(epm, ftc, atol):
        print("\033[33;1m absolute tolerance OK \033[0m")
        # We should not care about sizeable relative differences if absolute
        # difference is small. atol is unstable for very small numbers but it
        # seems to be stable enough here
        isgood = True
    else:
        print("\033[1;41m FAIL \033[0m")
        isgood = False

    print("  - ftcalib :", f" {sep} ".join([str(np.round(f, 9)) for f in ftc]))
    print("  - EPM     :", f" {sep} ".join([str(np.round(e, 9)) for e in epm]))
    print("  - diff    :", f" {sep} ".join([str(np.round(e - f, 9)) for e, f in zip(epm, ftc)]))

    return isgood


def compare_basis(epm, ftc):
    degree = len(ftc["paramnames"]) // 2

    if "basis" in epm:
        basis_epm = epm["basis"]
        basis_ftc = [list(b) for b in ftc["basis"]]

        for i, b in enumerate(basis_ftc):
            basis_ftc[i] = basis_ftc[i][::-1]
            basis_ftc[i] += (degree - len(basis_ftc[i])) * [0]

        basis_epm = np.array(basis_epm)
        basis_ftc = np.array(basis_ftc).flatten()

        compare_tuples("tagger basis", "Basis", tuple(basis_ftc), tuple(basis_epm), rtol=1e-3, atol=1e-6, sep=';;')

    if "nodes" in epm:
        compare_tuples("tagger spline nodes", "Nodes", tuple(ftc["nodes"]), tuple(epm["nodes"]), rtol=1e-3, atol=1e-6, sep=';;')
