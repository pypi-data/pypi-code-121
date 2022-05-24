#!/usr/bin/env python3
# coding: utf-8

""" Object to manage a widget figure. """

# Built-in packages

# Third party packages
from IPython.display import display
from ipywidgets import widgets

from scipy import stats
import matplotlib.pyplot as plt
import numpy as np

# Local packages

__all__ = ['NapoleonFigure']


def plot_drawdown_and_histo_vol(xdate,xcours,nitems_in_year):
    T=xcours.size
    vol = np.zeros([T])
    dd = np.zeros([T])
    for t in range(1,T):
        dd[t] = xcours[t]/max(xcours[:t+1])-1
    for t in range(nitems_in_year,T):
        vol[t] = np.sqrt(252)*stats.tstd(xcours[t+1-nitems_in_year:t+1]/xcours[t-nitems_in_year:t]-1)
    f, ax = plt.subplots(2, 1, figsize=(8,8))
    ax[0].plot(xdate[(nitems_in_year+1):],dd[(nitems_in_year+1):], LineWidth= 2, label = "draw down")
    ax[1].plot(xdate[(nitems_in_year+1):],vol[(nitems_in_year+1):], LineWidth= 2, label = "1 year histo volatility")
    ax[0].legend()
    ax[1].legend()
    plt.show()

class NapoleonFigure:
    """ Object to display a figure linked to some widgets.

    Parameters
    ----------
    job : callable
        Function to call when an observed parameter is updated.
    output : widgets.Output, optional
        Object to display the figure. If None, a new widgets.Ouput is create.
        Default is None.
    clear : bool, optional
        If True clear the `output` at each update.
    kw_observed
        Any parameters to observe and pass at `job` when they are updated.

    Methods
    -------
    set_widget
    show
    check

    Attributes
    ----------
    widgets : dict of widgets.Widgets
        Dictionary of widget objects.
    job : callable
        Function to call when an observed parameter is updated. Take as
        parameters the observed parameters `kw_observed` and do an action (e.g
        computation, graphs, print, etc.).
    output : widgets.Output
        Object to display figure.
    handler : callable
        Function which update parameters, enter into `output` context manager
        and call `job`.
    clear : bool
        If True clear the `output` at each update.
    kw_observed : dict
        Parameters to observe and to pass to `job`.

    Warnings
    --------
    Each widgets.Widgets object must get as description attribute the same name
    than the specific observed parameter in `kw_observed`.

    """

    def __init__(self, job, output=None, clear=True, **kw_observed):
        """ Initialize object. """
        self.output = widgets.Output() if output is None else output
        self.clear = clear
        self.job = job
        self.widgets = {}
        self.handler = self._gen_handler(kw_observed.keys())
        self.kw_observed = kw_observed

    def _gen_handler(self, catch_params):
        """ Generate a handler function to be passed in the widget.

        Parameters
        ----------
        catch_params : list of str
            Parameters to catch/observe for the widget.

        Returns
        -------
        callable
            Function which update parameters, enter into `output` context
            manager and call `job`.

        """
        # Define handler
        def handler(change, force=False):
            """ Update parameters and do something. """
            if force:
                with self.output:
                    # Do something with updated parameters
                    self.job(**self.kw_observed)

                return

            params = change['owner'].description
            if params in catch_params:
                # Update parameters
                self.kw_observed[params] = change['new']

            else:
                return

            if self.clear:
                self.output.clear_output()

            with self.output:
                # Do something with updated parameters
                self.job(**self.kw_observed)

        return handler

    def set_widget(self, *widgets):
        """ Append widget to dictionary of widgets.

        Parameters
        ----------
        *widgets : widgets.Widgets object

        Warnings
        --------
        Each widgets.Widgets object must get as description attribute the same
        name than the specific observed parameter in `kw_observed`.

        """
        for w in widgets:
            self.widgets[w.description] = w

    def show(self, display_widget=True):
        """ Display widget and do the job.

        Parameters
        ----------
        display_widget : bool or list of str
            - If list of name, display only widgets with the same name.
            - If True, display all the widgets.
            - Otherwise, don't display any widgets.

        """
        if isinstance(display_widget, list):
            for descr in display_widget:
                # display(self.fig['widgets'][descr])
                display(self.widgets[descr])

        elif display_widget:
            # for w in self.fig['widgets'].values():
            for w in self.widgets.values():
                display(w)

        self.check()

    def check(self):
        """ Start to observe `kw_observed` parameters and display `output`. """
        for w in self.widgets.values():
            w.observe(self.handler, names='value')

        display(self.output)
