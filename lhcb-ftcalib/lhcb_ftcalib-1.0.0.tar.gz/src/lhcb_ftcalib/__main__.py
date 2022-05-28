import os
import sys
import re
import argparse
import uproot
import numpy as np

from ._version import __version__
from .TaggerCollection import TaggerCollection
from .PolynomialCalibration import PolynomialCalibration
from .NSplineCalibration import NSplineCalibration
from .BSplineCalibration import BSplineCalibration
from .save_calibration import save_calibration
from .apply_tagger import TargetTaggerCollection, get_link_by_name
from .printing import (warning, info, FTCalibException, section_header,
                       print_tagger_statistics, MissingBranch, MissingFile, MissingTree)


def main():
    try:
        args = parse_ftcalib_args()
        section_header(f"lhcb_ftcalib version {__version__}")
        loadplan = read_file(args.rootfile,
                             ID        = args.id_branch,
                             TAGGERS   = args.taggers,
                             SSTAGGERS = args.SStaggers,
                             OSTAGGERS = args.OStaggers,
                             TAU       = args.tau,
                             TAUERR    = args.tauerr,
                             WEIGHT    = args.weights,
                             SEL       = args.selection,
                             ask       = args.interactive)
    except FTCalibException as ex:
        print(ex)
        return
    if loadplan is None:
        print("Aborted")
        return

    run(args, load_data(args, loadplan), loadplan)


class RootFile:
    def __init__(self, filename, filetype="root"):
        self.filename = filename
        self.df = None
        self.filetype = filetype

    def append_data(self, df):
        if self.df is None:
            self.df = df
        else:
            for branch in df.columns.values:
                self.df[branch] = df[branch]

    def write(self):
        if self.filetype == "root":
            with uproot.recreate(self.filename) as File:
                File["TaggingTree"] = self.df
        elif self.filetype == "csv":
            self.df.to_csv(self.filename, sep=";")


def parse_ftcalib_args():
    # Pre parser just in case user wants to see version
    parser_dryrun = argparse.ArgumentParser(description="LHCb Flavour Tagging calibration software", add_help=False)
    parser_dryrun.add_argument("--version", "-v", action="store_true", dest="version", help="print version")
    parser_dryrun.add_argument("--help", "-h", action="store_true", help="help")
    args, _ = parser_dryrun.parse_known_args()

    if len(sys.argv) == 1:  # No argument at all
        print(f"ftcalib {__version__}")
        print("Try `ftcalib --help`")
        exit(0)
    elif args.version:
        print(f"ftcalib {__version__}")
        exit(0)

    parser = argparse.ArgumentParser(description="LHCb Flavour Tagging calibration software")
    parser.add_argument("rootfile",  type=str, help="ROOT file and tree to read tagging data from. (example: \"file.root:DecayTree\")")
    parser.add_argument("-t",         dest="taggers",    type=str, nargs="+", default=[], help="Enumeration of taggers to find in file. This argument will try to match partial names, e.g. \"MuonLatest\"->\"B_OSMuonLatest_TAGDEC/ETA\"")
    parser.add_argument("-SS",        dest="SStaggers",  type=str, nargs="+", default=[], help="Enumeration of same side taggers to find in file. This argument will try to match partial names, e.g. \"MuonLatest\"->\"B_OSMuonLatest_TAGDEC/ETA\"")
    parser.add_argument("-OS",        dest="OStaggers",  type=str, nargs="+", default=[], help="Enumeration of opposite side taggers to find in file. This argument will try to match partial names, e.g. \"MuonLatest\"->\"B_OSMuonLatest_TAGDEC/ETA\"")
    parser.add_argument("-id",        dest="id_branch",  type=str, help="Name of the B meson id branch")
    parser.add_argument("-mode",      dest="mode",       type=str, choices=["Bu", "Bd", "Bs"],  help="Calibration mode")
    parser.add_argument("-tau",       dest="tau",        type=str, help="Name of the decay time branch")
    parser.add_argument("-tauerr",    dest="tauerr",     type=str, help="Name of the decay time uncertainty branch")
    parser.add_argument("-timeunit",  dest="timeunit",   type=str, default="ns", choices=["ns", "ps", "fs"], help="Decay time unit")
    parser.add_argument("-weights",   dest="weights",    type=str, help="Name of the per-event weight branch")
    parser.add_argument("-op",        dest="op",         type=str, required=True, nargs='+', choices=["calibrate", "combine", "apply"], help="What to do with the loaded taggers")
    parser.add_argument("-write",     dest="write",      type=str, help="Name of a root file where to store calibrated branches")
    parser.add_argument("-selection", dest="selection",  type=str, help=r"Selection expression (example: 'eventNumber%%2==0;eventNumber%%2==1'), selection after semicolon is used for combination calibration (optional)")
    parser.add_argument("-input_cal", dest="input_cal",  type=str, help="JSON file of the input calibrations")
    parser.add_argument("-plot",      dest="plot",       action="store_true", help="If set, plots calibration curves")

    parser.add_argument("-fun",  type=str, dest="fun", nargs=2, default=["POLY", 2], help="CalibrationFunction followed by number of parameters per flavour (default: %(default)s). Available calibration functions: ['POLY', 'NSPLINE', 'BSPLINE']")
    parser.add_argument("-link", type=str, dest="link", choices=["mistag", "logit", "rlogit", "probit", "rprobit", "cauchit", "rcauchit"], default="mistag", help="Link function (default: %(default)s)")

    parser.add_argument("-i", action="store_true", dest="interactive", help="Interactive mode, will ask for confirmation")
    parser.add_argument("-filetype", type=str, default="root", choices=["root", "csv"], dest="filetype", help="Filetype to use instead of root files")

    args = parser.parse_args()

    if "apply" in args.op and args.input_cal is None:
        raise FTCalibException("You need to provide a file with input calibrations using the \"-input_cal\" argument")
    if args.input_cal is not None and not os.path.exists(args.input_cal):
        raise FTCalibException(f"Input calibration file {args.input_cal} does not exist")
    if args.id_branch is None and "calibrate" in args.op:
        raise FTCalibException("An ID branch is required for calibrations")

    return args


def assign_eta_omega(search_result):
    """ search_result is a list of two branches. This function
        identifies the mistag and tag dec branch """
    dec = next(b for b in search_result if b.endswith("DEC"))
    eta = next(b for b in search_result if b.endswith("ETA"))
    name = dec.replace("_TAGDEC", "").replace("_DEC", "").replace("_DECISION", "")
    return name, dec, eta


def get_selection_branches(selection, all_branches):
    info("Parsing selection", selection)

    def getbranches(sel):
        def is_bool(match):
            return match in ("and", "or", "xor", "not")

        functions = re.compile(r"[A-Za-z]+[_A-Za-z0-9]*\(")  # any identifier followed by '(' is a "function", not a branch
        selvars  = re.compile("[A-Za-z]+[_A-Za-z0-9]*")
        funcs = [match[:-1] for match in functions.findall(sel)]
        selvars = [match for match in selvars.findall(sel) if match not in funcs and not is_bool(match)]
        selvars = list(set(selvars))
        return selvars

    if ";" in selection:
        selection = selection.split(";")
        selvars = list(set(getbranches(selection[0]) + getbranches(selection[1])))
    else:
        selvars = getbranches(selection)

    info("Selection branches: ", selvars)

    return selvars


def read_file(File, ID, TAGGERS=[], SSTAGGERS=[], OSTAGGERS=[], TAU=None, TAUERR=None, WEIGHT=None, SEL=None, ask=False):
    # Open file while anticipating all possible user errors
    loadplan = {"taggers"   : {},
                "sstaggers" : {},
                "ostaggers" : {},
                "branches"  : []}

    def clean_sel_string(sel):
        return sel.strip().replace("\"", "").replace("\'", "")

    if SEL is not None:
        SEL = clean_sel_string(SEL)
        if ";" in SEL:
            loadplan["selection1"] = SEL.split(";")[0]
            loadplan["selection2"] = SEL.split(";")[1]
        else:
            loadplan["selection1"] = SEL
            loadplan["selection2"] = None
    else:
        loadplan["selection1"] = None
        loadplan["selection2"] = None

    if ":" in File:
        filename, treename = File.split(":")
    else:
        filename, treename = File, None

    if not os.path.exists(filename):
        raise MissingFile(f"File {filename} not found")

    tfile = uproot.open(filename)
    if treename is None:
        warning(f"TTree not specified, reading from first TTree in file \"{tfile.keys()[0]}\"")
        treename = tfile.keys()[0]
    else:
        if treename not in tfile:
            raise MissingTree(f"TTree \"{treename}\" not found in file {filename}. Available trees: {tfile.keys()}")
    tree = tfile[treename]
    info(f"Reading data from {filename}:{treename}")

    branches = tree.keys()

    def add_if(branch):
        if branch is not None:
            if branch not in branches:
                raise MissingBranch(f"Branch \"{branch}\" not found in {filename}:{treename}")
            loadplan["branches"].append(branch)

    add_if(ID)
    add_if(TAU)
    add_if(TAUERR)
    add_if(WEIGHT)

    # Get list of all possible taggers
    if SEL is not None:
        loadplan["sel_branches"] = get_selection_branches(SEL, branches)
        loadplan["branches"] += loadplan["sel_branches"]

    alltaggers = list(set(TAGGERS + SSTAGGERS + OSTAGGERS))

    for tagger_hint in alltaggers:
        search = [branch for branch in branches if tagger_hint in branch]
        search = [branch for branch in search if branch.endswith("ETA") or branch.endswith("DEC")]
        if len(search) != 2:
            raise FTCalibException(f"Too many or None of the branches in the file are matching the tagger hint \"{tagger_hint}\":\n\t* " + '\n\t* '.join(search))

        tagger, dec, eta = assign_eta_omega(search)
        if tagger_hint in TAGGERS and tagger not in loadplan["taggers"]:
            loadplan["taggers"][tagger] = {"dec": dec, "mistag": eta}
        if tagger_hint in SSTAGGERS and tagger not in loadplan["sstaggers"]:
            loadplan["sstaggers"][tagger] = {"dec": dec, "mistag": eta}
        if tagger_hint in OSTAGGERS and tagger not in loadplan["ostaggers"]:
            loadplan["ostaggers"][tagger] = {"dec": dec, "mistag": eta}

        loadplan["branches"].append(dec)
        loadplan["branches"].append(eta)

    info("The following taggers have been found")
    for k, v in loadplan["taggers"].items():
        print(f"\t->\033[94m\"{k}\"\033[0m: eta =\033[3;1m", v["mistag"], "\033[0mand d =\033[3;1m", v["dec"], "\033[0m")
    for k, v in loadplan["sstaggers"].items():
        print(f"\t-> \033[94m\"{k}\"\033[0m: eta =\033[3;1m", v["mistag"], "\033[0mand d =\033[3;1m", v["dec"], "\033[0m")
    for k, v in loadplan["ostaggers"].items():
        print(f"\t-> \033[94m\"{k}\"\033[0m: eta =\033[3;1m", v["mistag"], "\033[0mand d =\033[3;1m", v["dec"], "\033[0m")

    if ask:
        if not (input("Continue? <y/n> ") in ("Y", "y", "Yes", "yes")):
            return None

    loadplan["ID"]       = ID
    loadplan["TAU"]      = TAU
    loadplan["TAUERR"]   = TAUERR
    loadplan["weight"]   = WEIGHT
    loadplan["tree"]     = treename
    loadplan["file"]     = filename
    loadplan["branches"] = list(set(loadplan["branches"]))  # There can be duplicate due to event selection

    return loadplan


def load_data(args, loadplan):
    data = uproot.open(loadplan["file"])[loadplan["tree"]].arrays(loadplan["branches"], library="pd")

    # Convert to picosenconds
    timefactor = {"ns" : 1e3, "ps" : 1.0, "fs" : 1e-3}[args.timeunit]
    if loadplan["TAU"] is not None:
        data.loc[:, loadplan["TAU"]] *= timefactor
    if loadplan["TAUERR"] is not None:
        data.loc[:, loadplan["TAUERR"]] *= timefactor

    # pandas dataframe queries have problems with uint64 => convert to int64
    for c in data.columns.values:
        if data[c].dtype == np.uint64:
            # pandas eval has weird data type limitations
            warning(f"Branch {c} has type uint64. Converting to int64 for pandas")
            data[c] = data[c].astype(np.int64)

    return data


def write_branches(root_file, tc, calibrated, append=False, write_extra_branches=False):
    df = tc.get_dataframe(calibrated=calibrated)

    if write_extra_branches:
        df["ID"] = tc[0].stats._full_data.decay_flav.copy()
        if tc[0].stats._has_tau:
            df["TAU"] = tc[0].stats._full_data.tau
        if tc[0].stats._has_tauerr:
            df["TAUERR"] = tc[0].stats._full_data.tau_err
        df["weight"] = tc[0].stats._full_data.weight

    info(f"Writing file {root_file.filename}")
    root_file.append_data(df)


def validate_ops(args):
    # Check whether order of requested calibration steps makes sense / is supported
    state = "___start"
    dfa = {
        "___start":  {"calibrate" : "calibrate", "apply" : "apply", "combine" : None},
        "apply":     {"calibrate" : None,        "apply" : None,    "combine" : "END"},
        "calibrate": {"calibrate" : None,        "apply" : None,    "combine" : "combine"},
        "combine":   {"calibrate" : "END",       "apply" : None,    "combine" : None},
        "END":       {"calibrate" : None,        "apply" : None,    "combine" : None},
    }
    for i, op in enumerate(args.op):
        nextstate = dfa[state][op]
        if nextstate is None:
            if state == "___start":
                raise FTCalibException(f"Argument {i}: Procedure cannot begin with operation \"{op}\"")
            else:
                raise FTCalibException(f"Argument {i}: Operation \"{op}\" cannot come after \"{state}\"" + (" (nothing left to do)" if state == "END" else ""))
        state = nextstate


def run(args, data, loadplan):
    # Interpret selection strings
    def boolean_sel(sel):
        # Returns boolean list of selected events
        if sel is None:
            return None
        data.eval(f"FTCSELECTION={sel}", inplace=True)
        assert data.FTCSELECTION.dtype == bool
        selection = data.FTCSELECTION.copy()
        rem = [b for b in loadplan["sel_branches"] if b not in loadplan["branches"]]
        data.drop(columns=["FTCSELECTION"] + rem, inplace=True)
        return selection

    sel1 = boolean_sel(loadplan["selection1"])
    sel2 = boolean_sel(loadplan["selection2"])
    if "apply" in args.op and args.selection is not None:
        warning("Can only apply calibrations to full statistics, ignoring selection")

    validate_ops(args)

    def get_tagger_collection(taggertype, apply_tagger, selection):
        # Puts taggers into tagger collections
        nonlocal data
        if len(loadplan[taggertype]) == 0:
            return None

        def fetch(branch):
            return data[loadplan[branch]] if loadplan[branch] is not None else None

        if apply_tagger:
            tc = TargetTaggerCollection()
            for name, tagbranch in loadplan[taggertype].items():
                tc.create_tagger(name      = name,
                                 eta_data  = data[tagbranch["mistag"]],
                                 dec_data  = data[tagbranch["dec"]],
                                 B_ID      = fetch("ID"),
                                 mode      = args.mode,
                                 tau_ps    = fetch("TAU"),
                                 tauerr_ps = fetch("TAUERR"),
                                 weight    = fetch("weight"))
        else:
            tc = TaggerCollection()
            for name, tagbranch in loadplan[taggertype].items():
                tc.create_tagger(name      = name,
                                 eta_data  = data[tagbranch["mistag"]],
                                 dec_data  = data[tagbranch["dec"]],
                                 B_ID      = data[loadplan["ID"]],
                                 mode      = args.mode,
                                 selection = selection,
                                 tau_ps    = fetch("TAU"),
                                 tauerr_ps = fetch("TAUERR"),
                                 weight    = fetch("weight"))
        return tc

    tc_any, tc_ss, tc_os = (get_tagger_collection("taggers",   apply_tagger="apply" in args.op, selection=sel1),
                            get_tagger_collection("sstaggers", apply_tagger="apply" in args.op, selection=sel1),
                            get_tagger_collection("ostaggers", apply_tagger="apply" in args.op, selection=sel1))

    del data  # All the data is stored in taggers now

    calibration_filename = args.write + ".json" if args.write is not None else "out.json"
    calibration_rootfile = args.write + ".root" if args.write is not None else "out.root"
    stored_extra_branches = False

    print(args)
    output_rootfile = RootFile(calibration_rootfile, filetype=args.filetype)

    def calibration_steps(tc, write_uncalib_branches):
        nonlocal stored_extra_branches
        if tc is not None:
            if args.fun != ["POLY", 2] or args.link != "mistag":
                if args.fun[0] == "POLY":
                    tc.set_calibration(PolynomialCalibration(int(args.fun[1]), get_link_by_name(args.link)))
                elif args.fun[0] == "NSPLINE":
                    tc.set_calibration(NSplineCalibration(int(args.fun[1]), get_link_by_name(args.link)))
                elif args.fun[0] == "BSPLINE":
                    tc.set_calibration(BSplineCalibration(int(args.fun[1]), get_link_by_name(args.link)))
            tc.calibrate()
            if args.plot:
                tc.plot_calibration_curves(savepath="/".join(args.write.split("/")[:-1]) if args.write is not None else ".")
            save_calibration(tc, title=calibration_filename)
            if args.write is not None:
                if write_uncalib_branches:
                    write_branches(output_rootfile, tc, calibrated=False, append=True, write_extra_branches=not stored_extra_branches)
                    stored_extra_branches = True
                write_branches(output_rootfile, tc, calibrated=True, append=True, write_extra_branches=not stored_extra_branches)

    def combination_steps(tc, combination_name, apply_calib):
        if tc is not None:
            if len(tc) > 1:
                if apply_calib:
                    Combination = tc.combine_taggers(combination_name, calibrated=True)
                else:
                    Combination = tc.combine_taggers(combination_name, calibrated=True, next_selection=sel2)
                return Combination

    def apply_steps(tc):
        if tc is not None:
            tc.load_calibrations(args.input_cal)
            tc.apply()
            write_branches(output_rootfile, tc, calibrated=True, append=True)

    # Workflows for applying taggers and calibrating them are forced to be separate
    if "apply" in args.op:
        combinations = None
        for i, operation in enumerate(args.op):
            if operation == "apply":
                apply_steps(tc_any)
                apply_steps(tc_ss)
                apply_steps(tc_os)
            if operation == "combine":
                combinations = TargetTaggerCollection()

                any_comb = combination_steps(tc_any, combination_name="Combination", apply_calib=True)
                if any_comb is not None:
                    combinations.add_taggers(any_comb)
                ss_comb = combination_steps(tc_ss,  combination_name="SS_Combination", apply_calib=True)
                if ss_comb is not None:
                    combinations.add_taggers(ss_comb)
                os_comb = combination_steps(tc_os,  combination_name="OS_Combination", apply_calib=True)
                if os_comb is not None:
                    combinations.add_taggers(os_comb)

                print_tagger_statistics(combinations, calibrated=False, selected=False)
                write_branches(output_rootfile, combinations, calibrated=False, append=True)
                combinations.load_calibrations(args.input_cal)
                combinations.apply()  # Apply directly
                print_tagger_statistics(combinations, calibrated=True, selected=False)
                write_branches(output_rootfile, combinations, calibrated=True, append=True)
    else:
        # Execute calibration and combination steps
        combinations = None
        for i, operation in enumerate(args.op):
            if operation == "calibrate":
                if combinations is not None:
                    # Calibrate all the combinations individually
                    calibration_steps(combinations, write_uncalib_branches=False)
                else:
                    calibration_steps(tc_any, write_uncalib_branches=True)
                    calibration_steps(tc_ss, write_uncalib_branches=True)
                    calibration_steps(tc_os, write_uncalib_branches=True)
            if operation == "combine":
                combinations = TaggerCollection()

                any_comb = combination_steps(tc_any, combination_name="Combination", apply_calib=False)
                if any_comb is not None:
                    combinations.add_taggers(any_comb)
                    tc_any.destroy()  # Free memory
                ss_comb  = combination_steps(tc_ss,  combination_name="SS_Combination", apply_calib=False)
                if ss_comb is not None:
                    combinations.add_taggers(ss_comb)
                    tc_ss.destroy()
                os_comb  = combination_steps(tc_os,  combination_name="OS_Combination", apply_calib=False)
                if os_comb is not None:
                    combinations.add_taggers(os_comb)
                    tc_os.destroy()

                if len(combinations) > 0:
                    print_tagger_statistics(combinations, calibrated=False, selected=False)
                    write_branches(output_rootfile, combinations, calibrated=False, append=True, write_extra_branches=False)

    output_rootfile.write()


if __name__ == "__main__":
    main()
