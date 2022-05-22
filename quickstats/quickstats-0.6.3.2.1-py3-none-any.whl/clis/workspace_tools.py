import os
import click

from .core import DelimitedStr

@click.command(name='build_xml_ws')
@click.option('-i', '--filename', 'source', required=True, 
              help='Input xml file.')
@click.option('--binned/--unbinned', 'use_binned', default=False, show_default=True,
              help='Fit to binned data.')
@click.option('--data_storage_type', default="vector", show_default=True, 
              type=click.Choice(['vector', 'tree', 'composite']),
              help='Set RooAbsData StorageType. Available choices: "vector", "tree", "composite".')
@click.option('-d', '--basedir', default=None, 
              help='Base directory to which files in the xmls are referenced. '
                   'By default, the directory of the input xml file is used.')
@click.option('-t', '--minimizer_type', default="Minuit2", show_default=True,
              help='Minimizer type')
@click.option('-a', '--minimizer_algo', default="Migrad", show_default=True,
              help='Minimizer algorithm')
@click.option('-c', '--num_cpu', type=int, default=1, show_default=True,
              help='Number of CPUs to use per parameter')
@click.option('-e', '--eps', type=float, default=1.0, show_default=True,
              help='Convergence criterium')
@click.option('--retry', type=int, default=0, show_default=True,
              help='Maximum number of retries upon a failed fit')
@click.option('--strategy', type=int, default=1, show_default=True,
              help='Default minimization strategy')
@click.option('--print_level', type=int, default=-1, show_default=True,
              help='Minimizer print level')
@click.option('--fix-cache/--no-fix-cache', default=True, show_default=True,
              help='Fix StarMomentMorph cache')
@click.option('--fix-multi/--no-fix-cache',  default=True, show_default=True,
              help='Fix MultiPdf level 2')
@click.option('--max_calls', type=int, default=-1, show_default=True,
              help='Maximum number of function calls')
@click.option('--max_iters', type=int, default=-1, show_default=True,
              help='Maximum number of Minuit iterations')
@click.option('--optimize', type=int, default=2, show_default=True,
              help='Optimize constant terms')
@click.option('--offset/--no-offset', default=True, show_default=True,
              help='Offset likelihood')
@click.option('-v', '--verbosity',  default="INFO", show_default=True,
              help='verbosity level ("DEBUG", "INFO", "WARNING", "ERROR")')
def build_xml_ws(**kwargs):
    """
    Build workspace from XML config files
    """
    _kwargs = {}
    for arg_name in ["source", "use_binned", "data_storage_type",
                     "basedir", "verbosity"]:
        _kwargs[arg_name] = kwargs.pop(arg_name)
    _kwargs['minimizer_config'] = kwargs
    from quickstats.components.workspaces import XMLWSBuilder
    builder = XMLWSBuilder(**_kwargs)
    builder.generate_workspace()
    
@click.command(name='modify_ws')
@click.option('-i', '--filename', 'source', required=True, 
              help='Input xml/json file.')
@click.option('-t', '--minimizer_type', default="Minuit2", show_default=True,
              help='Minimizer type')
@click.option('-a', '--minimizer_algo', default="Migrad", show_default=True,
              help='Minimizer algorithm')
@click.option('-c', '--num_cpu', type=int, default=1, show_default=True,
              help='Number of CPUs to use per parameter')
@click.option('-e', '--eps', type=float, default=1.0, show_default=True,
              help='Convergence criterium')
@click.option('--retry', type=int, default=0, show_default=True,
              help='Maximum number of retries upon a failed fit')
@click.option('--strategy', type=int, default=1, show_default=True,
              help='Default minimization strategy')
@click.option('--print_level', type=int, default=-1, show_default=True,
              help='Minimizer print level')
@click.option('--fix-cache/--no-fix-cache', default=True, show_default=True,
              help='Fix StarMomentMorph cache')
@click.option('--fix-multi/--no-fix-cache',  default=True, show_default=True,
              help='Fix MultiPdf level 2')
@click.option('--max_calls', type=int, default=-1, show_default=True,
              help='Maximum number of function calls')
@click.option('--max_iters', type=int, default=-1, show_default=True,
              help='Maximum number of Minuit iterations')
@click.option('--optimize', type=int, default=2, show_default=True,
              help='Optimize constant terms')
@click.option('--offset/--no-offset', default=True, show_default=True,
              help='Offset likelihood')
@click.option('-v', '--verbosity',  default="INFO", show_default=True,
              help='verbosity level ("DEBUG", "INFO", "WARNING", "ERROR")')
def modify_ws(**kwargs):
    """
    Modify workspace from XML/json config files
    """
    _kwargs = {}
    for arg_name in ["source", "verbosity"]:
        _kwargs[arg_name] = kwargs.pop(arg_name)
    _kwargs['minimizer_config'] = kwargs
    from quickstats.components.workspaces import XMLWSModifier
    modifier = XMLWSModifier(**_kwargs)
    modifier.create_modified_workspace()
    
kItemChoices = ['workspace', 'dataset', 'category', 'snapshot', 'pdf',
                'function', 'poi', 'nuisance_parameter', 'global_observables',
                'constrained_nuisance_parameter', 'unconstrained_nuisance_parameter',
                'auxiliary']
kDefaultItems = ",".join(['workspace', 'dataset', 'category', 'poi', 'pdf',
                          'function', 'nuisance_parameter', 'global_observable',
                          'auxiliary'])
kDefaultVisibility = ",".join(["workspace=0b11001", "category=0b10011", "snapshot=0b10011",
                               "dataset=0b11011", "pdf=0b01011", "function=0b01011" , "poi=0b01011",
                               "nuisance_parameter=0b01011", "global_observable=0b01011", "auxiliary=0b01011"])

@click.command(name='compare_ws')
@click.option('-l', '--left', required=True, 
              help='Path to the input workspace file (left of comparison).')
@click.option('-r', '--right', required=True, 
              help='Path to the input workspace file (right of comparison).')
@click.option('--items', cls=DelimitedStr, type=click.Choice(kItemChoices),
              default=kDefaultItems, show_default=True,
              help='Items to include in the comparison (seperated by commas).')
@click.option('--indent', default="   ", show_default=True,
              help='Indentation for each row.')
@click.option('--visibility', default=kDefaultVisibility, show_default=True,
              help='\b\n Set visibility of the items included in the comparison:'
                   '\b\n boolean mask for showing definitions of certain objects'
                   '\b\n 0b00001 = show definitions for unique objects'
                   '\b\n 0b00010 = show definitions for redefined objects'
                   '\b\n 0b00100 = show definitions for reconstituted objects'
                   '\b\n 0b01000 = show definitions for renamed/remapped objects'
                   '\b\n 0b10000 = show definitions for identical objects')
@click.option('--save_text', default=None,
              help='Save summary print out as a text file.')
@click.option('--save_json_data', default=None,
              help='Save comparison data as a json file.')
@click.option('--save_excel_data', default=None,
              help='Save comparison data as an excel file.')
@click.option('-v', '--verbosity',  default="INFO", show_default=True,
              help='verbosity level ("DEBUG", "INFO", "WARNING", "ERROR")')
def compare_ws(**kwargs):
    """
    Compare two workspace files
    """
    from quickstats.components.workspaces import WSComparer
    comparer = WSComparer(kwargs["left"], kwargs["right"], items=kwargs["items"],
                          visibility_map=kwargs["visibility"])
    comparer.load_data()
    comparer.process_data()
    summary_str = comparer.get_summary_str(indent=kwargs["indent"])
    print(summary_str)
    save_text = kwargs["save_text"]
    save_json_data = kwargs["save_json_data"]
    save_excel_data = kwargs["save_excel_data"]
    if save_text is not None:
        with open(save_text, "w") as f:
            f.write(summary_str)
    if save_json_data is not None:
        comparer.save_json(save_json_data)
    if save_excel_data is not None:
        comparer.save_excel(save_excel_data)