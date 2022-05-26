#!python
'''
QC validation pipeline script

Gathers input arguments, connects to XNAT and attempts to validate scans which are considered 'usable'
Uses an specific version of the BBRC-VALIDATOR which determines specific set of tests used.

Validation generates both a JSON file for a posteriori machine-based analysis and a PDF report file
'''


def setup_xnat(config_file):
    import json
    from pyxnat import Interface
    with open(config_file) as f:
        j = json.load(f)
    if 'jsession_id' in j:
        xnat_instance = Interface(server=j['server'],
                                  verify=j['verify'],
                                  anonymous=True)
        jsession_id = {'JSESSIONID': str(j['jsession_id'])}
        xnat_instance._http.cookies.update(jsession_id)
    else:
        xnat_instance = Interface(config=config_file)
    return xnat_instance


def get_lut(project):
    import logging as log
    import os.path as op
    import json
    import bbrc

    f = op.abspath(op.join(op.dirname(bbrc.__file__), 'data',
                           'scan_type_luts.json'))
    with open(f, 'r') as fp:
        luts = json.load(fp)

    if project in luts:
        lut = luts[project]
        log.info('Using custom scan-type definitions for project `{}`.'.format(project))
    else:
        # load current/baseline scan-type definitions (ALFA1 protocol)
        lut = luts['ALFA1']
        log.info('No scan-type definitions found for project `{}`, '
                 'using `ALFA1` definitions.'.format(project))

    return lut


def run_validator(arguments):
    import sys
    import traceback
    import logging as log
    import os.path as op
    # BEGINNING Path hack.
    sys.path.insert(0, op.abspath('..'))
    # END Path hack.
    from bbrc import validation as v
    config_file = op.abspath(arguments.config.name)
    experiment_id = arguments.experiment
    output = op.abspath(arguments.output.name)

    from bbrc import __version__
    log.info('BBRC-validator version: %s' % __version__)

    if arguments.verbose:
        log.getLogger().setLevel(log.INFO)
    else:
        log.getLogger().setLevel(log.WARNING)

    if arguments.validator is not None:
        validator = arguments.validator
    else:
        validator = 'ArchivingValidator'

    try:
        xnat_instance = setup_xnat(config_file)

        # gather the scan-types LUT
        project_id = xnat_instance.array.experiments(experiment_id=experiment_id)\
            .data[0]['project']
        lut = get_lut(project_id)

        val = getattr(v, validator)(lut, xnat_instance)
        val.run(experiment_id)

        # STORE results as json file
        val.dump(output.replace('.pdf', '.json'))

        # GENERATE human-readable reports
        val.report(output)
        if xnat_instance._user and not xnat_instance._anonymous:
            xnat_instance.disconnect()

    except Exception as e:
        log.error(e)
        log.error(traceback.format_exc())
        sys.exit(1)


def create_parser():
    import argparse
    arg_parser = argparse.ArgumentParser(
        description='Run a validator against an experiment')
    arg_parser.add_argument(
        '--config', '-c', help='XNAT configuration file',
        type=argparse.FileType('r'), required=True)
    arg_parser.add_argument(
        '--experiment', '-e', required=True,
        help='XNAT experiment unique identifier')
    arg_parser.add_argument(
        '--validator', '-v', required=False, default=None,
        help='Validator name (default:ArchivingValidator)')
    arg_parser.add_argument(
        '--output', '-o', required=True, type=argparse.FileType('w'),
        help='PDF file to store the report')
    arg_parser.add_argument(
        '--verbose', '-V', action='store_true', default=False,
        help='Display verbosal information (optional)', required=False)
    return arg_parser


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    run_validator(args)
