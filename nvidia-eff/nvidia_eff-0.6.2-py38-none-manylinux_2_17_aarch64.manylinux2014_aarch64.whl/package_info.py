# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.

# Version of the project - please follow semantic versioning 2.0: https://semver.org/
MAJOR = 0
MINOR = 6
PATCH = 2
PRE_RELEASE = ''

# Use the following formatting: major.minor.patch[-pre_release]
# Examples: 23.0.123 | 1.0.22-alpha5
__version__ = str(MAJOR) + "." + str(MINOR) + "." + str(PATCH) + ("-" + PRE_RELEASE if PRE_RELEASE != "" else "")

# Version of the file format.
__format_version__ = 3

# Other package info.
__package_name__ = "nvidia-eff"
__description__ = "NVIDIA Exchange File Format"
__keywords__ = "nvidia, eff, archive"

__contact_names__ = "Tomasz Kornuta, Varun Praveen"
__contact_emails__ = "tkornuta@nvidia.com, vpraveen@nvidia.com"

__license__ = "NVIDIA Proprietary Software"
