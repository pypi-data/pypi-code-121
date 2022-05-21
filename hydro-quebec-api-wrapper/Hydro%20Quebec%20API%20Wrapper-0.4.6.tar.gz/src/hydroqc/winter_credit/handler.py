"""Winter credit processing."""
import datetime
import logging
from typing import Optional, Callable, Any

from hydroqc.winter_credit.peak import Peak, Anchor
from hydroqc.winter_credit.consts import (
    EST_TIMEZONE,
    DEFAULT_MORNING_PEAK_START,
    DEFAULT_EVENING_PEAK_START,
)
from hydroqc.error import HydroQcWinterCreditError
from hydroqc.hydro_api.client import HydroClient


def winter_credit_enabled(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorate any methods that use self.data to avoid useless calls."""
    # def myfunction(self: WinterCreditHandler) -> Optional[Any]:
    def myfunction(self: Any) -> Optional[Any]:
        if self.is_enabled:
            return func(self)
        self._logger.info("Winter credit not enabled.")
        return None

    return myfunction


def _now() -> datetime.datetime:
    """Get EST localized now datetime."""
    return EST_TIMEZONE.localize(datetime.datetime.now())


class WinterCreditHandler:
    """Winter Credit extra logic.

    This class supplements Hydro API data by providing calculated values for pre_heat period,
    anchor period detection as well as next event information.
    """

    # peaks: list[Peak]

    def __init__(
        self,
        webuser_id: str,
        customer_id: str,
        contract_id: str,
        hydro_client: HydroClient,
        logger: logging.Logger,
    ):
        """Winter Credit constructor."""
        self._no_partenaire_demandeur: str = webuser_id
        self._no_partenaire_titulaire: str = customer_id
        self._no_contrat: str = contract_id
        self._hydro_client: HydroClient = hydro_client
        self._logger: logging.Logger = logger

        self._raw_data: dict[str, Any] = {}

    # Basics
    @property
    def webuser_id(self) -> str:
        """Get webuser id."""
        return self._no_partenaire_demandeur

    @property
    def customer_id(self) -> str:
        """Get customer id."""
        return self._no_partenaire_titulaire

    @property
    def contract_id(self) -> str:
        """Get contract id."""
        return self._no_contrat

    @property
    def is_enabled(self) -> bool:
        """Is winter credit mode actived."""
        if "optionTarifActuel" not in self._raw_data:
            # If we don't know, let's try to get the information
            return True
        return self._raw_data["optionTarifActuel"] == "CPC"

    # Fetch raw data
    async def refresh_data(self) -> None:
        """Get data from HydroQuebec web site."""
        self._logger.debug("Fetching data from HydroQuebec...")
        self._raw_data = await self._hydro_client.get_winter_credit(
            self.webuser_id, self.customer_id, self.contract_id
        )
        self._logger.debug("Data fetched from HydroQuebec...")
        # Ensure that peaks are sorted by date
        if self._raw_data["periodesEffacementsHivers"]:
            self._raw_data["periodesEffacementsHivers"][0][
                "periodesEffacementHiver"
            ].sort(key=lambda x: (x["dateEffacement"], x["heureDebut"]))

    @property
    def raw_data(self) -> dict[str, Any]:
        """Return raw collected data."""
        return self._raw_data

    # Internals
    @property
    def _raw_critical_peaks(self) -> list[dict[str, Any]]:
        """Shortcut to get quickly critical peaks."""
        return self._raw_data["periodesEffacementsHivers"][0]["periodesEffacementHiver"]

    def _set_peak_critical(self, peak: Peak) -> None:
        """Determine if the passed peak is critical or not, and save it to the object."""
        if peak.morning_evening.upper() == "EVENING":
            default_start_time_str = DEFAULT_EVENING_PEAK_START.strftime("%H:%M:%S")
        elif peak.morning_evening.upper() == "MORNING":
            default_start_time_str = DEFAULT_MORNING_PEAK_START.strftime("%H:%M:%S")
        else:
            raise HydroQcWinterCreditError("Bad morning_evening value")

        for critical_peak in self._raw_critical_peaks:
            critical_peak_date = datetime.datetime.strptime(
                critical_peak["dateEffacement"], "%Y-%m-%dT%H:%M:%S.%f%z"
            ).date()
            if (
                critical_peak_date == peak.day
                and critical_peak["heureDebut"] == default_start_time_str
            ):
                raw_stats = critical_peak.copy()
                peak.set_critical(raw_stats)
                return

    # general data
    @property  # type: ignore[misc]
    @winter_credit_enabled
    def winter_start_date(self) -> datetime.datetime:
        """Get start date of the winter credits."""
        return datetime.datetime.strptime(
            self._raw_data["periodesEffacementsHivers"][0]["dateDebutPeriodeHiver"],
            "%Y-%m-%dT%H:%M:%S.%f%z",
        )

    @property  # type: ignore[misc]
    @winter_credit_enabled
    def winter_end_date(self) -> datetime.datetime:
        """Get end date of the winter credits."""
        return datetime.datetime.strptime(
            self._raw_data["periodesEffacementsHivers"][0]["dateFinPeriodeHiver"],
            "%Y-%m-%dT%H:%M:%S.%f%z",
        )

    @property  # type: ignore[misc]
    @winter_credit_enabled
    def cumulated_credit(self) -> float:
        """Get cumulated credits."""
        if self._raw_data["montantEffaceProjete"] == "":
            return 0.0
        try:
            return float(self._raw_data["montantEffaceProjete"])
        except ValueError as exp:
            raise HydroQcWinterCreditError("Bad cumulated credit raw value") from exp

    # Peaks data
    @property  # type: ignore[misc]
    @winter_credit_enabled
    def peaks(self) -> list[Peak]:
        """Get all peaks of the current winter."""
        current_date = self.winter_start_date
        delta = datetime.timedelta(days=1)
        peak_list = []
        while current_date < self.winter_end_date:
            # Morning
            peak = Peak(current_date, "morning")
            self._set_peak_critical(peak)
            peak_list.append(peak)
            # Evening
            peak = Peak(current_date, "evening")
            self._set_peak_critical(peak)
            peak_list.append(peak)
            # Next day
            current_date += delta
        peak_list.sort(key=lambda x: x.start_date)
        return peak_list

    @property  # type: ignore[misc]
    @winter_credit_enabled
    def sonic(self) -> list[Peak]:
        """Piaf's joke."""
        return self.peaks

    @property  # type: ignore[misc]
    @winter_credit_enabled
    def critical_peaks(self) -> list[Peak]:
        """Get all critical peaks of the current credits."""
        return [p for p in self.peaks if p.is_critical]

    # Current peak
    @property  # type: ignore[misc]
    @winter_credit_enabled
    def current_peak(self) -> Optional[Peak]:
        """Get current peak.

        Return None if no peak is currently running
        FIXME This could be USELESS
        """
        now = _now()
        peaks = [p for p in self.peaks if p.start_date < now < p.end_date]
        if len(peaks) > 1:
            raise HydroQcWinterCreditError("There is more than one current peak !")
        if len(peaks) == 1:
            return peaks[0]
        return None

    @property  # type: ignore[misc]
    @winter_credit_enabled
    def current_peak_is_critical(self) -> Optional[bool]:
        """Return True if the current peak is critical."""
        if self.current_peak:
            return bool(self.current_peak.is_critical)
        return None

    # In progress
    @property  # type: ignore[misc]
    @winter_credit_enabled
    def current_state(self) -> str:
        """Get the current state of the winter credit handler.

        It returns critical_anchor, anchor, critical_peak, peak or normal
        This value should help for automation.
        """
        now = _now()
        current_anchors = [
            p.anchor
            for p in self.peaks
            if p.anchor.start_date < now < p.anchor.end_date
        ]
        if current_anchors and current_anchors[0].is_critical:
            return "critical_anchor"
        if current_anchors and not current_anchors[0].is_critical:
            return "anchor"

        current_peaks = [p for p in self.peaks if p.start_date < now < p.end_date]
        if current_peaks and current_peaks[0].is_critical:
            return "critical_peak"
        if current_peaks and not current_peaks[0].is_critical:
            return "peak"
        return "normal"

    @property  # type: ignore[misc]
    @winter_credit_enabled
    def preheat_in_progress(self) -> bool:
        """Get the preheat state.

        Returns True if we have a preheat period is in progress.
        """
        now = _now()
        if self.next_peak is None:
            return False
        return self.next_peak.preheat.start_date < now < self.next_peak.preheat.end_date

    # Upcoming
    @property  # type: ignore[misc]
    @winter_credit_enabled
    def is_any_critical_peak_coming(self) -> bool:
        """Get critical state of the upcoming events.

        It will return True if one of the "not completed yet" peak is critical.

        Retourne True si au moins un des prochains peaks non terminés est critical.
        """
        return bool(self.next_critical_peak)

    # Next peak
    @property  # type: ignore[misc]
    @winter_credit_enabled
    def next_peak(self) -> Optional[Peak]:
        """Get next peak or current peak."""
        now = _now()
        peaks = [p for p in self.peaks if now < p.end_date]
        if not peaks:
            return None
        next_peak = min(peaks, key=lambda x: x.start_date)
        return next_peak

    @property  # type: ignore[misc]
    @winter_credit_enabled
    def next_peak_is_critical(self) -> bool:
        """Return True if the following next peak is critical.

        This method is quite useless because, to call this attribute

        * we need to write::

            contract.winter_credit.next_peak_is_critical

        * but it equivalent to::

            contract.winter_credit.next_peak.is_critical

        """
        if self.next_peak is None:
            return False
        return self.next_peak.is_critical

    @property  # type: ignore[misc]
    @winter_credit_enabled
    def next_critical_peak(self) -> Optional[Peak]:
        """Get next peak or current peak."""
        now = _now()
        peaks = [p for p in self.critical_peaks if now < p.end_date]
        if not peaks:
            return None
        next_peak = min(peaks, key=lambda x: x.start_date)
        return next_peak

    # Today peaks
    @property  # type: ignore[misc]
    @winter_credit_enabled
    def today_morning_peak(self) -> Optional[Peak]:
        """Get the peak of today morning."""
        now = _now()
        peaks = [p for p in self.peaks if p.day == now.date() and p.is_morning]
        if len(peaks) > 1:
            raise HydroQcWinterCreditError(
                "There is more than one morning peak today !"
            )
        if len(peaks) == 1:
            return peaks[0]
        return None

    @property  # type: ignore[misc]
    @winter_credit_enabled
    def today_evening_peak(self) -> Optional[Peak]:
        """Get the peak of today evening."""
        now = _now()
        peaks = [p for p in self.peaks if p.day == now.date() and p.is_evening]
        if len(peaks) > 1:
            raise HydroQcWinterCreditError(
                "There is more than one evening peak today !"
            )
        if len(peaks) == 1:
            return peaks[0]
        return None

    # Tomorrow Peaks
    @property  # type: ignore[misc]
    @winter_credit_enabled
    def tomorrow_morning_peak(self) -> Optional[Peak]:
        """Get the peak of tomorrow morning."""
        now = _now()
        peaks = [
            p
            for p in self.peaks
            if p.day == now.date() + datetime.timedelta(days=1) and p.is_morning
        ]
        if len(peaks) > 1:
            raise HydroQcWinterCreditError(
                "There is more than one morning peak tomorrow !"
            )
        if len(peaks) == 1:
            return peaks[0]
        return None

    @property  # type: ignore[misc]
    @winter_credit_enabled
    def tomorrow_evening_peak(self) -> Optional[Peak]:
        """Get the peak of tomorrow evening."""
        now = _now()
        peaks = [
            p
            for p in self.peaks
            if p.day == now.date() + datetime.timedelta(days=1) and p.is_evening
        ]
        if len(peaks) > 1:
            raise HydroQcWinterCreditError(
                "There is more than one evening peak tomorrow !"
            )
        if len(peaks) == 1:
            return peaks[0]
        return None

    # Yesterday peaks
    @property  # type: ignore[misc]
    @winter_credit_enabled
    def yesterday_morning_peak(self) -> Optional[Peak]:
        """Get the peak of yesterday morning."""
        now = _now()
        peaks = [
            p
            for p in self.peaks
            if p.day == now.date() - datetime.timedelta(days=1) and p.is_morning
        ]
        if len(peaks) > 1:
            raise HydroQcWinterCreditError(
                "There is more than one morning peak yesterday !"
            )
        if len(peaks) == 1:
            return peaks[0]
        return None

    @property  # type: ignore[misc]
    @winter_credit_enabled
    def yesterday_evening_peak(self) -> Optional[Peak]:
        """Get the peak of yesterday evening."""
        now = _now()
        peaks = [
            p
            for p in self.peaks
            if p.day == now.date() - datetime.timedelta(days=1) and p.is_evening
        ]
        if len(peaks) > 1:
            raise HydroQcWinterCreditError(
                "There is more than one evening peak yesterday !"
            )
        if len(peaks) == 1:
            return peaks[0]
        return None

    # Anchors
    @property  # type: ignore[misc]
    @winter_credit_enabled
    def next_anchor(self) -> Optional[Anchor]:
        """Next or current anchor."""
        now = _now()
        anchors = [p.anchor for p in self.peaks if now < p.anchor.end_date]
        if anchors:
            next_anchor = min(anchors, key=lambda x: x.start_date)
            return next_anchor
        return None
