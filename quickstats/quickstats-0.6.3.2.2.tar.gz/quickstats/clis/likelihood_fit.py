import os
import json
import click

@click.command(name='likelihood_fit')
@click.option('-i', '--input_file', "filename", required=True, 
              help='Path to the input workspace file.')
@click.option('-o', '--outname', default='fit_result.json', show_default=True,
              help='Name of output file.')
@click.option('--display/--no-display', default=True, show_default=True,
              help='Display fit result.')
@click.option('--save/--no-save', "save_result", default=False, show_default=True,
              help='Save fit result')
@click.option('--save_log/--skip_log', default=False, show_default=True,
              help='Save log file')
@click.option('--save_ws', default=None, show_default=True,
              help='Save fitted workspace to a given path.')
@click.option('--save_snapshot', default=None, show_default=True,
              help='Save fitted values of all variables as a snapshot and restore all variables to '
              'their initial values. Should be used together with --save_ws.')
@click.option('--outdir', default="pulls", show_default=True,
              help='Output directory for pulls output')
@click.option('--export_as_np_pulls/--skip_export_as_np_pulls', default=False, show_default=True,
              help='Export (constrained) NP results for pulls plot')
@click.option('-w', '--workspace', 'ws_name', default=None, show_default=True,
              help='Name of workspace. Auto-detect by default.')
@click.option('-m', '--model_config', 'mc_name', default=None, show_default=True,
              help='Name of model config. Auto-detect by default.')
@click.option('-d', '--data', 'data_name', default='combData', show_default=True,
              help='Name of dataset.')
@click.option('-s', '--snapshot', 'snapshot_name', default=None, show_default=True,
              help='Name of initial snapshot')
@click.option('-r', '--profile', 'profile_param', default="", show_default=True,
              help='Parameters to profile')
@click.option('-f', '--fix', 'fix_param', default="", show_default=True,
              help='Parameters to fix')
@click.option('--constrain/--no-constrain', 'constrain_nuis', default=True, show_default=True,
              help='Use constrained NLL (i.e. include systematics)')
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
@click.option('--hesse/--no-hesse', default=False, show_default=True,
              help='Evaluate errors using Hesse.')
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
@click.option('--batch_mode/--no-batch', default=False, show_default=True,
              help='Batch mode when evaluating likelihood')
@click.option('--int_bin_precision', type=float, default=-1., show_default=True,
              help='Integrate the PDF over the bins instead of using the probability '
                   'density at the bin centre')
@click.option('-v', '--verbosity', default='INFO', show_default=True,
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
              help='Verbosity level.')
def likelihood_fit(**kwargs):
    """
    Perform likelihood fit on a workspace
    """
    _kwargs = {}
    for arg_name in ["outname", "save_log", "display", "save_result",
                     "export_as_np_pulls", "outdir", "save_ws", "save_snapshot"]:
        _kwargs[arg_name] = kwargs.pop(arg_name)
    _init_kwargs = {}
    for arg_name in ["filename", "data_name", "verbosity"]:
        _init_kwargs[arg_name] = kwargs.pop(arg_name)
    _init_kwargs['config'] = kwargs
    _init_kwargs['poi_name'] = []
    from quickstats.components import AnalysisBase   
    if _kwargs['save_log']:
        from quickstats.concurrent.logging import standard_log
        log_path = os.path.splitext(_kwargs["outname"])[0] + ".log"
        with standard_log(log_path) as logger:
            analysis = AnalysisBase(**_init_kwargs)
            if _kwargs['export_as_np_pulls']:
                analysis.minimizer.configure(hesse=True)
            fit_result = analysis.nll_fit(mode=3)
        print(f"INFO: Saved fit log to `{log_path}`")
    else:
        analysis = AnalysisBase(**_init_kwargs)
        fit_result = analysis.nll_fit(mode=3)
    output = {}
    output['fit_result'] = fit_result
    df = {'pois':{}, 'nuisance_parameters':{}}
    analysis.load_snapshot("currentSnapshot")
    df['pois']['prefit'] = analysis.model.as_dataframe('pois')
    df['nuisance_parameters']['prefit'] = analysis.model.as_dataframe('nuisance_parameters')
    analysis.load_snapshot("nllFit")
    df['pois']['postfit'] = analysis.model.as_dataframe('pois')
    df['nuisance_parameters']['postfit'] = analysis.model.as_dataframe('nuisance_parameters')
    if _kwargs['display']:
        import pandas as pd
        pd.set_option('display.max_rows', None)
    for key in ['pois', 'nuisance_parameters']:
        df[key]['combined'] = df[key]['prefit'].drop(["value", "error"], axis=1)
        df[key]['combined']['value_prefit'] = df[key]['prefit']['value']
        df[key]['combined']['value_postfit'] = df[key]['postfit']['value']
        df[key]['combined']['error_prefit'] = df[key]['prefit']['error']
        df[key]['combined']['error_postfit'] = df[key]['postfit']['error']
        output[key] = df[key]['combined'].to_dict("list")
        if _kwargs['display']:
            print("{}:".format(key.title()))
            print(df[key]['combined'])
            print()
    if _kwargs['save_result']:
        import json
        with open(_kwargs["outname"], "w") as f:
            json.dump(output, f, indent=2)
        print(f"INFO: Saved fit result to `{_kwargs['outname']}`")
    if _kwargs['export_as_np_pulls']:
        outdir = _kwargs['outdir']
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        nuis_df = df[key]['combined'].drop(['min', 'max', 'is_constant', 'error_prefit'], axis=1)
        nuis_df = nuis_df.rename(columns={"value_prefit":"nuis_nom", "name":"nuisance", 
                                          "value_postfit":"nuis_hat", "error_postfit":"nuis_hi"})
        nuis_df["nuis_lo"] = nuis_df["nuis_hi"]
        nuis_df["nuis_prefit"] = 1.0
        nuis_df = nuis_df.set_index(['nuisance'])
        constrained_np = [i.GetName() for i in analysis.model.get_constrained_nuisance_parameters()]
        nuis_df = nuis_df.loc[constrained_np].reset_index()
        nuis_data = nuis_df.to_dict('index')
        import json
        for i in nuis_data:
            data = nuis_data[i]
            np_name = data['nuisance']
            outpath = os.path.join(outdir, f"{np_name}.json")
            with open(outpath, "w") as outfile:
                json.dump({"nuis": data}, outfile, indent=2)
    if _kwargs["save_ws"] is not None:
        filename = _kwargs["save_ws"]
        if _kwargs["save_snapshot"] is not None:
            snapshot_name = _kwargs["save_snapshot"]
            analysis.save_snapshot(snapshot_name)
            analysis.load_snapshot(analysis.kInitialSnapshotName)
        analysis.save(filename)
        
@click.command(name='np_correlation')
@click.option('-i', '--input_file', "filename", required=True, 
              help='Path to the input workspace file.')
@click.option('-o', '--basename', default='NP_correlation_matrix', show_default=True,
              help='Base name of the output.')
@click.option('--select', default=None, show_default=True,
              help='Select specific NPs to be stored in the final output (for json and plot only). '
                   'Use comma to separate the selection (wild card is supported).')
@click.option('--remove', default=None, show_default=True,
              help='Select specific NPs to be removed in the final output (for json and plot only). '
                   'Use comma to separate the selection (wild card is supported).')
@click.option('--save_plot/--no_save_plot', default=True, show_default=True,
              help='Save NP correlation matrix as a plot in pdf format')
@click.option('--save_json/--no_save_json', default=False, show_default=True,
              help='Save NP correlation matrix as a json file')
@click.option('--save_root/--no_save_root', default=False, show_default=True,
              help='Save NP correlation matrix as a 2D histogram in a root file')
@click.option('--plot_style', default="default", show_default=True,
              help='Plot style if save_plot is enabled. Choose between \"default\" and '
                   f'\"viridis\". Alternatively, a path to a yaml config file can be used')
@click.option('-w', '--workspace', 'ws_name', default=None, show_default=True,
              help='Name of workspace. Auto-detect by default.')
@click.option('-m', '--model_config', 'mc_name', default=None, show_default=True,
              help='Name of model config. Auto-detect by default.')
@click.option('-d', '--data', 'data_name', default='combData', show_default=True,
              help='Name of dataset.')
@click.option('-s', '--snapshot', 'snapshot_name', default=None, show_default=True,
              help='Name of initial snapshot')
@click.option('-r', '--profile', 'profile_param', default="", show_default=True,
              help='Parameters to profile')
@click.option('-f', '--fix', 'fix_param', default="", show_default=True,
              help='Parameters to fix')
@click.option('--constrain/--no-constrain', 'constrain_nuis', default=True, show_default=True,
              help='Use constrained NLL (i.e. include systematics)')
@click.option('-t', '--minimizer_type', default="Minuit2", show_default=True,
              help='Minimizer type')
@click.option('-a', '--minimizer_algo', default="Migrad", show_default=True,
              help='Minimizer algorithm')
@click.option('-c', '--num_cpu', type=int, default=1, show_default=True,
              help='Number of CPUs to use per parameter')
@click.option('-e', '--eps', type=float, default=1.0, show_default=True,
              help='Convergence criterium')
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
@click.option('--batch_mode/--no-batch', default=False, show_default=True,
              help='Batch mode when evaluating likelihood')
@click.option('--int_bin_precision', type=float, default=-1., show_default=True,
              help='Integrate the PDF over the bins instead of using the probability '
                   'density at the bin centre')
@click.option('-v', '--verbosity', default='INFO', show_default=True,
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
              help='Verbosity level.')
def np_correlation(**kwargs):
    """
    Evaluate post-fit NP correlation matrix
    """
    _kwargs = {}
    for arg_name in ["basename", "save_plot", "save_json", "save_root",
                     "plot_style", "select", "remove"]:
        _kwargs[arg_name] = kwargs.pop(arg_name)
    _init_kwargs = {}
    for arg_name in ["filename", "data_name", "verbosity"]:
        _init_kwargs[arg_name] = kwargs.pop(arg_name)
    _init_kwargs['config'] = kwargs
    _init_kwargs['poi_name'] = []
    from quickstats.components import AnalysisBase   
    analysis = AnalysisBase(**_init_kwargs)
    analysis.minimizer.configure(hesse=True)
    analysis.nll_fit(mode=3)
    fit_result = analysis.roofit_result
    basename = os.path.splitext(_kwargs['basename'])[0]
    from quickstats.utils.roofit_utils import get_correlation_matrix
    if _kwargs['save_root']:
        correlation_hist = get_correlation_matrix(fit_result, lib="root")
        outname = basename + ".root"
        correlation_hist.SaveAs(outname)
        print(f"INFO: Saved correlation histogram to `{outname}`")
        correlation_hist.Delete()
    from quickstats.utils.common_utils import filter_by_wildcards
    if _kwargs['save_json'] or _kwargs['save_plot']:
        df = get_correlation_matrix(fit_result, lib='pandas')
        labels = list(df.columns)
        selected = filter_by_wildcards(labels, _kwargs['select'])
        selected = filter_by_wildcards(selected, _kwargs['remove'], exclusion=True)
        to_drop = list(set(labels) - set(selected))
        df = df.drop(to_drop, axis=0).drop(to_drop, axis=1)
        if _kwargs['save_json']:
            data = df.to_dict()
            outname = basename + ".json"
            with open(outname, "w") as out:
                json.dump(data, out, indent=2)
            print(f"INFO: Saved correlation data to `{outname}`")
        if _kwargs['save_plot']:
            import matplotlib.pyplot as plt
            from quickstats.plots import CorrelationPlot
            plotter = CorrelationPlot(df)
            ax = plotter.draw_style(_kwargs['plot_style'])
            outname = basename + ".pdf"
            plt.savefig(outname, bbox_inches="tight")
            print(f"INFO: Saved correlation plot to `{outname}`")