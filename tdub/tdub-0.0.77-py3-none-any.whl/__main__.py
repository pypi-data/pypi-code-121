"""tdub command line interface."""

from __future__ import annotations

# stdlib
import json
import logging
import os
import shutil
from pathlib import PosixPath

# third party
import click

# tdub
from tdub import setup_logging

setup_logging()
log = logging.getLogger("tdub-cli")


@click.group(context_settings=dict(max_content_width=82, help_option_names=['-h', '--help']))
def cli():
    """Top Level CLI function."""
    pass


@cli.group("train")
def train():
    """Tasks to perform machine learning steps."""
    pass


@cli.group("apply")
def cli_apply():
    """Tasks to apply machine learning models to data."""
    pass


@cli.group("rex")
def rex():
    """Tasks interacting with TRExFitter results."""
    pass


@cli.group("misc")
def misc():
    """Tasks under a miscellaneous umbrella."""


@train.command("prep")
@click.argument("datadir", type=click.Path(resolve_path=True, exists=True))
@click.argument("region", type=click.Choice(["1j1b", "2j1b", "2j2b"]))
@click.argument("outdir", type=click.Path(resolve_path=True))
@click.option("-p", "--pre-exec", type=click.Path(resolve_path=True), help="Python code to pre-execute")
@click.option("-n", "--nlo-method", type=str, default="DR", help="tW simluation NLO method", show_default=True)
@click.option("-x", "--override-selection", type=str, help="override selection with contents of file")
@click.option("-t", "--use-tptrw", is_flag=True, help="apply top pt reweighting")
@click.option("-r", "--use-trrw", is_flag=True, help="apply top recursive reweighting")
@click.option("-i", "--ignore-list", type=str, help="variable ignore list file")
@click.option("-m", "--multiple-ttbar-samples", is_flag=True, help="use multiple ttbar MC samples")
@click.option("-a", "--use-inc-af2", is_flag=True, help="use inclusive af2 samples")
@click.option("-f", "--bkg-sample-frac", type=float, help="use a fraction of the background")
@click.option("-d", "--use-dilep", is_flag=True, help="train with dilepton samples")
def train_prep(
    datadir,
    region,
    outdir,
    pre_exec,
    nlo_method,
    override_selection,
    use_tptrw,
    use_trrw,
    ignore_list,
    multiple_ttbar_samples,
    use_inc_af2,
    bkg_sample_frac,
    use_dilep,
):
    """Prepare data for training."""
    if pre_exec is not None:
        exec(PosixPath(pre_exec).read_text())

    from tdub.ml_train import prepare_from_root, persist_prepared_data
    from tdub.data import avoids_for, quick_files
    from tdub.frames import drop_cols

    qf = quick_files(datadir)
    sig_files = qf[f"tW_{nlo_method}"] if use_dilep else qf[f"tW_{nlo_method}_inc"]
    if multiple_ttbar_samples:
        bkg_files = qf["ttbar_inc_AFII"] + qf["ttbar_PS"]
    elif use_inc_af2:
        sig_files = qf[f"tW_{nlo_method}_inc_AFII"]
        bkg_files = qf["ttbar_inc_AFII"]
    else:
        bkg_files = qf["ttbar"] if use_dilep else qf["ttbar_inc"]

    override_sel = override_selection
    if override_sel:
        override_sel = PosixPath(override_sel).read_text().strip()
    df, y, w = prepare_from_root(
        sig_files,
        bkg_files,
        region,
        weight_mean=1.0,
        override_selection=override_sel,
        use_tptrw=use_tptrw,
        use_trrw=use_trrw,
        bkg_sample_frac=bkg_sample_frac,
    )
    drop_cols(df, *avoids_for(region))
    if ignore_list:
        drops = PosixPath(ignore_list).read_text().strip().split()
        drop_cols(df, *drops)
    outdir = PosixPath(outdir)
    persist_prepared_data(outdir, df, y, w)
    (outdir / "region.txt").write_text(f"{region}\n")
    (outdir / "nlo_method.txt").write_text(f"{nlo_method}\n")
    (outdir / "files_sig.txt").write_text("{}\n".format("\n".join(sig_files)))
    (outdir / "files_bkg.txt").write_text("{}\n".format("\n".join(bkg_files)))


@train.command("single")
@click.argument("datadir", type=click.Path(resolve_path=True, exists=True))
@click.argument("outdir", type=click.Path(resolve_path=True))
@click.option("-p", "--pre-exec", type=click.Path(exists=True, resolve_path=True), help="Python code to pre-execute")
@click.option("-s", "--test-size", type=float, default=0.40, help="training test size", show_default=True)
@click.option("-e", "--early-stop", type=int, default=10, help="number of early stopping rounds", show_default=True)
@click.option("-k", "--use-sklearn", is_flag=True, help="use sklearn instead of lgbm")
@click.option("-g", "--use-xgboost", is_flag=True, help="use xgboost instead of lgbm")
@click.option("-l", "--learning-rate", type=float, default=0.1, help="learning_rate model parameter", show_default=True)
@click.option("-n", "--num-leaves", type=int, default=16, help="num_leaves model parameter", show_default=True)
@click.option("-m", "--min-child-samples", type=int, default=500, help="min_child_samples model parameter", show_default=True)
@click.option("-d", "--max-depth", type=int, default=5, help="max_depth model parameter", show_default=True)
@click.option("-r", "--reg-lambda", type=float, default=0, help="lambda (L2) regularization", show_default=True)
@click.option("-a", "--auto-region", is_flag=True, help="Use parameters associated with region", show_default=True)
def train_single(
    datadir,
    outdir,
    pre_exec,
    test_size,
    early_stop,
    use_sklearn,
    use_xgboost,
    learning_rate,
    num_leaves,
    min_child_samples,
    max_depth,
    reg_lambda,
    auto_region,
):
    """Execute single training round."""
    if pre_exec is not None:
        exec(PosixPath(pre_exec).read_text())

    from tdub.ml_train import single_training
    import pandas as pd
    import numpy as np

    datadir = PosixPath(datadir)
    df = pd.read_hdf(datadir / "df.h5", "df")
    y = np.load(datadir / "labels.npy")
    w = np.load(datadir / "weights.npy")
    df.selection_used = (
        datadir / "selection.txt"
    ).read_text().strip()
    extra_sum = {
        "region": PosixPath(datadir / "region.txt").read_text().strip(),
        "nlo_method": PosixPath(datadir / "nlo_method.txt").read_text().strip(),
    }

    train_axes = dict(
        learning_rate=learning_rate,
        num_leaves=num_leaves,
        min_child_samples=min_child_samples,
        max_depth=max_depth,
        reg_lambda=reg_lambda,
    )

    if auto_region:
        from tdub.ml_train import default_bdt_parameters
        train_axes = default_bdt_parameters(extra_sum["region"])
    else:
        train_axes = dict(
            learning_rate=learning_rate,
            num_leaves=num_leaves,
            min_child_samples=min_child_samples,
            max_depth=max_depth,
            reg_lambda=reg_lambda,
        )

    single_training(
        df,
        y,
        w,
        train_axes,
        outdir,
        test_size=test_size,
        early_stopping_rounds=early_stop,
        extra_summary_entries=extra_sum,
        use_sklearn=use_sklearn,
        use_xgboost=use_xgboost,
    )


@train.command("scan")
@click.argument("datadir", type=click.Path(exists=True, resolve_path=True))
@click.argument("workspace", type=click.Path(exists=False))
@click.option("-p", "--pre-exec", type=click.Path(resolve_path=True), help="Python code to pre-execute")
@click.option("-e", "--early-stop", type=int, default=10, help="number of early stopping rounds", show_default=True)
@click.option("-s", "--test-size", type=float, default=0.40, help="training test size", show_default=True)
@click.option("--overwrite", is_flag=True, help="overwrite existing workspace")
@click.option("--and-submit", is_flag=True, help="submit the condor jobs")
def train_scan(
    datadir,
    workspace,
    pre_exec,
    early_stop,
    test_size,
    overwrite,
    and_submit,
):
    """Perform a parameter scan via condor jobs.

    DATADIR points to the intput ROOT files, training is performed on
    the REGION and all output is saved to WORKSPACE.

    $ tdub train scan /data/path 2j2b scan_2j2b

    """
    if pre_exec is not None:
        exec(PosixPath(pre_exec).read_text())

    from tdub.batch import create_condor_workspace
    import tdub.config
    import itertools

    ws = create_condor_workspace(workspace, overwrite=overwrite)
    (ws / "res").mkdir()

    runs = []
    i = 0
    if pre_exec is None:
        pre_exec = "_NONE"
    else:
        pre_exec = str(PosixPath(pre_exec).resolve())

    pd = tdub.config.DEFAULT_SCAN_PARAMETERS
    itr = itertools.product(
        pd.get("max_depth"),
        pd.get("num_leaves"),
        pd.get("learning_rate"),
        pd.get("min_child_samples"),
        pd.get("reg_lambda"),
    )

    log.info("Scan grid:")
    log.info(" - max_depth: {}".format(pd.get("max_depth")))
    log.info(" - num_leaves: {}".format(pd.get("num_leaves")))
    log.info(" - learning_rate: {}".format(pd.get("learning_rate")))
    log.info(" - min_child_samples: {}".format(pd.get("min_child_samples")))
    log.info(" - reg_lambda: {}".format(pd.get("reg_lambda")))

    for (max_depth, num_leaves, learning_rate, min_child_samples, reg_lambda) in itr:
        suffix = "{}-{}-{}-{}-{}".format(
            max_depth, num_leaves, learning_rate, min_child_samples, reg_lambda,
        )
        outdir = ws / "res" / f"{i:04d}_{suffix}"
        arglist = (
            "{} {} -p {} -s {} "
            "--learning-rate {} "
            "--num-leaves {} "
            "--min-child-samples {} "
            "--max-depth {} "
            "--reg-lambda {} "
            "--early-stop {} "
        ).format(
            datadir,
            outdir,
            pre_exec,
            test_size,
            learning_rate,
            num_leaves,
            min_child_samples,
            max_depth,
            reg_lambda,
            early_stop,
        )
        arglist = arglist.replace("-p _NONE ", "")
        runs.append(arglist)
        i += 1

    with (ws / "run.sh").open("w") as outscript:
        print("#!/bin/bash\n\n", file=outscript)
        for run in runs:
            print(f"tdub train single {run}\n", file=outscript)
    os.chmod(ws / "run.sh", 0o755)

    import pycondor

    condor_dag = pycondor.Dagman(name="dag_train_scan", submit=str(ws / "sub"))
    condor_job_scan = pycondor.Job(
        name="job_train_scan",
        universe="vanilla",
        getenv=True,
        notification="Error",
        extra_lines=["notify_user = ddavis@phy.duke.edu"],
        executable=shutil.which("tdub"),
        submit=str(ws / "sub"),
        error=str(ws / "err"),
        output=str(ws / "out"),
        log=str(ws / "log"),
        dag=condor_dag,
    )
    for run in runs:
        condor_job_scan.add_arg(f"train single {run}")
    condor_job_check = pycondor.Job(
        name="job_train_check",
        universe="vanilla",
        getenv=True,
        notification="Error",
        extra_lines=["notify_user = ddavis@phy.duke.edu"],
        executable=shutil.which("tdub"),
        submit=str(ws / "sub"),
        error=str(ws / "err"),
        output=str(ws / "out"),
        log=str(ws / "log"),
        dag=condor_dag,
    )
    condor_job_check.add_arg(f"train check {ws}")
    condor_job_check.add_parent(condor_job_scan)

    if and_submit:
        condor_dag.build_submit()
    else:
        condor_dag.build()

    # log.info(f"prepared {len(runs)} jobs for submission")
    # with (ws / "condor.sub").open("w") as f:
    #     condor_preamble(ws, shutil.which("tdub"), memory="2GB", GetEnv=True, to_file=f)
    #     for run in runs:
    #         add_condor_arguments(f"train-single {run}", f)
    # if and_submit:
    #     condor_submit(workspace)

    return 0


@train.command("check")
@click.argument("workspace", type=click.Path(exists=True))
@click.option("-p", "--print-top", is_flag=True, help="Print the top results")
@click.option("-n", "--n-res", type=int, default=10, help="Number of top results to print", show_default=True)
def train_check(workspace, print_top, n_res):
    """Check the results of a parameter scan WORKSPACE."""
    from tdub.ml_train import SingleTrainingSummary
    import shutil

    results = []
    top_dir = PosixPath(workspace)
    resdirs = (top_dir / "res").iterdir()
    for resdir in resdirs:
        if resdir.name == "logs" or not resdir.is_dir():
            continue
        summary_file = resdir / "summary.json"
        if not summary_file.exists():
            log.warn("no summary file for %s" % str(resdir))
        with summary_file.open("r") as f:
            summary = json.load(f)
            if summary["bad_ks"]:
                continue
            res = SingleTrainingSummary(**summary)
            res.workspace = resdir
            res.summary = summary
            results.append(res)

    auc_sr = sorted(results, key=lambda r: -r.auc)
    ks_pvalue_sr = sorted(results, key=lambda r: -r.ks_pvalue_sig)
    max_auc_rounded = str(round(auc_sr[0].auc, 2))

    potentials = []
    for res in ks_pvalue_sr:
        curauc = str(round(res.auc, 2))
        if curauc == max_auc_rounded and res.ks_pvalue_bkg > 0.95:
            potentials.append(res)
        if len(potentials) > 15:
            break

    for result in potentials:
        print(result)

    best_res = potentials[0]
    if os.path.exists(top_dir / "best"):
        shutil.rmtree(top_dir / "best")
    shutil.copytree(best_res.workspace, top_dir / "best")
    print(best_res.workspace.name)
    print(best_res.summary)

    return 0


@train.command("fold")
@click.argument("scandir", type=click.Path(exists=True))
@click.argument("datadir", type=click.Path(exists=True))
@click.option("-t", "--use-tptrw", is_flag=True, help="use top pt reweighting")
@click.option("-n", "--n-splits", type=int, default=3, help="number of splits for folding", show_default=True)
def train_fold(scandir, datadir, use_tptrw, n_splits):
    """Perform a folded training based on a hyperparameter scan result."""
    from tdub.ml_train import folded_training, prepare_from_root
    from tdub.data import quick_files

    scandir = PosixPath(scandir).resolve()
    summary_file = scandir / "best" / "summary.json"
    outdir = scandir / "foldres"
    if outdir.exists():
        log.warn(f"fold result already exists for {scandir}, exiting")
        return 0
    summary = None
    with summary_file.open("r") as f:
        summary = json.load(f)
    nlo_method = summary["nlo_method"]
    best_iteration = summary["best_iteration"]
    if best_iteration > 0:
        summary["all_params"]["n_estimators"] = best_iteration
    region = summary["region"]
    branches = summary["features"]
    selection = summary["selection_used"]
    qf = quick_files(datadir)
    df, y, w = prepare_from_root(
        qf[f"tW_{nlo_method}"],
        qf["ttbar"],
        region,
        override_selection=selection,
        branches=branches,
        weight_mean=1.0,
        use_tptrw=use_tptrw,
    )
    folded_training(
        df,
        y,
        w,
        summary["all_params"],
        {"verbose": 10},
        str(outdir),
        summary["region"],
        kfold_kw={"n_splits": n_splits, "shuffle": True},
    )
    return 0


@cli_apply.command("single")
@click.argument("infile", type=click.Path(exists=True))
@click.argument("arrname", type=str)
@click.argument("outdir", type=click.Path())
@click.option("-f", "--fold-results", type=click.Path(exists=True), multiple=True, help="fold output directories")
@click.option("-s", "--single-results", type=click.Path(exists=True), multiple=True, help="single result dirs")
def apply_single(infile, arrname, outdir, fold_results=None, single_results=None):
    """Generate BDT response array for INFILE and save to .npy file.

    We generate the .npy files using either single training results
    (-s flag) or folded training results (-f flag).

    """
    if len(single_results) > 0 and len(fold_results) > 0:
        raise ValueError("Cannot use -f and -s together with apply-single")

    from tdub.ml_apply import build_array, FoldedTrainSummary, SingleTrainSummary
    from tdub.data import SampleInfo
    from tdub.data import selection_branches
    from tdub.frames import raw_dataframe
    import numpy as np

    outdir = PosixPath(outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    trs = None
    if len(fold_results) > 0:
        trs = [FoldedTrainSummary(p) for p in fold_results]
    elif len(single_results) > 0:
        trs = [SingleTrainSummary(p) for p in single_results]
    else:
        raise ValueError("-f or -s required")

    necessary_branches = ["OS", "elmu", "reg2j1b", "reg2j2b", "reg1j1b"]
    for res in trs:
        necessary_branches += res.features
        necessary_branches += selection_branches(res.selection_used)
    necessary_branches = sorted(set(necessary_branches), key=str.lower)

    log.info("Loading necessary branches:")
    for nb in necessary_branches:
        log.info(f" - {nb}")

    stem = PosixPath(infile).stem
    sampinfo = SampleInfo(stem)
    tree = f"WtLoop_{sampinfo.tree}"
    log.info(f"Using tree {tree}")
    df = raw_dataframe(infile, tree=tree, branches=necessary_branches)
    npyfilename = outdir / f"{stem}.{arrname}.npy"
    result_arr = build_array(trs, df)
    np.save(npyfilename, result_arr)


@cli_apply.command("all")
@click.argument("datadir", type=click.Path(exists=True))
@click.argument("arrname", type=str)
@click.argument("outdir", type=click.Path(resolve_path=True))
@click.argument("workspace", type=click.Path())
@click.option("-f", "--fold-results", type=click.Path(exists=True, resolve_path=True), multiple=True, help="fold output directories")
@click.option("-s", "--single-results", type=click.Path(exists=True, resolve_path=True), multiple=True, help="single result dirs")
@click.option("--and-submit", is_flag=True, help="submit the condor jobs")
def apply_all(
    datadir,
    arrname,
    outdir,
    workspace,
    fold_results=None,
    single_results=None,
    and_submit=False,
):
    """Generate BDT response arrays for all ROOT files in DATADIR."""
    import glob
    import shutil
    import pycondor

    if len(single_results) > 0 and len(fold_results) > 0:
        raise ValueError("Cannot use -f and -s together with apply-single")
    results_flags = None
    if len(fold_results) > 0:
        results_flags = "-f {}".format(" -f ".join(fold_results))
    elif len(single_results) > 0:
        results_flags = "-s {}".format(" -s ".join(single_results))
    else:
        raise ValueError("-f or -s required")

    ws = PosixPath(workspace).resolve()

    outpath = PosixPath(outdir).resolve()
    outpath.mkdir(exist_ok=True)

    datapath = PosixPath(datadir).resolve(strict=True)
    all_files = glob.glob(f"{datapath}/*.root")
    arglist = [f"{f} {arrname} {outpath} {results_flags}" for f in all_files]

    condor_dag = pycondor.Dagman(name="dag_train_scan", submit=str(ws / "sub"))
    condor_job_scan = pycondor.Job(
        name="job_apply_all",
        universe="vanilla",
        getenv=True,
        notification="Error",
        extra_lines=["notify_user = ddavis@phy.duke.edu"],
        executable=shutil.which("tdub"),
        submit=str(ws / "sub"),
        error=str(ws / "err"),
        output=str(ws / "out"),
        log=str(ws / "log"),
        dag=condor_dag,
    )
    for run in arglist:
        condor_job_scan.add_arg(f"apply single {run}")

    if and_submit:
        condor_dag.build_submit()
    else:
        condor_dag.build()


@train.command("itables")
@click.argument("summary-file", type=click.Path(exists=True))
def itables(summary_file):
    """Generate importance tables."""
    import tdub.config
    import json
    from textwrap import dedent
    tdub.config.init_meta_table()
    summary = json.loads(PosixPath(summary_file).read_text())
    imp_gain = summary["importances_gain"]
    imp_split = summary["importances_split"]
    names = imp_gain.keys()
    imp_gain = [round(x, 4) for x in imp_gain.values()]
    imp_split = [round(x, 4) for x in imp_split.values()]
    imp_gain, names, imp_split = (list(reversed(t)) for t in zip(*sorted(zip(imp_gain, names, imp_split))))
    print(dedent("""\
    \\begin{table}[htbp]
      \\begin{center}
        \\caption{XXX}
        \\label{XXX}
        \\begin{tabular}{lcc}
          \\toprule
          Variable & Importance (gain) & Importance (split) \\\\
          \\midrule"""))
    for n, g, s in zip(names, imp_gain, imp_split):
        print("      {} & {} & {} \\\\".format(tdub.config.PLOTTING_META_TABLE["titles"][n]["mpl"], g, s))
    print(dedent("""\
          \\bottomrule
        \\end{tabular}
      \\end{center}
    \\end{table}
    """))


@train.command("shapes")
@click.argument("datadir", type=click.Path(exists=True))
@click.option("-o", "--outdir", type=click.Path(), help="Directory to save output.")
def train_shapes(datadir, outdir):
    """Generate shape comparison plots."""
    if outdir is None:
        outdir = PosixPath.cwd()
    else:
        outdir = PosixPath(outdir)
        outdir.mkdir(exist_ok=True, parents=True)

    import tdub.internal.shapecomps as tdisc
    import tdub.ml_train as tdmlt
    import tdub.config
    tdub.config.init_meta_table()
    meta_table = tdub.config.PLOTTING_META_TABLE
    datadir = PosixPath(datadir)
    region = (datadir / "region.txt").read_text().strip()
    df, y, w = tdmlt.load_prepped(datadir)
    var_region_binning = tdmlt.var_and_binning_for_region(df, region, meta_table)
    for v, r, b in var_region_binning:
        tdisc.dist_comparison_plot(v, r, b, df, y, w, meta_table, outdir=outdir)


@rex.command("stacks")
@click.argument("rex-dir", type=click.Path(exists=True))
@click.option("--chisq/--no-chisq", default=True, help="Do or don't print chi-square information.")
@click.option("--internal/--no-internal", default=True, help="Do or don't include internal label.")
@click.option("--thesis/--no-thesis", default=False, help="Use thesis label")
@click.option("--png/--no-png", default=False, help="Also save PNG version of plots.")
@click.option("-n", "--n-test", type=int, default=-1, help="Test only n plots (for stacks).")
def rex_stacks(rex_dir, chisq, internal, thesis, png, n_test):
    """Generate plots from TRExFitter result."""
    import tdub.rex
    import tdub.config
    outdir = PosixPath(rex_dir) / "matplotlib"
    outdir.mkdir(exist_ok=True)
    tdub.config.init_meta_table()
    tdub.config.init_meta_logy()
    if thesis:
        tdub.config.IS_THESIS = True
    tdub.rex.plot_all_regions(
        rex_dir,
        outdir,
        stage="pre",
        show_chisq=chisq,
        n_test=n_test,
        internal=internal,
        thesis=thesis,
        save_png=png,
    )
    tdub.rex.plot_all_regions(
        rex_dir,
        outdir,
        stage="post",
        show_chisq=chisq,
        n_test=n_test,
        internal=internal,
        thesis=thesis,
        save_png=png,
    )
    return 0


@rex.command("impact")
@click.argument("rex-dir", type=click.Path(exists=True))
@click.option("--thesis", is_flag=True, help="Flat to use thesis label.")
def rex_impact(rex_dir, thesis):
    """Generate impact plot from TRExFitter result."""
    import tdub.rex
    tdub.rex.nuispar_impact_plot_top20(rex_dir, thesis=thesis)
    return 0


@rex.command("stabs")
@click.argument("umbrella", type=click.Path(exists=True))
@click.option("-o", "--outdir", type=click.Path(), help="Output directory.")
@click.option("-t", "--tests", type=str, multiple=True, help="Tests to run.")
def rex_stabs(umbrella, outdir, tests):
    """Generate stability tests based on rexpy output."""
    import tdub.rex
    if outdir is not None:
        outdir = PosixPath(outdir)
    if len(tests) == 0 or "all" in tests:
        tests = "all"
    tdub.rex.stability_test_standard(PosixPath(umbrella), outdir=outdir, tests=tests)


@rex.command("impstabs")
@click.argument("herwig704", type=click.Path(exists=True))
@click.argument("herwig713", type=click.Path(exists=True))
@click.option("-o", "--outdir", type=click.Path(), help="Output directory.")
def rex_impstabs(herwig704, herwig713, outdir):
    """Generate impact stability tests based on rexpy output."""
    import tdub.rex
    if outdir is not None:
        outdir = PosixPath(outdir)
    tdub.rex.stability_test_parton_shower_impacts(
        PosixPath(herwig704),
        PosixPath(herwig713),
        outdir=outdir,
    )


@rex.command("grimpacts")
@click.argument("rex-dir", type=click.Path(exists=True))
@click.option("--tablefmt", type=str, default="orgtbl", help="Format passed to tabulate.")
@click.option("--include-total", is_flag=True, help="Include FullSyst entry")
def rex_grimpacts(rex_dir, tablefmt, include_total):
    """Print summary of grouped impacts."""
    from tdub.rex import grouped_impacts_table
    print(grouped_impacts_table(rex_dir, tablefmt=tablefmt, include_total=include_total))


@rex.command("index")
@click.argument("rex-dir", type=click.Path(exists=True))
def rex_index(rex_dir):
    """Generate index.html file for the workspace."""
    from tdub.internal.rexindex import index_dot_html
    index_dot_html(rex_dir)


@misc.command("soverb")
@click.argument("datadir", type=click.Path(exists=True))
@click.argument("selections", type=click.Path(exists=True))
@click.option("-t", "--use-tptrw", is_flag=True, help="use top pt reweighting")
def misc_soverb(datadir, selections, use_tptrw):
    """Get signal over background using data in DATADIR and a SELECTIONS file.

    the format of the JSON entries should be "region": "numexpr selection".

    """
    from tdub.frames import raw_dataframe, apply_weight_tptrw, satisfying_selection
    from tdub.data import quick_files
    from tdub.data import selection_branches

    with open(selections) as f:
        selections = json.load(f)

    necessary_branches = set()
    for selection, query in selections.items():
        necessary_branches |= selection_branches(query)
    necessary_branches = list(necessary_branches) + ["weight_tptrw_tool"]

    qf = quick_files(datadir)
    bkg = qf["ttbar"] + qf["Diboson"] + qf["Zjets"] + qf["MCNP"]
    sig = qf["tW_DR"]

    sig_df = raw_dataframe(sig, branches=necessary_branches)
    bkg_df = raw_dataframe(bkg, branches=necessary_branches, entrysteps="1GB")
    apply_weight_tptrw(bkg_df)

    for sel, query in selections.items():
        s_df, b_df = satisfying_selection(sig_df, bkg_df, selection=query)
        print(sel, s_df["weight_nominal"].sum() / b_df["weight_nominal"].sum())


@misc.command("drdscomps")
@click.argument("datadir", type=click.Path(exists=True))
@click.option("-o", "--outdir", type=click.Path(), help="Output directory.")
@click.option("--thesis", is_flag=True, help="Flag for thesis label.")
def misc_drdscomps(datadir, outdir, thesis):
    """Generate plots comparing DR and DS (with BDT cuts shown)."""
    import tdub.internal.drds as tdid

    curdir = PosixPath.cwd().resolve()
    if outdir is not None:
        outdir = PosixPath(outdir).resolve()
    else:
        outdir = curdir
    outdir.mkdir(exist_ok=True, parents=True)
    os.chdir(outdir)
    tdid.bdt_cut_plots(datadir, thesis=thesis)
    os.chdir(curdir)


def run_cli():
    """Run main CLI."""
    import tdub.config
    tdub.config.AVOID_IN_CLF_1j1b = []
    tdub.config.AVOID_IN_CLF_2j1b = []
    tdub.config.AVOID_IN_CLF_2j2b = []
    cli()


if __name__ == "__main__":
    run_cli()
