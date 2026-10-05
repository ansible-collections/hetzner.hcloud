# Note that this module util is **PRIVATE** to the collection. It can have breaking changes at any time.
# Do not use this from other collections or standalone plugins/modules!

from __future__ import annotations

from ._vendor.hcloud.load_balancers import (
    LoadBalancer,
    PublicNetwork,
)


def prepare_result(o: LoadBalancer) -> dict:
    return {
        "id": o.id,
        "name": o.name,
        "public_net": prepare_public_net_result(o.public_net),
        "ipv4_address": o.public_net.ipv4.ip,
        "ipv6_address": o.public_net.ipv6.ip,
        "private_ipv4_address": (o.private_net[0].ip if len(o.private_net) else None),
        "load_balancer_type": o.load_balancer_type.name,
        "algorithm": o.algorithm.type,
        "location": o.location.name,
        "labels": o.labels,
        "delete_protection": o.protection["delete"],
        "disable_public_interface": not o.public_net.enabled,
    }


def prepare_public_net_result(o: PublicNetwork) -> dict:
    return {
        "ipv4": {
            "primary_ip": o.ipv4.primary_ip and o.ipv4.primary_ip.id,
            "blocked": o.ipv4.blocked,
            "ip_address": o.ipv4.ip,
            "dns_ptr": o.ipv4.dns_ptr,
        },
        "ipv6": {
            "primary_ip": o.ipv6.primary_ip and o.ipv6.primary_ip.id,
            "blocked": o.ipv6.blocked,
            "ip_address": o.ipv6.ip,
            "dns_ptr": o.ipv6.dns_ptr,
        },
    }
