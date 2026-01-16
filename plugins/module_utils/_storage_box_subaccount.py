# Note that this module util is **PRIVATE** to the collection. It can have breaking changes at any time.
# Do not use this from other collections or standalone plugins/modules!

from __future__ import annotations

from ._vendor.hcloud.storage_boxes import (
    BoundStorageBox,
    BoundStorageBoxSubaccount,
)

NAME_LABEL_KEY = "ansible-name"


def get_by_label_name(storage_box: BoundStorageBox, name: str):
    """
    Kept for backward compatible upgrade from label based name.
    """
    result = storage_box.get_subaccount_list(
        label_selector=f"{NAME_LABEL_KEY}={name}",
    )
    if len(result.subaccounts) == 1:
        return result.subaccounts[0]
    return None


def prepare_result(o: BoundStorageBoxSubaccount):
    return {
        "storage_box": o.storage_box.id,
        "id": o.id,
        "name": o.name,
        "description": o.description,
        "username": o.username,
        "home_directory": o.home_directory,
        "server": o.server,
        "access_settings": {
            "reachable_externally": o.access_settings.reachable_externally,
            "samba_enabled": o.access_settings.samba_enabled,
            "ssh_enabled": o.access_settings.ssh_enabled,
            "webdav_enabled": o.access_settings.webdav_enabled,
            "readonly": o.access_settings.readonly,
        },
        "labels": o.labels,
        "created": o.created.isoformat(),
    }
