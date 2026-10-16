from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlateNumber:
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.isalnum():
            raise ValueError("plate value must be non-empty alphanumeric")

    @classmethod
    def normalize(cls, raw: str) -> PlateNumber:
        cleaned = "".join(character for character in raw.upper() if character.isalnum())
        return cls(cleaned)
