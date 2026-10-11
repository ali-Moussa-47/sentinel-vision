from __future__ import annotations

import re
from dataclasses import dataclass

_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class EmailAddressInvalidError(ValueError):
    pass


@dataclass(frozen=True)
class EmailAddress:
    value: str

    def __post_init__(self) -> None:
        if not _PATTERN.match(self.value):
            raise EmailAddressInvalidError(f"invalid email address: {self.value!r}")
