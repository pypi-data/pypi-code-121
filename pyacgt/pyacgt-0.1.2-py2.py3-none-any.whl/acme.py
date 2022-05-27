import subprocess as sub
from typing import List, Tuple, Union, Text, Any
from .util import cmd_exists, Words
import sys, os, platform

# from typing_extensions import typing as T
# import typing_extensions as TE

__all__ = ["makeACMEInput", "runACMEinput"]
if platform.system() == "Windows":
    __ACME_EXTENSION__ = "_win.exe"
elif platform.system() == "Linux":
    __ACME_EXTENSION__ = "_linux"
elif platform.system() == "Darwin":
    __ACME_EXTENSION__ = "_osx"
__ACME_EXE__ = os.path.join(sys.prefix, "bin/acme" + __ACME_EXTENSION__)
# sep=os.linesep


def __dir__() -> List[Text]:
    return __all__


def __getattr__(name: str) -> Any:
    if name not in __all__:
        raise AttributeError(name)
    return globals()[name]


def makeACMEinput(
    gens: List[str],
    relators: List[str],
    *,  # After this is keyword-only arguments.
    prog: str = "Prog8",
    equiv: bool = False,
    stat: bool = False,
    asIs: bool = True,
    param: bool = True,
    mess: int = 0,
    cullMode: int = 2,
    clen: int = 0,
    dumpMode: int = 1,
    dlen: int = 0,
    termMode: int = 1,
    tlen: int = 0,
    headerText: Union[str, List[str]] = "",
    footerText: Union[str, List[str]] = "",
) -> str:
    """
    Generates ACME input string for G = <gens|relators>.

    Parameters
    ----------
    gens : List[str]
        generators for the group you want to test.
    relators: List[str]
        relators in `gens` for the group under test
    prog: str
        what program from ACME to run. Valid options are `prog8`, `plan9`, `rev10`, `temp11`, `duodec`,
    equiv: bool
        if equiv is true, then all equivalent presentations due to relator cycling and inversion are added as root nodes to the search tree before any AC-moves are made. Default:False
    stat: bool
        If stat is true, printout details of the tree as they're processed. Default: False
    param: bool
        Dump parameters to output. Default: True
    asIs: bool
        before any commands run, the presentation is passed through a "massaging routine", if asIs is false, then we freely and cyclically reduce the presentation and sort the relators by shortlex. Default:True
    mess: int
        set the interval between progress messages. Setting this to zero turns off progress messages. Default: 0.
    cullMode: int
        See ACME documentation.
    clen: int
        ACME documentation.
    dumpMode: int
        See ACME documentation.
    dlen: int
        See ACME documentation.
    termMode: int
        See ACME documentation.
    tlen: int
        See ACME documentation.
    headerText: Union[str,List[str]]
        Add one or more note(s) before the output of the program. Useful for logging parameters.
    footerText: Union[str,List[str]]
        Add one or more note(s) after the output of the program. Useful for logging parameters.

    Return
    ------
    str
        `ACME` input code for G = <gens|relators>
    """
    try:
        assert prog.lower() in {"prog8", "plan9", "rev10", "temp11", "duodec"}
    except AssertionError as e:
        e.args = tuple(
            list(e.args)
            + ["Program must be one of 'prog8', 'plan9', 'rev10', 'temp11', 'duodec'"]
        )
        raise
    lines = []
    lines.append(f'Gr: {", ".join(gens)};')
    lines.append(f'Rel: {", ".join(relators)};')
    lines.append("Mess: 1;" if mess else "Mess: 0;")
    lines.append("Stat: 1;" if stat else "Stat: 0;")
    lines.append("Equiv: 1;" if equiv else "Equiv: 0;")
    lines.append("AsIs: 1;" if asIs else "AsIs: 0;")
    lines.append(f"Cull: {cullMode},{clen};" if cullMode != 0 else f"Cull: {cullMode};")
    lines.append(f"Term: {termMode},{tlen};" if termMode == 2 else f"Term: {termMode};")
    lines.append(f"Dump: {dumpMode},{dlen};" if dumpMode == 2 else f"Dump: {dumpMode};")
    lines.append("Text: ;")
    if type(headerText) == list and len(headerText) > 0:
        lines += [f"Text: {line};" for line in headerText]
    elif type(headerText) == str:
        lines.append(f"Text: {headerText};")
    lines.append("Param: 1;" if param else "Param: 0;")
    lines.append("Text: ;")
    lines.append(f"{prog};")
    lines.append("Text: ;")
    if type(footerText) == list and len(footerText) > 0:
        lines += [f"Text: {line};" for line in footerText]
    elif type(footerText) == str:
        lines.append(f"Text: {footerText};")
    lines.append("Bye;")
    return os.linesep.join(lines)


def runACMEinput(
    template: str, returnAll: bool = False
) -> Union[Tuple[sub.Popen[bytes], Tuple[bytes, bytes], str], str]:
    """
    Runs acme on `template`

    Parameters
    ----------
    template : str
        acme code template (input string) for some group under test.
    returnAll: bool
        whether or not to return all variables (with `returnAll==True`) or just the output (`returnAll==False`, this is the default behavior)

    Return
    ------
    Union[Tuple[sub.Popen, Tuple[bytes], str],str]
        Either a tuple (sub.Popen, Tuple[bytes], str) or a single str.
    """
    try:
        assert cmd_exists(__ACME_EXE__)
    except AssertionError as e:
        e.args = tuple(list(e.args) + ["Could not find ACME on system path."])
        raise
    acme = sub.Popen(__ACME_EXE__, stdout=sub.PIPE, stdin=sub.PIPE, stderr=sub.STDOUT)
    stdout = acme.communicate(input=str.encode(template, "utf-8"))
    output = stdout[0].decode()
    if returnAll:
        return acme, stdout, output
    else:
        return output
