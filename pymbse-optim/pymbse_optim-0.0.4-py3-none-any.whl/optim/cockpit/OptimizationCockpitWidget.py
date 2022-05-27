from itertools import accumulate
from typing import List

import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from pymbse.optim.cache_database_api import get_best_optimization_snapshot, get_selected_optimization_snapshot
from pymbse.optim.design_variable import DesignVariableFactory
from pymbse.optim.constants import SCORE_KEYWORD

INDIVIDUAL_IX_COLUMN = 'individual_ix'
GENERATION_IX_COLUMN = 'generation_ix'
FIGURES_OF_MERIT_COLUMN = 'figures_of_merit'


class OptimizationCockpitWidget:
    """ A class providing a plotly widget for an optimization cockpit. The cockpit displays:
    - progress of the optimization
    - objective variable table
    - comparison of fitness function of a selected individual to the current best one
    - comparison of design variables of a selected individual to the current best one
    - selected geometry overview
    The cockpit is interactive and allows for selecting an individual to display its geometry

    """

    def __init__(self,
                 ip_with_port_cache: str,
                 optimization_ix: int,
                 score_df: pd.DataFrame,
                 is_log_y=False) -> None:
        """ Constructor of an OptimizationCockpitWidget instance

        :param gen_opt: genetic optimization instance
        :param score_df: a dataframe with logger. It contains three columns: generation_ix, individual_ix, score
        :param config: optimization config instance
        :param is_log_y: if True, than the score plot has logarithmic y-scale
        """
        self.ip_with_port_cache = ip_with_port_cache
        self.optimization_ix = optimization_ix
        self.min_logger_df = score_df
        self.is_log_y = is_log_y

        fig = make_subplots(
            rows=3, cols=2,
            shared_xaxes=False,
            vertical_spacing=0.03,
            column_widths=[0.35, 0.65],
            row_heights=[0.15, 0.2, 0.65],
            specs=[[{"type": "xy"}, {"type": "table"}], [{"type": "xy", "rowspan": 2}, {"type": "scatter"}],
                   [None, {"type": "scatter"}]]
        )

        self.widget = go.FigureWidget(fig)

    def show(self) -> go.FigureWidget:
        """ Method displaying the widget by returning the field that contains it.

        :return: optimization cockpit widget
        """
        return self.widget

    def build(self) -> None:
        """ Method building the optimization cockpit widget with plotly library

        """
        self.update_title(len(self.min_logger_df), self.min_logger_df.loc[self.min_logger_df.index[-1], SCORE_KEYWORD])

        # Display fitness function graph with callback
        self.display_fitness_function_graph(row=2, col=2)

        index_best = self.min_logger_df[SCORE_KEYWORD].idxmin()
        # Display selected generation objective table
        fom_best_dct = self.min_logger_df.loc[index_best, FIGURES_OF_MERIT_COLUMN]
        fom_best_df = pd.DataFrame(data=[fom_best_dct])
        self.display_objective_table(fom_best_df)

        # Display figures of merit comparison cumulative bar graph
        self.display_fitness_function_comparison_graph(fom_best_dct, fom_best_dct, row=1, col=1)

        # Display design variables  bar graph
        best_opt_snap = get_best_optimization_snapshot(self.ip_with_port_cache, self.optimization_ix)
        best_gen_dvs_df = pd.DataFrame(best_opt_snap['input_parameters']['individual_dct']['gen_dvs'])
        best_gen_dvs = DesignVariableFactory.init_genetic_design_variables_with_df(best_gen_dvs_df)
        self.display_design_variables_graph(best_gen_dvs, best_gen_dvs, row=2, col=1)

        # Display geometry graph
        self.display_custom_graph(best_opt_snap, row=3, col=2)

        # Create callback function
        def callback(object: "OptimizationCockpitWidget"):
            def update_point(trace, points, selector):
                index_sel = points.point_inds[0]

                # Update selected generation objective table
                widget_data = object.widget.data[1]
                fom_sel_dct = object.min_logger_df.loc[index_sel, FIGURES_OF_MERIT_COLUMN]
                fom_sel_df = pd.DataFrame(fom_sel_dct, index=[FIGURES_OF_MERIT_COLUMN])
                OptimizationCockpitWidget.update_objective_table(widget_data, fom_sel_df)

                # Clear remaining graphs before display
                object.widget.data = [object.widget.data[0], object.widget.data[1]]

                # Display fitness function comparison graph
                object.display_fitness_function_comparison_graph(fom_sel_dct, fom_best_dct, row=1, col=1)

                # Display design variables graph
                generation_ix = object.min_logger_df.loc[index_sel, GENERATION_IX_COLUMN]
                individual_ix = object.min_logger_df.loc[index_sel, INDIVIDUAL_IX_COLUMN]
                sel_opt_snap = get_selected_optimization_snapshot(object.ip_with_port_cache,
                                                                  int(object.optimization_ix),
                                                                  int(generation_ix),
                                                                  int(individual_ix))
                sel_gen_dvs_df = pd.DataFrame(sel_opt_snap['input_parameters']['individual_dct']['gen_dvs'])
                sel_gen_dvs = DesignVariableFactory.init_genetic_design_variables_with_df(sel_gen_dvs_df)
                object.display_design_variables_graph(best_gen_dvs, sel_gen_dvs, row=2, col=1)

                # Display geometry graph
                object.display_custom_graph(sel_opt_snap, row=3, col=2)

                object.update_title(index_sel, object.min_logger_df.loc[index_sel, SCORE_KEYWORD])

            return update_point

        scatter = self.widget.data[0]
        self.widget.layout.hovermode = 'closest'
        scatter.on_click(callback(self))

    def update_title(self, index_gen: int, fitness_function: float) -> None:
        """ Method updating the widget title with generation index and fitness function value

        :param index_gen: generation index (0-based)
        :param fitness_function: fitness function value
        """
        self.widget.update_layout(
            height=1000,
            showlegend=False,
            title_x=0.5,
            title_text="Optimization Cockpit - index: %d - fitness function: %f" % (index_gen, fitness_function),
        )

    def display_fitness_function_graph(self, row=2, col=2) -> None:
        """ Method displaying the fitness function graph in the widget at a given index (row and column)

        :param row: row index of the graph (1-based)
        :param col: column index of the graph (1-based)
        """
        self.widget.add_trace(
            go.Scatter(
                x=self.min_logger_df.index.values,
                y=self.min_logger_df[SCORE_KEYWORD].values,
                mode="lines+markers",
                name="fitness",
            ),
            row=row, col=col
        )
        if self.is_log_y:
            self.widget.update_yaxes(type='log', row=row, col=col)

    def display_objective_table(self, fom_df: pd.DataFrame, row=1, col=2) -> None:
        """ Method displaying the objective table in the widget

        :param fom_df: a dataframe with information to be displayed
        """
        self.widget.add_trace(
            go.Table(
                header=dict(
                    values=fom_df.columns,
                    font=dict(size=10),
                    align="left"
                ),
                cells=dict(
                    values=[fom_df[k].tolist() for k in fom_df.columns],
                    align="left")),
            row=row, col=col)

    @staticmethod
    def update_objective_table(widget_data, obj_df: pd.DataFrame) -> None:
        """ Static method updating the objective table

        :param widget_data: reference to the table widget in the cockpit
        :param obj_df: new objective dataframe
        """
        widget_data.cells = dict(
            values=[obj_df[k].tolist() for k in obj_df.columns],
            align="left")

    def display_fitness_function_comparison_graph(self, fom_sel: dict, fom_best: dict, row=1, col=1) -> None:
        """ Method displaying a fitness function comparison graph. The bar graph contains contributions of each of the
        objectives.

        :param fom_sel: dictionary with figures of merit for a selected individual
        :param fom_best: dictionary with figures of merit for the best individual so far
        :param row: row index of the graph in the widget (1-based)
        :param col: column index of the graph in the widget (1-based)
        """
        cum_fom_sel = list(accumulate(fom_sel.values()))
        cum_fom_best = list(accumulate(fom_best.values()))

        hover_text_sel = ['%s: %f' % fom_value for fom_value in fom_sel.items()]
        hover_text_best = ['%s: %f' % fom_value for fom_value in fom_best.items()]

        # Display separately
        n = len(cum_fom_sel)
        for i in range(n):
            trace = go.Bar(
                x=[cum_fom_best[n - i - 1], cum_fom_sel[n - i - 1]],
                y=['Best', 'Actual'],
                hovertext=[hover_text_best[n - i - 1], hover_text_sel[n - i - 1]],
                orientation='h',
                hoverinfo='text',
                offsetgroup=1
            )
            self.widget.append_trace(trace, row, col)

    def display_design_variables_graph(self, best_gen_dvs: list, sel_gen_dvs: list, row=2, col=1) -> None:
        """ Method displaying the design variables graph. The graph compares a selected individual with the best one.

        :param best_gen_dvs: list of design variables for the best individual
        :param sel_gen_dvs: list of design variables for a selected individual
        :param row: row index of the graph in the widget (1-based)
        :param col: column index of the graph in the widget (1-based)
        """

        trace_best = prepare_bar_plot_with_fraction(best_gen_dvs, 'Best')
        trace_sel = prepare_bar_plot_with_fraction(sel_gen_dvs, 'Selected')

        self.widget.add_traces([trace_best, trace_sel], rows=row, cols=col)

    def display_custom_graph(self, optimization_snapshot: dict, row=3, col=2) -> None:
        """ Method displaying a geometry preview for a selected index.

        :param optimization_snapshot: an optimization snapshot dictionary
        :param row: row index of the graph in the widget (1-based)
        :param col: column index of the graph in the widget (1-based)
        """
        go_scatter = OptimizationCockpitWidget.prepare_custom_trace_for_plot(optimization_snapshot)
        self.widget.add_traces(go_scatter, rows=row, cols=col)

    @staticmethod
    def prepare_custom_trace_for_plot(optimization_snapshot: dict) -> list:
        return []


def prepare_bar_plot_with_fraction(gen_dvs, name: str) -> go.Bar:
    return go.Bar(x=prepare_fractions_for_bar_plot(gen_dvs),
                  hovertext=prepare_hover_texts_for_bar_plot(gen_dvs),
                  y=[gen_dv.get_compact_variable_name() for gen_dv in gen_dvs],
                  name=name,
                  orientation='h')


def prepare_fractions_for_bar_plot(design_variables: List) -> List[float]:
    """ Prepare a list of fractions of design variable values for a bar plot display

    :param design_variables: a list of design variables
    :return: a list of fractions for a bar plot
    """
    return [dv.get_fraction(dv.value) for dv in design_variables]


def prepare_hover_texts_for_bar_plot(design_variables) -> List[str]:
    """ Prepare a list of hover texts for a bar plot display

    :param design_variables: a list of design variables
    :return:a list of hover texts for a bar plot
    """
    return [dv.get_hover_text(dv.value) for dv in design_variables]
