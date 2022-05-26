#!python
"""
Collects all JSON from validation steps and compiles some global scores over an
XNAT instance.
"""


def validation_scores(arguments):
    import traceback
    import logging as log
    import os.path as op
    import json
    import dateparser
    from bbrc.validation.utils import collect_reports
    from pyxnat import Interface

    import bbrc
    f = op.join(op.dirname(bbrc.__file__), 'data', 'versions.json')
    with open(f, 'r') as fp:
        versions = json.load(fp)

    config_file = op.abspath(arguments.config.name)
    version = arguments.version

    from bbrc import __version__
    log.info('BBRC-validator version: %s' % __version__)

    if arguments.verbose:
        log.getLogger().setLevel(log.INFO)
    else:
        log.getLogger().setLevel(log.WARNING)

    try:
        x = Interface(config=config_file)
        j = collect_reports(x, validator_name=arguments.validator,
                            project=arguments.project)

        fields = []
        for k, v in j.items():
            if 'version' not in v.keys():
                log.warning('Version not found in report %s' % k)
                continue
            if v['version'] != version and version != '*':
                continue
            fields.extend(list(v.keys()))
        fields = list(set(fields))

        try:
            for e in ['version', 'generated', 'experiment_id']:
                fields.remove(e)
        except ValueError:
            msg = 'No valid %s reports found (version %s).' \
                  % (arguments.validator, version)
            log.error(msg)
            exit(1)

        res = []
        for k, v in j.items():
            if 'version' not in v.keys():
                log.warning('Version not found in report %s' % k)
                continue
            if v['version'] != version:
                if v['version'] not in versions.keys():
                    msg = 'Version %s (%s) not registered as a '\
                          'valid/existing version (%s)'\
                          % (v['version'], v['generated'], v['experiment_id'])
                    log.warning(msg)
                    continue

                if version != '*':
                    d = dateparser.parse(versions[version]['date'])
                    if dateparser.parse(v['generated']) < d:
                        continue

            row = [v['experiment_id'], v['version']]
            row.extend([v.get(f, {'has_passed': None})['has_passed']
                        for f in fields])
            res.append(row)

        import pandas as pd
        fields.insert(0, 'version')
        fields.insert(0, 'experiment_id')

        df = pd.DataFrame(res, columns=fields).set_index('experiment_id')
        df.to_excel(arguments.output.name)

        if x._user and not x._anonymous:
            x.disconnect()

    except Exception as e:
        log.error(e)
        log.error(traceback.format_exc())
        exit(1)


def create_parser():
    import argparse
    arg_parser = argparse.ArgumentParser(description='Compile validation scores')
    arg_parser.add_argument(
        '--config', '-c', help='XNAT configuration file',
        type=argparse.FileType('r'), required=True)
    arg_parser.add_argument(
        '--version', '-v', required=False, default='*',
        help='Filter specific version (optional)')
    arg_parser.add_argument(
        '--validator', required=False, default='ArchivingValidator',
        help='Validator name (default:ArchivingValidator)')
    arg_parser.add_argument(
        '--output', '-o', required=True, type=argparse.FileType('wt'),
        help='Excel output file')
    arg_parser.add_argument(
        '--project', '-p', required=False, default=None,
        help='Specific XNAT project to collect validation results from (optional)')
    arg_parser.add_argument(
        '--verbose', '-V', action='store_true', required=False, default=False,
        help='Display verbosal information (optional)')
    return arg_parser


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    validation_scores(args)
