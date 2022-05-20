# Copyright (c) 2021-2022, NVIDIA CORPORATION & AFFILIATES
#
# SPDX-License-Identifier: BSD-3-Clause

"""
Interface to CuPy operations.
"""

__all__ = ['CupyPackage']

import cupy as cp

from .package_ifc import Package


class CupyPackage(Package):

    @staticmethod
    def get_current_stream(device_id):
        with cp.cuda.Device(device_id):
            stream = cp.cuda.get_current_stream()
        return stream

    @staticmethod
    def to_stream_pointer(stream):
        return stream.ptr

    @staticmethod
    def to_stream_context(stream):
        return stream

    @staticmethod
    def create_external_stream(device_id, stream_ptr):
        return cp.cuda.ExternalStream(stream_ptr)

    @staticmethod
    def create_stream(device_id):
        with cp.cuda.Device(device_id):
            stream = cp.cuda.Stream(null=False, non_blocking=False, ptds=False)
        return stream
