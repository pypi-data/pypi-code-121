"""Pretty print functions for inputs and outputs."""
from collections import OrderedDict
import logging
import sys
from typing import Any, Dict, List, Tuple

import numpy

from cosapp.systems import System

logger = logging.getLogger(__name__)

# Default value use in list_inputs method to be able to tell if the caller set a value to out_stream
_DEFAULT_OUT_STREAM = object()


def list_inputs(
    system: System,
    values: bool = True,
    inwards: bool = False,
    hierarchical: bool = True,
    print_arrays: bool = False,
    itself: bool = False,
    out_stream=_DEFAULT_OUT_STREAM,
) -> List[Tuple[str, Dict[str, Any]]]:
    """
    Return and optionally log a list of input names and other optional information.

    Parameters
    ----------
    system : System
        System to be listed
    values : bool, optional
        When True, display/return input values. Default is True.
    inwards : bool, optional
        When True, display/return inwards values. Default is False.
    hierarchical : bool, optional
        When True, human readable output shows variables in hierarchical format.
    print_arrays : bool, optional
        When False, in the columnar display, just display norm of any ndarrays with size > 1.
        The norm is surrounded by vertical bars to indicate that it is a norm.
        When True, also display full values of the ndarray below the row. Format is affected
        by the values set with numpy.set_printoptions
        Default is False.
    itself : bool, optional
        When True, include own inwards, outwards and port in the list
    out_stream : file-like object
        Where to send human readable output. Default is sys.stdout.
        Set to None to suppress.

    Returns
    -------
    list
        list of input names and other optional information about those inputs
    """
    if not values and not inwards:
        logger.warning("Expect at least values or inwards to be True.")

    inputs = get_list_inputs(system, values=values, inwards=inwards, itself=itself)
    if out_stream == _DEFAULT_OUT_STREAM:
        out_stream = sys.stdout

    if out_stream:
        _write_outputs("input", inputs, hierarchical, print_arrays, out_stream)

    return inputs


def list_outputs(
    system: System,
    values: bool = True,
    local: bool = False,
    residuals: bool = False,
    hierarchical: bool = True,
    print_arrays: bool = False,
    itself: bool = False,
    out_stream=_DEFAULT_OUT_STREAM,
) -> List[Tuple[str, Dict[str, Any]]]:
    """
    Return and optionally log a list of input names and other optional information.

    Parameters
    ----------
    system : System
        System to be listed
    values : bool, optional
        When True, display/return input values. Default is True.
    local : bool, optional
        When True, display/return local values. Default is False.
    residuals : bool, optional
        When True, display/return residual values. Default is False.
    hierarchical : bool, optional
        When True, human readable output shows variables in hierarchical format.
    print_arrays : bool, optional
        When False, in the columnar display, just display norm of any ndarrays with size > 1.
        The norm is surrounded by vertical bars to indicate that it is a norm.
        When True, also display full values of the ndarray below the row. Format is affected
        by the values set with numpy.set_printoptions
        Default is False.
    itself : bool, optional
        When True, include own inwards, outwards and port in the list
    out_stream : file-like object
        Where to send human readable output. Default is sys.stdout.
        Set to None to suppress.

    Returns
    -------
    list
        list of output names and other optional information about those outputs
    """
    if not values and not local and not residuals:
        logger.warning("Expect at least values or inwards or residuals to be True.")

    outputs = get_list_outputs(
        system, values=values, local=local, residuals=residuals, itself=itself
    )
    if out_stream == _DEFAULT_OUT_STREAM:
        out_stream = sys.stdout

    if out_stream:
        _write_outputs("output", outputs, hierarchical, print_arrays, out_stream)

    return outputs


def get_list_outputs(
    system: System,
    values: bool = True,
    residuals: bool = False,
    local: bool = False,
    parent_name: str = "",
    itself: bool = False,
) -> List[Tuple[str, Dict[str, Any]]]:
    """Return and optionally log a list of input names and other optional information.

    Parameters
    ----------
    system : System
        System to be listed
    values : bool, optional
        When True, take into account input values. Default is True.
    residuals : bool, optional
        When True, take into account residual values. Default is False.
    local : bool, optional
        When True, display/return local variables. Default is False.
    parent_name : string, optional
        Where to store parent name during recursion
    itself : bool, optional
        When True, include own inwards, outwards and port in the list
    Returns
    -------
    list_out
        list of output names and other optional information about those outputs
    """
    path_name = lambda *args: parent_name + ".".join(args)

    list_out = list()
    if len(system.children) == 0 or itself:
        for name_port, port in system.outputs.items():
            outward = (name_port == System.OUTWARDS)
            if local and outward:
                for name_val in port:
                    val = port[name_val]
                    if isinstance(val, (int, float, numpy.float64)):
                        outs = {"value": val}
                        if residuals:
                            outs["resids"] = ""
                        # if unit:  # TODO
                        #     outs['unit'] = meta[name]['unit']
                        pathname = path_name(system.name, name_val)
                        list_out.append((pathname, outs))
            if values and not outward:
                for name_val in port:
                    val = port[name_val]
                    if isinstance(val, (int, float, numpy.float64)):
                        outs = {"value": val}
                        if residuals:
                            outs["resids"] = ""
                        # if unit:  # TODO
                        #     outs['unit'] = meta[name]['unit']
                        pathname = path_name(system.name, port.name, name_val)
                        list_out.append((pathname, outs))
        if residuals:
            for residue, obj in system.residues.items():
                name_val = residue
                val = obj.value
                if isinstance(val, (int, float, numpy.float64)):
                    outs = {"resids": val}
                    if values:
                        outs["value"] = ""
                    # if unit:  # TODO
                    #     outs['unit'] = meta[name]['unit']
                    pathname = path_name(system.name, "residue", name_val)
                    list_out.append((pathname, outs))

    parent_name = parent_name + system.name + "."
    for child in system.children.values():
        list_out.extend(
            get_list_outputs(
                child,
                values=values,
                local=local,
                residuals=residuals,
                parent_name=parent_name,
                itself=itself,
            )
        )
    return list_out


def get_list_inputs(
    system: System,
    values: bool = True,
    inwards: bool = False,
    parent_name: str = "",
    with_unfrozen_data: bool = True,
    itself: bool = False,
) -> List[Tuple[str, Dict[str, Any]]]:
    """Return and optionally log a list of input names and other optional information.

    Parameters
    ----------
    system : System
        System to be listed
    values : bool, optional
        When True, take into account input values. Default is True.
    inwards : bool, optional
        When True, take into account inwards values. Default is False
    parent_name : string, optional
        Where to store parent name during recursion
    with_unfrozen_data: bool, optional
        When True, include the unfrozen inwards. Default is True
    itself : bool, optional
        When True, include own inwards, outwards and port in the list
    Returns
    -------
    list_in
        list of input names and other optional information about those inputs
    """
    path_name = lambda *args: parent_name + ".".join(args)

    list_in = list()
    if len(system.children) == 0 or itself:
        for name_port, port in system.inputs.items():
            if inwards and name_port == System.INWARDS:
                for name_val in port:
                    val = port[name_val]
                    # if name_val not in ['data.map', 'data.map_file']:
                    if isinstance(val, (int, float, numpy.float64)):
                        outs = {"value": val}
                        # if unit:  #TODO
                        #     outs['unit'] = meta[name]['unit']
                        pathname = path_name(system.name, name_val)
                        list_in.append((pathname, outs))
                    # TODO something not right in the following two lines
                    if not with_unfrozen_data and not port.is_frozen(val):
                        list_in.pop(pathname)
            if values and name_port != System.INWARDS:
                for name_val in port:
                    val = port[name_val]
                    if isinstance(val, (int, float, numpy.float64)):
                        outs = {"value": val}
                        # if unit:  #TODO
                        #     outs['unit'] = meta[name]['unit']
                        pathname = path_name(system.name, port.name, name_val)
                        list_in.append((pathname, outs))

    parent_name = parent_name + system.name + "."
    for child in system.children.values():
        list_in.extend(
            get_list_inputs(
                child,
                values=values,
                inwards=inwards,
                parent_name=parent_name,
                itself=itself,
            )
        )
    return list_in


def _write_outputs(
    in_or_out: str, outputs: list, hierarchical: bool, print_arrays: bool, out_stream
) -> None:
    """
    Write table of variable names, values, residuals, and metadata to out_stream.

    The output values could actually represent input variables.
    In this context, outputs refers to the data that is being logged to an output stream.

    Parameters
    ----------
    in_or_out : str, {'input', 'output'}
        indicates whether the values passed in are from inputs or output variables.
    outputs : list
        list of (name, dict of vals and metadata) tuples.
    hierarchical : bool
        When True, human readable output shows variables in hierarchical format.
    print_arrays : bool
        When False, in the columnar display, just display norm of any ndarrays with size > 1.
        The norm is surrounded by vertical bars to indicate that it is a norm.
        When True, also display full values of the ndarray below the row. Format  is affected
        by the values set with numpy.set_printoptions
        Default is False.
    out_stream : file-like object
        Where to send human readable output.
        Set to None to suppress.
    """

    # Formatting parameters for _write_outputs and _write_output_row methods
    #     that are used by list_inputs and list_outputs methods
    _column_widths = {
        "value": 20,
        "resids": 20,
        "unit": 10,
        "shape": 10,
        "lower": 20,
        "upper": 20,
        "ref": 20,
        "ref0": 20,
        "res_ref": 20,
    }
    _align = ""
    _column_spacing = 2
    _indent_inc = 2

    if out_stream is None:
        return

    # Make a dict of outputs. Makes it easier to work with in this method
    dict_of_outputs = OrderedDict()
    for name, vals in outputs:
        dict_of_outputs[name] = vals

    count = len(dict_of_outputs)
    # Write header
    pathname = "model"
    header_name = "Input" if in_or_out == "input" else "Output"
    if in_or_out == "input":
        header = "%d %s(s) in '%s'" % (count, header_name, pathname)
    else:
        header = "%d %s(s) in '%s'" % (count, header_name, pathname)
    out_stream.write(header + "\n")
    out_stream.write("-" * len(header) + "\n" + "\n")

    if not count:
        return

    # Need an ordered list of possible output values for the two cases: inputs and outputs
    #  so that we do the column output in the correct order
    if in_or_out == "input":
        out_types = ("value", "unit")
    else:
        out_types = (
            "value",
            "resids",
            "unit",
            "shape",
            "lower",
            "upper",
            "ref",
            "ref0",
            "res_ref",
        )
    # Figure out which columns will be displayed
    # Look at any one of the outputs, they should all be the same
    outputs = dict_of_outputs[list(dict_of_outputs)[0]]
    column_names = []
    for out_type in out_types:
        if out_type in outputs:
            column_names.append(out_type)
    top_level_system_name = "top"
    # Find with width of the first column in the table
    #    Need to look through all the possible varnames to find the max width
    max_varname_len = max(len(top_level_system_name), len("varname"))
    if hierarchical:
        for name in dict_of_outputs:
            for i, name_part in enumerate(name.split(".")):
                total_len = (i + 1) * _indent_inc + len(name_part)
                max_varname_len = max(max_varname_len, total_len)
    else:
        for name in dict_of_outputs:
            max_varname_len = max(max_varname_len, len(name))

    # Determine the column widths of the data fields by finding the max width for all rows
    for column_name in column_names:
        _column_widths[column_name] = len(
            column_name
        )  # has to be able to display name!
    # for name in _var_allprocs_abs_names[in_or_out]:
    #     if name in dict_of_outputs:
    for name in dict_of_outputs:
        for column_name in column_names:
            if (
                isinstance(dict_of_outputs[name][column_name], numpy.ndarray)
                and dict_of_outputs[name][column_name].size > 1
            ):
                out = f"|{numpy.linalg.norm(dict_of_outputs[name][column_name])}|"
            else:
                out = str(dict_of_outputs[name][column_name])
            _column_widths[column_name] = max(
                _column_widths[column_name], len(str(out))
            )
    # Write out the column headers
    column_header = "{:{align}{width}}".format(
        "varname", align=_align, width=max_varname_len
    )
    column_dashes = max_varname_len * "-"
    for column_name in column_names:
        column_header += _column_spacing * " "
        column_header += "{:{align}{width}}".format(
            column_name, align=_align, width=_column_widths[column_name]
        )
        column_dashes += _column_spacing * " " + _column_widths[column_name] * "-"
    out_stream.write(column_header + "\n")
    out_stream.write(column_dashes + "\n")

    # Write out the variable names and optional values and metadata
    if hierarchical:
        out_stream.write(top_level_system_name + "\n")

        cur_sys_names = []
        # _var_allprocs_abs_names has all the vars across all procs in execution order
        #   But not all the values need to be written since, at least for output vars,
        #      the output var lists are divided into explicit and implicit
        # for varname in _var_allprocs_abs_names[in_or_out]:
        #     if varname not in dict_of_outputs:
        #         continue
        for varname in dict_of_outputs:
            # For hierarchical, need to display system levels in the rows above the
            #   actual row containing the var name and values. Want to make use
            #   of the hierarchies that have been written about this.
            existing_sys_names = []
            varname_sys_names = varname.split(".")[:-1]
            for i, sys_name in enumerate(varname_sys_names):
                if varname_sys_names[: i + 1] != cur_sys_names[: i + 1]:
                    break
                else:
                    existing_sys_names = cur_sys_names[: i + 1]

            # What parts of the hierarchy for this varname need to be written that
            #   were not already written above this
            remaining_sys_path_parts = varname_sys_names[len(existing_sys_names) :]

            # Write the Modules in the var name path
            indent = len(existing_sys_names) * _indent_inc
            for i, sys_name in enumerate(remaining_sys_path_parts):
                indent += _indent_inc
                out_stream.write(indent * " " + sys_name + "\n")
            cur_sys_names = varname_sys_names

            indent += _indent_inc
            row = "{:{align}{width}}".format(
                indent * " " + varname.split(".")[-1],
                align=_align,
                width=max_varname_len,
            )
            _write_outputs_rows(
                out_stream, row, column_names, dict_of_outputs[varname], print_arrays
            )
    else:
        for name in dict_of_outputs:
            row = "{:{align}{width}}".format(name, align=_align, width=max_varname_len)
            _write_outputs_rows(
                out_stream, row, column_names, dict_of_outputs[name], print_arrays
            )
    out_stream.write(2 * "\n")


def _write_outputs_rows(
    out_stream,
    row: str,
    column_names: List[str],
    dict_of_outputs: Dict[str, Any],
    print_arrays: bool,
):
    """
    For one variable, write name, values, residuals, and metadata to out_stream.

    Parameters
    ----------
    out_stream : file-like object
        Where to send human readable output.
        Set to None to suppress.
    row : str
        The string containing the contents of the beginning of this row output.
        Contains the name of the System or varname, possibley indented to show hierarchy.

    column_names : list of str
        Indicates which columns will be written in this row.

    dict_of_outputs : dict
        Contains the values to be written in this row. Keys are columns names.

    print_arrays : bool
        When False, in the columnar display, just display norm of any ndarrays with size > 1.
        The norm is surrounded by vertical bars to indicate that it is a norm.
        When True, also display full values of the ndarray below the row. Format  is affected
        by the values set with numpy.set_printoptions
        Default is False.

    """
    # Formatting parameters for _write_outputs and _write_output_row methods
    #     that are used by list_inputs and list_outputs methods
    _column_widths = {
        "value": 20,
        "resids": 20,
        "unit": 10,
        "shape": 10,
        "lower": 20,
        "upper": 20,
        "ref": 20,
        "ref0": 20,
        "res_ref": 20,
    }
    _align = ""
    _column_spacing = 2
    _indent_inc = 2

    if out_stream is None:
        return
    have_array_values = []  # keep track of which values are arrays
    for column_name in column_names:
        row += _column_spacing * " "
        if (
            isinstance(dict_of_outputs[column_name], numpy.ndarray)
            and dict_of_outputs[column_name].size > 1
        ):
            have_array_values.append(column_name)
            out = f"|{numpy.linalg.norm(dict_of_outputs[column_name])}|"
        else:
            out = str(dict_of_outputs[column_name])
        row += "{:{align}{width}}".format(
            out, align=_align, width=_column_widths[column_name]
        )
    out_stream.write(row + "\n")
    if print_arrays:
        left_column_width = len(row)
        spacing = left_column_width * " "
        for column_name in have_array_values:
            out_stream.write(f"{spacing}  {column_name}:\n")
            out_str = str(dict_of_outputs[column_name])
            indented_lines = [
                (left_column_width + _indent_inc) * " " + s
                for s in out_str.splitlines()
            ]
            out_stream.write("\n".join(indented_lines) + "\n")
