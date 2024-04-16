from __future__ import annotations

import json
from unittest.mock import MagicMock

from plugins.inventory.hcloud import InventoryModule, first_ipv6_address
from plugins.module_utils.vendor.hcloud.servers import BoundServer


def test_first_ipv6_address():
    found = first_ipv6_address("2001:db8::/64")
    assert isinstance(found, str)
    assert found == "2001:db8::1"


def test_build_inventory_server():
    client = MagicMock()
    inventory = InventoryModule()
    inventory.get_option = MagicMock()
    inventory.get_option.return_value = None

    server = BoundServer(
        client,
        {
            "id": 45921624,
            "name": "my-server",
            "labels": {},
            "status": "running",
            "public_net": {
                "ipv4": {
                    "id": 56583278,
                    "ip": "127.0.0.1",
                    "blocked": False,
                    "dns_ptr": "static.1.0.0.127.clients.your-server.de",
                },
                "ipv6": {"id": 56583279, "ip": "2001:db8::/64", "blocked": False, "dns_ptr": []},
                "floating_ips": [],
                "firewalls": [],
            },
            "private_net": [],
            "server_type": {"id": 1, "name": "cx11", "architecture": "x86"},
            "datacenter": {
                "id": 3,
                "name": "hel1-dc2",
                "location": {"id": 3, "name": "hel1"},
            },
            "image": {"id": 114690387, "name": "debian-12", "os_flavor": "debian", "os_version": "12"},
        },
    )
    # pylint: disable=protected-access
    variables = inventory._build_inventory_server(server)

    # Ensure the host_vars are json serializable
    json.dumps(variables)

    assert variables == {
        "id": 45921624,
        "name": "my-server",
        "status": "running",
        "type": "cx11",
        "server_type": "cx11",
        "architecture": "x86",
        "location": "hel1",
        "datacenter": "hel1-dc2",
        "labels": {},
        "ipv4": "127.0.0.1",
        "ipv6": "2001:db8::1",
        "ipv6_network": "2001:db8::",
        "ipv6_network_mask": "64",
        "private_networks": [],
        "image_id": 114690387,
        "image_name": "debian-12",
        "image_os_flavor": "debian",
        "ansible_host": None,
    }
