from abc import abstractmethod

import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator

import Fumagalli_Motta_Tarantino_2020 as Models
import Fumagalli_Motta_Tarantino_2020.Types as Types


class IVisualize:
    """
    Interface for all visualization classes containing useful methods.

    Notes
    -----
    This module is compatible with python versions starting from 3.9, due to introduction of PEP 585. Therefore, the compatibility
    with mybinder.org is not guaranteed (uses at the moment python 3.7).
    """

    colors: list[str] = [
        "indianred",
        "salmon",
        "khaki",
        "greenyellow",
        "limegreen",
        "turquoise",
        "powderblue",
        "lavender",
        "thistle",
        "lavenderblush",
        "pink",
    ]
    """Standard colors used in visualizations."""

    def __init__(self, model: Models.OptimalMergerPolicy, **kwargs):
        """
        Parameters
        ----------
        model: Fumagalli_Motta_Tarantino_2020.Models.OptimalMergerPolicy
            Model to plot the outcomes on asset range from.
        """
        self.set_light_mode()
        self.model: Models.OptimalMergerPolicy = model
        self.fig, self.ax = plt.subplots(**kwargs)

    @staticmethod
    def set_dark_mode():
        plt.style.use("dark_background")

    @staticmethod
    def set_light_mode():
        plt.style.use("default")

    def _set_legend(self) -> None:
        self.ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0)

    def _set_tight_layout(self) -> None:
        self.fig.tight_layout()

    @abstractmethod
    def plot(self, **kwargs) -> (plt.Figure, plt.Axes):
        """
        Plots the visual representation for the object.

        Example
        -------
        ```
        model = Models.OptimalMergerPolicy()
        visualizer = MergerPoliciesAssetRange(m)
        fig, ax = visualizer.plot()
        # use the figure and axes as you wish, but for example:
        fig.show()
        ```

        Parameters
        ----------
        kwargs
            Options for the plots for further customization.

        Returns
        -------
        Figure
            Containing the axes with the plots (use Figure.show() to display).
        Axes
            Containing the plots (arrange custom summary).
        """
        raise NotImplementedError

    def show(self, **kwargs) -> None:
        """
        Shows the visual representation for the object.

        Example
        -------
        ```
        model = Models.OptimalMergerPolicy()
        visualizer = MergerPoliciesAssetRange(m)
        visualizer.show()
        ```

        Parameters
        ----------
        kwargs
            Same options as Fumagalli_Motta_Tarantino_2020.Visualize.IVisualize.plot.
        """
        self.plot(**kwargs)
        self.fig.show()

    @staticmethod
    def _parameter_latex(model: Models.BaseModel) -> str:
        """
        Generates a legend for the parameter values of a Fumagalli_Motta_Tarantino_2020.Models.BaseModel in latex format.

        Parameters
        ----------
        model: Fumagalli_Motta_Tarantino_2020.Models.BaseModel
            Input model to generate the legend from.

        Returns
        -------
        str
            Containing the legend for the parameter values.
        """
        separator_name_value = "="
        separator_parameters = " | "
        output_str = ""
        for (parameter, value, separator) in [
            ("A", model.startup_assets, separator_parameters),
            ("B", model.private_benefit, separator_parameters),
            ("K", model.development_costs, separator_parameters),
            ("p", model.success_probability, "\n"),
            ("CS^m", model.cs_without_innovation, separator_parameters),
            (
                "\\pi^m_I",
                model.incumbent_profit_without_innovation,
                separator_parameters,
            ),
            ("CS^M", model.cs_with_innovation, separator_parameters),
            ("\\pi^M_I", model.incumbent_profit_with_innovation, separator_parameters),
            ("CS^d", model.cs_duopoly, separator_parameters),
            ("\\pi^d_I", model.incumbent_profit_duopoly, separator_parameters),
            ("\\pi^d_S", model.startup_profit_duopoly, ""),
        ]:
            output_str += f"${parameter}{separator_name_value}{round(value, ndigits=3)}${separator}"
        return output_str

    @staticmethod
    def _get_summary_latex(summary: Types.OptimalMergerPolicySummary) -> str:
        """
        Generates a chronological entry for the legend based on the input model.

        Parameters
        ----------
        summary: Fumagalli_Motta_Tarantino_2020.Types.OptimalMergerPolicySummary
            Summary of the model.

        Returns
        -------
        str
            Chronological entry for the legend of the input model.
        """
        separator: str = "$\\to$"
        return (
            f"{summary.optimal_policy.abbreviation()}: "
            f"{summary.early_bidding_type.abbreviation()}"
            f"{IVisualize._get_is_takeover_legend(summary.early_bidding_type, summary.early_takeover)}{separator}"
            f"{IVisualize._get_development_attempt_legend(summary.development_attempt)}"
            f"{IVisualize._get_development_outcome_legend(summary.development_attempt, summary.development_outcome)}{separator}"
            f"{summary.late_bidding_type.abbreviation()}"
            f"{IVisualize._get_is_takeover_legend(summary.late_bidding_type, summary.late_takeover)}"
        )

    @staticmethod
    def _get_is_takeover_legend(bid_attempt: Types.Takeover, is_takeover: bool) -> str:
        """
        Generates a string representation for legend about the takeover (option and approval).

        Parameters
        ----------
        bid_attempt: Fumagalli_Motta_Tarantino_2020.Types.Takeover
            Option for takeover chosen by the incumbent.
        is_takeover: bool
            If true, the takeover is approved by AA and the start-up.

        Returns
        -------
        str
            String representation for legend about takeover (option and approval).
        """
        if bid_attempt is Types.Takeover.No:
            return ""
        return "$(\\checkmark)$" if is_takeover else "$(\\times)$"

    @staticmethod
    def _get_development_attempt_legend(is_developing: bool) -> str:
        """
        Generates a string representation for legend about the development attempt.

        Parameters
        ----------
        is_developing: bool
            True, if the owner is developing the product (otherwise, the product is shelved).

        Returns
        -------
        str
            String representation for legend about the development attempt.
        """
        return "$D$" if is_developing else "$\\emptyset$"

    @staticmethod
    def _get_development_outcome_legend(
        is_developing: bool, is_successful: bool
    ) -> str:
        """
        Generates a string representation for legend about the development outcome.

        Parameters
        ----------
        is_developing: bool
            True, if the owner is developing the product (otherwise, the product is shelved).
        is_successful: bool
            True, if the development of the product is successful.

        Returns
        -------
        str
            String representation for legend about the development outcome.
        """
        if is_developing:
            return "$(\\checkmark)$" if is_successful else "$(\\times)$"
        return ""

    @staticmethod
    def _get_symbol_legend() -> str:
        """
        Generates a legend for the used abbreviations in the plot legends.

        Returns
        -------
        str
            Containing the legend for the used abbreviations.
        """
        return (
            "${\\bf Merger\\thickspace policies}$:\n"
            f"{Types.MergerPolicies.legend()}\n"
            "${\\bf Bidding\\thickspace types}$:\n"
            f"{Types.Takeover.legend()}\n"
            "${\\bf Takeover\\thickspace outcome\\thickspace}$:\n"
            f"{Types.Takeover.Pooling.abbreviation()}|{Types.Takeover.Separating.abbreviation()}$(\\checkmark)$: Takeover is approved by the startup and AA\n"
            f"{Types.Takeover.Pooling.abbreviation()}|{Types.Takeover.Separating.abbreviation()}$(\\times)$: Takeover is blocked  by AA or not accepted by the startup\n"
            "${\\bf Development\\thickspace outcome}$:\n"
            f"$\\emptyset$: Product development was shelved\n"
            f"$D(\\checkmark)$: Product development was attempted and successful\n"
            f"$D(\\times)$: Product development was attempted and not successful\n"
        )


class AssetRange(IVisualize):
    """
    Visualizes the outcomes over an assets range for a specific model.
    """

    def __init__(self, model: Models.OptimalMergerPolicy, **kwargs) -> None:
        super(AssetRange, self).__init__(model, **kwargs)
        self.labels: list[str] = []
        self.colors: dict[str, str] = {}

    def _get_outcomes_asset_range(
        self,
    ) -> list[Types.OptimalMergerPolicySummary]:
        """
        Generates a list with all essential threshold concerning the assets of a start-up and an additional list with
        summaries of the outcomes of the model in between the thresholds.

        Returns
        -------
        (list[Fumagalli_Motta_Tarantino_2020.Types.ThresholdItem], list[Fumagalli_Motta_Tarantino_2020.Types.OptimalMergerPolicySummary])
            List containing the essential asset thresholds in the model and list containing the summaries of the outcomes of the model.
        """
        asset_range: list[Types.ThresholdItem] = self._get_asset_thresholds()
        summaries: list[Types.OptimalMergerPolicySummary] = []
        for i in range(len(asset_range) - 1):
            self.model.startup_assets = (
                self.model.asset_distribution.inverse_cumulative(asset_range[i].value)
                + self.model.asset_distribution.inverse_cumulative(
                    asset_range[i + 1].value
                )
            ) / 2
            summaries.append(self.model.summary())
        return summaries

    def _get_asset_thresholds(self) -> list[Types.ThresholdItem]:
        """
        Generates a list with all essential threshold concerning the assets of a start-up.

        Returns
        -------
        list[Fumagalli_Motta_Tarantino_2020.Types.ThresholdItem]
            List containing the essential asset thresholds in the model.
        """
        min_threshold = Types.ThresholdItem("0.5", 0.5)
        max_threshold = Types.ThresholdItem(
            "$F(K)$",
            self.model.asset_distribution.cumulative(self.model.development_costs),
        )
        thresholds = self._get_essential_thresholds()
        essential_thresholds: list[Types.ThresholdItem] = []
        for threshold in thresholds:
            if min_threshold.value < threshold.value < max_threshold.value:
                essential_thresholds.append(threshold)
        thresholds = sorted(essential_thresholds, key=lambda x: x.value)
        thresholds.insert(0, min_threshold)
        thresholds.append(max_threshold)
        return thresholds

    def _get_essential_thresholds(self):
        thresholds: list[Types.ThresholdItem] = [
            Types.ThresholdItem(
                "$\\Gamma$", self.model.asset_distribution_threshold_strict
            ),
            Types.ThresholdItem("$\\Phi$", self.model.asset_distribution_threshold),
            Types.ThresholdItem(
                "$\\Phi^T$", self.model.asset_distribution_threshold_laissez_faire
            ),
            Types.ThresholdItem(
                "$\\Phi^{\\prime}$",
                self.model.asset_distribution_threshold_intermediate,
            ),
            Types.ThresholdItem("$F(\\bar{A})$", self.model.asset_threshold_cdf),
            Types.ThresholdItem(
                "$F(\\bar{A}^T)$", self.model.asset_threshold_late_takeover_cdf
            ),
        ]
        return thresholds

    @staticmethod
    def _get_x_labels_ticks(
        asset_thresholds: list[Types.ThresholdItem],
    ) -> (list[float], list[str]):
        """
        Generates the locations of the ticks on the x-axis and the corresponding labels on the x-axis.

        Parameters
        ----------
        asset_thresholds: list[Fumagalli_Motta_Tarantino_2020.Types.ThresholdItem]
            List with all threshold the assets.

        Returns
        -------
        (list[float], list[str])
            A list containing the ticks on the x-axis and a list containing the labels on the x-axis.
        """
        x_ticks: list[float] = []
        x_labels: list[str] = []
        for threshold in asset_thresholds:
            x_ticks.append(threshold.value)
            x_labels.append(threshold.name)
        return x_ticks, x_labels

    def _set_x_ticks(self, asset_thresholds: list[Types.ThresholdItem]) -> None:
        x_ticks, x_labels = self._get_x_labels_ticks(asset_thresholds)
        self.ax.xaxis.set_major_locator(FixedLocator(x_ticks[::2]))
        self.ax.xaxis.set_minor_locator(FixedLocator(x_ticks[1::2]))
        self.ax.set_xticklabels(x_labels[::2])
        self.ax.set_xticklabels(x_labels[1::2], minor=True)
        self.ax.tick_params(
            which="minor",
            bottom=False,
            top=True,
            labelbottom=False,
            labeltop=True,
            axis="x",
        )
        self.ax.tick_params(which="both", length=6, axis="x")
        for threshold in asset_thresholds:
            if threshold.value != max(item.value for item in asset_thresholds):
                self.ax.axvline(threshold.value, linestyle="--", color="k")

    @staticmethod
    def _get_y_ticks(
        spacing: float, bar_height: float, y_labels: list[str]
    ) -> list[float]:
        return [(i + 1) * spacing + bar_height * i for i in range(len(y_labels))]

    def _set_y_ticks(self, bar_height, spacing, y_labels):
        y_ticks = self._get_y_ticks(spacing, bar_height, y_labels)
        self.ax.set_yticks(y_ticks)
        self.ax.set_yticklabels(y_labels)

    def _get_label_color(self, label) -> (str, str):
        """
        Returns the color and the final label for a legend entry.

        Through this method, duplications in the legend are avoided.

        Parameters
        ----------
        label: str

        Returns
        -------
        (str, str)
            String representing the final label and a string representing the color.
        """
        if label in self.labels:
            return "_nolegend_", self.colors[label]
        self.colors[label] = IVisualize.colors[len(self.labels)]
        self.labels.append(label)
        return label, self.colors[label]

    def _get_summaries(self) -> list[list[Types.OptimalMergerPolicySummary]]:
        return [self._get_outcomes_asset_range()]

    def plot(self, **kwargs) -> (plt.Figure, plt.Axes):
        asset_range = self._get_asset_thresholds()
        merger_policies_summaries = self._get_summaries()
        assert asset_range is not None
        assert merger_policies_summaries is not None
        self.labels.clear()
        self.colors.clear()

        spacing: float = kwargs.get("spacing", 0.1)
        bar_height: float = kwargs.get("bar_height", 0.2)
        y_labels: list[str] = []
        for number_merger_policy, summaries in enumerate(merger_policies_summaries):
            y_labels.append(summaries[0].set_policy.abbreviation())
            for summary_index, summary in enumerate(summaries):
                length: float = (
                    asset_range[summary_index + 1].value
                    - asset_range[summary_index].value
                )
                label: str = self._get_summary_latex(summary)
                label, color = self._get_label_color(label)
                self.ax.barh(
                    y=spacing * (number_merger_policy + 1)
                    + bar_height * number_merger_policy,
                    width=length,
                    left=asset_range[summary_index].value,
                    height=bar_height,
                    color=color,
                    label=label,
                )
        self._set_legend()
        if kwargs.get("legend", True):
            self.ax.annotate(
                self._get_symbol_legend(),
                xy=(asset_range[0].value, 0),
                xytext=(0, -50),
                textcoords="offset points",
                horizontalalignment="left",
                verticalalignment="top",
            )
        self.ax.margins(y=spacing, x=0)
        self._set_x_ticks(asset_range)
        self._set_y_ticks(bar_height, spacing, y_labels)
        self.ax.set_xlabel("Cumulative Distribution Value of Assets $F(A)$")
        self.ax.set_ylabel("Merger Policy")
        self._set_tight_layout()
        return self.fig, self.ax


class MergerPoliciesAssetRange(AssetRange):
    def __init__(self, model: Models.OptimalMergerPolicy, **kwargs):
        super(MergerPoliciesAssetRange, self).__init__(model, **kwargs)

    def _get_outcomes_different_merger_policies(
        self,
    ) -> list[list[Types.OptimalMergerPolicySummary]]:
        outcomes: list[list[Types.OptimalMergerPolicySummary]] = []
        for merger_policy in Types.MergerPolicies:
            self.model.merger_policy = merger_policy
            outcomes.append(self._get_outcomes_asset_range())
        return outcomes

    def _get_summaries(self) -> list[list[Types.OptimalMergerPolicySummary]]:
        return self._get_outcomes_different_merger_policies()


class Timeline(IVisualize):
    """
    Visualizes the timeline of events for a specific model.
    """

    def __init__(self, model: Models.OptimalMergerPolicy, **kwargs):
        super(Timeline, self).__init__(model, **kwargs)

    def _prepare_content(self) -> (list[str], list[str]):
        """
        Generates the label and points in time of the events in the model.

        Returns
        -------
        (list[str], list[str])
            List containing label for the events and list containing the points in time of the events.
        """
        summary: Types.OptimalMergerPolicySummary = self.model.summary()
        values: list[str] = [
            "AA establishes "
            + self._policy_str(summary.set_policy)
            + "\nmerger policy",
            self._takeover_attempt_str(summary.early_bidding_type),
            self._takeover_str(summary.early_takeover),
            self._development_str(
                summary.development_attempt,
                summary.early_takeover,
                self.model.is_killer_acquisition(),
            ),
            self._success_str(summary.development_outcome),
            self._takeover_attempt_str(summary.late_bidding_type),
            self._takeover_str(summary.late_takeover),
            "Payoffs",
        ]
        x_labels: list[str] = [
            "t=0",
            "t=1a",
            "t=1b",
            "t=1c",
            "t=1d",
            "t=2a",
            "t=2b",
            "t=3",
        ]
        return values, x_labels

    @staticmethod
    def _takeover_attempt_str(takeover: Types.Takeover) -> str:
        """
        Generate label for takeover event.

        Parameters
        ----------
        takeover: Fumagalli_Motta_Tarantino_2020.Types.Takeover
            Option for takeover chosen by the incumbent.

        Returns
        -------
        str
            Label for takeover event.
        """
        return str(takeover) + "\nby incumbent"

    @staticmethod
    def _policy_str(policy: Types.MergerPolicies) -> str:
        """
        Generate label for establishing of merger policy event.

        Parameters
        ----------
        policy: Fumagalli_Motta_Tarantino_2020.Types.MergerPolicies
            Policy established by the AA at beginning.

        Returns
        -------
        str
            Label for establishing of merger policy event.
        """
        policy_str = str(policy).lower()
        if "intermediate" in policy_str:
            return policy_str.replace("intermediate", "intermediate\n")
        return policy_str

    @staticmethod
    def _takeover_str(is_takeover: bool) -> str:
        """
        Generates a label about the takeover event (option and approval).

        Parameters
        ----------
        is_takeover: bool
            If true, the takeover is approved by AA and the start-up.

        Returns
        -------
        str
            Label about the takeover event (option and approval).
        """
        if is_takeover:
            return "Takeover\napproved"
        return "No takeover\noccurs"

    @staticmethod
    def _development_str(
        is_development: bool, is_early_takeover: bool, is_killer_acqui: bool
    ) -> str:
        """
        Generates a label about the development event (attempt and shelving).

        Parameters
        ----------
        is_development: bool
            True, if the owner is developing the product (otherwise, the product is shelved).
        is_early_takeover: bool
            True, if an early takeover occurs.

        Returns
        -------
        str
            Label about the development event (attempt and shelving).
        """
        owner = "Incumbent" if is_early_takeover else "Start-up"
        killer_acqui_str = "\n(killer acquisition)" if is_killer_acqui else ""
        if is_development:
            return f"{owner}\ndevelops product"
        return f"{owner}\nshelves product{killer_acqui_str}"

    @staticmethod
    def _success_str(is_successful: bool) -> str:
        """
        Generates a label about the development outcome event.

        Parameters
        ----------
        is_successful: bool
            True, if the development of the product is successful.

        Returns
        -------
        str
            Label about the development outcome event.
        """
        if is_successful:
            return "Development is\nsuccessful"
        return "Development is\nnot successful"

    def plot(self, **kwargs) -> (plt.Figure, plt.Axes):
        values, x_labels = self._prepare_content()
        x_ticks = range(len(x_labels))

        # height of lines from points in time
        # levels = np.tile([1, -1], int(np.ceil(len(x_ticks) / 2)))[: len(x_ticks)]
        levels = [-1, 1, 0.6, -1, 1, -1, -0.6, 1]

        # Create figure and plot a stem plot with the date
        self.ax.set(title="Timeline")
        self.ax.annotate(
            self._parameter_latex(self.model),
            xy=(math.fsum(x_ticks) / len(x_ticks), 1.9),
            horizontalalignment="center",
            verticalalignment="top",
            fontsize="x-small",
        )

        self.ax.vlines(
            x_ticks, 0, levels, color="lightgray", linewidths=1
        )  # The vertical stems.
        self.ax.plot(
            x_ticks, np.zeros_like(x_ticks), "-o", color="k", markerfacecolor="w"
        )  # Baseline and markers on it.

        # annotate lines
        for d, l, r in zip(x_ticks, levels, values):
            self.ax.annotate(
                str(r),
                xy=(d, l),
                xytext=(0, np.sign(l) * 8),
                textcoords="offset points",
                horizontalalignment="center",
                verticalalignment="bottom" if l > 0 else "top",
            )

        # set x-axis
        self.ax.set_xticks(x_ticks)
        self.ax.set_xticklabels(x_labels)

        # remove y-axis and spines
        self.ax.yaxis.set_visible(False)
        self.ax.spines[["left", "top", "right"]].set_visible(False)

        self.ax.margins(y=0.45)
        return self.fig, self.ax


class Payoffs(IVisualize):
    def plot(self, **kwargs) -> (plt.Figure, plt.Axes):
        payoffs: dict[str, float] = self._get_payoffs()
        bar_width = 0.35
        spacing = 0.05

        self._plot_payoffs_bars(payoffs, bar_width, spacing, **kwargs)

        self.ax.set_title("Payoffs for different Market Configurations")
        self._set_legend()
        if kwargs.get("legend", True):
            self.ax.annotate(
                self._get_payoff_legend(),
                xy=(-bar_width, 0),
                xytext=(0, -30),
                textcoords="offset points",
                horizontalalignment="left",
                verticalalignment="top",
            )
        self._set_tight_layout()

    def _plot_payoffs_bars(
        self, payoffs: dict[str, float], bar_width: float, spacing: float, **kwargs
    ) -> None:
        """
        Plots the bars representing the payoffs for different market configurations of different stakeholders on the specified axis.

        Parameters
        ----------
        axis matplotlib.axes.Axes
            To plot the bars on.
        bar_width: float
            Width of a bar in the plot.
        spacing: float
            Spacing between the bars on the plot.
        **kwargs
            Optional key word arguments for the payoff plot.<br>
            - opacity : Opacity of the not optimal payoffs.<br>
        """
        max_values: list[int] = self._set_max_values(list(payoffs.values()))
        for number_bar, (label, height) in enumerate(payoffs.items()):
            x_coordinate: float = self._get_x_coordinate(bar_width, number_bar, spacing)
            self.ax.annotate(
                label,
                xy=(x_coordinate, 0),
                xytext=(0, -5),
                textcoords="offset points",
                horizontalalignment="center",
                verticalalignment="top",
            )
            if number_bar > 3:
                label = "__nolegend__"
            else:
                label = label[:-3] + "$"
            self.ax.bar(
                x=x_coordinate,
                width=bar_width,
                height=height,
                label=label,
                color=self._get_color(number_bar),
                alpha=kwargs.get("max_opacity", 1)
                if number_bar in max_values
                else kwargs.get("min_opacity", 0.5),
            )
            self.ax.tick_params(
                axis="x",  # changes apply to the x-axis
                which="both",  # both major and minor ticks are affected
                bottom=False,  # ticks along the bottom edge are off
                labelbottom=False,
            )  # labels along the bottom edge are off

    @staticmethod
    def _set_max_values(payoffs: list[float]) -> list[int]:
        return [
            Payoffs._get_max_index(0, payoffs),
            Payoffs._get_max_index(1, payoffs),
            Payoffs._get_max_index(2, payoffs),
            Payoffs._get_max_index(3, payoffs),
        ]

    @staticmethod
    def _get_max_index(offset_index: int, payoffs: list[float]) -> int:
        values: list[float] = payoffs[offset_index::4]
        max_value: float = max(values)
        group_index: int = values.index(max_value)
        return group_index * 4 + offset_index

    @staticmethod
    def _get_x_coordinate(bar_width, number_bar, spacing):
        group_spacing: int = (math.trunc(number_bar / 4) % 4) * 8
        return spacing * (number_bar + 1 + group_spacing) + bar_width * number_bar

    @staticmethod
    def _get_color(number_bar: int) -> str:
        return IVisualize.colors[number_bar % 4]

    def _get_payoffs(self) -> dict[str, float]:
        return {
            "$\\pi_S^m$": 0,
            "$\\pi_I^m$": self.model.incumbent_profit_without_innovation,
            "$CS^m$": self.model.cs_without_innovation,
            "$W^m$": self.model.w_without_innovation,
            "$\\pi^M_S$": 0,
            "$\\pi^M_I$": self.model.incumbent_profit_with_innovation,
            "$CS^M$": self.model.cs_with_innovation,
            "$W^M$": self.model.w_with_innovation,
            "$\\pi^d_S$": self.model.startup_profit_duopoly,
            "$\\pi^d_I$": self.model.incumbent_profit_duopoly,
            "$CS^d$": self.model.cs_duopoly,
            "$W^d$": self.model.w_duopoly,
        }

    @staticmethod
    def _get_payoff_legend() -> str:
        return (
            "$\\pi_S$: Profit of the start-up\n"
            "$\\pi_I$: Profit of the incumbent\n"
            "$CS$: Consumer surplus\n"
            "$W$: Total welfare\n"
            "$m$: Monopoly without the innovation\n"
            "$M$: Monopoly after successful development by the incumbent\n"
            "$d$: Duopoly (requires successful development by the start-up)\n"
        )
