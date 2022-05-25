# Copyright 2021 Cognite AS
from .change_point_detector import cpd_ed_pelt
from .drift_detector import drift
from .steady_state import ssd_cpd, ssid, vma
from .unchanged_signal_detector import unchanged_signal_detector


TOOLBOX_NAME = "Detect"

__all__ = ["drift", "ssid", "vma", "ssd_cpd", "cpd_ed_pelt", "unchanged_signal_detector"]
