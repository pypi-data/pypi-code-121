from typing import Any, List, Optional

from nwon_baseline.typings import AnyDict


def ensure_paged_results(
    api_result: AnyDict, expected_number_of_results: Optional[int] = None
) -> List[Any]:
    """
    Ensure a dictionary contains a results key with the expected number of results.
    """

    results = api_result["results"]

    assert isinstance(results, list), "'results' is not a list"

    if expected_number_of_results is not None:
        assert (
            len(results) == expected_number_of_results
        ), f"Expected {expected_number_of_results} result(s), but got {len(results)}"

    return results
