from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AlertImage:
    filename: str
    content_type: str
    content: bytes

    def __post_init__(self) -> None:
        if not self.filename.strip():
            raise ValueError("image filename must not be blank")
        parts = self.content_type.split("/")
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise ValueError("content_type must be 'maintype/subtype'")
        if not self.content:
            raise ValueError("image content must not be empty")


@dataclass(frozen=True)
class Alert:
    title: str
    body: str
    image: AlertImage | None = None

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("alert title must not be blank")
        if not self.body.strip():
            raise ValueError("alert body must not be blank")
