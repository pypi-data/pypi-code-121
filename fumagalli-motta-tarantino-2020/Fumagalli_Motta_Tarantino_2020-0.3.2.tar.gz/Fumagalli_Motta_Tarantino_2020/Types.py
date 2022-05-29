from dataclasses import dataclass
from enum import Enum


class MergerPolicies(Enum):
    """
    Defines the available merger policies in the models.
    """

    Strict = "Strict"
    """The AA authorises only takeovers that, at the moment in which they are reviewed, are expected to increase total welfare."""
    Intermediate_late_takeover_prohibited = "Intermediate (late takeover prohibited)"
    """The AA blocks late takeovers, but is more lenient with early takeovers."""
    Intermediate_late_takeover_allowed = "Intermediate (late takeover allowed)"
    """The AA authorises late takeovers, but is stricter with early takeovers."""
    Laissez_faire = "Laissez-faire"
    """The intervention threshold of the AA is so high that any acquisition would be allowed."""

    def abbreviation(self) -> str:
        """
        Generates a string containing the abbreviation of the current merger policy.

        Returns
        -------
        str
            Abbreviation of the current merger policy.
        """
        if self is MergerPolicies.Intermediate_late_takeover_prohibited:
            return "$I^P$"
        if self is MergerPolicies.Intermediate_late_takeover_allowed:
            return "$I^A$"
        return f"${self.value[0]}$"

    def __str__(self) -> str:
        """
        Returns the string representation of the current merger policy.

        Returns
        -------
        str
            String representation of the current merger policy.
        """
        return self.value

    @staticmethod
    def legend() -> str:
        """
        Generates a string containing the legend of the possible merger policies.

        Returns
        -------
        str
            Containing the legend for the merger policies.
        """
        return (
            f"{MergerPolicies.Strict.abbreviation()}: Strict\n"
            f"{MergerPolicies.Intermediate_late_takeover_prohibited.abbreviation()}: Intermediate (late takeover prohibited)\n"
            f"{MergerPolicies.Intermediate_late_takeover_allowed.abbreviation()}: Intermediate (late takeover allowed)\n"
            f"{MergerPolicies.Laissez_faire.abbreviation()}: Laissez-faire"
        )


class Takeover(Enum):
    """
    Defines the available options for a takeover of the start-up by the incumbent.
    """

    No = "No bid"
    """The incumbent does not bid for the start-up."""
    Separating = "Separating bid"
    """The incumbent offers a low takeover price targeting only the credit-rationed start-ups."""
    Pooling = "Pooling bid"
    """The incumbent offers a high takeover price such that a start-up would always accept, irrespective of the amount of own assets."""

    def abbreviation(self) -> str:
        """
        Generates a string containing the abbreviation of the current takeover option.

        Returns
        -------
        str
            Abbreviation of the current takeover option.
        """
        return f"${self.value[0]}$"

    def __str__(self) -> str:
        """
        Returns the string representation of the current takeover option.

        Returns
        -------
        str
            String representation of the current takeover option.
        """

        return self.value

    @staticmethod
    def legend() -> str:
        """
        Generates a string containing the legend of the possible takeover options.

        Returns
        -------
        str
            Containing the legend for the takeover options.
        """
        return (
            f"{Takeover.No.abbreviation()}: No bid by the incumbent\n"
            f"{Takeover.Separating.abbreviation()}: Separating bid by the incumbent\n"
            f"{Takeover.Pooling.abbreviation()}: Pooling bid by the incumbent"
        )


@dataclass(frozen=True)
class ThresholdItem:
    """
    Threshold item containing the name (string representation) and the value (threshold express in float value).
    """

    name: str
    value: float

    def __eq__(self, other):
        return self.value == other.value

    def __lt__(self, other):
        return self.value < other.value


@dataclass(frozen=True)
class Summary:
    """
    Summary of Fumagalli_Motta_Tarantino_2020.Models.MergerPolicy.
    """

    set_policy: MergerPolicies
    credit_rationed: bool
    early_bidding_type: Takeover
    late_bidding_type: Takeover
    development_attempt: bool
    development_outcome: bool
    early_takeover: bool
    late_takeover: bool


@dataclass(frozen=True)
class OptimalMergerPolicySummary(Summary):
    """
    Summary of Fumagalli_Motta_Tarantino_2020.Models.OptimalMergerPolicy.
    """

    optimal_policy: MergerPolicies
