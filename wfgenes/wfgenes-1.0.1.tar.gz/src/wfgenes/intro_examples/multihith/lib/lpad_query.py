""" A simple command line interface to query FireWorks """
import json, yaml
from argparse import ArgumentParser
from fireworks.scripts.lpad_run import get_lp
from fireworks.fw_config import CONFIG_FILE_DIR
from dbquery import db_select

def query():
    m_description = 'A command line interface to query FireWorks'
    parser = ArgumentParser(description=m_description)
    parser.add_argument('-o', '--output', choices=['json', 'yaml'],
                        default='json', type=lambda s: s.lower(),
                        help='Set output format: json or yaml.')
    parser.add_argument('-c', '--config_dir',
                        help='path to configuration file (if -l unspecified)',
                        default=CONFIG_FILE_DIR)
    parser.add_argument('-l', '--launchpad_file',
                        help='path to launchpad file', default=None)
    parser.add_argument('-f', '--query_file', required=True,
                        help='path to query file')
    args = parser.parse_args()

    dumpf = yaml.dump if args.output == 'yaml' else json.dumps
    dumpkw = {'yaml': {'default_flow_style': False},
              'json': {'sort_keys': True, 'indent': 2,
                       'separators': (',', ': ')}}

    fmt = args.query_file.split('.')[-1]
    assert fmt in ['json', 'yaml']
    with open(args.query_file, 'r') as inp:
        query_dict = json.load(inp) if fmt == 'json' else yaml.safe_load(inp)
    assert query_dict is not None, 'empty query not allowed'
    print(dumpf(db_select(get_lp(args), **query_dict), **dumpkw[args.output]))
