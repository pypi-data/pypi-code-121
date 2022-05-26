import json
from pathlib import Path

import pytest

from sym.flow.cli.helpers.iam_policies import IAMPolicies

# From the following TF:
#
# resource "sym_resources" "production_bucket" {
#   label = "Prod"
#   arn = "arn:aws:s3:::foobar"
# }
#


@pytest.fixture
def expected_policy_json():
    def _expected_policy_json(name):
        path = Path(__file__).resolve().parent / f"expected_{name}_policy.json"
        return path.read_text()

    return _expected_policy_json


def _prepare_policy(policy):
    return sorted(json.loads(policy)["Statement"], key=lambda x: x["Sid"])


def assert_policies(policy1, policy2):
    assert _prepare_policy(policy1) == _prepare_policy(policy2)


def test_iam_policies(expected_policy_json):
    policies = IAMPolicies(name="SymAccess")
    policies.add_arn("arn:aws:s3:::foobar")

    assert_policies(policies.read_policy(), expected_policy_json("read"))
    assert_policies(policies.write_policy(), expected_policy_json("write"))
    assert_policies(policies.admin_policy(), expected_policy_json("admin"))
