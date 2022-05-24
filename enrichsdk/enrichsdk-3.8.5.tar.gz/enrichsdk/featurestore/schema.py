"""
Metadata Format for FeatureStore
"""
import os
import sys
import json
from datetime import datetime, timedelta
from collections import OrderedDict


class FeatureGroupBase:
    """
    Customizable metadata class
    """

    def __init__(self, *args, **kwargs):

        self.schema = kwargs.pop("schema", "unknown:enrich")
        self.attributes = []
        self.elements = {}

    def validate(self):
        """
        Check if the required attributes are present, have
        the right format, and content
        """

        errors = []

        # Attr may be present or absent
        for attr in self.attributes:
            if attr.get("required", True):
                if attr["name"] not in self.elements:
                    errors.append("%(name)s is missing" % attr)
                    continue
            if attr["name"] not in self.elements:
                continue

            value = self.elements[attr["name"]]
            if "type" in attr:
                if not isinstance(value, attr["type"]):
                    errors.append("%(name)s has wrong datatype" % attr)
                    continue

            # Validate function can be explicitly or implicitly specified
            validatefunc = None
            if "validate" in attr:
                validatefunc = attr["validate"]
            elif hasattr(self, "validate_" + attr["name"]):
                validatefunc = getattr(self, "validate_" + attr["name"])

            if validatefunc is not None:
                if not callable(validatefunc):
                    errors.append("%(name)s validate function is not callable" % attr)
                    continue

                try:
                    vresult, verrors = validatefunc(attr, value)
                    if not vresult:
                        if isinstance(verrors, str):
                            errors.append(verrors)
                        elif isinstance(verrors, list):
                            errors.extend(verrors)
                        else:
                            errors.append(str(verrors))
                        continue

                except Exception as e:
                    errors.append(
                        "{} validate function has error: {}".format(
                            attr["name"], str(e)
                        )
                    )
                    continue

        return len(errors) == 0, errors

    def export(self, dummy=False):
        """
        Export an ordered dictionary with the content
        """
        response = OrderedDict([])
        response["schema"] = self.schema
        for attr in self.attributes:
            required = attr.get("required", True)
            name = attr["name"]

            if dummy:
                response[attr["name"]] = attr["default"]
                continue

            if name not in self.elements:
                if not required:
                    continue
                else:
                    raise Exception("Incomplete metdata. Missing: {}".format(name))

            value = self.elements[attr["name"]]
            if hasattr(value, "serialize"):
                value = value.serialize()

            try:
                json.dumps(value)
            except:
                raise Exception("Unable to serialize")

            response[attr["name"]] = value

        return response

    def add(self, attrname, value):
        """
        Add an attribute
        """
        selected = None
        for attr in self.attributes:
            if attrname != attr["name"]:
                selected = attr
                continue

        if selected is None:
            raise Exception("Unknown attribute name specified")

        attrtype = selected.get("type", str)
        if not isinstance(attrtype, list):
            self.elements[attrname] = value
        else:
            # A list
            if attrname not in self.elements:
                self.elements[attrname] = []

            if isinstance(value, list):
                self.elements[attrname].extend(value)
            else:
                self.elements[attrname].append(value)

    def validate_simple_dict(self, attr, value):

        if not isinstance(value, dict):
            return False, "Invalid metadata type"

        if len(value) == 0:
            return False, "Empty metadata"

        return True, ""


class FeatureGroupSpec(FeatureGroupBase):
    """
    Specification of the featuregroup

    Required fields:
       name: Name of the feature group,
       description: Description of the feature group
       owner: email address or other identity (str),
       version: version of this feature group (str)
       join_keys: list of strings
       execution_spec: Uninterpreted dictionary



    Optional field: run
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, schema="v1:spec:featurestore:enrich", **kwargs)
        self.attributes = []

        # Collect all the attributes
        defaults = {
            "name": "online.customer_persona.buyer",
            "description": "Customer attributes",
            "owner": "john@acmeinc.com",
            "version": "v1.2",
        }
        for attr, default in defaults.items():
            self.attributes.append({"name": attr, "default": default, "type": str})

        for attr in ["joinkeys"]:
            self.attributes.append(
                {
                    "name": attr,
                    "type": list,
                    "default": ["customer_id", "division_id"],
                    "required": True,
                }
            )

        for attr in ["executionspec"]:
            self.attributes.append(
                {
                    "name": attr,
                    "type": dict,
                    "required": True,
                    "default": {
                        "cron": "0 20/1 * * * 2",
                        "pipeline": {"name": "SortIdentifier"},
                    },
                    "validate": self.validate_simple_dict,
                }
            )

    def validate_joinkeys(self, attr, value):

        if not isinstance(value, list):
            return False, "Invalid joinkeys"

        if len(value) == 0:
            return False, "Empty join keys"

        for v in value:
            if not instance(v, str) or len(v) == 0:
                return False, "Invalid/empty joinkeys: {}".format(str(value))

        return True, ""


class FeatureGroupRun(FeatureGroupBase):
    """
    Data about featuregroup runs
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, schema="v1:run:featurestore:enrich", **kwargs)
        self.attributes = []

        defaults = {
            "featuregroup_id": 3,
            "runid": "customer-291712-291122",
            "path": "enrich-acme/customer_persona/buyer/2020-01-02/data.pq",
            "run_start": (datetime.now() + timedelta(seconds=-3600 * 2.5)).isoformat(),
        }

        # Collect all the attributes
        for attr, default in defaults.items():
            self.attributes.append({"name": attr, "default": default, "type": str})

        for attr in ["run_end"]:
            self.attributes.append(
                {
                    "name": attr,
                    "type": str,
                    "default": (
                        datetime.now() + timedelta(seconds=-3600 * 1)
                    ).isoformat(),
                    "required": False,
                }
            )

        for attr in ["columns"]:
            self.attributes.append(
                {
                    "name": attr,
                    "type": list,
                    "default": [
                        {
                            "name": "buyer_id",
                        },
                        {
                            "name": "cm",
                        },
                        {
                            "name": "ltv",
                        },
                        {
                            "name": "first_date",
                        },
                        {"name": "last_date"},
                    ],
                    "required": True,
                }
            )

        for attr in ["metadata"]:
            self.attributes.append(
                {
                    "name": attr,
                    "type": dict,
                    "required": True,
                    "default": {
                        "execution": {
                            "description": "Experimental pipeline for testing transforms",
                            "cmdline": [
                                "/home/pingali/.virtualenvs/dev/bin/enrichpkg",
                                "test-transform",
                                "--capture",
                                "transforms/PLPSortMain/",
                            ],
                            "host": "whale",
                            "pid": 3043,
                            "runid": "exp-pipeline-20180922-192321",
                            "name": "ExperimentalPipeline",
                            "end_time": "2019-09-16T15:11:32",
                            "start_time": "2019-09-16T15:11:32",
                            "stats": {
                                "platform": {
                                    "distribution": ["Ubuntu", "16.04", "xenial"],
                                    "node": "whale",
                                    "processor": "x86_64",
                                    "release": "4.15.0-60-generic",
                                    "python": "3.5.2",
                                    "os": "Linux",
                                },
                                "user": "pingali",
                            },
                        }
                    },
                    "validate": self.validate_simple_dict,
                }
            )

    def validate_columns(self, attr, value):

        valid, message = super().validate_simple_dict(attr, value)
        if not valid:
            return valid, message

        for v in value:
            if not instance(v, dict) or len(v) == 0:
                return False, "Invalid/empty columns: {}".format(attr["name"])

            if "name" not in v:
                return False, "Invalid/empty columns: {}".format(attr["name"])

        return True, ""
