from __future__ import annotations

from ..module_utils.vendor.hcloud.floating_ips import (
    BoundFloatingIP,
)


def prepare_result(o: BoundFloatingIP):
    return {
        "id": o.id,
        "name": o.name,
        "description": o.description,
        "ip": o.ip,
        "type": o.type,
        "home_location": o.home_location.name,
        "labels": o.labels,
        "server": o.server.name if o.server is not None else None,
        "delete_protection": o.protection["delete"],
    }
