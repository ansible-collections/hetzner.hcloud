from __future__ import annotations

from ansible_collections.hetzner.hcloud.plugins.inventory.hcloud import (
    first_ipv6_address,
)


def test_first_ipv6_address():
    found = first_ipv6_address("2001:db8::/64")
    assert isinstance(found, str)
    assert found == "2001:db8::1"
