from pathlib import Path

import pytest

from register2park.config import ConfigError, RegistrationConfig

VALID_CONFIG = """
[property]
query = "Example Property"
result_match = "Example Property, Example City"

[resident]
unit = "101"

[vehicle]
make = "Example Make"
model = "Example Model"
plate = "ABC123"

[contact]
email = "operator@example.com"
"""


def write_config(tmp_path: Path, content: str = VALID_CONFIG) -> Path:
    path = tmp_path / "config.toml"
    path.write_text(content, encoding="utf-8")
    return path


def test_loads_valid_private_config(tmp_path: Path) -> None:
    config = RegistrationConfig.from_toml(write_config(tmp_path))

    assert config.property_query == "Example Property"
    assert config.license_plate == "ABC123"
    assert "ABC123" not in config.redacted_summary()
    assert "operator@example.com" not in config.redacted_summary()


def test_rejects_unedited_placeholder_config(tmp_path: Path) -> None:
    example = Path("config.example.toml").read_text(encoding="utf-8")

    with pytest.raises(ConfigError, match="Replace placeholder values"):
        RegistrationConfig.from_toml(write_config(tmp_path, example))


def test_rejects_missing_required_section(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match=r"Missing \[contact\] section"):
        RegistrationConfig.from_toml(
            write_config(
                tmp_path, VALID_CONFIG.replace('[contact]\nemail = "operator@example.com"', "")
            )
        )


def test_rejects_invalid_email(tmp_path: Path) -> None:
    content = VALID_CONFIG.replace("operator@example.com", "not-an-email")

    with pytest.raises(ConfigError, match="valid email"):
        RegistrationConfig.from_toml(write_config(tmp_path, content))
