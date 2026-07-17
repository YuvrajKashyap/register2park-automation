import pytest

from register2park.flow import FlowError, find_property_result


def test_finds_one_matching_property_result() -> None:
    labels = ["Example North", "Example South, Example City"]

    assert find_property_result(labels, "South, Example City") == 1


def test_property_match_is_case_insensitive() -> None:
    assert find_property_result(["EXAMPLE PROPERTY, EXAMPLE CITY"], "example city") == 0


def test_rejects_ambiguous_property_results() -> None:
    with pytest.raises(FlowError, match="More than one"):
        find_property_result(["Example North", "Example North Annex"], "Example North")


def test_rejects_single_unexpected_result() -> None:
    with pytest.raises(FlowError, match="did not contain"):
        find_property_result(["Different Property"], "Expected Property")
