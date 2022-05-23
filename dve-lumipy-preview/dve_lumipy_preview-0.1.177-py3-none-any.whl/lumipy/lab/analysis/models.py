from typing import Optional
from typing import Union, List

import numpy as np
import statsmodels.api as sm
from pandas import DataFrame
from statsmodels.regression.quantile_regression import QuantReg

_cms_scheme = {
    'scatter_plot': {'color': 'black', 'alpha': 0.5},
    'median_line': {'color': 'black', 'ls': '--'},
    'outer_band': {'color': 'lime', 'alpha': 1.0},
    'inner_band': {'color': 'yellow', 'alpha': 1.0},
}


def _make_monochrome_scheme(c):
    return {
        'scatter_plot': {'color': c, 'alpha': 0.667},
        'median_line': {'color': c, 'ls': '--'},
        'outer_band': {'color': c, 'alpha': 1 / 6},
        'inner_band': {'color': c, 'alpha': 1 / 3},
    }


class ScalingModel:
    """This class encapsulates the analysis of how an attribute of an experiment scales with a single input value.

    It consists of a set of quantile regressions that put bounds on the scaling behaviour alongside helper methods
    for plotting this relationship, getting its parameters and predicting its values.

    """

    def __init__(self, data: DataFrame, x: str, y: str):
        """The constructor method of the scaling model.

        Args:
            data (DataFrame): dataframe from an experimental run.
            x (str): the independent variable column name in the dataframe.
            y (str): the dependent variable column name in the dataframe.
        """

        if len(data) == 0:
            raise ValueError('The model input dataframe was empty.')

        self.data = data[(~data.errored) & (~data.force_stopped)].copy()
        self.errors = data[data.errored].copy()

        if self.data.shape[0] == 0:
            name = data.iloc[0].ExperimentName
            raise ValueError(f"There was no non-errored data to use from the experiment {name}!")

        self.x = x
        self.y = y

        model = QuantReg(
            self.data[self.y],
            sm.add_constant(self.data[self.x])
        )

        quantiles = [0.05, 0.25, 0.5, 0.75, 0.95]
        self.fits = {q: model.fit(q) for q in quantiles}

    def predict(self, x: Union[float, List[float], np.array]) -> DataFrame:
        """Predict the 5th, 25th, 50th, 75th and 95th percentiles for given values of the experiment input value.

        Args:
            x (Union[float, List[float], np.array]): a single input value, or array of values, to predict for.

        Returns:
            DataFrame: a dataframe with a row for each value of x and a column for each percentile.
        """
        output = {}

        for q, m in self.fits.items():
            if isinstance(x, (float, int)):
                _x = np.asarray([x, 0]).reshape(-1, 1)
                _x = sm.add_constant(_x)
                output[q] = m.predict(_x)[0]
            elif len(x) == 1:
                _x = np.asarray([x[0], 0]).reshape(-1, 1)
                _x = sm.add_constant(_x)
                output[q] = m.predict(_x)[0]
            else:
                _x = np.asarray(x)
                _x = sm.add_constant(_x)
                output[q] = m.predict(_x)

        if isinstance(x, (float, int)) or len(x) == 1:
            ex_df = DataFrame([output])
        else:
            ex_df = DataFrame(output)

        ex_df['x'] = x
        ex_df = ex_df.set_index('x')
        return ex_df

    def fit_results(self) -> DataFrame:
        """Returns a summary dataframe containing the parameters, p values and std errors for each quantile regression
        line in the model.

        Returns:
            DataFrame: data frame with the fit results.
        """
        rows = []
        for q, m in self.fits.items():
            m.conf_int()
            rows.append({
                'quantile': q,
                'c': m.params[0],
                'm': m.params[1],
                'c_stderr': m.bse[0],
                'm_stderr': m.bse[1],
            })

        fr_df = DataFrame(rows).set_index('quantile')
        fr_df['c_frac_err'] = fr_df['c_stderr'] / fr_df['c']
        fr_df['m_frac_err'] = fr_df['m_stderr'] / fr_df['m']
        return fr_df

    def outliers(self) -> DataFrame:
        """Get lines in the input data that might be outliers according to the fit model.

        Data points are flagged as outliers if they are above the upper quartile + 1.5 * the interquartile range (IQR)
        or are below the lower quartile - 1.5 * IQR.

        Returns:
            DataFrame: dataframe of rows in the input data that may be outliers.
        """
        odf = self.predict(self.data[self.x].values).reset_index()
        odf['IQR'] = odf[0.75] - odf[0.25]
        odf['y'] = self.data[self.y].values
        odf['execution_id'] = self.data['execution_id'].values
        odf = odf[(odf['y'] > odf[0.75] + 1.5 * odf['IQR']) | (odf['y'] < odf[0.25] - 1.5 * odf['IQR'])]
        return self.data[self.data.execution_id.isin(odf.execution_id.tolist())]

    def add_plot(self, ax, label: str, color_scheme: Optional[str] = 'cms', show_datapoints: Optional[bool] = True):

        """Add a plot of this scaling model's quantile bands, its median line and the data points that the model was
        fit with to a matplotlib axes object.

        Args:
            ax: the matplotlib axes to draw the plot on.
            label (str): the label to add to entries in the legend that will distinguish this relationship.
            color_scheme (str): the color scheme to use. This can be either 'cms' (for a CERN CMS-style brazil band) or
            any valid matplotlib named color.
            show_datapoints (bool): show the observed datapoints. Set to false if a comparison plot's getting too busy.

        """
        if color_scheme == 'cms':
            scheme = _cms_scheme
        else:
            scheme = _make_monochrome_scheme(color_scheme)

        data = self.data

        if show_datapoints:
            ax.scatter(
                data[self.x],
                data[self.y],
                s=10, zorder=99,
                label=f'Observation ({label})',
                **scheme['scatter_plot']
            )

        x_min = self.data[self.x].min()
        x_max = self.data[self.x].max()

        x = np.linspace(x_min, x_max, 3)
        pred = self.predict(x)

        ax.plot(x, pred[0.5], label=f'Median ({label})', **scheme['median_line'])
        ax.fill_between(x, pred[0.25], pred[0.75], label=f'p25-p75 Range ({label})', **scheme['inner_band'])
        ax.fill_between(x, pred[0.75], pred[0.95], label=f'p5-p95 Range ({label})', **scheme['outer_band'])
        ax.fill_between(x, pred[0.05], pred[0.25], **scheme['outer_band'])

    def remove_outliers(self) -> 'ScalingModel':
        """Fit a model, remove outliers from the input data and then fit a new model.

        Returns:
            ScalingModel: a new scaling model fit to data with outliers removed
        """
        outliers = self.outliers()
        data = self.data[~self.data.execution_id.isin(outliers.execution_id)].copy()
        return ScalingModel(data, self.x, self.y)
