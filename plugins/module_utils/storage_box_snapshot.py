from __future__ import annotations

from ..module_utils.vendor.hcloud.storage_boxes import (
    BoundStorageBoxSnapshot,
)


def prepare_result(o: BoundStorageBoxSnapshot):
    return {
        "storage_box": o.storage_box.id,
        "id": o.id,
        "name": o.name,
        "description": o.description,
        "labels": o.labels,
        "stats": {
            "size": o.stats.size,
            "size_filesystem": o.stats.size_filesystem,
        },
        "is_automatic": o.is_automatic,
        "created": o.created.isoformat(),
    }
