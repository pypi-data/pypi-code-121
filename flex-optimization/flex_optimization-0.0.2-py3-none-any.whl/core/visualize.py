import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

from flex_optimization.core.recorder import Recorder


class OptimizationVis:
    def __init__(self, recorder: Recorder):
        self.recorder = recorder
        self.df: pd.DataFrame = self.recorder.df

    def plot_by_expt(self) -> go.Figure:
        fig = go.Figure()
        for col in self.df.columns:
            fig.add_trace(go.Scatter(x=self.df.index, y=self.df[col], name=col,
                                     mode="markers+lines", line=dict(width=1)
                                     ))

        return fig

    def plot_3d_vis(self, indept_var: list[str] = None) -> go.Figure:
        if len(self.df) < 3:
            raise ValueError("2 independent variable are required to visualized in 3D.")
        if indept_var is None:
            cols = list(self.df.columns[:2]) + ["metric"]
        else:
            if len(indept_var) != 2:
                raise ValueError("Two independent variable names must be provided")

            cols = indept_var + ["metric"]

        fig = go.Figure()
        fig.add_trace(go.Scatter3d(x=self.df[cols[0]], y=self.df[cols[1]], z=self.df[cols[2]],
                                   mode="markers+lines", line=dict(width=1)
                                   ))
        return fig

    def plot_4d_vis(self, indept_var: list[str] = None, metric_vis: str = "color") -> go.Figure:
        if len(self.df) < 4:
            raise ValueError("3 independent variable are required to visualized in 4D.")
        if indept_var is None:
            cols = list(self.df.columns[:3])
        else:
            if len(indept_var) != 3:
                raise ValueError("Three independent variable names must be provided")
            cols = indept_var

        if metric_vis == "color":
            cols.append("metric")
        elif metric_vis == "z":
            cols.insert(2, "metric")
        else:
            raise ValueError("Invalid metric_vis value.")

        fig = px.scatter_3d(self.df, x=cols[0], y=cols[1], z=cols[2], color=cols[3])
        return fig

    def plot_5d_vis(self, indept_var: list[str] = None, metric_vis: str = "color") -> go.Figure:
        if len(self.df) < 5:
            raise ValueError("4 independent variable are required to visualized in 5D.")
        if indept_var is None:
            cols = list(self.df.columns[:3])
        else:
            if len(indept_var) != 3:
                raise ValueError("Three independent variable names must be provided")
            cols = indept_var

        if metric_vis == "color":
            cols.insert(3, "metric")
        elif metric_vis == "z":
            cols.insert(2, "metric")
        elif metric_vis == "size":
            cols.append("metric")
        else:
            raise ValueError("Invalid metric_vis value.")

        fig = px.scatter_3d(self.df, x=cols[0], y=cols[1], z=cols[2], color=cols[3], size=cols[4])

        return fig
