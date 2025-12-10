from __future__ import annotations

from ..module_utils.vendor.hcloud.storage_boxes import (
    BoundStorageBox,
    BoundStorageBoxSubaccount,
)

NAME_LABEL_KEY = "ansible-name"


def get_by_name(storage_box: BoundStorageBox, name: str):
    if not name:
        raise ValueError(f"invalid storage box subaccount name: '{name}'")

    result = storage_box.get_subaccount_list(
        label_selector=f"{NAME_LABEL_KEY}={name}",
    )
    if len(result.subaccounts) == 0:
        return None
    if len(result.subaccounts) == 1:
        return result.subaccounts[0]

    raise ValueError(f"found multiple storage box subaccount with the same name: {name}")


def prepare_result(o: BoundStorageBoxSubaccount, name: str):
    return {
        "storage_box": o.storage_box.id,
        "id": o.id,
        "name": name,
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
