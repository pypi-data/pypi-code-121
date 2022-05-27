import logging
import os
from pathlib import Path

import ipywidgets as widgets
from IPython.display import display
from ipyfilechooser import FileChooser

from nmrquant.engine.calculator import Quantifier
from nmrquant.engine.visualizer import *

mod_logger = logging.getLogger("RMNQ_logger.ui.notebook")


class Rnb:
    """Class to control RMNQ notebook interface"""

    def __init__(self, verbose=False):

        self.quantifier = Quantifier(verbose)

        self.home = None
        self.run_dir = None

        # Initialize child logger for class instances
        self.logger = logging.getLogger("RMNQ_logger.ui.notebook.Rnb")
        # fh = logging.FileHandler(f"{self.run_name}.log")
        handler = logging.StreamHandler()
        if verbose:
            handler.setLevel(logging.DEBUG)
        else:
            handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        if not self.logger.hasHandlers():
            self.logger.addHandler(handler)

        widgetstyle = {'description_width': 'initial'}

        self.display = False
        self.fmt = False

        self.upload_datafile_btn = FileChooser(os.getcwd())
        self.upload_datafile_btn.title = "Select Datafile"
        self.upload_database_btn = FileChooser(os.getcwd())
        self.upload_database_btn.title = "Select Database"
        self.upload_template_btn = FileChooser(os.getcwd())
        self.upload_template_btn.title = "Select Template"

        self.strd_btn = widgets.Text(value='', description='Strd concentration:', disabled=True,
                                     style=widgetstyle)

        self.dilution_text = widgets.Text(value='', description='Dilution factor:', style=widgetstyle, disabled=True)

        self.submit_btn = widgets.Button(description='Submit data', disabled=False,
                                         button_style='', tooltip='Click to submit selection',
                                         icon='', style=widgetstyle)

        self.calculate_btn = widgets.Button(description='Calculate',
                                            disabled=True, button_style='',
                                            tooltip='Click to calculate and export',
                                            icon='', style=widgetstyle)

        self.plots_btn = widgets.Button(description='Make plots',
                                        disabled=True, button_style='',
                                        tooltip='Click to generate plots', icon='',
                                        style=widgetstyle)

        self.generate_metadata_btn = widgets.Button(description='Generate Template',
                                                    disabled=True, button_style='',
                                                    tooltip='Click to generate template in parent folder',
                                                    icon='', style=widgetstyle)

        self.export_mean_checkbox = widgets.Checkbox(value=False, description="Mean export",
                                                     disabled=True, style=widgetstyle)

        self.format_chooser = widgets.Dropdown(
            options=['png', 'svg', 'jpeg'],
            value='svg',
            description='Choose plot format:',
            disabled=True,
            style=widgetstyle
        )

        self.plot_choice_dropdown = widgets.SelectMultiple(options=["individual_histogram",
                                                                    "meaned_histogram",
                                                                    "individual_lineplot",
                                                                    "summary_lineplot"],
                                                           value=("individual_histogram", "individual_histogram"),
                                                           description="Choose plot(s) to create",
                                                           disabled=True, style=widgetstyle)

    def reset(self, verbose):
        """Function to reset the object in notebook
        (only for notebook use because otherwise cell refresh
        doesn't reinitialize the object)"""
        os.chdir(self.home)
        self.__init__(verbose)

    # noinspection PyTypeChecker
    def make_gui(self):
        """Display the widgets and build the GUI"""
        display(self.upload_datafile_btn,
                self.upload_database_btn,
                self.upload_template_btn,
                self.submit_btn,
                self.export_mean_checkbox,
                self.dilution_text,
                self.strd_btn,
                self.format_chooser,
                self.generate_metadata_btn,
                self.calculate_btn,
                self.plot_choice_dropdown,
                self.plots_btn)

    def generate_template(self, event):
        """Generate template from input data spectrum count"""

        datafile = self.upload_datafile_btn.selected
        if self.quantifier.data is None:
            self.quantifier.get_data(datafile)
        directory = self.upload_datafile_btn.selected_path
        self.quantifier.generate_metadata(directory)
        self.logger.info(
            "Template has been created. Check parent folder for template.xlsx")

    def _submit_button_click(self, event):
        """Submit button function that enables the rest of the widgets and finishes preparation of the different
        input files."""

        # Enable all the other widgets
        self.export_mean_checkbox.disabled = False
        self.dilution_text.disabled = False
        self.calculate_btn.disabled = False
        self.plot_choice_dropdown.disabled = False
        self.plots_btn.disabled = False
        self.format_chooser.disabled = False
        self.generate_metadata_btn.disabled = False

        self.home = Path(self.upload_datafile_btn.selected_path)

        self.logger.debug("Initializing datafile")

        # Check if quantifier contains the data. If not, load it in from upload datafile button
        if self.quantifier.data is None:
            self.quantifier.get_data(self.upload_datafile_btn.selected)

        # Check if standard should be used to calculate concentrations (internal or external calibration)
        if self.quantifier.use_strd:
            self.logger.info("External calibration detected. Please enter the concentration of standard")
            self.strd_btn.disabled = False

        # Finish initalizing data variables and data files
        self.logger.debug("Initializing database")
        self.quantifier.get_db(self.upload_database_btn.selected)

        self.logger.debug("Initializing template")
        self.quantifier.import_md(self.upload_template_btn.selected)

        return self.logger.info('Data variables initialized')

    def process_data(self, event):
        """Make destination folder, clean data and calculate results"""

        # Make target directory
        self.run_dir = self.home / "Results"
        self.run_dir.mkdir()
        os.chdir(self.run_dir)

        # Get dilution factor and prepare data for calculations
        self.logger.info("Computing data")
        self.quantifier.dilution_factor = float(self.dilution_text.value)

        # Check type of calibration and if Strd concentration should be used
        if self.quantifier.use_strd:
            try:
                self.quantifier.compute_data(float(self.strd_btn.value), self.export_mean_checkbox.value)
            except ValueError:
                self.logger.error("Standard concentration must be a number")
        else:
            self.quantifier.compute_data(1, self.export_mean_checkbox.value)
        self.quantifier.export_data(".", "Results",
                                    export_mean=self.export_mean_checkbox.value)

    def build_plots(self, event):
        """Control plot creation. Make destination folders and generate plots."""

        self.fmt = self.format_chooser.value
        times = self.quantifier.conc_data.index.get_level_values("Time_Points").unique()
        replicates = self.quantifier.conc_data.index.get_level_values("Replicates").unique()
        # conditions = self.quantifier.conc_data.index.get_level_values("Conditions").unique()

        if "individual_histogram" in self.plot_choice_dropdown.value:
            if len(times) > 1:
                self.logger.error("Too many time points for individual histograms. Please generate line plots instead")
            else:
                self.logger.info("Building Individual Histograms...")
                indhist = self.run_dir / 'Histograms_Individual'
                indhist.mkdir()
                os.chdir(indhist)

                for metabolite in self.quantifier.metabolites:
                    if len(replicates) > 1:
                        plot = IndHistB(self.quantifier.conc_data, metabolite, self.display)
                    else:
                        plot = IndHistA(self.quantifier.conc_data, metabolite, self.display)
                    fig = plot()
                    fig.savefig(f"{metabolite}.{self.fmt}", format=self.fmt, bbox_inches='tight')
                self.logger.info("Individual histograms have been generated")
            os.chdir(self.run_dir)

        if "meaned_histogram" in self.plot_choice_dropdown.value:
            self.logger.info("Building Meaned Histograms...")
            if len(times) > 1:
                self.logger.error("Too many time points for individual histograms. Please generate line plots instead")
            elif not hasattr(self.quantifier, "mean_data") or not hasattr(self.quantifier, "std_data"):
                self.logger.error("Means and SD data missing. Please select 'export mean' option to generate required"
                                  "data")
            else:
                meanhist = self.run_dir / 'Histograms_Meaned'
                meanhist.mkdir()
                os.chdir(meanhist)

                for metabolite in self.quantifier.metabolites:
                    plot = MultHistB(self.quantifier.mean_data, self.quantifier.std_data, metabolite, self.display)
                    fig = plot()
                    fig.savefig(f"{metabolite}.{self.fmt}", format=self.fmt, bbox_inches='tight')
                self.logger.info("Meaned histograms have been generated")
            os.chdir(self.run_dir)

        if "individual_lineplot" in self.plot_choice_dropdown.value:
            self.logger.info("Building Individual Lineplots...")
            if len(times) == 1:
                self.logger.error("Not enough time points to generate kinetic plots. Please select a histogram "
                                  "representation instead")
            else:
                indline = self.run_dir / "Lineplots_Individual"
                indline.mkdir()
                os.chdir(indline)

                for metabolite in self.quantifier.metabolites:
                    if (len(replicates) == 1) or "Replicates" not in self.quantifier.conc_data.index.names:
                        plot = NoRepIndLine(self.quantifier.conc_data, metabolite, self.display)
                        fig = plot()
                        fig.savefig(f"{metabolite}.{self.fmt}", format=self.fmt, bbox_inches='tight')
                    else:
                        plot = IndLine(self.quantifier.conc_data, metabolite, self.display)
                        figures = plot()
                        for (fname, fig) in figures:
                            fig.savefig(f"{fname}.{self.fmt}", format=self.fmt, bbox_inches='tight')
                self.logger.info("Individual lineplots have been generated")
            os.chdir(self.run_dir)

        if "summary_lineplot" in self.plot_choice_dropdown.value:
            self.logger.info("Building Summary Lineplots...")
            if len(times) == 1:
                self.logger.error("Not enough time points to generate kinetic plots. Please select a histogram "
                                  "representation instead")
            else:

                sumline = self.run_dir / "Lineplots_Summary"
                sumline.mkdir()
                os.chdir(sumline)

                if len(replicates) == 1 or "Replicates" not in self.quantifier.conc_data.index.names:
                    self.logger.warning(
                        "No replicates detected. Plots will still be generated but to remove the useless"
                        "error bars, please select 'individual_lineplot' instead")
                for metabolite in self.quantifier.metabolites:
                    plot = MeanLine(self.quantifier.conc_data, metabolite, self.display)
                    fig = plot()
                    fig.savefig(f"{metabolite}.{self.fmt}", format=self.fmt, bbox_inches='tight')
                self.logger.info("Summary lineplots have been generated")
            os.chdir(self.run_dir)

        os.chdir(self.home)

    def load_events(self):
        """Load events for all the different buttons"""

        self.generate_metadata_btn.on_click(self.generate_template)
        self.submit_btn.on_click(self._submit_button_click)
        self.calculate_btn.on_click(self.process_data)
        self.plots_btn.on_click(self.build_plots)
