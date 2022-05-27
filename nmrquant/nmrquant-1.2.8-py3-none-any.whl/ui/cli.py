import argparse
import os
from pathlib import Path
import sys

from nmrquant.engine.calculator import Quantifier
from nmrquant.engine.visualizer import *


def parse_args():
    """
    Get user arguments from CLI input

    :return: class: 'Argument Parser'
    """
    parser = argparse.ArgumentParser(
        description="Software for 1D proton NMR quantification")

    parser.add_argument("datafile", type=str,
                        help="Path to data file to process")

    parser.add_argument("-d", "--database", type=str,
                        help="Path to proton database")
    parser.add_argument("-F", "--dilution_factor", type=float, default=1.11,
                        help="Dilution factor used to calculate concentrations")
    parser.add_argument("-t", "--template", type=str,
                        help="Path to template file. ")
    parser.add_argument("-k", "--make_template", type=str,
                        help="Input path to export template to")
    parser.add_argument("-f", "--format", type=str, default="svg",
                        help="Choose a format for the plots. Choices: svg, png, jpeg")

    parser.add_argument('-b', '--barplot', choices=["individual", "meaned"], action="append",
                        type=str, help='Choose histogram to build. Enter "individual" or "meaned" ')
    parser.add_argument('-l', '--lineplot', choices=["individual", "meaned"], action="append",
                        type=str, help='Choose lineplot to build. Enter "individual" or "meaned" ')

    parser.add_argument('-m', '--mean', action='store_true', default=False,
                        help='Add if means and stds should be calculated on replicates')
    parser.add_argument('-c', '--tsp_concentration', type=float,
                        help='Add tsp concentration if calibration is external')

    parser.add_argument("-e", "--export", type=str, help="Name for exported file")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Add option for debug mode")

    return parser


def process(args):
    """
    Command Line Interface process of nmrquant

    :param args: Arguments passed by the parser
    :return: Excel file export message
    """

    cli_quant = Quantifier(verbose=args.verbose)
    for i, arg in enumerate(sys.argv):
        cli_quant.logger.debug(f"Argument {i} = {arg}")
    home = Path(args.datafile).absolute()
    home = home.parent
    if not home.exists():
        raise TypeError("The input datafile path does not exist")
    destination = home / "Results"
    destination.mkdir()
    # Get data
    try:
        cli_quant.get_data(fr"{args.datafile}")
    except Exception:
        cli_quant.logger.exception("Error reading input data")
    if hasattr(args, "k"):
        cli_quant.generate_metadata(destination)
    else:
        db_path, tp_path = Path(args.database).absolute(), Path(args.template).absolute()
        for path in [db_path, tp_path]:
            if not path.exists():
                raise TypeError(f"The path {path} does not exist")
        # Get database and template
        try:
            cli_quant.get_db(fr"{db_path}")
            cli_quant.import_md(fr'{tp_path}')
        except Exception:
            cli_quant.logger.exception("Error reading database or template file")
        # Process data
        if cli_quant.use_strd:
            try:
                cli_quant.compute_data(args.tsp_concentration, args.mean)
            except AttributeError:
                raise ("TSP concentration not referenced. Please add '-c' to arguments "
                       "followed by the TSP concentration")
            except Exception:
                cli_quant.logger.exception("Unknown error while calculating concentrations using tsp concentration")
        else:
            try:
                cli_quant.compute_data(1, mean=args.mean)
            except Exception:
                cli_quant.logger.exception("Unknown error while calculating concentrations")
        # Get name for exported excel file
        if args.export:
            if not isinstance(args.export, str):
                raise TypeError("Export file name must be a valid string of characters")
            file_name = args.export
        else:
            file_name = "Results"
        os.chdir(destination)
        cli_quant.export_data(file_name=file_name,
                              destination=destination,
                              export_mean=args.mean)
        cli_quant.logger.debug(f"Barplot args are: {args.barplot}")
        times = cli_quant.conc_data.index.get_level_values("Time_Points").unique()
        replicates = cli_quant.conc_data.index.get_level_values("Replicates").unique()
        display = False
        if args.barplot:
            if "individual" in args.barplot:
                if len(times) > 1:
                    cli_quant.logger.error(
                        "Too many time points for individual histograms. Please generate line plots instead")
                else:
                    cli_quant.logger.info("Trying to build individual histograms...")
                    ind_bp = destination / 'Histograms_Individual'
                    ind_bp.mkdir()
                    os.chdir(ind_bp)
                    for metabolite in cli_quant.metabolites:
                        cli_quant.logger.info(f"Plotting {metabolite}")
                        if len(replicates) > 1:
                            plot = IndHistB(cli_quant.conc_data, metabolite, display)
                        else:
                            plot = IndHistA(cli_quant.conc_data, metabolite, display)
                        fig = plot()
                        fig.savefig(f"{metabolite}.{args.format}", format=args.format)
                    cli_quant.logger.info("Individual histograms have been generated")
                os.chdir(destination)
            if "meaned" in args.barplot:
                cli_quant.logger.info("Trying to build meaned histograms...")
                if len(times) > 1:
                    cli_quant.logger.error("Too many time points for meaned histograms. Please generate line plots "
                                           "instead")
                elif not hasattr(cli_quant, "mean_data") or not hasattr(cli_quant, "std_data"):
                    cli_quant.logger.error("Means and SD data missing. Please add 'export mean' argument to generate "
                                           "required data")
                else:
                    meaned_bp = destination / 'Histograms_Meaned'
                    meaned_bp.mkdir()
                    os.chdir(meaned_bp)
                    for metabolite in cli_quant.metabolites:
                        cli_quant.logger.info(f"Plotting {metabolite}")
                        plot = MultHistB(cli_quant.mean_data, cli_quant.std_data, metabolite, display)
                        fig = plot()
                        fig.savefig(f"{metabolite}.{args.format}", format=args.format)
                    cli_quant.logger.info("Meaned histograms have been generated")
                os.chdir(destination)
        if args.lineplot:
            if "individual" in args.lineplot:
                cli_quant.logger.info("Trying to build Individual Lineplots...")
                if len(times) == 1:
                    cli_quant.logger.error("Not enough time points to generate kinetic plots. Please select a "
                                           "histogram representation instead")
                else:
                    ind_lp = destination / "Lineplots_Individual"
                    ind_lp.mkdir()
                    os.chdir(ind_lp)
                for metabolite in cli_quant.metabolites:
                    cli_quant.logger.info(f"Plotting {metabolite}")
                    if (len(replicates) == 1) or "Replicates" not in cli_quant.conc_data.index.names:
                        plot = NoRepIndLine(cli_quant.conc_data, metabolite, display)
                        fig = plot()
                        fig.savefig(f"{metabolite}.{args.format}", format=args.format)
                    else:
                        plot = IndLine(cli_quant.conc_data, metabolite, display)
                        figures = plot()
                        for (fname, fig) in figures:
                            fig.savefig(f"{fname}.{args.format}", format=args.format)
                cli_quant.logger.info("Individual lineplots have been generated")
            os.chdir(destination)
            if "meaned" in args.lineplot:
                cli_quant.logger.info("Trying to build summary lineplots...")
                if len(times) == 1:
                    cli_quant.logger.error("Not enough time points to generate kinetic plots. Please select a "
                                           "histogram representation instead")
                else:
                    meaned_lp = destination / "Lineplots_Meaned"
                    meaned_lp.mkdir()
                    os.chdir(meaned_lp)
                    if len(replicates) == 1 or "Replicates" not in cli_quant.conc_data.index.names:
                        cli_quant.logger.warning(
                            "No replicates detected. Plots will still be generated but to remove the pointless"
                            "error bars, select individual lineplots instead")
                    for metabolite in cli_quant.metabolites:
                        cli_quant.logger.info(f"Plotting {metabolite}")
                        plot = MeanLine(cli_quant.conc_data, metabolite, display)
                        fig = plot()
                        fig.savefig(f"{metabolite}.{args.format}", format=args.format)
                    cli_quant.logger.info("Meaned lineplots have been generated")
            os.chdir(destination)
        cli_quant.logger.info(f"Finished. Check {destination} for results")


def start_cli():
    parser = parse_args()
    args = parser.parse_args()
    process(args)
