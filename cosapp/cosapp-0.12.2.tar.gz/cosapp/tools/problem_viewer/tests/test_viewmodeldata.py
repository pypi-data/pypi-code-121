""" Unit tests for the problem interface."""

import unittest
import os

from tempfile import mkdtemp
from collections import OrderedDict

from cosapp.tools.problem_viewer.problem_viewer import _get_viewer_data, view_model
from cosapp.tests.library.systems.others import ComplexTurbofan


class TestViewModelData(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.dir = mkdtemp()
        self.problem_filename = os.path.join(self.dir, "problem_n2")
        self.problem_html_filename = self.problem_filename
        self.expected_tree = OrderedDict(
            [
                ("name", "turbofan"),
                ("type", "subsystem"),
                ("subsystem_type", "group"),
                (
                    "children",
                    [
                        OrderedDict(
                            [
                                ("name", "atm"),
                                ("type", "subsystem"),
                                ("subsystem_type", "group"),
                                (
                                    "children",
                                    [
                                        OrderedDict(
                                            [
                                                ("name", "inwards"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "Pt"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "Tt"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "fl_out"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "Tt"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "Pt"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                    ],
                                ),
                            ]
                        ),
                        OrderedDict(
                            [
                                ("name", "inlet"),
                                ("type", "subsystem"),
                                ("subsystem_type", "group"),
                                (
                                    "children",
                                    [
                                        OrderedDict(
                                            [
                                                ("name", "fl_in"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "Tt"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "Pt"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "W_in"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "W"),
                                                                ("type", "param"),
                                                            ]
                                                        )
                                                    ],
                                                ),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "fl_out"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "Tt"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "Pt"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "W"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                    ],
                                ),
                            ]
                        ),
                        OrderedDict(
                            [
                                ("name", "fanC"),
                                ("type", "subsystem"),
                                ("subsystem_type", "group"),
                                (
                                    "children",
                                    [
                                        OrderedDict(
                                            [
                                                ("name", "inwards"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "gh"),
                                                                ("type", "param"),
                                                            ]
                                                        )
                                                    ],
                                                ),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "fl_in"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "Tt"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "Pt"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "W"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "mech_in"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "XN"),                                                                
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "PW"),                                                                
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "ductC"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "group"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "fl_in"),
                                                                ("type", "subsystem"),
                                                                (
                                                                    "subsystem_type",
                                                                    "component",
                                                                ),
                                                                (
                                                                    "children",
                                                                    [
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "Tt",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "param",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "Pt",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "param",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "W",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "param",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                    ],
                                                                ),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "merger"),
                                                                ("type", "subsystem"),
                                                                (
                                                                    "subsystem_type",
                                                                    "group",
                                                                ),
                                                                (
                                                                    "children",
                                                                    [
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "fl1_in",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "subsystem",
                                                                                ),
                                                                                (
                                                                                    "subsystem_type",
                                                                                    "component",
                                                                                ),
                                                                                (
                                                                                    "children",
                                                                                    [
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Tt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "param",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Pt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "param",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "W",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "param",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                    ],
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "fl2_in",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "subsystem",
                                                                                ),
                                                                                (
                                                                                    "subsystem_type",
                                                                                    "component",
                                                                                ),
                                                                                (
                                                                                    "children",
                                                                                    [
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Tt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "param",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Pt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "param",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "W",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "param",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                    ],
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "fl_out",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "subsystem",
                                                                                ),
                                                                                (
                                                                                    "subsystem_type",
                                                                                    "component",
                                                                                ),
                                                                                (
                                                                                    "children",
                                                                                    [
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Tt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "unknown",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Pt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "unknown",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "W",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "unknown",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                    ],
                                                                                ),
                                                                            ]
                                                                        ),
                                                                    ],
                                                                ),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "duct"),
                                                                ("type", "subsystem"),
                                                                (
                                                                    "subsystem_type",
                                                                    "group",
                                                                ),
                                                                (
                                                                    "children",
                                                                    [
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "inwards",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "subsystem",
                                                                                ),
                                                                                (
                                                                                    "subsystem_type",
                                                                                    "component",
                                                                                ),
                                                                                (
                                                                                    "children",
                                                                                    [
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "A",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "param",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "cst_loss",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "param",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "glp",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "param",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                    ],
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "fl_in",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "subsystem",
                                                                                ),
                                                                                (
                                                                                    "subsystem_type",
                                                                                    "component",
                                                                                ),
                                                                                (
                                                                                    "children",
                                                                                    [
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Tt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "param",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Pt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "param",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "W",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "param",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                    ],
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "outwards",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "subsystem",
                                                                                ),
                                                                                (
                                                                                    "subsystem_type",
                                                                                    "component",
                                                                                ),
                                                                                (
                                                                                    "children",
                                                                                    [
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "PR",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "unknown",
                                                                                                ),
                                                                                            ]
                                                                                        )
                                                                                    ],
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "fl_out",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "subsystem",
                                                                                ),
                                                                                (
                                                                                    "subsystem_type",
                                                                                    "component",
                                                                                ),
                                                                                (
                                                                                    "children",
                                                                                    [
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Tt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "unknown",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Pt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "unknown",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "W",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "unknown",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                    ],
                                                                                ),
                                                                            ]
                                                                        ),
                                                                    ],
                                                                ),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "bleed"),
                                                                ("type", "subsystem"),
                                                                (
                                                                    "subsystem_type",
                                                                    "group",
                                                                ),
                                                                (
                                                                    "children",
                                                                    [
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "inwards",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "subsystem",
                                                                                ),
                                                                                (
                                                                                    "subsystem_type",
                                                                                    "component",
                                                                                ),
                                                                                (
                                                                                    "children",
                                                                                    [
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "split_ratio",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "param",
                                                                                                ),
                                                                                            ]
                                                                                        )
                                                                                    ],
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "fl_in",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "subsystem",
                                                                                ),
                                                                                (
                                                                                    "subsystem_type",
                                                                                    "component",
                                                                                ),
                                                                                (
                                                                                    "children",
                                                                                    [
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Tt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "param",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Pt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "param",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "W",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "param",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                    ],
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "fl1_out",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "subsystem",
                                                                                ),
                                                                                (
                                                                                    "subsystem_type",
                                                                                    "component",
                                                                                ),
                                                                                (
                                                                                    "children",
                                                                                    [
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Tt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "unknown",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Pt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "unknown",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "W",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "unknown",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                    ],
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "fl2_out",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "subsystem",
                                                                                ),
                                                                                (
                                                                                    "subsystem_type",
                                                                                    "component",
                                                                                ),
                                                                                (
                                                                                    "children",
                                                                                    [
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Tt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "unknown",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Pt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "unknown",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "W",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "unknown",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                    ],
                                                                                ),
                                                                            ]
                                                                        ),
                                                                    ],
                                                                ),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "fl_out"),
                                                                ("type", "subsystem"),
                                                                (
                                                                    "subsystem_type",
                                                                    "component",
                                                                ),
                                                                (
                                                                    "children",
                                                                    [
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "Tt",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "unknown",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "Pt",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "unknown",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "W",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "unknown",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                    ],
                                                                ),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "fan"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "group"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "inwards"),
                                                                ("type", "subsystem"),
                                                                (
                                                                    "subsystem_type",
                                                                    "component",
                                                                ),
                                                                (
                                                                    "children",
                                                                    [
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "gh",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "param",
                                                                                ),
                                                                            ]
                                                                        )
                                                                    ],
                                                                ),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "fl_in"),
                                                                ("type", "subsystem"),
                                                                (
                                                                    "subsystem_type",
                                                                    "component",
                                                                ),
                                                                (
                                                                    "children",
                                                                    [
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "Tt",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "param",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "Pt",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "param",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "W",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "param",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                    ],
                                                                ),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "mech_in"),
                                                                ("type", "subsystem"),
                                                                (
                                                                    "subsystem_type",
                                                                    "component",
                                                                ),
                                                                (
                                                                    "children",
                                                                    [
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "XN",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "param",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "PW",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "param",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                    ],
                                                                ),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "outwards"),
                                                                ("type", "subsystem"),
                                                                (
                                                                    "subsystem_type",
                                                                    "component",
                                                                ),
                                                                (
                                                                    "children",
                                                                    [
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "pcnr",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "unknown",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "pr",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "unknown",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "effis",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "unknown",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "wr",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "unknown",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "PWfan",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "unknown",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                    ],
                                                                ),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "fl_out"),
                                                                ("type", "subsystem"),
                                                                (
                                                                    "subsystem_type",
                                                                    "component",
                                                                ),
                                                                (
                                                                    "children",
                                                                    [
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "Tt",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "unknown",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "Pt",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "unknown",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "W",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "unknown",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                    ],
                                                                ),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "fl_out"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "Tt"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "Pt"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "W"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                    ],
                                ),
                            ]
                        ),
                        OrderedDict(
                            [
                                ("name", "merger"),
                                ("type", "subsystem"),
                                ("subsystem_type", "group"),
                                (
                                    "children",
                                    [
                                        OrderedDict(
                                            [
                                                ("name", "fl1_in"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "Tt"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "Pt"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "W"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "fl2_in"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "Tt"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "Pt"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "W"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "fl_out"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "Tt"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "Pt"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "W"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                    ],
                                ),
                            ]
                        ),
                        OrderedDict(
                            [
                                ("name", "duct"),
                                ("type", "subsystem"),
                                ("subsystem_type", "group"),
                                (
                                    "children",
                                    [
                                        OrderedDict(
                                            [
                                                ("name", "inwards"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "A"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "cst_loss"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "glp"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "fl_in"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "Tt"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "Pt"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "W"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "outwards"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "PR"),
                                                                ("type", "unknown"),
                                                            ]
                                                        )
                                                    ],
                                                ),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "fl_out"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "Tt"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "Pt"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "W"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                    ],
                                ),
                            ]
                        ),
                        OrderedDict(
                            [
                                ("name", "bleed"),
                                ("type", "subsystem"),
                                ("subsystem_type", "group"),
                                (
                                    "children",
                                    [
                                        OrderedDict(
                                            [
                                                ("name", "inwards"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "split_ratio"),
                                                                ("type", "param"),
                                                            ]
                                                        )
                                                    ],
                                                ),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "fl_in"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "Tt"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "Pt"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "W"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "fl1_out"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "Tt"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "Pt"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "W"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "fl2_out"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "Tt"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "Pt"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "W"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                    ],
                                ),
                            ]
                        ),
                        OrderedDict(
                            [
                                ("name", "noz"),
                                ("type", "subsystem"),
                                ("subsystem_type", "group"),
                                (
                                    "children",
                                    [
                                        OrderedDict(
                                            [
                                                ("name", "inwards"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "Acol"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "Aexit"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "fl_in"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "Tt"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "Pt"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "W"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "outwards"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "WRnozzle"),
                                                                ("type", "unknown"),
                                                            ]
                                                        )
                                                    ],
                                                ),

                                            ]
                                        ),
                                    ],
                                ),
                            ]
                        ),
                    ],
                ),
            ]
        )

        self.expected_conns = [
            OrderedDict([("src", "atm.fl_out.Tt"), ("tgt", "inlet.fl_in.Tt")]),
            OrderedDict([("src", "atm.fl_out.Pt"), ("tgt", "inlet.fl_in.Pt")]),
            OrderedDict([("src", "inlet.fl_out.Tt"), ("tgt", "fanC.fl_in.Tt")]),
            OrderedDict([("src", "inlet.fl_out.Pt"), ("tgt", "fanC.fl_in.Pt")]),
            OrderedDict([("src", "inlet.fl_out.W"), ("tgt", "fanC.fl_in.W")]),
            OrderedDict([("src", "fanC.fl_out.Tt"), ("tgt", "merger.fl1_in.Tt")]),
            OrderedDict([("src", "fanC.fl_out.Pt"), ("tgt", "merger.fl1_in.Pt")]),
            OrderedDict([("src", "fanC.fl_out.W"), ("tgt", "merger.fl1_in.W")]),
            OrderedDict([("src", "bleed.fl2_out.Tt"), ("tgt", "merger.fl2_in.Tt")]),
            OrderedDict([("src", "bleed.fl2_out.Pt"), ("tgt", "merger.fl2_in.Pt")]),
            OrderedDict([("src", "bleed.fl2_out.W"), ("tgt", "merger.fl2_in.W")]),
            OrderedDict([("src", "merger.fl_out.Tt"), ("tgt", "duct.fl_in.Tt")]),
            OrderedDict([("src", "merger.fl_out.Pt"), ("tgt", "duct.fl_in.Pt")]),
            OrderedDict([("src", "merger.fl_out.W"), ("tgt", "duct.fl_in.W")]),
            OrderedDict([("src", "duct.fl_out.Tt"), ("tgt", "bleed.fl_in.Tt")]),
            OrderedDict([("src", "duct.fl_out.Pt"), ("tgt", "bleed.fl_in.Pt")]),
            OrderedDict([("src", "duct.fl_out.W"), ("tgt", "bleed.fl_in.W")]),
            OrderedDict([("src", "bleed.fl1_out.Tt"), ("tgt", "noz.fl_in.Tt")]),
            OrderedDict([("src", "bleed.fl1_out.Pt"), ("tgt", "noz.fl_in.Pt")]),
            OrderedDict([("src", "bleed.fl1_out.W"), ("tgt", "noz.fl_in.W")]),
            OrderedDict([("src", "fanC.fl_in.Tt"), ("tgt", "fanC.ductC.fl_in.Tt")]),
            OrderedDict([("src", "fanC.fl_in.Pt"), ("tgt", "fanC.ductC.fl_in.Pt")]),
            OrderedDict([("src", "fanC.fl_in.W"), ("tgt", "fanC.ductC.fl_in.W")]),
            OrderedDict([("src", "fanC.mech_in.XN"), ("tgt", "fanC.fan.mech_in.XN")]),
            OrderedDict([("src", "fanC.mech_in.PW"), ("tgt", "fanC.fan.mech_in.PW")]),
            OrderedDict([("src", "fanC.inwards.gh"), ("tgt", "fanC.fan.inwards.gh")]),
            OrderedDict(
                [("src", "fanC.ductC.fl_out.Tt"), ("tgt", "fanC.fan.fl_in.Tt")]
            ),
            OrderedDict(
                [("src", "fanC.ductC.fl_out.Pt"), ("tgt", "fanC.fan.fl_in.Pt")]
            ),
            OrderedDict([("src", "fanC.ductC.fl_out.W"), ("tgt", "fanC.fan.fl_in.W")]),
            OrderedDict([("src", "fanC.fan.fl_out.Tt"), ("tgt", "fanC.fl_out.Tt")]),
            OrderedDict([("src", "fanC.fan.fl_out.Pt"), ("tgt", "fanC.fl_out.Pt")]),
            OrderedDict([("src", "fanC.fan.fl_out.W"), ("tgt", "fanC.fl_out.W")]),
            OrderedDict([("src", "fanC.ductC.fl_in.Tt"), ("tgt", "fanC.ductC.merger.fl1_in.Tt")]),
            OrderedDict([("src", "fanC.ductC.fl_in.Pt"), ("tgt", "fanC.ductC.merger.fl1_in.Pt")]),
            OrderedDict([("src", "fanC.ductC.fl_in.W"), ("tgt", "fanC.ductC.merger.fl1_in.W")]),
            OrderedDict([("src", "fanC.ductC.bleed.fl2_out.Tt"), ("tgt", "fanC.ductC.merger.fl2_in.Tt")]),
            OrderedDict([("src", "fanC.ductC.bleed.fl2_out.Pt"), ("tgt", "fanC.ductC.merger.fl2_in.Pt")]),
            OrderedDict([("src", "fanC.ductC.bleed.fl2_out.W"), ("tgt", "fanC.ductC.merger.fl2_in.W")]),
            OrderedDict([("src", "fanC.ductC.bleed.fl1_out.Tt"), ("tgt", "fanC.ductC.fl_out.Tt")]),
            OrderedDict([("src", "fanC.ductC.bleed.fl1_out.Pt"), ("tgt", "fanC.ductC.fl_out.Pt")]),
            OrderedDict([("src", "fanC.ductC.bleed.fl1_out.W"), ("tgt", "fanC.ductC.fl_out.W")]),
            OrderedDict([("src", "fanC.ductC.merger.fl_out.Tt"), ("tgt", "fanC.ductC.duct.fl_in.Tt")]),
            OrderedDict([("src", "fanC.ductC.merger.fl_out.Pt"), ("tgt", "fanC.ductC.duct.fl_in.Pt")]),
            OrderedDict([("src", "fanC.ductC.merger.fl_out.W"), ("tgt", "fanC.ductC.duct.fl_in.W")]),
            OrderedDict([("src", "fanC.ductC.duct.fl_out.Tt"),
                    ("tgt", "fanC.ductC.bleed.fl_in.Tt")]),
            OrderedDict([("src", "fanC.ductC.duct.fl_out.Pt"),
                    ("tgt", "fanC.ductC.bleed.fl_in.Pt")]),
            OrderedDict([("src", "fanC.ductC.duct.fl_out.W"),
                    ("tgt", "fanC.ductC.bleed.fl_in.W")]),
                    ]

        self.expected_tree_default = OrderedDict(
            [
                ("name", "turbofan"),
                ("type", "subsystem"),
                ("subsystem_type", "group"),
                (
                    "children",
                    [
                        OrderedDict(
                            [
                                ("name", "atm"),
                                ("type", "subsystem"),
                                ("subsystem_type", "group"),
                                (
                                    "children",
                                    [
                                        OrderedDict(
                                            [
                                                ("name", "inwards"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                ("children", []),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "fl_out"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "Tt"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "Pt"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                    ],
                                ),
                            ]
                        ),
                        OrderedDict(
                            [
                                ("name", "inlet"),
                                ("type", "subsystem"),
                                ("subsystem_type", "group"),
                                (
                                    "children",
                                    [
                                        OrderedDict(
                                            [
                                                ("name", "fl_in"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "Tt"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "Pt"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "W_in"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "W"),
                                                                ("type", "param"),
                                                            ]
                                                        )
                                                    ],
                                                ),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "fl_out"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "Tt"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "Pt"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "W"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                    ],
                                ),
                            ]
                        ),
                        OrderedDict(
                            [
                                ("name", "fanC"),
                                ("type", "subsystem"),
                                ("subsystem_type", "group"),
                                (
                                    "children",
                                    [
                                        OrderedDict(
                                            [
                                                ("name", "inwards"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                ("children", []),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "fl_in"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "Tt"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "Pt"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "W"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "mech_in"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "XN"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "PW"),                                                                
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "ductC"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "group"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "fl_in"),
                                                                ("type", "subsystem"),
                                                                (
                                                                    "subsystem_type",
                                                                    "component",
                                                                ),
                                                                (
                                                                    "children",
                                                                    [
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "Tt",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "param",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "Pt",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "param",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "W",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "param",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                    ],
                                                                ),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "merger"),
                                                                ("type", "subsystem"),
                                                                (
                                                                    "subsystem_type",
                                                                    "group",
                                                                ),
                                                                (
                                                                    "children",
                                                                    [
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "fl1_in",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "subsystem",
                                                                                ),
                                                                                (
                                                                                    "subsystem_type",
                                                                                    "component",
                                                                                ),
                                                                                (
                                                                                    "children",
                                                                                    [
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Tt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "param",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Pt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "param",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "W",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "param",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                    ],
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "fl2_in",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "subsystem",
                                                                                ),
                                                                                (
                                                                                    "subsystem_type",
                                                                                    "component",
                                                                                ),
                                                                                (
                                                                                    "children",
                                                                                    [
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Tt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "param",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Pt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "param",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "W",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "param",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                    ],
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "fl_out",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "subsystem",
                                                                                ),
                                                                                (
                                                                                    "subsystem_type",
                                                                                    "component",
                                                                                ),
                                                                                (
                                                                                    "children",
                                                                                    [
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Tt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "unknown",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Pt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "unknown",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "W",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "unknown",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                    ],
                                                                                ),
                                                                            ]
                                                                        ),
                                                                    ],
                                                                ),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "duct"),
                                                                ("type", "subsystem"),
                                                                (
                                                                    "subsystem_type",
                                                                    "group",
                                                                ),
                                                                (
                                                                    "children",
                                                                    [
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "inwards",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "subsystem",
                                                                                ),
                                                                                (
                                                                                    "subsystem_type",
                                                                                    "component",
                                                                                ),
                                                                                (
                                                                                    "children",
                                                                                    [],
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "fl_in",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "subsystem",
                                                                                ),
                                                                                (
                                                                                    "subsystem_type",
                                                                                    "component",
                                                                                ),
                                                                                (
                                                                                    "children",
                                                                                    [
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Tt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "param",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Pt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "param",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "W",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "param",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                    ],
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "outwards",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "subsystem",
                                                                                ),
                                                                                (
                                                                                    "subsystem_type",
                                                                                    "component",
                                                                                ),
                                                                                (
                                                                                    "children",
                                                                                    [],
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "fl_out",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "subsystem",
                                                                                ),
                                                                                (
                                                                                    "subsystem_type",
                                                                                    "component",
                                                                                ),
                                                                                (
                                                                                    "children",
                                                                                    [
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Tt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "unknown",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Pt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "unknown",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "W",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "unknown",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                    ],
                                                                                ),
                                                                            ]
                                                                        ),
                                                                    ],
                                                                ),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "bleed"),
                                                                ("type", "subsystem"),
                                                                (
                                                                    "subsystem_type",
                                                                    "group",
                                                                ),
                                                                (
                                                                    "children",
                                                                    [
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "inwards",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "subsystem",
                                                                                ),
                                                                                (
                                                                                    "subsystem_type",
                                                                                    "component",
                                                                                ),
                                                                                (
                                                                                    "children",
                                                                                    [],
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "fl_in",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "subsystem",
                                                                                ),
                                                                                (
                                                                                    "subsystem_type",
                                                                                    "component",
                                                                                ),
                                                                                (
                                                                                    "children",
                                                                                    [
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Tt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "param",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Pt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "param",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "W",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "param",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                    ],
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "fl1_out",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "subsystem",
                                                                                ),
                                                                                (
                                                                                    "subsystem_type",
                                                                                    "component",
                                                                                ),
                                                                                (
                                                                                    "children",
                                                                                    [
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Tt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "unknown",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Pt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "unknown",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "W",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "unknown",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                    ],
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "fl2_out",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "subsystem",
                                                                                ),
                                                                                (
                                                                                    "subsystem_type",
                                                                                    "component",
                                                                                ),
                                                                                (
                                                                                    "children",
                                                                                    [
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Tt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "unknown",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "Pt",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "unknown",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        OrderedDict(
                                                                                            [
                                                                                                (
                                                                                                    "name",
                                                                                                    "W",
                                                                                                ),
                                                                                                (
                                                                                                    "type",
                                                                                                    "unknown",
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                    ],
                                                                                ),
                                                                            ]
                                                                        ),
                                                                    ],
                                                                ),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "fl_out"),
                                                                ("type", "subsystem"),
                                                                (
                                                                    "subsystem_type",
                                                                    "component",
                                                                ),
                                                                (
                                                                    "children",
                                                                    [
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "Tt",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "unknown",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "Pt",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "unknown",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "W",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "unknown",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                    ],
                                                                ),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "fan"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "group"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "inwards"),
                                                                ("type", "subsystem"),
                                                                (
                                                                    "subsystem_type",
                                                                    "component",
                                                                ),
                                                                ("children", []),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "fl_in"),
                                                                ("type", "subsystem"),
                                                                (
                                                                    "subsystem_type",
                                                                    "component",
                                                                ),
                                                                (
                                                                    "children",
                                                                    [
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "Tt",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "param",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "Pt",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "param",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "W",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "param",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                    ],
                                                                ),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "mech_in"),
                                                                ("type", "subsystem"),
                                                                (
                                                                    "subsystem_type",
                                                                    "component",
                                                                ),
                                                                (
                                                                    "children",
                                                                    [
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "XN",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "param",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "PW",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "param",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                    ],
                                                                ),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "outwards"),
                                                                ("type", "subsystem"),
                                                                (
                                                                    "subsystem_type",
                                                                    "component",
                                                                ),
                                                                ("children", []),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "fl_out"),
                                                                ("type", "subsystem"),
                                                                (
                                                                    "subsystem_type",
                                                                    "component",
                                                                ),
                                                                (
                                                                    "children",
                                                                    [
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "Tt",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "unknown",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "Pt",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "unknown",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        OrderedDict(
                                                                            [
                                                                                (
                                                                                    "name",
                                                                                    "W",
                                                                                ),
                                                                                (
                                                                                    "type",
                                                                                    "unknown",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                    ],
                                                                ),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "fl_out"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "Tt"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "Pt"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "W"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                    ],
                                ),
                            ]
                        ),
                        OrderedDict(
                            [
                                ("name", "merger"),
                                ("type", "subsystem"),
                                ("subsystem_type", "group"),
                                (
                                    "children",
                                    [
                                        OrderedDict(
                                            [
                                                ("name", "fl1_in"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "Tt"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "Pt"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "W"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "fl2_in"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "Tt"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "Pt"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "W"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "fl_out"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "Tt"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "Pt"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "W"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                    ],
                                ),
                            ]
                        ),
                        OrderedDict(
                            [
                                ("name", "duct"),
                                ("type", "subsystem"),
                                ("subsystem_type", "group"),
                                (
                                    "children",
                                    [
                                        OrderedDict(
                                            [
                                                ("name", "inwards"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                ("children", []),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "fl_in"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "Tt"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "Pt"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "W"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "outwards"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                ("children", []),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "fl_out"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "Tt"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "Pt"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "W"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                    ],
                                ),
                            ]
                        ),
                        OrderedDict(
                            [
                                ("name", "bleed"),
                                ("type", "subsystem"),
                                ("subsystem_type", "group"),
                                (
                                    "children",
                                    [
                                        OrderedDict(
                                            [
                                                ("name", "inwards"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                ("children", []),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "fl_in"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "Tt"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "Pt"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "W"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "fl1_out"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "Tt"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "Pt"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "W"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "fl2_out"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "Tt"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "Pt"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "W"),
                                                                ("type", "unknown"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                    ],
                                ),
                            ]
                        ),
                        OrderedDict(
                            [
                                ("name", "noz"),
                                ("type", "subsystem"),
                                ("subsystem_type", "group"),
                                (
                                    "children",
                                    [
                                        OrderedDict(
                                            [
                                                ("name", "inwards"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                ("children", []),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "fl_in"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                (
                                                    "children",
                                                    [
                                                        OrderedDict(
                                                            [
                                                                ("name", "Tt"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "Pt"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                        OrderedDict(
                                                            [
                                                                ("name", "W"),
                                                                ("type", "param"),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                        OrderedDict(
                                            [
                                                ("name", "outwards"),
                                                ("type", "subsystem"),
                                                ("subsystem_type", "component"),
                                                ("children", []),
                                            ]
                                        ),
                                    ],
                                ),
                            ]
                        ),
                    ],
                ),
            ]
        )

        self.expected_conns_default = [
            OrderedDict([("src", "atm.fl_out.Tt"), ("tgt", "inlet.fl_in.Tt")]),
            OrderedDict([("src", "atm.fl_out.Pt"), ("tgt", "inlet.fl_in.Pt")]),
            OrderedDict([("src", "inlet.fl_out.Tt"), ("tgt", "fanC.fl_in.Tt")]),
            OrderedDict([("src", "inlet.fl_out.Pt"), ("tgt", "fanC.fl_in.Pt")]),
            OrderedDict([("src", "inlet.fl_out.W"), ("tgt", "fanC.fl_in.W")]),
            OrderedDict([("src", "fanC.fl_out.Tt"), ("tgt", "merger.fl1_in.Tt")]),
            OrderedDict([("src", "fanC.fl_out.Pt"), ("tgt", "merger.fl1_in.Pt")]),
            OrderedDict([("src", "fanC.fl_out.W"), ("tgt", "merger.fl1_in.W")]),
            OrderedDict([("src", "bleed.fl2_out.Tt"), ("tgt", "merger.fl2_in.Tt")]),
            OrderedDict([("src", "bleed.fl2_out.Pt"), ("tgt", "merger.fl2_in.Pt")]),
            OrderedDict([("src", "bleed.fl2_out.W"), ("tgt", "merger.fl2_in.W")]),
            OrderedDict([("src", "merger.fl_out.Tt"), ("tgt", "duct.fl_in.Tt")]),
            OrderedDict([("src", "merger.fl_out.Pt"), ("tgt", "duct.fl_in.Pt")]),
            OrderedDict([("src", "merger.fl_out.W"), ("tgt", "duct.fl_in.W")]),
            OrderedDict([("src", "duct.fl_out.Tt"), ("tgt", "bleed.fl_in.Tt")]),
            OrderedDict([("src", "duct.fl_out.Pt"), ("tgt", "bleed.fl_in.Pt")]),
            OrderedDict([("src", "duct.fl_out.W"), ("tgt", "bleed.fl_in.W")]),
            OrderedDict([("src", "bleed.fl1_out.Tt"), ("tgt", "noz.fl_in.Tt")]),
            OrderedDict([("src", "bleed.fl1_out.Pt"), ("tgt", "noz.fl_in.Pt")]),
            OrderedDict([("src", "bleed.fl1_out.W"), ("tgt", "noz.fl_in.W")]),
            OrderedDict([("src", "fanC.fl_in.Tt"), ("tgt", "fanC.ductC.fl_in.Tt")]),
            OrderedDict([("src", "fanC.fl_in.Pt"), ("tgt", "fanC.ductC.fl_in.Pt")]),
            OrderedDict([("src", "fanC.fl_in.W"), ("tgt", "fanC.ductC.fl_in.W")]),
            OrderedDict([("src", "fanC.mech_in.XN"), ("tgt", "fanC.fan.mech_in.XN")]),
            OrderedDict([("src", "fanC.mech_in.PW"), ("tgt", "fanC.fan.mech_in.PW")]),
            OrderedDict(
                [("src", "fanC.ductC.fl_out.Tt"), ("tgt", "fanC.fan.fl_in.Tt")]
            ),
            OrderedDict(
                [("src", "fanC.ductC.fl_out.Pt"), ("tgt", "fanC.fan.fl_in.Pt")]
            ),
            OrderedDict([("src", "fanC.ductC.fl_out.W"), ("tgt", "fanC.fan.fl_in.W")]),
            OrderedDict([("src", "fanC.fan.fl_out.Tt"), ("tgt", "fanC.fl_out.Tt")]),
            OrderedDict([("src", "fanC.fan.fl_out.Pt"), ("tgt", "fanC.fl_out.Pt")]),
            OrderedDict([("src", "fanC.fan.fl_out.W"), ("tgt", "fanC.fl_out.W")]),
            OrderedDict(
                [("src", "fanC.ductC.fl_in.Tt"), ("tgt", "fanC.ductC.merger.fl1_in.Tt")]
            ),
            OrderedDict(
                [("src", "fanC.ductC.fl_in.Pt"), ("tgt", "fanC.ductC.merger.fl1_in.Pt")]
            ),
            OrderedDict(
                [("src", "fanC.ductC.fl_in.W"), ("tgt", "fanC.ductC.merger.fl1_in.W")]
            ),
            OrderedDict(
                [
                    ("src", "fanC.ductC.bleed.fl2_out.Tt"),
                    ("tgt", "fanC.ductC.merger.fl2_in.Tt"),
                ]
            ),
            OrderedDict(
                [
                    ("src", "fanC.ductC.bleed.fl2_out.Pt"),
                    ("tgt", "fanC.ductC.merger.fl2_in.Pt"),
                ]
            ),
            OrderedDict(
                [
                    ("src", "fanC.ductC.bleed.fl2_out.W"),
                    ("tgt", "fanC.ductC.merger.fl2_in.W"),
                ]
            ),
            OrderedDict(
                [
                    ("src", "fanC.ductC.bleed.fl1_out.Tt"),
                    ("tgt", "fanC.ductC.fl_out.Tt"),
                ]
            ),
            OrderedDict(
                [
                    ("src", "fanC.ductC.bleed.fl1_out.Pt"),
                    ("tgt", "fanC.ductC.fl_out.Pt"),
                ]
            ),
            OrderedDict(
                [("src", "fanC.ductC.bleed.fl1_out.W"), ("tgt", "fanC.ductC.fl_out.W")]
            ),
            OrderedDict(
                [
                    ("src", "fanC.ductC.merger.fl_out.Tt"),
                    ("tgt", "fanC.ductC.duct.fl_in.Tt"),
                ]
            ),
            OrderedDict(
                [
                    ("src", "fanC.ductC.merger.fl_out.Pt"),
                    ("tgt", "fanC.ductC.duct.fl_in.Pt"),
                ]
            ),
            OrderedDict(
                [
                    ("src", "fanC.ductC.merger.fl_out.W"),
                    ("tgt", "fanC.ductC.duct.fl_in.W"),
                ]
            ),
            OrderedDict(
                [
                    ("src", "fanC.ductC.duct.fl_out.Tt"),
                    ("tgt", "fanC.ductC.bleed.fl_in.Tt"),
                ]
            ),
            OrderedDict(
                [
                    ("src", "fanC.ductC.duct.fl_out.Pt"),
                    ("tgt", "fanC.ductC.bleed.fl_in.Pt"),
                ]
            ),
            OrderedDict(
                [
                    ("src", "fanC.ductC.duct.fl_out.W"),
                    ("tgt", "fanC.ductC.bleed.fl_in.W"),
                ]
            ),
        ]

    def test_model_viewer_has_correct_data_from_problem(self):
        """
        Verify that the correct model structure data exists when stored as compared
        to the expected structure, using the SellarStateConnection model.
        """
        p = ComplexTurbofan("turbofan")

        model_viewer_data = _get_viewer_data(p, include_orphan_vars=True)
        tree_json = model_viewer_data["tree"]
        conns_json = model_viewer_data["connections_list"]

        assert self.expected_tree == tree_json
        assert self.expected_conns == conns_json

    def test_model_viewer_takes_into_account_include_wards(self):
        """
        Test that model viewer does not show include_wards by default.
        """
        p = ComplexTurbofan("turbofan")

        model_viewer_data = _get_viewer_data(p, include_orphan_vars=False)
        tree_json = model_viewer_data["tree"]
        conns_json = model_viewer_data["connections_list"]

        assert self.expected_tree_default == tree_json
        assert self.expected_conns_default == conns_json

    def test_view_model_from_problem(self):
        """
        Test that an n2 html file is generated from a Problem.
        """
        p = ComplexTurbofan("turbofan")

        view_model(p, outfile=self.problem_filename, show_browser=False)

        # Check that the html file has been created and has something in it.
        self.assertTrue(
            os.path.isfile(self.problem_html_filename),
            (self.problem_html_filename + " is not a valid file."),
        )
        self.assertGreater(os.path.getsize(self.problem_html_filename), 100)
