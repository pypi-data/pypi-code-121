"""Module for working with datasets."""

from __future__ import annotations

# stdlib
from enum import Enum
from pathlib import PosixPath
import logging
import os
import re
from typing import Union, Set, Dict, Iterable, List, Optional

# external
import formulate
import uproot
from uproot.reading import ReadOnlyDirectory
from uproot.behaviors.TTree import TTree

# tdub
import tdub.config

log = logging.getLogger(__name__)

DataSource = Union[
    str, Iterable[str], os.PathLike, Iterable[os.PathLike], ReadOnlyDirectory, TTree
]


class Region(Enum):
    """A simple enum class for easily using region information.

    Attributes
    ----------
    r1j1b
        Label for our `1j1b` region.
    r2j1b
        Label for our `2j1b` region.
    r2j2b
        Label for our `2j2b` region.

    Examples
    --------
    Using this enum for grabing the ``2j2b`` region from a set of
    files:

    >>> from tdub.data import Region, selection_for
    >>> from tdub.frames import iterative_selection
    >>> df = iterative_selection(files, selection_for(Region.r2j2b))

    """

    r1j1b = 0
    r2j1b = 1
    r2j2b = 2
    rUnkn = 9

    @staticmethod
    def from_str(s: str) -> Region:
        """Get enum value for the given string.

        This function supports three ways to define a region; prefixed
        with "r", prefixed with "reg", or no prefix at all. For
        example, ``Region.r2j2b`` can be retrieved like so:

        - ``Region.from_str("r2j2b")``
        - ``Region.from_str("reg2j2b")``
        - ``Region.from_str("2j2b")``

        Parameters
        ----------
        s : str
            String representation of the desired region

        Returns
        -------
        Region
            Enum version

        Examples
        --------
        >>> from tdub.data import Region
        >>> Region.from_str("1j1b")
        <Region.r1j1b: 0>

        """
        if s.startswith("reg"):
            rsuff = s.split("reg")[-1]
            return Region.from_str(rsuff)
        elif s.startswith("r"):
            return Region[s]
        else:
            if s == "2j2b":
                return Region.r2j2b
            elif s == "2j1b":
                return Region.r2j1b
            elif s == "1j1b":
                return Region.r1j1b
            else:
                raise ValueError(f"{s} doesn't correspond to a Region")

    def __str__(self) -> str:
        """Convert to string, removing prefix 'r'."""
        return self.name[1:]


def as_region(region: str | Region) -> Region:
    """Convert input to :py:obj:`~Region`.

    Meant to be similar to :py:func:`numpy.asarray` function.

    Parameters
    ----------
    region : str or Region
        Region already as a Region or as a str

    Returns
    -------
    Region
        Region representation.

    Examples
    --------
    >>> from tdub.data import as_region, Region
    >>> as_region("r2j1b")
    <Region.r2j1b: 1>
    >>> as_region(Region.r2j2b)
    <Region.r2j2b: 2>

    """
    if isinstance(region, str):
        return Region.from_str(region)
    return region


class SampleInfo:
    """Describes a sample's attritubes given it's name.

    Parameters
    ----------
    input_file : str
        File stem containing the necessary groups to parse.

    Attributes
    ----------
    phy_process : str
        Physics process (e.g. ttbar or tW_DR or Zjets)
    dsid : int
        Dataset ID
    sim_type : str
        Simulation type, "FS" or "AFII"
    campaign : str
        Campaign, MC16{a,d,e}
    tree : str
        Original tree (e.g. "nominal" or "EG_SCALE_ALL__1up")

    Examples
    --------
    >>> from tdub.data import SampleInfo
    >>> sampinfo = SampleInfo("ttbar_410472_AFII_MC16d_nominal.root")
    >>> sampinfo.phy_process
    ttbar
    >>> sampinfo.dsid
    410472
    >>> sampinfo.sim_type
    AFII
    >>> sampinfo.campaign
    MC16d
    >>> sampinfo.tree
    nominal

    """

    _parse: re.Pattern = re.compile(
        r"""(?P<phy_process>\w+)_
        (?P<dsid>[0-9]{6})_
        (?P<sim_type>(FS|AFII))_
        (?P<campaign>MC16(a|d|e))_
        (?P<tree>\w+)
        (\.\w+|$)""",
        re.X,
    )

    def __init__(self, input_file: str) -> None:
        """Class constructor."""
        if "Data_Data" in input_file:
            self.phy_process = "Data"
            self.dsid = 0
            self.sim_type = "Data"
            self.campaign = "Data"
            self.tree = "nominal"
        else:
            m: re.Match | None = SampleInfo._parse.match(input_file)
            if not m:
                raise ValueError(f"{input_file} cannot be parsed by SampleInfo regex")
            self.phy_process = m.group("phy_process")
            if self.phy_process.startswith("MCNP"):
                self.phy_process = "MCNP"
            self.dsid = int(m.group("dsid"))
            self.sim_type = m.group("sim_type")
            self.campaign = m.group("campaign")
            self.tree = m.group("tree")


def avoids_for(region: str | Region) -> list[str]:
    """Get the features to avoid for the given region.

    See the :py:mod:`tdub.config` module for definition of the
    variables to avoid (and how to modify them).

    Parameters
    ----------
    region : str or tdub.data.Region
        Region to get the associated avoided branches.

    Returns
    -------
    list(str)
        Features to avoid for the region.

    Examples
    --------
    >>> from tdub.data import avoids_for, Region
    >>> avoids_for(Region.r2j1b)
    ['HT_jet1jet2', 'deltaR_lep1lep2_jet1jet2met', 'mass_lep2jet1', 'pT_jet2']
    >>> avoids_for("2j2b")
    ['deltaR_jet1_jet2']

    """
    region = as_region(region)
    if region == Region.r1j1b:
        return tdub.config.AVOID_IN_CLF_1j1b
    elif region == Region.r2j1b:
        return tdub.config.AVOID_IN_CLF_2j1b
    elif region == Region.r2j2b:
        return tdub.config.AVOID_IN_CLF_2j2b
    else:
        raise ValueError(f"Incompatible region: {region}")


def branches_from(
    source: DataSource,
    tree: str = "WtLoop_nominal",
    ignore_weights: bool = False,
) -> list[str]:
    """Get a list of branches from a data source.

    If the `source` is a list of files, the first file is the only
    file that is parsed.

    Parameters
    ----------
    source : str, list(str), os.PathLike, list(os.PathLike), or uproot File/Tree
        What to parse to get the branch information.
    tree : str
        Name of the tree to get branches from
    ignore_weights : bool
        Flag to ignore all branches starting with `weight_`.

    Returns
    -------
    list(str)
        Branches from the source.

    Raises
    ------
    TypeError
        If `source` can't be used to find a list of branches.

    Examples
    --------
    >>> from tdub.data import branches_from
    >>> branches_from("/path/to/file.root", ignore_weights=True)
    ["pT_lep1", "pT_lep2"]
    >>> branches_from("/path/to/file.root")
    ["pT_lep1", "pT_lep2", "weight_nominal", "weight_tptrw"]

    """
    if isinstance(source, (str, PosixPath)):
        t = uproot.open(source).get(tree)
    elif isinstance(source, list):
        t = uproot.open(source[0]).get(tree)
    elif isinstance(source, uproot.reading.ReadOnlyDirectory):
        t = source.get(tree)
    elif isinstance(source, uproot.behaviors.TTree.TTree):
        t = source
    else:
        raise TypeError("Cannot use source (it is type %s)" % str(type(source)))
    branches = t.keys()

    if ignore_weights:
        weights = set(filter(re.compile(r"(weight_\w+)").match, branches))
        branches = set(branches) ^ weights

    return list(sorted(branches, key=str.lower))


def categorize_branches(source: list[str]) -> dict[str, list[str]]:
    """Categorize branches into a separated lists.

    The categories:

    - `kinematics`: for kinematic features (used for classifiers)
    - `weights`: for any branch that starts or ends with ``weight``
    - `meta`: for meta information (final state information)

    Parameters
    ----------
    source : list(str)
        Complete list of branches to be categorized.

    Returns
    -------
    dict(str, list(str))
        Dictionary connecting categories to their associated list of
        branchess.

    Examples
    --------
    >>> from tdub.data import categorize_branches, branches_from
    >>> branches = ["pT_lep1", "pT_lep2", "weight_nominal", "weight_sys_jvt", "reg2j2b"]
    >>> cated = categorize_branches(branches)
    >>> cated["weights"]
    ['weight_sys_jvt', 'weight_nominal']
    >>> cated["meta"]
    ['reg2j2b']
    >>> cated["kinematics"]
    ['pT_lep1', 'pT_lep2']

    Using a ROOT file:

    >>> root_file = PosixPath("/path/to/file.root")
    >>> cated = categorize_branches(branches_from(root_file))

    """
    metas = {
        "reg1j1b",
        "reg2j1b",
        "reg2j2b",
        "reg1j0b",
        "reg2j0b",
        "isMC16a",
        "isMC16d",
        "isMC16e",
        "OS",
        "SS",
        "elmu",
        "elel",
        "mumu",
        "charge_lep1",
        "charge_lep2",
        "pdgId_lep1",
        "pdgId_lep2",
        "runNumber",
        "randomRunNumber",
        "eventNumber",
    }
    bset = set(source)
    weight_re = re.compile(r"(^weight_\w+)|(\w+_weight$)")
    weights = set(filter(weight_re.match, bset))
    metas = metas & set(bset)
    kinematics = (set(bset) ^ weights) ^ metas
    return {
        "kinematics": sorted(kinematics, key=str.lower),
        "weights": sorted(weights, key=str.lower),
        "meta": sorted(metas, key=str.lower),
    }


def features_for(region: str | Region) -> list[str]:
    """Get the feature list for a region.

    See the :py:mod:`tdub.config` module for the definitions of the
    feature lists (and how to modify them).

    Parameters
    ----------
    region : str or tdub.data.Region
        Region as a string or enum entry. Using ``"ALL"`` returns a
        list of unique features from all regions.

    Returns
    -------
    list(str)
        Features for that region (or all regions).

    Examples
    --------
    >>> from pprint import pprint
    >>> from tdub.data import features_for
    >>> pprint(features_for("reg2j1b"))
    ['mass_lep1jet1',
     'mass_lep1jet2',
     'mass_lep2jet1',
     'mass_lep2jet2',
     'pT_jet2',
     'pTsys_lep1lep2jet1jet2met',
     'psuedoContTagBin_jet1',
     'psuedoContTagBin_jet2']

    """
    # first allow retrieval of all features
    if region == "ALL":
        return sorted(
            set(tdub.config.FEATURESET_1j1b)
            | set(tdub.config.FEATURESET_2j1b)
            | set(tdub.config.FEATURESET_2j2b),
            key=str.lower,
        )

    region = as_region(region)
    if region == Region.r1j1b:
        return tdub.config.FEATURESET_1j1b
    if region == Region.r2j1b:
        return tdub.config.FEATURESET_2j1b
    if region == Region.r2j2b:
        return tdub.config.FEATURESET_2j2b
    else:
        raise ValueError(f"Incompatible region: {region}")


def quick_files(
    datapath: str | os.PathLike,
    campaign: str | None = None,
    tree: str = "nominal",
) -> dict[str, list[str]]:
    """Get a dictionary connecting sample processes to file lists.

    The lists of files are sorted alphabetically. These types of
    samples are currently tested:

    - `tW_DR` (410648, 410649 full sim)
    - `tW_DR_AFII` (410648, 410649 fast sim)
    - `tW_DR_PS` (411038, 411039 fast sim)
    - `tW_DR_inc` (410646, 410647 full sim)
    - `tW_DR_inc_AFII` (410646, 410647 fast sim)
    - `tW_DS` (410656, 410657 full sim)
    - `tW_DS_inc` (410654, 410655 ful sim)
    - `ttbar` (410472 full sim)
    - `ttbar_AFII` (410472 fast sim)
    - `ttbar_PS` (410558 fast sim)
    - `ttbar_PS713` (411234 fast sim)
    - `ttbar_hdamp` (410482 fast sim)
    - `ttbar_inc` (410470 full sim)
    - `ttbar_inc_AFII` (410470 fast sim)
    - `Diboson`
    - `Zjets`
    - `MCNP`
    - `Data`

    Parameters
    ----------
    datapath : str or os.PathLike
        Path where all of the ROOT files live.
    campaign : str, optional
        Enforce a single campaign ("MC16a", "MC16d", or "MC16e").
    tree : str
        Upstream AnalysisTop ntuple tree.

    Returns
    -------
    dict(str, list(str))
        The dictionary of processes and their associated files.

    Examples
    --------
    >>> from pprint import pprint
    >>> from tdub.data import quick_files
    >>> qf = quick_files("/path/to/some_files") ## has 410472 ttbar samples
    >>> pprint(qf["ttbar"])
    ['/path/to/some/files/ttbar_410472_FS_MC16a_nominal.root',
     '/path/to/some/files/ttbar_410472_FS_MC16d_nominal.root',
     '/path/to/some/files/ttbar_410472_FS_MC16e_nominal.root']
    >>> qf = quick_files("/path/to/some/files", campaign="MC16d")
    >>> pprint(qf["tW_DR"])
    ['/path/to/some/files/tW_DR_410648_FS_MC16d_nominal.root',
     '/path/to/some/files/tW_DR_410649_FS_MC16d_nominal.root']
    >>> qf = quick_files("/path/to/some/files", campaign="MC16a")
    >>> pprint(qf["Data"])
    ['/path/to/some/files/Data15_data15_Data_Data_nominal.root',
     '/path/to/some/files/Data16_data16_Data_Data_nominal.root']

    """
    if campaign is None:
        camp = ""
    else:
        if campaign not in ("MC16a", "MC16d", "MC16e"):
            raise ValueError(f"{campaign} but be either 'MC16a', 'MC16d', or 'MC16e'")
        camp = f"_{campaign}"

    path = str(PosixPath(datapath).resolve())
    files = os.listdir(path)

    patterns = {
        "tW_DR": f"tW_DR_41064(8|9)_FS_MC16(a|d|e)_{tree}.root$",
        "tW_DR_AFII": f"tW_DR_41064(8|9)_AFII_MC16(a|d|e)_{tree}.root$",
        "tW_DR_PS": f"tW_DR_41103(8|9)_AFII_MC16(a|d|e)_{tree}.root$",
        "tW_DR_inc": f"tW_DR_41064(6|7)_FS_MC16(a|d|e)_{tree}.root$",
        "tW_DR_inc_AFII": f"tW_DR_41064(6|7)_AFII_MC16(a|d|e)_{tree}.root$",
        "tW_DS": f"tW_DS_41065(6|7)_FS_MC16(a|d|e)_{tree}.root$",
        "tW_DS_inc": f"tW_DS_41065(4|5)_FS_MC16(a|d|e)_{tree}.root$",
        "ttbar": f"ttbar_410472_FS_MC16(a|d|e)_{tree}.root$",
        "ttbar_AFII": f"ttbar_410472_AFII_MC16(a|d|e)_{tree}.root$",
        "ttbar_PS": f"ttbar_410558_AFII_MC16(a|d|e)_{tree}.root$",
        "ttbar_PS713": f"ttbar_411234_AFII_MC16(a|d|e)_{tree}.root$",
        "ttbar_hdamp": f"ttbar_410482_AFII_MC16(a|d|e)_{tree}.root$",
        "ttbar_inc": f"ttbar_410470_FS_MC16(a|d|e)_{tree}.root$",
        "ttbar_inc_AFII": f"ttbar_410470_AFII_MC16(a|d|e)_{tree}.root$",
        "Diboson": f"Diboson_[0-9]{{6}}_FS_MC16(a|d|e)_{tree}.root$",
        "Zjets": f"Zjets_[0-9]{{6}}_FS_MC16(a|d|e)_{tree}.root$",
        "MCNP": f"MCNP_[0-9]{{6}}_FS_MC16(a|d|e)_{tree}.root$",
    }

    if campaign == "MC16a":
        patterns["Data"] = f"Data1(5|6)_data1(5|6)_Data_Data_{tree}.root$"
    elif campaign == "MC16d":
        patterns["Data"] = f"Data17_data17_Data_Data_{tree}.root$"
    elif campaign == "MC16e":
        patterns["Data"] = f"Data18_data18_Data_Data_{tree}.root$"
    else:
        patterns["Data"] = f"Data1(5|6|7|8)_data1(5|6|7|8)_Data_Data_{tree}.root$"

    patterns = {k: re.compile(v) for k, v in patterns.items()}
    file_lists = {}
    for k, p in patterns.items():
        file_lists[k] = [f"{path}/{entry}" for entry in sorted(filter(p.match, files))]

    if campaign is not None:
        for k, v in file_lists.items():
            if k == "Data":
                continue
            file_lists[k] = sorted(filter(lambda x: camp in PosixPath(x).name, v))

    return file_lists


def selection_as_numexpr(selection: str) -> str:
    """Get the numexpr selection string from an arbitrary selection.

    Parameters
    -----------
    selection : str
        Selection string in ROOT or numexpr

    Returns
    -------
    str
        Selection in numexpr format.

    Examples
    --------
    >>> selection = "reg1j1b == true && OS == true && mass_lep1jet1 < 155"
    >>> from tdub.data import selection_as_numexpr
    >>> selection_as_numexpr(selection)
    '(reg1j1b == True) & (OS == True) & (mass_lep1jet1 < 155)'

    """
    return formulate.from_auto(selection).to_numexpr()


def selection_as_root(selection: str) -> str:
    """Get the ROOT selection string from an arbitrary selection.

    Parameters
    -----------
    selection : str
        The selection string in ROOT or numexpr

    Returns
    -------
    str
        The same selection in ROOT format.

    Examples
    --------
    >>> selection = "(reg1j1b == True) & (OS == True) & (mass_lep1jet1 < 155)"
    >>> from tdub.data import selection_as_root
    >>> selection_as_root(selection)
    '(reg1j1b == true) && (OS == true) && (mass_lep1jet1 < 155)'

    """
    return formulate.from_auto(selection).to_root()


def selection_branches(selection: str) -> set[str]:
    """Construct the minimal set of branches required for a selection.

    Parameters
    -----------
    selection : str
        Selection string in ROOT or numexpr

    Returns
    -------
    set(str)
        Necessary branches/variables

    Examples
    --------
    >>> from tdub.data import minimal_selection_branches
    >>> selection = "(reg1j1b == True) & (OS == True) & (mass_lep1lep2 > 100)"
    >>> minimal_branches(selection)
    {'OS', 'mass_lep1lep2', 'reg1j1b'}
    >>> selection = "reg2j1b == true && OS == true && (mass_lep1jet1 < 155)"
    >>> minimal_branches(selection)
    {'OS', 'mass_lep1jet1', 'reg2j1b'}

    """
    return formulate.from_auto(selection).variables


def selection_for(region: str | Region, additional: str | None = None) -> str:
    """Get the selection for a given region.

    We have three regions with a default selection (`1j1b`, `2j1b`,
    and `2j2b`), these are the possible argument options (in str or
    Enum form). See the :py:mod:`tdub.config` module for the
    definitions of the selections (and how to modify them).

    Parameters
    ----------
    region : str or Region
        Region to get the selection for
    additional : str, optional
        Additional selection (in ROOT or numexpr form). This will
        connect the region specific selection using `and`.

    Returns
    -------
    str
        Selection string in numexpr format.

    Examples
    --------
    >>> from tdub.data import Region, selection_for
    >>> selection_for(Region.r2j1b)
    '(reg2j1b == True) & (OS == True)'
    >>> selection_for("reg1j1b")
    '(reg1j1b == True) & (OS == True)'
    >>> selection_for("2j2b")
    '(reg2j2b == True) & (OS == True)'
    >>> selection_for("2j2b", additional="minimaxmbl < 155")
    '((reg2j2b == True) & (OS == True)) & (minimaxmbl < 155)'
    >>> selection_for("2j1b", additional="mass_lep1jetb < 155 && mass_lep2jetb < 155")
    '((reg1j1b == True) & (OS == True)) & ((mass_lep1jetb < 155) & (mass_lep2jetb < 155))'

    """
    region = as_region(region)
    if region == Region.r1j1b:
        selection = "(reg1j1b == True) & (OS == True)"
    elif region == Region.r2j1b:
        selection = "(reg2j1b == True) & (OS == True)"
    elif region == Region.r2j2b:
        selection = "(reg2j2b == True) & (OS == True)"
    else:
        raise ValueError("Incompatible region used")

    if additional is not None:
        additional = selection_as_numexpr(additional)
        selection = f"({selection}) & ({additional})"

    return selection
