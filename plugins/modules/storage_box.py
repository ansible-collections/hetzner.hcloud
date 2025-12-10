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
    - B(Experimental:) Storage Box support is experimental, breaking changes may occur within minor releases.
      See https://github.com/ansible-collections/hetzner.hcloud/issues/756 for more details.

author:
    - Jonas Lammler (@jooola)

options:
    id:
        description:
            - ID of the Storage Box to manage.
            - Required if no Storage Box O(name) is given.
            - If the ID is invalid, the module will fail.
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
        aliases: [type]
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
    snapshot_plan:
        description:
            - Snapshot plan of the Storage Box.
            - Use null to disabled the snapshot plan.
        type: dict
        suboptions:
            max_snapshots:
                description:
                    - Maximum amount of Snapshots that will be created by this Snapshot Plan.
                    - Older Snapshots will be deleted.
                type: int
                required: true
            hour:
                description:
                    - Hour when the Snapshot Plan is executed (UTC).
                type: int
                required: true
            minute:
                description:
                    - Minute when the Snapshot Plan is executed (UTC).
                type: int
                required: true
            day_of_week:
                description:
                    - Day of the week when the Snapshot Plan is executed.
                    - Starts at 1 for Monday til 7 for Sunday.
                    - Null means every day.
                type: int
            day_of_month:
                description:
                    - Day of the month when the Snapshot Plan is executed.
                    - Null means every day.
                type: int
    delete_protection:
        description:
            - Protect the Storage Box from deletion.
        type: bool
    snapshot:
        description:
            - Snapshot ID or Name to rollback to.
            - Only used when O(state=rollback_snapshot)
        type: str
    state:
        description:
            - State of the Storage Box.
            - C(reset_password) and C(rollback_snapshot) are not idempotent.
        default: present
        choices: [absent, present, reset_password, rollback_snapshot]
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

- name: Create a Storage Box with snapshot plan
  hetzner.hcloud.storage_box:
    name: my-storage-box
    storage_box_type: bx11
    location: fsn1
    password: my-secret
    snapshot_plan:
      max_snapshots: 10
      hour: 3
      minute: 30
    state: present

- name: Disable a Storage Box snapshot plan
  hetzner.hcloud.storage_box:
    name: my-storage-box
    snapshot_plan: null
    state: present

- name: Reset a Storage Box password
  hetzner.hcloud.storage_box:
    name: my-storage-box
    password: my-secret
    state: reset_password

- name: Rollback a Storage Box to a Snapshot
  hetzner.hcloud.storage_box:
    name: my-storage-box
    snapshot: 2025-12-03T13-47-47
    state: rollback_snapshot

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
        snapshot_plan:
            description: Snapshot plan of the Storage Box.
            returned: when enabled
            type: dict
            contains:
                max_snapshots:
                    description: Maximum amount of Snapshots that will be created by this Snapshot Plan.
                    returned: always
                    type: int
                    sample: 10
                hour:
                    description: Hour when the Snapshot Plan is executed (UTC).
                    returned: always
                    type: int
                    sample: 3
                minute:
                    description: Minute when the Snapshot Plan is executed (UTC).
                    returned: always
                    type: int
                    sample: 30
                day_of_week:
                    description: Day of the week when the Snapshot Plan is executed. Null means every day.
                    returned: always
                    type: int
                    sample: 1
                day_of_month:
                    description: Day of the month when the Snapshot Plan is executed. Null means every day.
                    returned: always
                    type: int
                    sample: 30
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
        stats:
            description: Statistics of the Storage Box.
            returned: always
            type: dict
            contains:
                size:
                    description: Current disk usage in bytes.
                    returned: always
                    type: int
                    sample: 10485760
                size_data:
                    description: Current disk usage for data in bytes.
                    returned: always
                    type: int
                    sample: 10485760
                size_snapshots:
                    description: Current disk usage for snapshots in bytes.
                    returned: always
                    type: int
                    sample: 10485760
"""

from ..module_utils import storage_box
from ..module_utils.client import client_resource_not_found
from ..module_utils.experimental import storage_box_experimental_warning
from ..module_utils.hcloud import AnsibleHCloud, AnsibleModule
from ..module_utils.vendor.hcloud import HCloudException
from ..module_utils.vendor.hcloud.locations import Location
from ..module_utils.vendor.hcloud.storage_box_types import StorageBoxType
from ..module_utils.vendor.hcloud.storage_boxes import (
    BoundStorageBox,
    StorageBoxAccessSettings,
    StorageBoxSnapshot,
    StorageBoxSnapshotPlan,
)


class AnsibleStorageBox(AnsibleHCloud):
    represent = "storage_box"

    storage_box: BoundStorageBox | None = None

    def __init__(self, module: AnsibleModule):
        storage_box_experimental_warning(module)
        super().__init__(module)

    def _prepare_result(self):
        if self.storage_box is not None:
            return storage_box.prepare_result(self.storage_box)
        return {}

    def _fetch(self):
        if self.module.params.get("id") is not None:
            self.storage_box = self.client.storage_boxes.get_by_id(self.module.params.get("id"))
        else:
            self.storage_box = self.client.storage_boxes.get_by_name(self.module.params.get("name"))

    def _create(self):
        self.fail_on_invalid_params(
            required=["name", "storage_box_type", "location", "password"],
        )
        params = {
            "name": self.module.params.get("name"),
            "storage_box_type": StorageBoxType(self.module.params.get("storage_box_type")),
            "location": Location(self.module.params.get("location")),
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
            self.storage_box = resp.storage_box
            resp.action.wait_until_finished()

        if (value := self.module.params.get("delete_protection")) is not None:
            if not self.module.check_mode:
                action = self.storage_box.change_protection(delete=value)
                action.wait_until_finished()

        if self.module.param_is_defined("snapshot_plan"):
            if (value := self.module.params.get("snapshot_plan")) is not None:
                if not self.module.check_mode:
                    action = self.storage_box.enable_snapshot_plan(StorageBoxSnapshotPlan.from_dict(value))
                    action.wait_until_finished()

        if not self.module.check_mode:
            self.storage_box.reload()

        self._mark_as_changed()

    def _update(self):
        need_reload = False

        if (value := self.module.params.get("storage_box_type")) is not None:
            if not self.storage_box.storage_box_type.has_id_or_name(value):
                if not self.module.check_mode:
                    action = self.storage_box.change_type(StorageBoxType(value))
                    action.wait_until_finished()
                    need_reload = True
                self._mark_as_changed()

        if (value := self.module.params.get("access_settings")) is not None:
            access_settings = StorageBoxAccessSettings.from_dict(value)
            if self.storage_box.access_settings.to_payload() != access_settings.to_payload():
                if not self.module.check_mode:
                    action = self.storage_box.update_access_settings(access_settings)
                    action.wait_until_finished()
                    need_reload = True
                self._mark_as_changed()

        if (value := self.module.params.get("delete_protection")) is not None:
            if self.storage_box.protection["delete"] != value:
                if not self.module.check_mode:
                    action = self.storage_box.change_protection(delete=value)
                    action.wait_until_finished()
                    need_reload = True
                self._mark_as_changed()

        if self.module.param_is_defined("snapshot_plan"):
            if (value := self.module.params.get("snapshot_plan")) is not None:
                snapshot_plan = StorageBoxSnapshotPlan.from_dict(value)
                if (
                    self.storage_box.snapshot_plan is None
                    or self.storage_box.snapshot_plan.to_payload() != snapshot_plan.to_payload()
                ):
                    if not self.module.check_mode:
                        action = self.storage_box.enable_snapshot_plan(snapshot_plan)
                        action.wait_until_finished()
                        need_reload = True
                    self._mark_as_changed()
            else:
                if self.storage_box.snapshot_plan is not None:
                    if not self.module.check_mode:
                        action = self.storage_box.disable_snapshot_plan()
                        action.wait_until_finished()
                        need_reload = True
                    self._mark_as_changed()

        params = {}
        if (value := self.module.params.get("name")) is not None and value != self.storage_box.name:
            self.fail_on_invalid_params(required=["id"])
            params["name"] = value
            self._mark_as_changed()

        if (value := self.module.params.get("labels")) is not None and value != self.storage_box.labels:
            params["labels"] = value
            self._mark_as_changed()

        # Update only if params holds changes or the data must be refreshed (actions
        # were triggered)
        if params or need_reload:
            if not self.module.check_mode:
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

    def reset_password(self):
        self.fail_on_invalid_params(
            required=["password"],
        )
        try:
            self._fetch()
            if self.storage_box is None:
                raise client_resource_not_found(
                    "storage box",
                    self.module.params.get("id") or self.module.params.get("name"),
                )
            if not self.module.check_mode:
                action = self.storage_box.reset_password(self.module.params.get("password"))
                action.wait_until_finished()

            self._mark_as_changed()

        except HCloudException as exception:
            self.fail_json_hcloud(exception)

    def rollback_snapshot(self):
        self.fail_on_invalid_params(
            required=["snapshot"],
        )
        try:
            self._fetch()
            if self.storage_box is None:
                raise client_resource_not_found(
                    "storage box",
                    self.module.params.get("id") or self.module.params.get("name"),
                )

            if not self.module.check_mode:
                action = self.storage_box.rollback_snapshot(StorageBoxSnapshot(self.module.params.get("snapshot")))
                action.wait_until_finished()

            self._mark_as_changed()

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
                        reachable_externally={"type": "bool", "default": False},
                        samba_enabled={"type": "bool", "default": False},
                        ssh_enabled={"type": "bool", "default": False},
                        webdav_enabled={"type": "bool", "default": False},
                        zfs_enabled={"type": "bool", "default": False},
                    ),
                },
                snapshot_plan={
                    "type": "dict",
                    "options": dict(
                        max_snapshots={"type": "int", "required": True},
                        hour={"type": "int", "required": True},
                        minute={"type": "int", "required": True},
                        day_of_week={"type": "int"},
                        day_of_month={"type": "int"},
                    ),
                },
                delete_protection={"type": "bool"},
                snapshot={"type": "str"},
                state={
                    "choices": ["absent", "present", "reset_password", "rollback_snapshot"],
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

    match module.params.get("state"):
        case "reset_password":
            o.reset_password()
        case "rollback_snapshot":
            o.rollback_snapshot()
        case "absent":
            o.absent()
        case _:
            o.present()

    result = o.get_result()

    # Legacy return value naming pattern
    result["hcloud_storage_box"] = result.pop(o.represent)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
