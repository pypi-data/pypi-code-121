__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

__version__ = "0.0.14"
AUTHOR = "Vanessa Sochat"
AUTHOR_EMAIL = "vsoch@users.noreply.github.com"
NAME = "compspec"
PACKAGE_URL = "https://github.com/compspec/compspec"
KEYWORDS = "diff, comparison, composition, specification, abi, compatibility, symbols"
DESCRIPTION = "Specification and model for describing and comparing things."
LICENSE = "LICENSE"

################################################################################
# Global requirements

INSTALL_REQUIRES = (
    ("clingo", {"min_version": None}),
    ("pyaml", {"min_version": None}),
)

TESTS_REQUIRES = (("pytest", {"min_version": "4.6.2"}),)
INSTALL_REQUIRES_ALL = INSTALL_REQUIRES + TESTS_REQUIRES
