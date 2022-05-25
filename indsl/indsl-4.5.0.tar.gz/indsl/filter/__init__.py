# Copyright 2021 Cognite AS
from .simple_filters import status_flag_filter
from .trend import trend_extraction_hilbert_transform
from .wavelet_filter import wavelet_filter


__all__ = ["wavelet_filter", "status_flag_filter", "trend_extraction_hilbert_transform"]

TOOLBOX_NAME = "Filter"
