from __future__ import annotations

import argparse
from collections.abc import Callable, Sequence
from pathlib import Path

from register2park.config import ConfigError, RegistrationConfig
from register2park.flow import FlowError, ParkingRegistrationFlow

InputFunction = Callable[[str], str]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run an operator-controlled guest parking registration workflow."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config.toml"),
        help="path to the private TOML configuration (default: config.toml)",
    )
    parser.add_argument(
        "--submit",
        action="store_true",
        help="allow the final registration submission; omitted means review mode",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="skip the typed confirmation for an intentionally unattended submit run",
    )
    parser.add_argument("--headless", action="store_true", help="run Chrome without a window")
    parser.add_argument(
        "--timeout",
        type=float,
        default=15,
        help="seconds to wait for each live page step (default: 15)",
    )
    parser.add_argument(
        "--keep-open-seconds",
        type=float,
        default=8,
        help="seconds to keep Chrome open after the workflow (default: 8)",
    )
    return parser


def confirm_submission(*, assume_yes: bool, input_fn: InputFunction = input) -> bool:
    if assume_yes:
        return True
    response = input_fn("This will submit a real parking registration. Type SUBMIT to continue: ")
    return response.strip() == "SUBMIT"


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.yes and not args.submit:
        parser.error("--yes is only valid together with --submit")
    if args.timeout <= 0:
        parser.error("--timeout must be greater than zero")
    if args.keep_open_seconds < 0:
        parser.error("--keep-open-seconds cannot be negative")

    try:
        config = RegistrationConfig.from_toml(args.config)
        print(config.redacted_summary())

        if args.submit and not confirm_submission(assume_yes=args.yes):
            print("Submission cancelled. No browser was opened.")
            return 2

        flow = ParkingRegistrationFlow(
            config,
            timeout_seconds=args.timeout,
            headless=args.headless,
            keep_open_seconds=args.keep_open_seconds,
        )
        flow.run(submit=args.submit)
        return 0
    except (ConfigError, FlowError) as exc:
        print(f"Error: {exc}")
        return 1
