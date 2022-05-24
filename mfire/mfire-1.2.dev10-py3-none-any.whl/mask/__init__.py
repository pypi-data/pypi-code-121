"""mfire.mask module

This module handles everything related to the mask

"""
from mfire.mask.mask_processor import MaskProcessor
from mfire.mask.fusion import extract_areaName, check_fusion, perform_poly_fusion
from mfire.mask.altitude_mask import generate_mask_by_altitude

__all__ = [
    "MaskProcessor",
    "extract_areaName",
    "check_fusion",
    "perform_poly_fusion",
    "generate_mask_by_altitude",
]
