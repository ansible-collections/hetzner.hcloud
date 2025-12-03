from __future__ import annotations

from ..module_utils.vendor.hcloud.storage_boxes import (
    BoundStorageBox,
)


def prepare_result(o: BoundStorageBox):
    return {
        "id": o.id,
        "name": o.name,
        "storage_box_type": o.storage_box_type.name,
        "location": o.location.name,
        "labels": o.labels,
        "delete_protection": o.protection["delete"],
        "access_settings": {
            "reachable_externally": o.access_settings.reachable_externally,
            "samba_enabled": o.access_settings.samba_enabled,
            "ssh_enabled": o.access_settings.ssh_enabled,
            "webdav_enabled": o.access_settings.webdav_enabled,
            "zfs_enabled": o.access_settings.zfs_enabled,
        },
        "username": o.username,
        "server": o.server,
        "system": o.system,
        "status": o.status,
        "stats": {
            "size": o.stats.size,
            "size_data": o.stats.size_data,
            "size_snapshots": o.stats.size_snapshots,
        },
    }
