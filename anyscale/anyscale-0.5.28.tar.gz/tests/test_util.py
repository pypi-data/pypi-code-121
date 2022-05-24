import time
from typing import Any, Dict
from unittest.mock import patch

import pytest

from anyscale.util import (
    _check_python_version,
    _ray_version_major_minor,
    _update_external_ids_for_policy,
    extract_versions_from_image_name,
    number_of_external_ids_in_policy,
    poll,
    sleep_till,
    updating_printer,
)


def test_updating_printer() -> None:
    out = ""

    def mock_print(
        string: str, *args: Any, end: str = "\n", flush: bool = False, **kwargs: Any
    ) -> None:
        nonlocal out
        out += string
        out += end

    with patch("anyscale.util.print", new=mock_print), patch(
        "shutil.get_terminal_size"
    ) as get_terminal_size_mock:
        get_terminal_size_mock.return_value = (10, 24)
        with updating_printer() as print_status:
            print_status("Step 1")
            print_status("Step 2")
            print_status("Step 3")

    assert out == (
        "\r          \r"
        "Step 1"
        "\r          \r"
        "Step 2"
        "\r          \r"
        "Step 3"
        "\r          \r"
    )


def test_updating_printer_multiline() -> None:
    out = ""

    def mock_print(
        string: str, *args: Any, end: str = "\n", flush: bool = False, **kwargs: Any
    ) -> None:
        nonlocal out
        out += string
        out += end

    with patch("anyscale.util.print", new=mock_print), patch(
        "shutil.get_terminal_size"
    ) as get_terminal_size_mock:
        get_terminal_size_mock.return_value = (10, 24)
        with updating_printer() as print_status:
            print_status("Step 1\nExtra stuff")
            print_status("ExtraLongLine12345")
            print_status("ExtraLongLine12345\nExtra stuff")
            print_status("Step 3")

    assert out == (
        "\r          \r"
        "Step 1..."
        "\r          \r"
        "ExtraLo..."
        "\r          \r"
        "ExtraLo..."
        "\r          \r"
        "Step 3"
        "\r          \r"
    )


STATEMENT_TEMPLATE = {
    "Action": "sts:AssumeRole",
    "Effect": "Allow",
    "Principal": {"AWS": "arn:aws:iam::ACCT_ID:root"},
}


@pytest.mark.parametrize(
    "statement_policy,expected_conditions",
    [
        pytest.param(
            [STATEMENT_TEMPLATE],
            [{"StringEquals": {"sts:ExternalId": ["new_id"]}}],
            id="OneStatement,NoPrior",
        ),
        pytest.param(
            [STATEMENT_TEMPLATE, STATEMENT_TEMPLATE],
            [{"StringEquals": {"sts:ExternalId": ["new_id"]}}] * 2,
            id="TwoStatements,NoPrior",
        ),
        pytest.param(
            [
                {
                    "Condition": {"StringEquals": {"sts:ExternalId": "old_id"}},
                    **STATEMENT_TEMPLATE,  # type: ignore
                }
            ],
            [{"StringEquals": {"sts:ExternalId": ["old_id", "new_id"]}}],
            id="OneStatement,OnePriorExternal",
        ),
        pytest.param(
            [
                {
                    "Condition": {"StringEquals": {"sts:ExternalId": "old_id"}},
                    **STATEMENT_TEMPLATE,  # type: ignore
                },
                STATEMENT_TEMPLATE,
            ],
            [
                {"StringEquals": {"sts:ExternalId": ["old_id", "new_id"]}},
                {"StringEquals": {"sts:ExternalId": ["new_id"]}},
            ],
            id="TwoStatements,OnePriorExternal",
        ),
        pytest.param(
            [
                {
                    "Condition": {"StringNotEquals": {"sts:ExternalId": "old_id"}},
                    **STATEMENT_TEMPLATE,  # type: ignore
                },
                STATEMENT_TEMPLATE,
            ],
            [
                {
                    "StringEquals": {"sts:ExternalId": ["new_id"]},
                    "StringNotEquals": {"sts:ExternalId": "old_id"},
                },
            ],
            id="OneStatemnt,OtherCondition",
        ),
    ],
)
def test_update_external_ids_for_policy(statement_policy, expected_conditions):
    policy_document = {
        "Statement": statement_policy,
        "Version": "2012-10-17",
    }
    new_policy = _update_external_ids_for_policy(policy_document, "new_id")

    for new, expected in zip(new_policy["Statement"], expected_conditions):
        assert new["Condition"] == expected


@pytest.mark.parametrize(
    "statement,num_ext_ids",
    [
        pytest.param(
            [STATEMENT_TEMPLATE, STATEMENT_TEMPLATE],
            0,
            id="MultipleStatements,NoExtID",
        ),
        pytest.param(
            [
                {
                    "Condition": {"StringEquals": {"sts:ExternalId": "old_id"}},
                    **STATEMENT_TEMPLATE,  # type: ignore
                },
                STATEMENT_TEMPLATE,
            ],
            1,
            id="OneExternalID,MultipleStatements",
        ),
        pytest.param(
            [
                {
                    "Condition": {
                        "StringEquals": {"sts:ExternalId": ["id_one", "id_two"]}
                    },
                    **STATEMENT_TEMPLATE,  # type: ignore
                }
            ],
            2,
            id="ExternalIdList",
        ),
    ],
)
def test_number_of_external_ids_in_policy(statement: Dict[str, Any], num_ext_ids: int):
    policy = {
        "Statement": statement,
        "Version": "2012-10-17",
    }
    assert number_of_external_ids_in_policy(policy) == num_ext_ids


@pytest.mark.parametrize(
    "image_name, expected, exception_substr",
    [
        ("anyscale/ray-ml:1.11.1-py38-gpu", ("py38", "1.11.1"), None),
        ("anyscale/ray:1.12-py37-cpu", ("py37", "1.12"), None),
        ("anyscale/ray:1.12-py37", ("py37", "1.12"), None),
        ("anyscale/ray:1.12py37", None, "got 1.12py37"),
    ],
)
def test_extract_versions_from_image_name(image_name, expected, exception_substr):
    if exception_substr is not None:
        with pytest.raises(ValueError) as exc_info:
            extract_versions_from_image_name(image_name)
        assert exception_substr in str(exc_info.value)
    else:
        python_version, ray_version = extract_versions_from_image_name(image_name)
        assert (python_version, ray_version) == expected


@pytest.mark.parametrize(
    "ray_version, expected, exception_substr",
    [
        ("1.12", (1, 12), None),
        ("0.0", (0, 0), None),
        ("0:0", (0, 0), "unexpected"),
        ("112", (0, 0), "unexpected"),
        ("", (0, 0), "unexpected"),
        ("1.x", (0, 0), "unexpected"),
        ("0x10.12", (0, 0), "unexpected"),
    ],
)
def test_ray_version_major_minor(ray_version, expected, exception_substr):
    if exception_substr is not None:
        with pytest.raises(Exception) as exc_info:
            _ray_version_major_minor(ray_version)
        assert exception_substr in str(exc_info.value)
    else:
        got = _ray_version_major_minor(ray_version)
        assert got == expected


@pytest.mark.parametrize(
    "python_version, exception_substr",
    [
        ("py36", None),
        ("py37", None),
        ("py38", None),
        ("py39", None),
        ("py10", "got py10"),
        ("py3.6", "got py3.6"),
        ("py3", "got py3."),
        ("py35", "got py35"),
    ],
)
def test_python_version_major_minor(python_version, exception_substr):
    if exception_substr is not None:
        with pytest.raises(Exception) as exc_info:
            _check_python_version(python_version)
        assert exception_substr in str(exc_info.value)
    else:
        _check_python_version(python_version)


def test_poll():
    """Test the poll function.
    """

    end_time = time.time() + 0.5
    sleep_till(end_time)
    assert time.time() == pytest.approx(end_time)

    # This should poll forever
    count = 0
    start_time = time.time()
    for i in poll(0.01):
        count += 1
        assert count == i
        if count > 100:
            break
    assert count == 101
    assert time.time() == pytest.approx(start_time + 1.01)

    # Assert we stop iterating at max iter
    expected_i = 1
    for i in poll(0.01, max_iter=5):
        assert i == expected_i
        expected_i += 1
        assert i <= 5
