"""Module containing robotframework library for describe-get-system proof of concept."""

from dgspoc.core import Dgs


def wait_for(duration):
    """pausing function
    | Parameters:
    |     duration (float): total seconds
    """
    Dgs.wait_for(duration)


def connect_device(host, adaptor='unreal-device', **kwargs):
    """generic function to establish device connection
    | Parameters:
    |     host (str): host name or address
    |     adaptor (str): an adaptor for device connection
    |     kwargs (dict): additional keyword arguments for connecting device connection
    | Returns:
    |     Adaptor: Adaptor connection of device.
    """
    result = Dgs.connect_device(host, adaptor=adaptor, **kwargs)
    return result


def disconnect_device(connection, **kwargs):
    """generic function to disconnect device connection
    | Parameters:
    |     connection (Adaptor): connection of device
    |     kwargs (dict): additional keyword arguments for disconnecting device connection
    | Returns:
    |     bool: True if successfully disconnected device, otherwise, False.
    """
    result = Dgs.disconnect_device(connection, **kwargs)
    return result


def release_device(connection, **kwargs):
    """generic function to release device connection
    | Parameters:
    |     connection (Adaptor): connection of device
    |     kwargs (dict): additional keyword arguments for releasing device connection
    | Returns:
    |     bool: True if successfully released device, otherwise, False.
    """
    result = Dgs.release_device(connection, **kwargs)
    return result


def execute(connection, cmdline, **kwargs):
    """generic function to execute command for device
    | Parameters:
    |     connection (Adaptor): connection of device
    |     cmdline (str): command line
    |     kwargs (dict): additional keyword arguments for command line execution
    | Returns:
    |     str: output of command line
    """
    result = Dgs.execute_cmdline(connection, cmdline, **kwargs)
    return result


def configure(connection, cfg, **kwargs):
    """generic function to configure device
    | Parameters:
    |     connection (Adaptor): connection of device
    |     cfg (str): configuration
    |     kwargs (dict): additional keyword arguments for configuring device
    | Returns:
    |     str: the result of device configuration
    """
    result = Dgs.configure_device(connection, cfg, **kwargs)
    return result


def reload(connection, reload_command, **kwargs):
    """generic function to reload device
    | Parameters:
    |     connection (Adaptor): connection of device
    |     reload_command (str): a reload command
    |     kwargs (dict): additional keyword arguments for reloading device
    | Returns:
    |     str: the result of reloading process
    """
    result = Dgs.reload_device(connection, reload_command, **kwargs)
    return result


def convert_and_filter(text, convertor='', template_ref='', select_statement=''):
    """generic function to convert text data struct and filter per select_statement
    | Parameters:
    |     text (str): output or text data
    |     convertor (str): cvs, json, or template
    |     template_ref (str): template-id or template filename
    |     select_statement (str): a select statement
    | Returns:
    |     list: the list of records
    """
    result = Dgs.convert_and_filter(
        text, convertor=convertor, template_ref=template_ref,
        select_statement=select_statement
    )
    return result
