# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 14:58:18 2021

@author: jvorsten
"""

# Python imports
import argparse
import os
import sys

# Third party imports

# Local imports
from trendreview.ddvav import DDVAVRules
from trendreview.GraphAll import GraphAll
from trendreview.reporting import FDDImageGeneration, FDDReporting
from trendreview.FDDExceptions import FDDException

# Declarations
SUPPORTED_EQUIPMENT = ['ddvav', 'GraphAll']
description = """
Fault Diagnostics and Detection for trend review of mechanical equipment
"""
DESCRIPTION_GRAPH_COLUMNS = """
Only graph the specified columns on the dependent axis when 
using the "GraphAll" option. Specify column header names with 
a space between each name. To graph all columns omit this argument.
"""
DESCRIPTION_SUPPORTED_EQUIPMENT = f"""
Type of mechanical equipment being trended. Must
be one of {SUPPORTED_EQUIPMENT}. Use GraphAll to create a graph of every
data column versus the primary axis (default: DateTime).
"""
parser = argparse.ArgumentParser(description=description)
parser.add_argument('--filepath', '-f', type=os.path.abspath,
                    required=True, dest='filepath',
                    help='file path to trended data in CSV format')
parser.add_argument('--type', '-t', type=str,
                    choices=SUPPORTED_EQUIPMENT, required=True,
                    dest='type',
                    help=DESCRIPTION_SUPPORTED_EQUIPMENT)
parser.add_argument('--report-path', type=argparse.FileType('w', encoding='utf-8'),
                    required=False, default='./report.txt',
                    dest='log_filepath',
                    help='Filename to save report, like c:/path/to/report.txt')
parser.add_argument('--datetime-header', type=str,
                    required=False, dest='independent_axis_name',
                    help=('Header label of independent axis used to graph data ' +
                          'against. Use to override default value of "DateTime".'),
                    default='DateTime')
parser.add_argument('--graph-columns', type=str, action='extend', nargs='+',
                    dest='graph_columns', default=None,
                    required=False, help=DESCRIPTION_GRAPH_COLUMNS)

# %%


def main(parser: argparse.ArgumentParser):
    """Entrypoint
    Parse user arguments and being based on arguments"""
    # Parse arguments
    namespace = parser.parse_args()
    filepath = os.path.abspath(namespace.filepath)
    equipment_type = namespace.type
    log_filepath = os.path.abspath(namespace.log_filepath.name)
    namespace.log_filepath.close()
    independent_axis_name = namespace.independent_axis_name
    graph_columns = namespace.graph_columns  # List

    # Review data and run report
    reporter = FDDReporting(log_filepath=log_filepath)

    # Apply fault detection rules for dual duct terminal unit and create report
    if equipment_type == 'ddvav':
        ddvavRules = DDVAVRules(filepath)
        methods = ddvavRules.get_rules()
        for method in methods:
            try:
                method(ddvavRules.data)
            except FDDException as e:
                reporter.log_exception(e, create_image=True)

    # Do not apply fault detection rules for any equipment
    # Create report and graph all data versus 'DateTime'
    if equipment_type == 'GraphAll':
        # Possilbe configuration in the future
        dependent_axis_names = graph_columns  # List of names
        # Load data
        graphall = GraphAll(filepath, parse_dates=independent_axis_name)
        graphall.graph_all_data(
            reporter, independent_axis_name, dependent_axis_names)

    return None


if __name__ == '__main__':
    sys.exit(main(parser))
