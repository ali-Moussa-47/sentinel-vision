from __future__ import annotations

import pytest

from sentinel_vision.communication.domain.email_address import (
    EmailAddress,
    EmailAddressInvalidError,
)


def test_valid_address_is_accepted() -> None:
    assert EmailAddress("alerts@example.com").value == "alerts@example.com"


@pytest.mark.parametrize("value", ["", "plain", "no@domain", "a@b", "a b@example.com"])
def test_invalid_address_is_rejected(value: str) -> None:
    with pytest.raises(EmailAddressInvalidError):
        EmailAddress(value)
