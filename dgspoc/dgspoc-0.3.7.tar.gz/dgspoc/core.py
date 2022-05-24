"""Module containing logic for describe-get-system proof of concept."""

import time
from io import StringIO

from textfsm import TextFSM


from dlapp import create_from_csv_data
from dlapp import create_from_json_data
from dlapp import DLQuery

from dgspoc.adaptor import Adaptor

from dgspoc.constant import CONVTYPE

from dgspoc.storage import TemplateStorage

from dgspoc.utils import DotObject
from dgspoc.utils import File
from dgspoc.utils import Misc
from dgspoc.utils import MiscArgs

from dgspoc.exceptions import DurationArgumentError
from dgspoc.exceptions import ConvertorTypeError
from dgspoc.exceptions import TemplateReferenceError


class Dgs:
    """Describe-Get-System class"""
    kwargs = DotObject()

    @classmethod
    def wait_for(cls, duration):
        """pausing method

        Parameters
        ----------
        duration (float): total seconds
        """

        is_number, number = Misc.try_to_get_number(duration, return_type=float)
        if is_number:
            time.sleep(number)
        else:
            failure = 'duration must be a number (unexpected: %s)' % duration
            raise DurationArgumentError(failure)

    @classmethod
    def connect_device(cls, host, adaptor='unreal-device', **kwargs):
        """generic connecting device

        Parameters
        ----------
        host (str): address of device
        adaptor (str): connection adaptor.
        kwargs (dict): additional keyword arguments for connecting device

        Returns
        -------
        Adaptor: a device connection
        """

        connection = Adaptor(adaptor, host, **kwargs)
        connection.connect()
        return connection

    @classmethod
    def disconnect_device(cls, connection, **kwargs):
        """generic disconnecting device

        Parameters
        ----------
        connection (Adaptor): instance of device connection
        kwargs (dict): additional keyword arguments for disconnection device connection

        Returns
        -------
        bool: True if successfully disconnected device connection, otherwise, False.
        """
        result = connection.disconnect(**kwargs)
        return result

    @classmethod
    def release_device(cls, connection, **kwargs):
        """generic releasing device

        Parameters
        ----------
        connection (Adaptor): instance of device connection
        kwargs (dict): additional keyword arguments for releasing device connection

        Returns
        -------
        bool: True if successfully released device connection, otherwise, False.
        """
        result = connection.release(**kwargs)
        return result

    @classmethod
    def execute_cmdline(cls, connection, cmdline, **kwargs):
        """generic device execution

        Parameters
        ----------
        connection (Adaptor): instance of device connection
        cmdline (str): command lines
        kwargs (dict): additional keyword arguments for command line execution

        Returns
        -------
        str: output of command line
        """
        result = connection.execute(cmdline, **kwargs)
        return result

    @classmethod
    def configure_device(cls, connection, cfg, **kwargs):
        """generic device configuration

        Parameters
        ----------
        connection (Adaptor): instance of device connection
        cfg (str): configuration lines
        kwargs (dict): additional keyword arguments for configuring device

        Returns
        -------
        str: the result of device configuration
        """
        result = connection.configure(cfg, **kwargs)
        return result

    @classmethod
    def reload_device(cls, connection, reload_command, **kwargs):
        """generic reloading device

        Parameters
        ----------
        connection (Adaptor): instance of device connection
        reload_command (str): reload command
        kwargs (dict): additional keyword arguments for reloading device

        Returns
        -------
        str: the result of reloading process
        """
        result = connection.reload(reload_command, **kwargs)
        return result

    @classmethod
    def convert_and_filter(cls, text, convertor='', template_ref='', select_statement=''):
        """generic method to convert text to data struct and filter result
        per select_statement

        Parameters
        ----------
        text (str): output or text data
        convertor (str): cvs, json, or template
        template_ref (str): template-id or template filename
        select_statement (str): a select statement

        Returns
        -------
        list: the list of records
        """

        if convertor == CONVTYPE.CSV:
            result = cls.do_filter_csv(text, select_statement=select_statement)
            return result

        elif convertor == CONVTYPE.JSON:
            result = cls.do_filter_json(text, select_statement=select_statement)
            return result
        elif convertor == CONVTYPE.TEMPLATE:
            result = cls.do_filter_template(text, template_ref,
                                            select_statement=select_statement)
            return result
        else:
            fmt = 'convertor MUST BE csv, json, or template (Unexpected: %s)'
            raise ConvertorTypeError(fmt % convertor)

    @classmethod
    def do_filter_csv(cls, text, select_statement=''):
        """generic method to convert csv text to list of dict and filter
        per select_statement

        Parameters
        ----------
        text (str): output or text data
        select_statement (str): a select statement

        Returns
        -------
        list: the list of records
        """

        query_obj = create_from_csv_data(text)
        result = query_obj.find(select_statement=select_statement)
        return result

    @classmethod
    def do_filter_json(cls, text, select_statement=''):
        """generic method to convert json text to data structure and filter
        per select_statement

        Parameters
        ----------
        text (str): output or text data
        select_statement (str): a select statement

        Returns
        -------
        list: the list of records
        """
        query_obj = create_from_json_data(text)
        result = query_obj.find(select_statement=select_statement)
        return result

    @classmethod
    def do_filter_template(cls, text, tmpl_ref, select_statement=''):
        """generic method to convert text to data struct using TextFSM and
        filter per select_statement

        Parameters
        ----------
        text (str): output or text data
        template_ref (str): template-id or template filename
        select_statement (str): a select statement

        Returns
        -------
        list: the list of records
        """

        tmpl_ref = str(tmpl_ref).strip()

        if not tmpl_ref:
            failure = 'Template reference CANT BE empty.'
            raise TemplateReferenceError(failure)

        parsed_args_result = MiscArgs.get_parsed_result_as_data_or_file(
            '--template-id', data=tmpl_ref
        )

        if not parsed_args_result.is_parsed:
            fmt = 'Invalid template reference format (Unexpected: %r)'
            raise TemplateReferenceError(fmt % tmpl_ref)

        if parsed_args_result.is_file:
            fn = parsed_args_result.filename
            if not File.is_exist(fn):
                fmt = '%r template file CANT BE FOUND.'
                raise TemplateReferenceError(fmt % fn)
            else:
                with open(fn) as stream:
                    template_parser = TextFSM(stream)
        else:
            tmpl_id = parsed_args_result.data
            if not TemplateStorage.check(tmpl_id):
                fmt = '%r template-id CANT BE FOUND in template storage.'
                raise TemplateReferenceError(fmt % tmpl_id)
            else:
                template = TemplateStorage.get(tmpl_id)
                stream = StringIO(template)
                template_parser = TextFSM(stream)

        rows = template_parser.ParseTextToDicts(text)

        if not select_statement:
            return rows
        else:
            query_node = DLQuery(rows)
            result = query_node.find(select=select_statement)
            return result


sleep = Dgs.wait_for
wait_for = Dgs.wait_for
connect_device = Dgs.connect_device
disconnect_device = Dgs.disconnect_device
release_device = Dgs.release_device
destroy_device = Dgs.reload_device
execute = Dgs.execute_cmdline
configure = Dgs.configure_device
reload = Dgs.reload_device
convert_and_filter = Dgs.convert_and_filter
