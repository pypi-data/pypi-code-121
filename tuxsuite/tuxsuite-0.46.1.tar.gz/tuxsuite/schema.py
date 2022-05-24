# -*- coding: utf-8 -*-

from voluptuous import Any, Optional, Required, Schema


def plan():
    return Schema(
        {
            Required("version"): 1,
            Optional("name"): str,
            Optional("description"): str,
            Required("jobs"): [
                Any(
                    {Optional("name"): str, Required("build"): dict},
                    {
                        Optional("name"): str,
                        Required("build"): dict,
                        Required("test"): dict,
                    },
                    {
                        Optional("name"): str,
                        Required("build"): dict,
                        Required("tests"): list,
                    },
                    {Optional("name"): str, Required("builds"): list},
                    {
                        Optional("name"): str,
                        Required("builds"): list,
                        Required("test"): dict,
                    },
                    {
                        Optional("name"): str,
                        Required("builds"): list,
                        Required("tests"): list,
                    },
                    {Optional("name"): str, Required("tests"): list},
                    {Optional("name"): str, Required("test"): dict},
                )
            ],
        }
    )


def bake_plan():
    return Schema(
        {
            Optional("common"): dict,
            Required("version"): 1,
            Optional("name"): str,
            Optional("description"): str,
            Required("jobs"): [
                Any(
                    {Optional("name"): str, Required("bake"): dict},
                    {Optional("name"): str, Required("bakes"): list},
                )
            ],
        }
    )
