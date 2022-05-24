import pytest

from cloudshell.cp.vcenter.utils.connectivity_helpers import is_correct_vnic


@pytest.mark.parametrize(
    ("expected_vnic", "vnic_label", "is_correct"),
    (
        ("2", "Network adapter 2", True),
        ("network adapter 1", "Network adapter 1", True),
        ("10", "Network adapter 10", True),
        ("Network adapter 3", "Network adapter 2", False),
        (" 3", "Network adapter 3", False),
        ("2", "not expected network name", False),
    ),
)
def test_is_correct_vnic(expected_vnic, vnic_label, is_correct):
    assert is_correct_vnic(expected_vnic, vnic_label) == is_correct
