from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EmailAttachment:
    filename: str
    content_type: str
    content: bytes

    def __post_init__(self) -> None:
        if not self.filename.strip():
            raise ValueError("attachment filename must not be blank")
        parts = self.content_type.split("/")
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise ValueError("content_type must be 'maintype/subtype'")
        if not self.content:
            raise ValueError("attachment content must not be empty")

    @property
    def maintype(self) -> str:
        return self.content_type.split("/", 1)[0]

    @property
    def subtype(self) -> str:
        return self.content_type.split("/", 1)[1]
