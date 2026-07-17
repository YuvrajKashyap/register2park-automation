from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ConfigError(ValueError):
    """Raised when the private registration configuration is invalid."""


PLACEHOLDERS = {
    "YOUR_PROPERTY_SEARCH_TERM",
    "EXPECTED_TEXT_FROM_THE_CORRECT_RESULT",
    "YOUR_UNIT_OR_APARTMENT",
    "YOUR_VEHICLE_MAKE",
    "YOUR_VEHICLE_MODEL",
    "YOUR_LICENSE_PLATE",
    "YOUR_EMAIL_ADDRESS",
}


@dataclass(frozen=True, slots=True)
class RegistrationConfig:
    property_query: str
    property_result_match: str
    unit: str
    vehicle_make: str
    vehicle_model: str
    license_plate: str
    confirmation_email: str

    @classmethod
    def from_toml(cls, path: Path) -> RegistrationConfig:
        if not path.is_file():
            raise ConfigError(
                f"Configuration file not found: {path}. Copy config.example.toml to config.toml."
            )

        try:
            raw = tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            raise ConfigError(f"Configuration is not valid TOML: {exc}") from exc

        config = cls(
            property_query=_required(raw, "property", "query"),
            property_result_match=_required(raw, "property", "result_match"),
            unit=_required(raw, "resident", "unit"),
            vehicle_make=_required(raw, "vehicle", "make"),
            vehicle_model=_required(raw, "vehicle", "model"),
            license_plate=_required(raw, "vehicle", "plate"),
            confirmation_email=_required(raw, "contact", "email"),
        )
        config.validate()
        return config

    def validate(self) -> None:
        values = {
            "property.query": self.property_query,
            "property.result_match": self.property_result_match,
            "resident.unit": self.unit,
            "vehicle.make": self.vehicle_make,
            "vehicle.model": self.vehicle_model,
            "vehicle.plate": self.license_plate,
            "contact.email": self.confirmation_email,
        }

        placeholder_fields = [name for name, value in values.items() if value in PLACEHOLDERS]
        if placeholder_fields:
            joined = ", ".join(placeholder_fields)
            raise ConfigError(f"Replace placeholder values in: {joined}")

        if "@" not in self.confirmation_email or self.confirmation_email.startswith("@"):
            raise ConfigError("contact.email must be a valid email address")

        for name, value in values.items():
            if any(character in value for character in ("\n", "\r", "\t")):
                raise ConfigError(f"{name} must be a single line")
            if len(value) > 120:
                raise ConfigError(f"{name} is unexpectedly long")

    def redacted_summary(self) -> str:
        return (
            "Configuration loaded: property, resident, vehicle, plate, and email values "
            "are present and will remain hidden."
        )


def _required(data: dict[str, Any], section: str, field: str) -> str:
    section_data = data.get(section)
    if not isinstance(section_data, dict):
        raise ConfigError(f"Missing [{section}] section")

    value = section_data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{section}.{field} must be a non-empty string")
    return value.strip()
