# Note that this module util is **PRIVATE** to the collection. It can have breaking changes at any time.
# Do not use this from other collections or standalone plugins/modules!

from __future__ import annotations

from ._vendor.hcloud.networks import NetworkMember


def prepare_result(o: NetworkMember):
    return {
        "id": o.id,
        "type": o.type,
        "ip": o.ip,
        "alias_ips": o.alias_ips,
        "subnet": o.subnet,
        "status": o.status,
    }
