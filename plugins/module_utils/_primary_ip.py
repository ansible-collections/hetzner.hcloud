# Note that this module util is **PRIVATE** to the collection. It can have breaking changes at any time.
# Do not use this from other collections or standalone plugins/modules!

from __future__ import annotations

from ._vendor.hcloud.primary_ips import (
    BoundPrimaryIP,
)


def prepare_result(o: BoundPrimaryIP):
    return {
        "id": o.id,
        "name": o.name,
        "ip": o.ip,
        "type": o.type,
        "location": o.location.name,
        "datacenter": o.datacenter and o.datacenter.name,
        "labels": o.labels,
        "delete_protection": o.protection["delete"],
        "assignee_id": o.assignee_id,
        "assignee_type": o.assignee_type,
        "auto_delete": o.auto_delete,
    }
