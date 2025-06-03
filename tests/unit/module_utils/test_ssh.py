from __future__ import annotations

import pytest
from ansible_collections.hetzner.hcloud.plugins.module_utils.ssh import (
    ssh_public_key_md5_fingerprint,
)


@pytest.mark.parametrize(
    ("public_key", "fingerprint"),
    [
        (
            "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILNWUEdTk1oxrjUZ5erbKUmJM3VxQ9DLocgt/HFohCf6 comment",
            "ce:cf:37:b9:38:40:ad:80:b2:8b:2c:5c:83:b5:af:0b",
        ),
        (
            "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILNWUEdTk1oxrjUZ5erbKUmJM3VxQ9DLocgt/HFohCf6",  # No comment
            "ce:cf:37:b9:38:40:ad:80:b2:8b:2c:5c:83:b5:af:0b",
        ),
        (
            "ecdsa-sha2-nistp521 AAAAE2VjZHNhLXNoYTItbmlzdHA1MjEAAAAIbmlzdHA1MjEAAACFBABOUmmgxbhhauMg97GMwHcjWXM35MwFmlSKx7klWpPr3jMbabGQzINFVXexgf6Tru0D5a7NU/Hkx9t2yOtqKHJOIQB5/NKktqYelul4X56WYV/64RSm6xIjcolNao9fUbawnIwh9mvaQQg5v1BiJfPJ6p6LcWPunzfm6DztU1tHwLtjTw== comment",  # noqa: E501
            "bf:61:7b:7f:ab:c7:af:25:aa:d7:d5:e8:5f:87:5c:66",
        ),
    ],
)
def test_ssh_public_key_md5_fingerprint(public_key: str, fingerprint: str):
    assert ssh_public_key_md5_fingerprint(public_key) == fingerprint
