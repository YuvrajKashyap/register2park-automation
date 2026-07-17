import pytest

from register2park.cli import build_parser, confirm_submission


def test_review_mode_is_the_default() -> None:
    args = build_parser().parse_args([])

    assert args.submit is False
    assert args.yes is False


@pytest.mark.parametrize(
    ("response", "expected"),
    [("SUBMIT", True), ("submit", False), ("yes", False), ("", False)],
)
def test_typed_confirmation_is_explicit(response: str, expected: bool) -> None:
    assert confirm_submission(assume_yes=False, input_fn=lambda _: response) is expected


def test_assume_yes_is_for_intentional_unattended_runs() -> None:
    assert confirm_submission(assume_yes=True, input_fn=lambda _: "") is True
