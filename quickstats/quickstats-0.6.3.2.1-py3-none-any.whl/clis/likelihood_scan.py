import os
import click

@click.command(name='likelihood_scan')
@click.option('-i', '--input_file', required=True, 
              help='Path to the input workspace file.')
@click.option('-p', '--param_expr', default=None,
              help='\b\n Parameter expression, e.g.'
                   '\b\n 1D scan: "poi_name=<poi_min>_<poi_max>_<step>"'
                   '\b\n 2D scan: "poi_1_name=<poi_1_min>_<poi_1_max>_<step_1>,'
                   '\b\n           poi_2_name=<poi_2_min>_<poi_2_max>_<step_2>"')
@click.option('--filter', 'filter_expr', default=None, show_default=True,
              help='\b Filter parameter points by expression.\n'
                   '\b Example: "mass=2*,350,400,450;klambda=1.*,2.*,-1.*,-2.*"\n'
                   '\b Refer to documentation for more information\n')
@click.option('--exclude', 'exclude_expr', default=None, show_default=True,
              help='\b Exclude parameter points by expression.\n'
                   '\b Example: "mass=2*,350,400,450;klambda=1.*,2.*,-1.*,-2.*"\n'
                   '\b Refer to documentation for more information\n')
@click.option('--min', 'poi_min', type=float, default=None, 
              help='(deprecated) Minimum POI value to scan.')
@click.option('--max', 'poi_max', type=float, default=None, 
              help='(deprecated) Maximum POI value to scan.')
@click.option('--step', 'poi_step', type=float, default=None, 
              help='(deprecated) Scan interval.')
@click.option('-p', '--poi', 'poi_name', default=None, show_default=True,
              help='(deprecated) POI to scan. If not specified, the first POI from the workspace is used.')
@click.option('--cache/--no-cache', default=True, show_default=True,
              help='Cache existing result.')
@click.option('-o', '--outname', default='{poi_names}.json', show_default=True,
              help='Name of output')
@click.option('--outdir', default='likelihood_scan', show_default=True,
              help='Output directory.')
@click.option('--save_log/--skip_log', default=True, show_default=True,
              help='Save log file.')
@click.option('-w', '--workspace', 'ws_name', default=None, show_default=True,
              help='Name of workspace. Auto-detect by default.')
@click.option('-m', '--model_config', 'mc_name', default=None, show_default=True,
              help='Name of model config. Auto-detect by default.')
@click.option('-d', '--data', 'data_name', default='combData', show_default=True,
              help='Name of dataset.')
@click.option('-s', '--snapshot', 'snapshot_name', default=None, show_default=True,
              help='Name of initial snapshot.')
@click.option('--uncond_snapshot', default=None, show_default=True,
              help='Name of snapshot with unconditional fit result.')
@click.option('-r', '--profile', 'profile_param', default="", show_default=True,
              help='Parameters to profile.')
@click.option('-f', '--fix', 'fix_param', default="", show_default=True,
              help='Parameters to fix.')
@click.option('--constrain/--no-constrain', 'constrain_nuis', default=True, show_default=True,
              help='Use constrained NLL (i.e. include systematics).')
@click.option('-t', '--minimizer_type', default="Minuit2", show_default=True,
              help='Minimizer type.')
@click.option('-a', '--minimizer_algo', default="Migrad", show_default=True,
              help='Minimizer algorithm.')
@click.option('-c', '--num_cpu', type=int, default=1, show_default=True,
              help='Number of CPUs to use per parameter.')
@click.option('--binned/--unbinned', 'binned_likelihood', default=True, show_default=True,
              help='Binned likelihood.')
@click.option('-e', '--eps', type=float, default=1.0, show_default=True,
              help='Convergence criterium.')
@click.option('--retry', type=int, default=0, show_default=True,
              help='Maximum number of retries upon a failed fit.')
@click.option('--strategy', type=int, default=1, show_default=True,
              help='Default minimization strategy.')
@click.option('--print_level', type=int, default=-1, show_default=True,
              help='Minimizer print level.')
@click.option('--fix-cache/--no-fix-cache', default=True, show_default=True,
              help='Fix StarMomentMorph cache.')
@click.option('--fix-multi/--no-fix-cache',  default=True, show_default=True,
              help='Fix MultiPdf level 2.')
@click.option('--max_calls', type=int, default=-1, show_default=True,
              help='Maximum number of function calls.')
@click.option('--max_iters', type=int, default=-1, show_default=True,
              help='Maximum number of Minuit iterations.')
@click.option('--optimize', type=int, default=2, show_default=True,
              help='Optimize constant terms.')
@click.option('--offset/--no-offset', default=True, show_default=True,
              help='Offset likelihood.')
@click.option('-v', '--verbosity', default='INFO', show_default=True,
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
              help='Verbosity level.')
@click.option('--parallel', type=int, default=-1, show_default=True,
              help='\b\n Parallelize job across the N workers.'
                   '\b\n Case  0: Jobs are run sequentially (for debugging).'
                   '\b\n Case -1: Jobs are run across N_CPU workers.')
def likelihood_scan(**kwargs):
    """
    Evaluate a set of parmeterised likelihood values
    """
    _kwargs = {}
    for arg_name in ["input_file", "param_expr", "data_name", "outdir", "filter_expr", "uncond_snapshot",
                     "exclude_expr", "outname", "cache", "save_log", "parallel", "verbosity"]:
        _kwargs[arg_name] = kwargs.pop(arg_name)
    _kwargs['config'] = kwargs
    
    # for backward compatibility
    _deprecated_kwargs = {}
    for arg_name in ["poi_min", "poi_max", "poi_step", "poi_name"]:
        _deprecated_kwargs[arg_name] = kwargs.pop(arg_name)
    if all(_deprecated_kwargs[arg_name] is not None for arg_name in ["poi_min", "poi_max", "poi_step"]):
        if _kwargs['param_expr'] is not None:
            raise RuntimeError("either `param_expr` or (`poi_min`, `poi_max`, `poi_step`) should be "
                               "given for 1D likelihood scan")
        print("WARNING: Likelihood scan using `poi_min`, `poi_max` and `poi_step` is "
              "deprecated. Use --param_expr \"<poi_name>=<poi_min>_<poi_max>_<poi_step>\" instead.")
        from quickstats.components import AnalysisBase
        analysis = AnalysisBase(_kwargs['input_file'], poi_name=_deprecated_kwargs['poi_name'],
                                data_name=_kwargs['data_name'], verbosity="WARNING")
        poi_name = analysis.poi.GetName()
        poi_min = _deprecated_kwargs['poi_min']
        poi_max = _deprecated_kwargs['poi_max']
        poi_step = _deprecated_kwargs['poi_step']
        _kwargs['param_expr'] = f"{poi_name}={poi_min}_{poi_max}_{poi_step}"
    elif (not all(_deprecated_kwargs[arg_name] is None for arg_name in ["poi_min", "poi_max", "poi_step"])) or \
         (_kwargs['param_expr'] is None):
        raise RuntimeError("either `param_expr` or (`poi_min`, `poi_max`, `poi_step`) should be "
                           "given for 1D likelihood scan")
    from quickstats.concurrent import ParameterisedLikelihood
    runner = ParameterisedLikelihood(**_kwargs)
    runner.run()
