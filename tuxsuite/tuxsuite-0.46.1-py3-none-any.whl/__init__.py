# -*- coding: utf-8 -*-


"""
This is the tuxsuite module.
"""

__version__ = "0.46.1"


from . import build
from . import config
from . import schema, exceptions
import logging
import click
from abc import ABC, abstractmethod


logging.basicConfig(format="%(levelname)s: %(message)s")


__config__ = None


def load_config():
    global __config__
    if not __config__:
        __config__ = config.Config()
    return __config__


class Configurable:
    """
    This class loads the configuration.
    """

    def __init__(self, *args, **kwargs):
        cfg = load_config()
        if "token" not in kwargs:
            kwargs["token"] = cfg.auth_token
        if "kbapi_url" not in kwargs:
            kwargs["kbapi_url"] = cfg.kbapi_url
        if "tuxapi_url" not in kwargs:
            kwargs["tuxapi_url"] = cfg.tuxapi_url
        if "group" not in kwargs:
            kwargs["group"] = cfg.group
        if "project" not in kwargs:
            kwargs["project"] = cfg.project
        super().__init__(*args, **kwargs)


class Build(Configurable, build.Build):
    """
    This class represents individual builds. It should be used to trigger
    builds, and optionally wait for them to finish.
    """


class Bitbake(Configurable, build.Bitbake):
    """
    This class represents individual builds. It should be used to trigger
    builds, and optionally wait for them to finish.
    """


class Plan(Configurable, build.Plan):
    """
    This class represent a test plan.
    """


class Test(Configurable, build.Test):
    """
    This class represents individual tests. It should be used to trigger
    tests, and optionally wait for them to finish.
    """


class Results(Configurable, build.Results):
    """
    This class represents individual results. It should be used to get results.
    """


class PlanType(ABC):
    """
    This class represents as Base class for all existing and upcoming different types of plans
    """

    plan_cfg = None

    @classmethod
    def load_plan(cls, config):
        if config and config.get("jobs"):
            # setting class variable plan_cfg to hold config data for respective plan type class
            cls.plan_cfg = config
            config_job = config["jobs"][0]
            # checking if it is bake plan
            if "bake" in config_job or "bakes" in config_job:
                return BakePlan()
            elif (
                "build" in config_job
                or "builds" in config_job
                or "test" in config_job
                or "tests" in config_job
            ):
                return BuildPlan()
            else:
                raise exceptions.UnsupportedJob("Unsupport jobtype")
        else:
            raise exceptions.InvalidConfiguration(
                "Plan configuration file must contain Jobs"
            )

    @abstractmethod
    def check_schema(self):
        pass

    @abstractmethod
    def apply(self):
        pass

    @abstractmethod
    def plan_info(self):
        pass

    @abstractmethod
    def create_builds(self):
        pass


class BuildPlan(PlanType):
    def check_schema(self, config):
        return schema.plan()(config)

    def apply(self, plan_config):
        for cfg in PlanType.plan_cfg["jobs"]:
            if (
                plan_config.job_name is not None
                and cfg.get("name") != plan_config.job_name
            ):
                continue
            builds = []
            if "build" in cfg:
                builds = [cfg["build"]]
            elif "builds" in cfg:
                builds = cfg["builds"]
            tests = []
            if "test" in cfg:
                tests = [cfg["test"]]
            elif "tests" in cfg:
                tests = cfg["tests"]

            if builds:
                for build_item in builds:
                    plan_config.plan.append({"build": build_item, "tests": tests})
            else:
                plan_config.plan.append({"build": None, "tests": tests})

    def plan_info(self, name, description):
        click.echo("Running Linux Kernel plan '{}': '{}'".format(name, description))

    def create_builds(self, plan, builds):
        for cfg in plan.config.plan:
            if cfg["build"] is not None:
                data = plan.args.copy()
                data.update(cfg["build"])
                if plan.args.get("no_cache"):
                    data["no_cache"] = True
                builds.append(build.Build(**data))
            else:
                builds.append(None)

        builds_to_submit = [b for b in builds if b]
        if builds_to_submit:
            req_data = {"builds": [], "patches": {}}
            for b in builds_to_submit:
                build_entry, patch = b.generate_build_request(plan=plan.plan)
                req_data["builds"].append(build_entry)
                req_data["patches"].update(patch)
            ret = build.post_request(f"{plan.url}/builds", plan.headers, req_data)
            # Updating builds_to_submit will update values in builds
            for (build_obj, data) in zip(builds_to_submit, ret):
                build_obj.build_data = data["download_url"]
                build_obj.uid = data["uid"]
                build_obj.status = data


class BakePlan(PlanType):
    def check_schema(self, config):
        return schema.bake_plan()(config)

    def apply(self, plan_config):
        for cfg in PlanType.plan_cfg["jobs"]:
            if (
                plan_config.job_name is not None
                and cfg.get("name") != plan_config.job_name
            ):
                continue
            builds = []
            if "bake" in cfg:
                builds = [cfg["bake"]]
            elif "bakes" in cfg:
                builds = cfg["bakes"]

            # currently builds only
            if builds:
                for build_item in builds:
                    plan_config.plan.append({"build": build_item, "tests": []})

    def plan_info(self, name, description):
        click.echo(
            "*** WARNING: BITBAKE SUPPORT IS EXPERIMENTAL ***\n"
            "Running Bake plan '{}': '{}'".format(name, description)
        )

    def create_builds(self, plan, builds):
        data = {
            key: value
            for key, value in plan.args.items()
            if key not in ["git_repo", "git_sha", "git_ref", "no_cache", "patch_series"]
        }
        for cfg in plan.config.plan:
            if cfg["build"] is not None:
                data["data"] = cfg["build"]
                builds.append(build.Bitbake(**data))
            else:
                builds.append(None)

        builds_to_submit = [b for b in builds if b]
        if builds_to_submit:
            req_data = {"oebuilds": []}
            for b in builds_to_submit:
                build_entry, manifest = b.generate_build_request(plan=plan.plan)
                build_entry["manifests"] = manifest
                del build_entry["manifest"]
                req_data["oebuilds"].append(build_entry)
            ret = build.post_request(f"{plan.url}/oebuilds", plan.headers, req_data)
            # Updating builds_to_submit will update values in builds
            for (bake_obj, data) in zip(builds_to_submit, ret):
                bake_obj.build_data = data["download_url"]
                bake_obj.uid = data["uid"]
                bake_obj.status = data
