#!/usr/bin/python

# Copyright: (c) 2025, Hetzner Cloud GmbH <info@hetzner-cloud.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import annotations

DOCUMENTATION = """
---
module: storage_box

short_description: Create and manage Storage Boxes in Hetzner.

description:
    - Create, update and delete Storage Boxes in Hetzner.
    - See the L(Storage Boxes API documentation,https://docs.hetzner.cloud/reference/hetzner#storage-boxes) for more details.

author:
    - Jonas Lammler (@jooola)

options:
    id:
        description:
            - ID of the Storage Box to manage.
            - Required if no Storage Box O(name) is given.
        type: int
    name:
        description:
            - Name of the Storage Box to manage.
            - Required if no Storage Box O(id) is given.
            - Required if the Storage Box does not exist.
        type: str
    storage_box_type:
        description:
            - Name or ID of the Storage Box Type for the Storage Box.
            - Required if the Storage Box does not exist.
        type: str
    location:
        description:
            - Name or ID of the Location for the Storage Box.
            - Required if the Storage Box does not exist.
        type: str
    password:
        description:
            - Password for the Storage Box.
            - Required if the Storage Box does not exist.
        type: str
    labels:
        description:
            - User-defined labels (key-value pairs) for the Storage Box.
        type: dict
    ssh_keys:
        description:
            - SSH public keys in OpenSSH format to inject into the Storage Box.
        type: list
        elements: str
    access_settings:
        description:
            - Access settings of the Storage Box.
        type: dict
        suboptions:
            reachable_externally:
                description:
                    - Whether access from outside the Hetzner network is allowed.
                type: bool
                default: false
            samba_enabled:
                description:
                    - Whether the Samba subsystem is enabled.
                type: bool
                default: false
            ssh_enabled:
                description:
                    - Whether the SSH subsystem is enabled.
                type: bool
                default: false
            webdav_enabled:
                description:
                    - Whether the WebDAV subsystem is enabled.
                type: bool
                default: false
            zfs_enabled:
                description:
                    - Whether the ZFS snapshot folder is visible.
                type: bool
                default: false
    delete_protection:
        description:
            - Protect the Storage Box from deletion.
        type: bool
        default: false
    state:
        description:
            - State of the Storage Box.
        default: present
        choices: [absent, present]
        type: str

extends_documentation_fragment:
  - hetzner.hcloud.hcloud
"""

EXAMPLES = """
- name: Create a Storage Box
  hetzner.hcloud.storage_box:
    name: my-storage-box
    storage_box_type: bx11
    location: fsn1
    password: my-secret
    labels:
        env: prod
    state: present

- name: Create a Storage Box with access settings
  hetzner.hcloud.storage_box:
    name: my-storage-box
    storage_box_type: bx11
    location: fsn1
    password: my-secret
    access_settings:
        reachable_externally: true
        ssh_enabled: true
        samba_enabled: false
        webdav_enabled: false
        zfs_enabled: false
    state: present

- name: Delete a Storage Box
  hetzner.hcloud.storage_box:
    name: my-storage-box
    state: absent
"""

RETURN = """
hcloud_storage_box:
    description: Details about the Storage Box.
    returned: always
    type: dict
    contains:
        id:
            description: ID of the Storage Box.
            returned: always
            type: int
            sample: 1937415
        name:
            description: Name of the Storage Box.
            returned: always
            type: str
            sample: my-storage-box
        storage_box_type:
            description: Name of the Storage Box Type.
            returned: always
            type: str
            sample: bx11
        location:
            description: Name of the Location of the Storage Box.
            returned: always
            type: str
            sample: fsn1
        labels:
            description: User-defined labels (key-value pairs) of the Storage Box.
            returned: always
            type: dict
            sample:
                env: prod
        delete_protection:
            description: Protect the Storage Box from deletion.
            returned: always
            type: bool
            sample: false
        access_settings:
            description: Access settings of the Storage Box.
            returned: always
            type: dict
            contains:
                reachable_externally:
                    description: Whether access from outside the Hetzner network is allowed.
                    returned: always
                    type: bool
                    sample: false
                samba_enabled:
                    description: Whether the Samba subsystem is enabled.
                    returned: always
                    type: bool
                    sample: false
                ssh_enabled:
                    description: Whether the SSH subsystem is enabled.
                    returned: always
                    type: bool
                    sample: true
                webdav_enabled:
                    description: Whether the WebDAV subsystem is enabled.
                    returned: always
                    type: bool
                    sample: false
                zfs_enabled:
                    description: Whether the ZFS snapshot folder is visible.
                    returned: always
                    type: bool
                    sample: false
        username:
            description: User name of the Storage Box.
            returned: always
            type: str
            sample: u505337
        server:
            description: FQDN of the Storage Box.
            returned: always
            type: str
            sample: u505337.your-storagebox.de
        system:
            description: Host system of the Storage Box.
            returned: always
            type: str
            sample: HEL1-BX136
        status:
            description: Status of the Storage Box.
            returned: always
            type: str
            sample: active

"""
# TODO: stats

from ansible.module_utils.basic import AnsibleModule

from ..module_utils.hcloud import AnsibleHCloud
from ..module_utils.vendor.hcloud import HCloudException
from ..module_utils.vendor.hcloud.actions import BoundAction
from ..module_utils.vendor.hcloud.storage_box_types import StorageBoxType
from ..module_utils.vendor.hcloud.storage_boxes import (
    BoundStorageBox,
    StorageBoxAccessSettings,
)


class AnsibleStorageBox(AnsibleHCloud):
    represent = "storage_box"

    storage_box: BoundStorageBox | None = None
    actions: list[BoundAction]

    def _prepare_result(self):
        o = self.storage_box
        if o is None:
            return {}

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
        }

    def _wait_actions(self):
        for a in self.actions:
            a.wait_until_finished()
        self.actions = []

    def _fetch(self):
        if self.module.params.get("id") is not None:
            self.storage_box = self.client.servers.get_by_id(self.module.params.get("id"))
        else:
            self.storage_box = self.client.servers.get_by_name(self.module.params.get("name"))

    def _create(self):
        self.fail_on_invalid_params(
            required=["name", "storage_box_type", "location", "password"],
        )
        params = {
            "name": self.module.params.get("name"),
            "storage_box_type": self.module.params.get("storage_box_type"),
            "location": self.module.params.get("location"),
            "password": self.module.params.get("password"),
        }

        if (value := self.module.params.get("labels")) is not None:
            params["labels"] = value

        if (value := self.module.params.get("access_settings")) is not None:
            params["access_settings"] = StorageBoxAccessSettings.from_dict(value)

        if (value := self.module.params.get("ssh_keys")) is not None:
            params["ssh_keys"] = value

        if not self.module.check_mode:
            resp = self.client.storage_boxes.create(**params)
            self.actions.append(resp.action)

            self.storage_box = resp.storage_box

        if (value := self.module.params.get("delete_protection")) is not None:
            action = self.storage_box.change_protection(delete=value)
            self.actions.append(action)

        if not self.module.check_mode:
            self._wait_actions()
            self.storage_box.reload()

        self._mark_as_changed()

    def _update(self):
        if (value := self.module.params.get("storage_box_type")) is not None:
            if not self.storage_box.storage_box_type.has_id_or_name(value):
                if not self.module.check_mode:
                    action = self.storage_box.change_type(StorageBoxType(value))
                    self.actions.append(action)
                self._mark_as_changed()

        if (value := self.module.params.get("access_settings")) is not None:
            access_settings = StorageBoxAccessSettings.from_dict(value)
            if self.storage_box.access_settings.to_payload() != access_settings.to_payload():
                if not self.module.check_mode:
                    action = self.storage_box.update_access_settings(access_settings)
                    self.actions.append(action)
                self._mark_as_changed()

        if (value := self.module.params.get("delete_protection")) is not None:
            if self.storage_box.protection["delete"] != value:
                if not self.module.check_mode:
                    action = self.storage_box.change_protection(delete=value)
                    self.actions.append(action)
                self._mark_as_changed()

        # self.storage_box.reset_password

        params = {}
        if (value := self.module.params.get("name")) is not None and value != self.storage_box.name:
            self.fail_on_invalid_params(required=["id"])
            params["name"] = value
            self._mark_as_changed()

        if (value := self.module.params.get("labels")) is not None and value != self.storage_box.labels:
            params["labels"] = value
            self._mark_as_changed()

        if not self.module.check_mode:
            self._wait_actions()

            self.storage_box = self.storage_box.update(**params)

    def _delete(self):
        if not self.module.check_mode:
            resp = self.storage_box.delete()
            resp.action.wait_until_finished()

        self.storage_box = None
        self._mark_as_changed()

    def present(self):
        try:
            self._fetch()
            if self.storage_box is None:
                self._create()
            else:
                self._update()

        except HCloudException as exception:
            self.fail_json_hcloud(exception)

    def absent(self):
        try:
            self._fetch()
            if self.storage_box is None:
                return
            self._delete()

        except HCloudException as exception:
            self.fail_json_hcloud(exception)

    @classmethod
    def define_module(cls):
        return AnsibleModule(
            argument_spec=dict(
                id={"type": "int"},
                name={"type": "str"},
                storage_box_type={"type": "str", "aliases": ["type"]},
                location={"type": "str"},
                password={"type": "str", "no_log": True},
                ssh_keys={"type": "list", "elements": "str", "no_log": False},
                labels={"type": "dict"},
                access_settings={
                    "type": "dict",
                    "options": dict(
                        reachable_externally={"type": "bool"},
                        samba_enabled={"type": "bool"},
                        ssh_enabled={"type": "bool"},
                        webdav_enabled={"type": "bool"},
                        zfs_enabled={"type": "bool"},
                    ),
                },
                delete_protection={"type": "bool"},
                state={
                    "choices": ["absent", "present"],
                    "default": "present",
                },
                **super().base_module_arguments(),
            ),
            required_one_of=[["id", "name"]],
            supports_check_mode=True,
        )


def main():
    module = AnsibleStorageBox.define_module()
    o = AnsibleStorageBox(module)

    state = module.params.get("state")
    if state == "absent":
        o.absent()
    else:
        o.present()

    result = o.get_result()

    module.exit_json(
        hcloud_storage_box=result["storage_box"],
    )


if __name__ == "__main__":
    main()
