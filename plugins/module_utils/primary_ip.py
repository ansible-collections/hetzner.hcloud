from __future__ import annotations

from ..module_utils.vendor.hcloud.primary_ips import (
    BoundPrimaryIP,
)


def prepare_result(o: BoundPrimaryIP):
    return {
        "id": o.id,
        "name": o.name,
        "ip": o.ip,
        "type": o.type,
        "datacenter": o.datacenter.name,
        "labels": o.labels,
        "delete_protection": o.protection["delete"],
        "assignee_id": o.assignee_id,
        "assignee_type": o.assignee_type,
        "auto_delete": o.auto_delete,
    }
