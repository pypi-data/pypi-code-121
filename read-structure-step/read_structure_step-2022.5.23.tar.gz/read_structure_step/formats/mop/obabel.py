"""
Implementation of the reader for XYZ files using OpenBabel
"""

import logging
from pathlib import Path
import re
import shutil
import string
import subprocess

from openbabel import openbabel
from read_structure_step.formats.registries import register_reader
import seamm
from .find_mopac import find_mopac

if "OpenBabel_version" not in globals():
    OpenBabel_version = None

logger = logging.getLogger("read_structure_step.read_structure")

metadata = {
    "CP": "constant pressure heat capacity",
    "CPR": "reference.constant pressure heat capacity",
    "D": "dipole moment",
    "DR": "reference.dipole moment",
    "H": "enthalpy of formation",
    "HR": "reference.enthalpy of formation",
    "S": "entropy",
    "SR": "reference.entropy",
    "I": "ionization energy",
    "IE": "ionization energy",
    "IA": "ionization energy",
    "IR": "reference.ionization energy",
    "GR": "reference.geometry",
}
multiplicities = {
    "SINGLET": 1,
    "DOUBLET": 2,
    "TRIPLET": 3,
    "QUARTET": 4,
    "QUINTET": 5,
    "SEXTET": 6,
    "SEPTET": 7,
    "OCTET": 8,
    "NONET": 9,
}


def _find_charge(regex, input_file):
    text = re.search(regex, input_file)
    if text is not None:
        return text.group(2)


def _find_standard(regex, input_file):
    text = re.search(regex, input_file)
    if text is not None:
        return text.group(0)


def _find_field(regex, input_file):
    text = re.search(regex, input_file)
    if text is not None:
        return (text.group(1), text.group(4), text.group(7))


def _find_open(regex, input_file):
    text = re.search(regex, input_file)
    if text is not None:
        return (text.group(2), text.group(3))


extras = {
    "structure": {
        "net_charge": {
            "regex": r"(CHARGE=)([\+\-]?\d)",
            "find": _find_charge,
            "value": None,
        },
        "field": {
            "regex": (
                r"FIELD=\(([-+]?\d+(\.\d+(e[-+]\d+)?)?)\,([-+]?\d+"
                r"(\.\d+(e[-+]\d+)?)?)\,([-+]?\d+(\.\d+(e[-+]\d+)?"
                r")?)\)"
            ),
            "find": _find_field,
            "value": None,
        },
        "open": {
            "regex": r"(OPEN\()(\d+)\,\s*(\d+)\)",
            "find": _find_open,
            "value": None,
        },
    },
}

obabel_error_identifiers = ["0 molecules converted"]


@register_reader(".mop")
def load_mop(
    file_name,
    configuration,
    extension=".mop",
    add_hydrogens=True,
    system_db=None,
    system=None,
    indices="1:end",
    subsequent_as_configurations=False,
    system_name="Canonical SMILES",
    configuration_name="sequential",
    printer=None,
    references=None,
    bibliography=None,
    save_data=True,
    **kwargs,
):
    """Read a MOPAC input file.

    Parameters
    ----------
    file_name : str or Path
        The path to the file, as either a string or Path.

    configuration : molsystem.Configuration
        The configuration to put the imported structure into.

    We'll use OpenBabel to read the file; however, OpenBabel is somewhat limited, so
    we'll first preprocess the file to extract extra data and also to fit it to the
    format that OpenBabel can handle.
    """
    global OpenBabel_version

    # Get the text in the file
    if isinstance(file_name, str):
        path = Path(file_name)
    else:
        path = file_name
    path.expanduser().resolve()
    lines = iter(path.read_text().splitlines())

    # Work through the file capturing data and also reformatting as needed.
    text = []
    # The file may have comments at the beginning or interspersed. The first non-comment
    # line is keywords, followed by two lines of description. Conventionally the first
    # line of description is a title.
    #
    # The keyword line may be extended in one of two ways. If there is an '&' keyword
    # in the first line of keywords, the second line contains keywords rather than
    # description. If that second line contains an '&', then the third line is also
    # taken as keywords, leaving no description lines.
    #
    # If the keyword line contains a '+' keyword, the next line is also considered to be
    # keywords, but in this case the number of description lines following the keyword
    # lines is unchanged.
    #
    # Finally, the MOPAC test data usually has three comment lines to start, with a
    # single number on the second line, which is the heat of formation calculated by
    # MOPAC. If this format is found the HOF is captured.
    run_mopac = False
    keywords = []
    description_lines = []
    energy = None
    geometry_lines = []
    raw_geometry_lines = []
    line_no = 0
    comment_lines = 0
    n_description_lines = 2
    section = "keywords"
    for line in lines:
        line_no += 1
        line = line.strip()
        if len(line) > 0 and line[0] == "*":
            comment_lines += 1
            if line_no == 2 and comment_lines == 2 and len(line.split()) == 2:
                try:
                    tmp_energy = float(line.split()[1])
                except ValueError:
                    pass
                else:
                    energy = tmp_energy
        else:
            if section == "keywords":
                tmp = line.split()
                keywords.extend(tmp)
                if "&" in tmp:
                    n_description_lines -= 1
                elif "+" in tmp:
                    pass
                else:
                    if n_description_lines > 0:
                        section = "description"
                    else:
                        section = "geometry"
            elif section == "description":
                description_lines.append(line)
                n_description_lines -= 1
                if n_description_lines == 0:
                    section = "geometry"
            elif section == "geometry":
                if line == "":
                    break
                raw_geometry_lines.append(line)
                # The element may have () after...
                line = re.sub(r"\(.*\)", "", line)
                # Look for dummy atoms
                if line.split()[0] in ("X", "XX", "99"):
                    run_mopac = True
                geometry_lines.append(line)

    # Sort out if the geometry looks like internals. Note that there may be a charge at
    # the end of each line.
    n_atoms = len(geometry_lines)
    # Need to know if the first atoms coordinates are zero ... which are the default
    # for missing values. Anyway, put default values into first line, treating as
    # Cartesians for time being.
    x0 = y0 = z0 = 0.0
    tmp = geometry_lines[0].split()
    el0 = tmp[0]
    if len(tmp) >= 6:
        z0 = float(tmp[5])
    if len(tmp) >= 4:
        y0 = float(tmp[3])
    if len(tmp) >= 2:
        x0 = float(tmp[1])
    geometry_lines[0] = f"{el0} {x0} 0 {y0} 0 {z0} 0"

    if n_atoms == 1:
        internals = False
    elif n_atoms > 2:
        internals = None
        for index, line in enumerate(geometry_lines[2:], 2):
            tmp = line.split()
            if len(tmp) > 7:
                if len(tmp) >= 9:
                    if index == 2:
                        if "0" in tmp[7:9]:
                            geometry_lines[index] = " ".join(tmp[0:7])
                    elif "0" in tmp[7:10]:
                        geometry_lines[index] = " ".join(tmp[0:7])
                    else:
                        internals = True
            else:
                if internals is None:
                    internals = False
        if internals is None:
            internals = True
    else:
        tmp = geometry_lines[1].split()
        if len(tmp) > 7:
            if tmp[7] == 1 or tmp[7] == 0:
                internals = True
            else:
                internals = False
        else:
            internals = False

    if n_atoms > 1:
        tmp = geometry_lines[1].split()
        x = y = z = 0.0
        el1 = tmp[0]
        if len(tmp) >= 6:
            z = float(tmp[5])
        if len(tmp) >= 4:
            y = float(tmp[3])
        if len(tmp) >= 2:
            x = float(tmp[1])
        if internals:
            geometry_lines[1] = f"{el1} {x} 1 {y} 0 {z} 0  1 0 0"
        else:
            geometry_lines[1] = f"{el1} {x} 1 {y} 0 {z} 0"

    if internals:
        # Add connectivity to first atom since OpenBabel requires
        geometry_lines[0] += "  0 0 0"
    else:
        # In Cartesians, OpenBabel requires 7 items per line
        for i in range(len(geometry_lines)):
            tmp = geometry_lines[i].split()
            el = tmp[0]
            x = y = z = 0.0
            if len(tmp) >= 6:
                z = float(tmp[5])
            if len(tmp) >= 4:
                y = float(tmp[3])
            if len(tmp) >= 2:
                x = float(tmp[1])
            geometry_lines[i] = f"{el} {x} 1 {y} 0 {z} 0"

    # Reassemble an input file.
    text = ["0SCF", "title", "description"]
    text.extend(geometry_lines)
    # An empty line denotes end of input, but OpenBabel requires a blank in the line
    text.append(" ")

    if internals:
        logger.info(f"Using internal coordinates for {file_name}")
    else:
        logger.info(f"Using Cartesians coordinates for {file_name}")

    input_data = "\n".join(text)
    logger.info(f"Input data:\n\n{input_data}\n")

    # Now try to convert using OpenBabel
    obConversion = openbabel.OBConversion()
    if internals:
        obConversion.SetInFormat("mopin")
    else:
        obConversion.SetInFormat("mopcrt")

    obMol = openbabel.OBMol()
    try:
        if run_mopac:
            raise RuntimeError("Forcing use of MOPAC output")
        success = obConversion.ReadString(obMol, input_data)
        if not success:
            raise RuntimeError("obConversion failed")
    except Exception:
        logger.info("**** falling back to MOPAC")
        # Try using a MOPAC output file instead. Works for e.g. mixed coordinates
        mopac_exe = find_mopac()
        if mopac_exe is None:
            raise FileNotFoundError("The MOPAC executable could not be found")

        # Create an input file
        text = ["0SCF", "title", "description"]
        text.extend(raw_geometry_lines)
        # An empty line denotes end of input
        text.append(" ")
        files = {"mopac.dat": "\n".join(text)}

        logger.debug(f"MOPAC input file:\n\n{files['mopac.dat']}\n")

        local = seamm.ExecLocal()
        result = local.run(
            cmd=[mopac_exe, "mopac.dat"], files=files, return_files=["mopac.out"]
        )

        if result["mopac.out"]["data"] is None:
            raise RuntimeError("MOPAC failed: " + result["mopac.out"]["exception"])

        text = result["mopac.out"]["data"]

        logger.debug(f"MOPAC output:\n\n{text}\n")

        obConversion.SetInFormat("mopout")
        success = obConversion.ReadString(obMol, text)

        if not success:
            raise RuntimeError("Could not process MOPAC file")

    if add_hydrogens:
        obMol.AddHydrogens()
    configuration.from_OBMol(obMol)

    # Record the charge, and the spin state
    charge = 0
    for keyword in keywords:
        if "CHARGE=" in keyword:
            charge = int(float(keyword.split("=")[1].strip()))
            break
    configuration.charge = charge

    n_active_electrons = None
    n_active_orbitals = None

    multiplicity = None
    for keyword in keywords:
        if keyword in multiplicities:
            multiplicity = multiplicities[keyword]
        elif "MS=" in keyword:
            try:
                multiplicity = int(2 * float(keyword.split("=")[1].strip())) + 1
            except Exception:
                ValueError(f"Error with multiplicity: '{keyword}'")
        elif keyword == "BIRADICAL":
            multiplicity = 1
            n_active_electrons = 2
            n_active_orbitals = 2
        elif "OPEN(" in keyword or "OPEN=(" in keyword:
            tmp = keyword.split("(")[1].rstrip(")")
            n_active_electrons, n_active_orbitals = tmp.split(",")
        elif "ROOT=" in keyword:
            tmp = keyword.split("=")
            configuration.state = tmp[1]

    if multiplicity is None:
        n_electrons = sum(configuration.atoms.atomic_numbers) - charge
        if n_electrons % 2 == 0:
            multiplicity = 1
        else:
            multiplicity = 2
    configuration.spin_multiplicity = multiplicity

    if n_active_electrons is not None:
        configuration.n_active_electrons = n_active_electrons
        configuration.n_active_orbitals = n_active_orbitals

    logger.info(f"{charge=} {multiplicity=}")
    logger.info(
        f"open({n_active_electrons},{n_active_orbitals}) {configuration.state=}"
    )

    # Set the system name
    if system_name is not None and system_name != "":
        lower_name = system_name.lower()
        if "from file" in lower_name:
            system.name = str(path)
        elif lower_name == "title":
            if len(description_lines) > 0:
                system.name = description_lines[0]
            else:
                system.name = str(path)
        elif "canonical smiles" in lower_name:
            system.name = configuration.canonical_smiles
        elif "smiles" in lower_name:
            system.name = configuration.smiles
        else:
            system.name = system_name

    # And the configuration name
    if configuration_name is not None and configuration_name != "":
        lower_name = configuration_name.lower()
        if "from file" in lower_name:
            configuration.name = obMol.GetTitle()
        elif "canonical smiles" in lower_name:
            configuration.name = configuration.canonical_smiles
        elif "smiles" in lower_name:
            configuration.name = configuration.smiles
        elif lower_name == "sequential":
            configuration.name = "1"
        else:
            configuration.name = configuration_name

    if references:
        # Add the citations for Open Babel
        references.cite(
            raw=bibliography["openbabel"],
            alias="openbabel_jcinf",
            module="read_structure_step",
            level=1,
            note="The principle Open Babel citation.",
        )

        # See if we can get the version of obabel
        if OpenBabel_version is None:
            path = shutil.which("obabel")
            if path is not None:
                path = Path(path).expanduser().resolve()
                try:
                    result = subprocess.run(
                        [str(path), "--version"],
                        stdin=subprocess.DEVNULL,
                        capture_output=True,
                        text=True,
                    )
                except Exception:
                    OpenBabel_version = "unknown"
                else:
                    OpenBabel_version = "unknown"
                    lines = result.stdout.splitlines()
                    for line in lines:
                        line = line.strip()
                        tmp = line.split()
                        if len(tmp) == 9 and tmp[0] == "Open":
                            OpenBabel_version = {
                                "version": tmp[2],
                                "month": tmp[4],
                                "year": tmp[6],
                            }
                        break

        if isinstance(OpenBabel_version, dict):
            try:
                template = string.Template(bibliography["obabel"])

                citation = template.substitute(
                    month=OpenBabel_version["month"],
                    version=OpenBabel_version["version"],
                    year=OpenBabel_version["year"],
                )

                references.cite(
                    raw=citation,
                    alias="obabel-exe",
                    module="read_structure_step",
                    level=1,
                    note="The principle citation for the Open Babel executables.",
                )
            except Exception:
                pass

    # Save keywords, description and any data encoded in the file to the database
    if save_data:
        properties = configuration.properties
        if len("keywords") != 0:
            key = "MOPAC.keywords"
            properties.add(
                key, "str", description="The keywords for MOPAC", noerror=True
            )
            properties.put(key, " ".join(keywords))
        if len(description_lines) > 0:
            key = "MOPAC.description"
            properties.add(
                key,
                "str",
                description="The description in the MOPAC input",
                noerror=True,
            )
            properties.put(key, "\n".join(description_lines))
        if energy is not None:
            key = "MOPAC.reference energy"
            properties.add(
                key,
                "float",
                description="The reference energy from MOPAC",
                noerror=True,
            )
            properties.put(key, energy)

        # Handle properties encoded in the description
        if len(description_lines) == 2 and "=" in description_lines[1]:
            # Don't handle geometry lines yet.
            if "GR=" not in description_lines[1] and "gr=" not in description_lines[1]:
                for key in description_lines[1].split():
                    if "=" in key:
                        try:
                            keyword, value = key.split("=")
                            keyword = keyword.upper()
                            if keyword in ("WT", "DWT", "IWT", "HWT", "GWT", "ROOT"):
                                continue
                            if keyword not in metadata:
                                print("\n".join(description_lines))
                                print(f"Missing keyword={keyword}")
                                print()
                                continue
                            keyword = metadata[keyword]
                            if "reference" in keyword:
                                description = keyword.split(".")[1]
                                properties.add(
                                    keyword,
                                    "str",
                                    description=f"Reference for the {description}.",
                                    noerror=True,
                                )
                            properties.put(keyword, value)
                        except Exception as e:
                            print(f"{e}: {key}")

    return [configuration]
