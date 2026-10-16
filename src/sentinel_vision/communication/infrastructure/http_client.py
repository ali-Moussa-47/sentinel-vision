from __future__ import annotations

import json
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from typing import Protocol

_File = tuple[str, str, bytes]


class HttpError(RuntimeError):
    pass


@dataclass(frozen=True)
class HttpResponse:
    status: int
    body: bytes


class HttpClient(Protocol):
    def post_json(self, url: str, headers: dict[str, str], payload: dict[str, object]) -> HttpResponse: ...

    def post_multipart(
        self, url: str, headers: dict[str, str], fields: dict[str, str], files: dict[str, _File]
    ) -> HttpResponse: ...


class UrllibHttpClient:
    def __init__(self, timeout_seconds: float = 10.0) -> None:
        self._timeout_seconds = timeout_seconds

    def post_json(self, url: str, headers: dict[str, str], payload: dict[str, object]) -> HttpResponse:
        body = json.dumps(payload).encode("utf-8")
        return self._send(url, {**headers, "Content-Type": "application/json"}, body)

    def post_multipart(
        self, url: str, headers: dict[str, str], fields: dict[str, str], files: dict[str, _File]
    ) -> HttpResponse:
        boundary = uuid.uuid4().hex
        body = _encode_multipart(boundary, fields, files)
        content_type = f"multipart/form-data; boundary={boundary}"
        return self._send(url, {**headers, "Content-Type": content_type}, body)

    def _send(self, url: str, headers: dict[str, str], body: bytes) -> HttpResponse:
        request = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self._timeout_seconds) as response:
                return HttpResponse(response.status, response.read())
        except urllib.error.HTTPError as error:
            return HttpResponse(error.code, error.read())
        except (urllib.error.URLError, OSError) as error:
            raise HttpError(f"request to {url} failed: {error}") from error


def _encode_multipart(boundary: str, fields: dict[str, str], files: dict[str, _File]) -> bytes:
    lines: list[bytes] = []
    for name, value in fields.items():
        lines.append(f"--{boundary}".encode())
        lines.append(f'Content-Disposition: form-data; name="{name}"'.encode())
        lines.append(b"")
        lines.append(value.encode("utf-8"))
    for name, (filename, content_type, content) in files.items():
        lines.append(f"--{boundary}".encode())
        lines.append(
            f'Content-Disposition: form-data; name="{name}"; filename="{filename}"'.encode()
        )
        lines.append(f"Content-Type: {content_type}".encode())
        lines.append(b"")
        lines.append(content)
    lines.append(f"--{boundary}--".encode())
    lines.append(b"")
    return b"\r\n".join(lines)
