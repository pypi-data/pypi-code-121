import os
import json

import pytest
from cpg_utils.config import (
    DEFAULT_CONFIG,
    DeployConfig,
    get_deploy_config,
    set_deploy_config,
    set_deploy_config_from_env
)


def test_default_config(monkeypatch):
    monkeypatch.delenv("CPG_DEPLOY_CONFIG", raising=False)
    monkeypatch.delenv("CLOUD", raising=False)
    set_deploy_config_from_env()
    dc = get_deploy_config()
    assert dc.to_dict() == DEFAULT_CONFIG


def test_env_config(monkeypatch, json_load):
    cfg1 = json_load("config_01.json")
    monkeypatch.setenv("CPG_DEPLOY_CONFIG", json.dumps(cfg1))
    set_deploy_config(DeployConfig.from_environment())
    dc = get_deploy_config()
    print(json.dumps(dc.to_dict(), indent=4))
    assert dc.to_dict() == cfg1


def test_env_override_config(monkeypatch):
    monkeypatch.delenv("CPG_DEPLOY_CONFIG", raising=False)
    monkeypatch.setenv("CLOUD", "bogus")
    with pytest.raises(AssertionError, match="Invalid cloud specification"):
        dc = DeployConfig.from_environment()
    monkeypatch.setenv("CLOUD", "azure")
    dc = DeployConfig.from_environment()
    assert dc.cloud == "azure"


def test_config_from_dict(json_load):
    cfg1 = json_load("config_01.json")
    dc = DeployConfig.from_dict(cfg1)
    assert dc.to_dict() == cfg1


def test_config_from_partial_dict(json_load):
    cfg1 = json_load("config_01.json")
    del cfg1["cloud"]
    with pytest.raises(TypeError, match="missing 1 required positional argument: 'cloud'"):
        dc = DeployConfig.from_dict(cfg1)
