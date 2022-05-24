"""Module containing the logic for describe-get-system operation"""

import sys
import re
import argparse
import operator
import shlex

from functools import partial
from textwrap import wrap

from dgspoc import version

from dgspoc.config import Data

from dgspoc.interpreter import ScriptBuilder

from dgspoc.utils import File
from dgspoc.utils import Printer
from dgspoc.utils import Text
from dgspoc.utils import DotObject
from dgspoc.utils import parse_template_result
from dgspoc.utils import Misc
from dgspoc.utils import MiscArgs

from dgspoc.constant import ECODE
from dgspoc.constant import CONVTYPE
from dgspoc.constant import COMMAND
from dgspoc.constant import FEATURE

from dgspoc.storage import TemplateStorage

from dgspoc.usage import validate_usage
from dgspoc.usage import validate_example_usage
from dgspoc.usage import show_usage
from dgspoc.usage import get_global_usage

from dgspoc.adaptor import Adaptor

from dgspoc.parser import ParsedOperation
from dgspoc.parser import CheckStatement

from dgspoc.batch import BatchBuilder

from dgspoc.report import DGSReportFile
from dgspoc.report import DGSReport

from templateapp import TemplateBuilder

from dlapp import DLQuery
from dlapp import create_from_csv_data
from dlapp import create_from_json_data

from pprint import pprint
from dlapp.collection import Tabular


class OptionSelector:
    def __init__(self, options, print_help=None):
        self.options = options
        self.print_help = print_help
        self.method = None
        self.prepare()

    def prepare(self):
        if self.options.template_id.strip():
            self.method = do_clear_template
        elif self.options.filepath.strip():
            self.method = do_delete_filepath
        else:
            if self.options.command == COMMAND.USAGE:
                self.method = do_show_global_usage
            elif self.options.command == COMMAND.INFO:
                self.method = do_show_info
            elif self.options.command == COMMAND.BUILD:
                feature = ''.join(self.options.operands[:1]).lower()
                if feature == FEATURE.TEMPLATE:
                    self.method = do_build_template
                elif feature == FEATURE.SCRIPT:
                    self.method = do_build_test_script
                elif feature == FEATURE.BATCH:
                    self.method = do_build_batch_script
                else:
                    exit_code = ECODE.SUCCESS if feature == 'usage' else ECODE.BAD
                    show_usage(self.options.command, exit_code=exit_code)
            elif self.options.command == COMMAND.SEARCH:
                self.method = do_search_template
            elif self.options.command == COMMAND.TEST:
                self.method = do_testing
            elif self.options.command == COMMAND.REPORT:
                self.method = do_reporting

    def process(self):
        if callable(self.method):
            self.method(self.options)
        else:
            if callable(self.print_help):
                self.print_help()
            else:
                print('*** Something is not right.  Check with developer.')
                sys.exit(ECODE.BAD)


def do_show_global_usage(options):
    if options.command == COMMAND.USAGE:
        print(get_global_usage())
        sys.exit(ECODE.SUCCESS)


def do_show_version(options):
    if options.command == 'version':
        print('{} v{}'.format(Data.console_cli_name, version))
        sys.exit(ECODE.SUCCESS)


def do_show_info(options):
    command, operands = options.command, options.operands

    name = command
    validate_usage(command, operands)
    validate_example_usage(name, operands)

    op_txt = ' '.join(operands).lower()

    lst = []
    default_lst = [
        'Describe-Get-System Proof of Concept',
        Data.get_app_info()
    ]

    is_showed_all = options.all or re.search('all', op_txt)
    is_showed_dependency = options.dependency or re.search('depend', op_txt)
    is_showed_storage = options.template_storage or re.search('template|storage', op_txt)

    if is_showed_all:
        lst.extend(default_lst)

    if is_showed_all or is_showed_dependency:
        lst and lst.append('--------------------')
        lst.append('Packages:')
        values = Data.get_dependency().values()
        for pkg in sorted(values, key=lambda item: item.get('package')):
            lst.append('  + Package: {0[package]}'.format(pkg))
            lst.append('             {0[url]}'.format(pkg))

    if is_showed_all or is_showed_storage:
        lst and lst.append('--------------------', )
        lst.append(Data.get_template_storage_info())

    Printer.print(lst) if lst else Printer.print(default_lst)
    sys.exit(ECODE.SUCCESS)


def do_build_template(options):
    command, operands = options.command, list(options.operands)
    op_count = len(operands)
    feature = str(operands[0]).lower().strip() if op_count > 0 else ''

    operands = operands[1:]
    name = '{}_{}'.format(command, feature)
    validate_usage(name, operands)
    validate_example_usage(name, operands)

    op_txt = ' '.join(operands).rstrip()

    if not op_txt:
        show_usage(name, exit_code=ECODE.BAD)

    if File.is_exist(op_txt):
        with open(op_txt) as stream:
            user_data = stream.read()
    else:
        user_data = op_txt

    try:
        factory = TemplateBuilder(
            user_data=user_data, author=options.author, email=options.email,
            company=options.company
        )

        template_id = options.tmplid.strip()
        filename = options.filename.strip()

        fmt1 = '+++ Successfully uploaded generated template to "{}" template ID.'
        fmt2 = '+++ Successfully saved generated template to {}'
        fmt3 = 'CANT save generated template to existing {} file.  Use replaced flag accordingly.'

        if template_id or filename:
            is_ok = True
            lst = []
            if template_id:
                is_uploaded = TemplateStorage.upload(
                    template_id, factory.template, replaced=options.replaced
                )
                is_ok &= is_uploaded
                msg = fmt1.format(template_id) if is_uploaded else TemplateStorage.message
                lst.append(msg)
            if filename:
                filename = File.get_path(filename)
                if File.is_exist(filename) and not options.replaced:
                    msg = fmt3.format(filename)
                    is_ok &= False
                else:
                    is_saved = File.save(options.filename, factory.template)
                    is_ok &= is_saved
                    msg = fmt2.format(filename) if is_saved else File.message

                lst and lst.append('=' * 20)
                lst.append(msg)

            lst and Printer.print(lst)
            sys.exit(ECODE.SUCCESS if is_ok else ECODE.BAD)
        else:
            print(factory.template)
            sys.exit(ECODE.SUCCESS)

    except Exception as ex:
        not options.quiet and print(Text(ex))
        sys.exit(ECODE.BAD)


def do_search_template(options):
    command, operands = options.command, list(options.operands)
    op_count = len(operands)
    feature = str(operands[0]).lower().strip() if op_count > 0 else ''
    if command == 'search' and feature == 'template':
        operands = operands[1:]
        name = '{}_{}'.format(command, feature)
        validate_usage(name, operands)
        validate_example_usage(name, operands)

        op_txt = ' '.join(operands).rstrip()

        if not op_txt:
            show_usage(name, exit_code=ECODE.BAD)

        tmpl_id_pattern = operands[0]
        is_found = TemplateStorage.search(tmpl_id_pattern)
        print(TemplateStorage.message)
        sys.exit(ECODE.SUCCESS if is_found else ECODE.BAD)

    elif command == 'search' and feature != 'template':
        exit_code = ECODE.SUCCESS if feature == 'usage' else ECODE.BAD
        show_usage('{}_template'.format(command), exit_code=exit_code)


def do_clear_template(options):
    template_id = options.template_id.strip()

    if re.match(r'(?i) *([*]|_+all_+) *$', template_id):
        fmt = ('*** Failed to clear %r template reference because '
               'Describe-Get-System prohibits multiple clearing')
        not options.quiet and print(fmt % template_id)
        sys.exit(ECODE.BAD)

    if template_id:
        result = MiscArgs.get_parsed_result_as_data_or_file(data=template_id)
        if result.is_file:
            is_deleted = File.delete(result.filename)
            not options.quiet and print('%s %s' % ('+++' if is_deleted else '***', File.message))
            sys.exit(ECODE.SUCCESS if is_deleted else ECODE.BAD)
        else:
            is_cleared = TemplateStorage.clear(template_id)
            if is_cleared:
                fmt = '+++ Successfully cleared %r template id in template storage.'
                message = fmt % template_id
            else:
                message = '*** %s' % TemplateStorage.message
            not options.quiet and print(message)
            sys.exit(ECODE.SUCCESS if is_cleared else ECODE.BAD)


def validate_test_data_flag(options):
    command = options.command
    feature = options.operands[0] if options.operands else ''
    if options.testfile == '' and options.adaptor == '':
        lst = ['CANT run {} test WITHOUT test data.'.format(feature),
               'Please use --test-file=<test-file-name> or',
               '           --adaptor=<adaptor_name> --execution="<device cmdline>"']
        Printer.print(lst)
        show_usage('{}_{}'.format(command, feature), exit_code=ECODE.BAD)


def get_test_from_adaptor(options):
    command = options.command
    feature = options.operands[0] if options.operands else ''
    name = '{}_{}'.format(command, feature)
    execution = options.execution.strip()
    if not execution:
        lst = [
            'ExecutionSyntaxError: must be',
            '--execution="--host=<addr_or_name> <cmdline>"',
        ]
        Printer.print(lst)
        show_usage(name, exit_code=ECODE.BAD)

    try:

        lst = execution.split(' ')

        parser = argparse.ArgumentParser(exit_on_error=False)
        parser.add_argument('items', nargs='*')
        parser.add_argument('--host', type=str, default='')
        parser.add_argument('other_items', nargs='*')
        parser_args = parser.parse_args(lst)

        host = parser_args.host
        cmdline = ' '.join(parser_args.items + parser_args.other_items)

        if not parser_args.host:
            lst = [
                'ExecutionSyntaxError: must be',
                '--execution="--host=<addr_or_name> <cmdline>"',
            ]
            Printer.print(lst)
            show_usage(name, exit_code=ECODE.BAD)

        device = Adaptor(options.adaptor, host)
        device.connect()
        test_data = device.execute(cmdline)
        device.disconnect()
        device.release()
        return test_data
    except Exception as ex:
        failure = 'AdaptorInquiryError - ({})'.format(Text(ex))
        not options.quiet and Printer.print(failure)
        sys.exit(ECODE.BAD)


def do_testing(options):
    pattern = '^--(template-id|(file(-?name)?))='
    command, operands = options.command, list(options.operands)
    adaptor = options.adaptor.strip().lower()
    action = options.action.strip()

    name = command
    validate_usage(name, operands)
    validate_example_usage(name, operands)
    is_showed = False
    if re.search(r'(?i)--showed\b', action):
        is_showed = True
        action = re.sub(r'(?i)--showed\b', '', action).strip()

    is_tabular = False
    if re.search(r'(?i)--tabular\b', action):
        is_tabular = True
        action = re.sub(r'(?i)--tabular\b', '', action).strip()

    adaptor = adaptor or 'stream'
    is_adaptor_stream = bool(re.match(r'(stream|file(name)?)$', adaptor))
    is_execute_cmdline = CheckStatement.is_execute_cmdline(action)

    if is_adaptor_stream:
        data = 'dummy execute %s' % action if not is_execute_cmdline else action

        node = ParsedOperation(data)
        test_data_file = re.sub(pattern, '', node.operation_ref.strip())
        File.message = ''
        output = File.get_content(test_data_file)
        if File.message:
            not options.quiet and print('*** %s' % File.message)
            sys.exit(ECODE.BAD)
        print(output)
        result = DotObject(test_data=output, template='', records=[], records_count=0)

        if node.has_select_statement or node.convertor:
            if node.is_csv or node.is_json:
                try:
                    lines = result.test_data.splitlines()
                    index = 0
                    pat = (r'(?i)\w{3} +\d\d? +\d{4} '
                           r'\d\d:\d\d:\d\d[.]\d\d\d for "\S+" - '
                           r'UNREAL-DEVICE-\w+-SERVICE-TIMESTAMP')
                    for i, line in enumerate(lines):
                        if re.match(pat, line):
                            index = i
                            break
                    test_data = '\n'.join(lines[index+1:])
                    method = create_from_json_data if node.is_json else create_from_csv_data
                    records = method(test_data).data
                    result.records = records
                    result.records_count = len(records)
                except Exception as ex:
                    not options.quiet and print('*** %s' % Text(ex))
                    sys.exit(ECODE.BAD)
            else:
                pfunc = partial(parse_template_result, test_file=test_data_file)
                if not node.convertor == CONVTYPE.TEMPLATE or not node.convertor_arg:
                    print('*** Invalid action: %s ***' % action)
                    sys.exit(ECODE.BAD)

                try:
                    if re.match('(?i)--file', node.convertor_arg.strip()):
                        template_file = re.sub(pattern, '', node.convertor_arg.strip())
                        result = pfunc(template_file=template_file)
                    else:
                        tmpl_id = re.sub(pattern, '', node.convertor_arg.strip())
                        if TemplateStorage.check(tmpl_id):
                            tmpl_data = TemplateStorage.get(tmpl_id)
                            result = pfunc(template_data=tmpl_data)
                        else:
                            fmt = '*** %r template id CANT find in template storage.'
                            print(fmt % tmpl_id)
                            sys.exit(ECODE.BAD)
                except Exception as ex:
                    failure = '*** %s' % ex
                    not options.quiet and print(failure)
                    sys.exit(ECODE.BAD)
        else:
            sys.exit(ECODE.SUCCESS)
    else:
        if not CheckStatement.is_performer_statement(action):
            failure = '*** Invalid action: %s ***' % action
            print(failure)
            sys.exit(ECODE.BAD)

        node = ParsedOperation(action)
        if not node.devices_names:
            failure = '*** Invalid action: %s ***' % action
            print(failure)
            sys.exit(ECODE.BAD)

        host = node.devices_names[0]
        connection = Adaptor(adaptor, host)
        tbl = dict(execution=connection.execute,
                   configuration=connection.configure,
                   reload=connection.reload)
        operation_method = tbl[node.name]
        connection.connect()
        output = operation_method(node.operation_ref)
        connection.release()

        if node.is_reload or node.is_configuration:
            print(output)
            sys.exit(ECODE.SUCCESS)

        if node.is_csv or node.is_json:
            try:
                lines = output.test_data.splitlines()
                index = 0
                pat = (r'(?i)\w{3} +\d\d? +\d{4} '
                       r'\d\d:\d\d:\d\d[.]\d\d\d for "\S+" - '
                       r'UNREAL-DEVICE-\w+-SERVICE-TIMESTAMP')
                for i, line in enumerate(lines):
                    if re.match(pat, line):
                        index = i
                        break
                test_data = '\n'.join(lines[index + 1:])
                method = create_from_json_data if node.is_json else create_from_csv_data
                records = method(test_data).data
                result = DotObject(
                    test_data=output, template='',
                    records=records, records_count=len(records)
                )
            except Exception as ex:
                not options.quiet and print('*** %s' % Text(ex))
                sys.exit(ECODE.BAD)
        elif node.is_template:
            pfunc = partial(parse_template_result, test_data=output)
            try:
                if re.match('(?i)--file', node.convertor_arg.strip()):
                    template_file = re.sub(pattern, '', node.convertor_arg.strip())
                    result = pfunc(template_file=template_file)
                else:
                    tmpl_id = re.sub(pattern, '', node.convertor_arg.strip())
                    if TemplateStorage.check(tmpl_id):
                        tmpl_data = TemplateStorage.get(tmpl_id)
                        result = pfunc(template_data=tmpl_data)
                    else:
                        fmt = '*** %r template id CANT find in template storage.'
                        print(fmt % tmpl_id)
                        sys.exit(ECODE.BAD)
            except Exception as ex:
                failure = '*** %s' % ex
                not options.quiet and print(failure)
                sys.exit(ECODE.BAD)
        else:
            if not node.has_select_statement:
                sys.exit(ECODE.SUCCESS)
            else:
                failure = '*** Invalid action: %s ***' % action
                print(failure)
                sys.exit(ECODE.BAD)

    if node.has_select_statement:
        query_obj = DLQuery(result.records)
        tested_records = query_obj.find(select=node.select_statement)
    else:
        tested_records = result.records

    if is_showed:
        Printer.print('User Test Data:')
        print(result.test_data)
        print()

        if result.template:
            Printer.print('Template:')
            print('%s\n' % result.template)
            print()

    lst = ['Parsed Results:']
    if node.has_select_statement:
        lst.append('    SELECT-STATEMENT: %s' % node.select_statement)
    Printer.print(lst)
    if is_tabular:
        Tabular(tested_records).print()
    else:
        pprint(tested_records)
    print()

    if node.is_need_verification and Misc.is_list(tested_records):
        total = len(tested_records)
        op = node.condition
        expected_number = node.expected_condition
        chk = getattr(operator, op)(total, expected_number)
        prefix = '' if chk else '*** CANT BE ***'
        tbl = dict(eq='==', ne='!=', lt='<', le='<=', gt='>', ge='>=')

        lst = ['Verification:',
               '    CONDITION: %s' % node.condition_data,
               '    STATUS   : %s' % ('Passed' if chk else 'Failed')]
        Printer.print(lst)

        fmt = '%s (total found records: %s) %s (expected total count: %s)'
        msg = (fmt % (prefix, total, tbl[op], expected_number)).strip()
        print(msg)
        print()

    if node.error:
        lst = ['Error:', '------', '\n'.join(wrap(node.error, width=76)), '']
        not options.quiet and Printer.print(lst)
        sys.exit(ECODE.BAD)
    else:
        sys.exit(ECODE.SUCCESS)


def do_build_test_script(options):
    command, operands = options.command, list(options.operands)

    feature = ''.join(operands[:1])
    operands = operands[1:]
    framework = 'unittest'
    for node in [FEATURE.UNITTEST, FEATURE.PYTEST, FEATURE.ROBOTFRAMEWORK]:
        if node == feature:
            framework = str(node)
            break

    name = '{}_script'.format(command)
    validate_usage(name, operands)
    validate_example_usage(name, operands)

    if len(operands) > 1:
        Printer.print('*** Application only support single script snippet.')
        show_usage(name, exit_code=ECODE.BAD)

    snippet_filename = operands[0]
    snippet_content = File.get_content(snippet_filename)
    if File.message:
        not options.quiet and Printer.print('*** %s' % File.message)
        sys.exit(ECODE.BAD)

    node = ScriptBuilder(
        snippet_content, framework=framework, is_logger=True,
        username=options.author, email=options.email, company=options.company
    )

    test_script = node.testscript.strip()

    if not test_script:
        fmt = '*** No script is generated for %r'
        Printer.print(fmt % snippet_filename)
        sys.exit(ECODE.BAD)

    if options.filename:
        File.save(options.filename, test_script)
        if File.message and not File.message.startswith('Successfully saved data'):
            fmt = '*** Failed to save the generated test script to %s\n*** %s'
            Printer.print(fmt % (options.filename, File.message))
            sys.exit(ECODE.BAD)
        else:
            fmt = '+++ Successfully saved the generated test script to %s'
            Printer.print(fmt % options.filename)
            sys.exit(ECODE.SUCCESS)
    else:
        print(test_script)
        sys.exit(ECODE.SUCCESS)


def do_build_batch_script(options):
    command, operands = options.command, list(options.operands)

    # feature = ''.join(operands[:1])
    operands = operands[1:]
    name = '{}_batch'.format(command)
    validate_usage(name, operands)
    validate_example_usage(name, operands)

    builder = BatchBuilder(options)
    batch_script = builder.script
    if batch_script:
        if options.filename:
            filename = options.filename

            batch_script += '\ndgs report --detail' if options.detail else '\ndgs report'
            batch_script += '\ndgs --delete=dgs_test_script_files --quiet'

            is_saved = File.save(filename, batch_script)
            if is_saved:
                fmt = '+++ Successfully saved %r batch file.'
                not options.quiet and print(fmt % filename)
                sys.exit(ECODE.SUCCESS)
            else:
                fmt = '*** Failed to save %r batch file.'
                not options.quiet and print(fmt % filename)
                not options.quiet and print('*** %s' % File.message)
                sys.exit(ECODE.BAD)
        else:
            print(batch_script)
            sys.exit(ECODE.SUCCESS)
    else:
        msg = '*** Failed to generate batch content because no test file is found.'
        not options.quiet and print(msg)
        sys.exit(ECODE.BAD)


def do_delete_filepath(options):
    filepath = options.filepath

    if File.is_exist(filepath):
        is_deleted = File.delete(filepath)
        fmt = '+++ %s' if is_deleted else '*** %s'
        not options.quiet and print(fmt % File.message)
        sys.exit(ECODE.SUCCESS if is_deleted else ECODE.BAD)

    are_deleted = None
    for file_path in shlex.split(filepath):
        if file_path == ',':
            continue

        file_path = file_path.rstrip(',').strip('{').strip('}')
        is_deleted = File.delete(file_path)
        fmt = '+++ %s' if is_deleted else '*** %s'
        not options.quiet and print(fmt % File.message)
        are_deleted = is_deleted if are_deleted is None else are_deleted and is_deleted

    if are_deleted is None:
        sys.exit(ECODE.BAD)
    else:
        sys.exit(ECODE.SUCCESS if are_deleted else ECODE.BAD)


def do_reporting(options):
    command, operands = options.command, list(options.operands)
    # feature = ''.join(operands[:1])
    # operands = operands[1:]
    name = command
    validate_usage(name, operands)
    validate_example_usage(name, operands)

    directory = operands[0] if operands else '.'
    report_files = DGSReportFile.get_report_files(directory)
    reporter = DGSReport(*report_files, detail=options.detail)
    report = reporter.generate()
    print(report)
    sys.exit(reporter.exit_code)
