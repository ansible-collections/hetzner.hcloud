#!/usr/bin/python

# Copyright: (c) 2025, Hetzner Cloud GmbH <info@hetzner-cloud.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import annotations

DOCUMENTATION = """
---
module: storage_box_snapshot

short_description: Create and manage Storage Box Snapshots in Hetzner.

description:
    - Create, update and delete Storage Box Snapshots in Hetzner.
    - See the L(Storage Box Snapshots API documentation,https://docs.hetzner.cloud/reference/hetzner#storage-box-snapshots) for more details.
    - B(Experimental:) Storage Box support is experimental, breaking changes may occur within minor releases.
      See https://github.com/ansible-collections/hetzner.hcloud/issues/756 for more details.

author:
    - Jonas Lammler (@jooola)

options:
    storage_box:
        description:
            - ID or Name of the parent Storage Box.
            - Using the ID is preferred, to reduce the amount of API requests.
        type: str
        required: true
    id:
        description:
            - ID of the Storage Box Snapshot to manage.
            - Required when updating or deleting and if no Storage Box Snapshot O(name) is given.
            - If the ID is invalid, the module will fail.
        type: int
    name:
        description:
            - Name of the Storage Box Snapshot to manage.
            - Storage Box Snapshot names are defined by the API and cannot be changed.
            - Required when updating or deleting and if no Storage Box Snapshot O(id) is given.
        type: str
    description:
        description:
            - Description of the Storage Box Snapshot.
        type: str
    labels:
        description:
            - User-defined labels (key-value pairs) for the Storage Box Snapshot.
        type: dict
    state:
        description:
            - State of the Storage Box Snapshot.
        default: present
        choices: [absent, present]
        type: str

extends_documentation_fragment:
  - hetzner.hcloud.hcloud
"""

EXAMPLES = """
- name: Create a Storage Box Snapshot
  hetzner.hcloud.storage_box_snapshot:
    storage_box: my-storage-box
    description: before app migration
    labels:
      env: prod
    state: present

- name: Delete a Storage Box Snapshot by name
  hetzner.hcloud.storage_box_snapshot:
    storage_box: my-storage-box
    name: 2025-12-03T13-47-47
    state: absent

- name: Delete a Storage Box Snapshot by id
  hetzner.hcloud.storage_box_snapshot:
    storage_box: 497436
    id: 405920
    state: absent
"""

RETURN = """
hcloud_storage_box_snapshot:
    description: Details about the Storage Box Snapshot.
    returned: always
    type: dict
    contains:
        storage_box:
            description: ID of the parent Storage Box.
            returned: always
            type: int
            sample: 497436
        id:
            description: ID of the Storage Box Snapshot.
            returned: always
            type: int
            sample: 405920
        name:
            description: Name of the Storage Box Snapshot.
            returned: always
            type: str
            sample: 2025-02-12T11-35-19
        description:
            description: Description of the Storage Box Snapshot.
            returned: always
            type: str
            sample: before app migration
        labels:
            description: User-defined labels (key-value pairs) of the Storage Box Snapshot.
            returned: always
            type: dict
            sample:
                env: prod
        stats:
            description: Statistics of the Storage Box Snapshot.
            returned: always
            type: dict
            contains:
                size:
                    description: Current storage requirements of the Snapshot in bytes.
                    returned: always
                    type: int
                    sample: 10485760
                size_filesystem:
                    description: Size of the compressed file system contained in the Snapshot in bytes.
                    returned: always
                    type: int
                    sample: 10485760
        is_automatic:
            description: Whether the Storage Box Snapshot was created automatically.
            returned: always
            type: bool
            sample: false
        created:
            description: Point in time when the Storage Box Snapshot was created (in RFC3339 format).
            returned: always
            type: str
            sample: "2025-12-03T13:47:47Z"
"""

from ..module_utils import storage_box, storage_box_snapshot
from ..module_utils.experimental import storage_box_experimental_warning
from ..module_utils.hcloud import AnsibleHCloud, AnsibleModule
from ..module_utils.vendor.hcloud import HCloudException
from ..module_utils.vendor.hcloud.storage_boxes import (
    BoundStorageBox,
    BoundStorageBoxSnapshot,
)


class AnsibleStorageBoxSnapshot(AnsibleHCloud):
    represent = "storage_box_snapshot"

    storage_box: BoundStorageBox | None = None
    storage_box_snapshot: BoundStorageBoxSnapshot | None = None

    def __init__(self, module: AnsibleModule):
        storage_box_experimental_warning(module)
        super().__init__(module)

    def _prepare_result(self):
        if self.storage_box_snapshot is None:
            return {}
        return storage_box_snapshot.prepare_result(self.storage_box_snapshot)

    def _fetch(self):
        self.storage_box = storage_box.get(self.client.storage_boxes, self.module.params.get("storage_box"))

        if (value := self.module.params.get("id")) is not None:
            self.storage_box_snapshot = self.storage_box.get_snapshot_by_id(value)
        elif (value := self.module.params.get("name")) is not None:
            self.storage_box_snapshot = self.storage_box.get_snapshot_by_name(value)

    def _create(self):
        params = {}

        if (value := self.module.params.get("description")) is not None:
            params["description"] = value

        if (value := self.module.params.get("labels")) is not None:
            params["labels"] = value

        if not self.module.check_mode:
            resp = self.storage_box.create_snapshot(**params)
            self.storage_box_snapshot = resp.snapshot
            resp.action.wait_until_finished()

            self.storage_box_snapshot.reload()

        self._mark_as_changed()

    def _update(self):
        self.fail_on_invalid_params(
            required_one_of=[["id", "name"]],
        )

        params = {}
        if (value := self.module.params.get("description")) is not None:
            if value != self.storage_box_snapshot.description:
                params["description"] = value
                self._mark_as_changed()

        if (value := self.module.params.get("labels")) is not None:
            if value != self.storage_box_snapshot.labels:
                params["labels"] = value
                self._mark_as_changed()

        # Update only if params holds changes
        if params:
            if not self.module.check_mode:
                self.storage_box_snapshot = self.storage_box_snapshot.update(**params)

    def _delete(self):
        if not self.module.check_mode:
            resp = self.storage_box_snapshot.delete()
            resp.action.wait_until_finished()

        self.storage_box_snapshot = None
        self._mark_as_changed()

    def present(self):
        try:
            self._fetch()
            if self.storage_box_snapshot is None:
                self._create()
            else:
                self._update()

        except HCloudException as exception:
            self.fail_json_hcloud(exception)

    def absent(self):
        try:
            self._fetch()
            if self.storage_box_snapshot is None:
                return
            self._delete()

        except HCloudException as exception:
            self.fail_json_hcloud(exception)

    @classmethod
    def define_module(cls):
        return AnsibleModule(
            argument_spec=dict(
                storage_box={"type": "str", "required": True},
                id={"type": "int"},
                name={"type": "str"},
                description={"type": "str"},
                labels={"type": "dict"},
                state={
                    "choices": ["absent", "present"],
                    "default": "present",
                },
                **super().base_module_arguments(),
            ),
            supports_check_mode=True,
        )


def main():
    module = AnsibleStorageBoxSnapshot.define_module()
    o = AnsibleStorageBoxSnapshot(module)

    match module.params.get("state"):
        case "absent":
            o.absent()
        case _:
            o.present()

    result = o.get_result()

    # Legacy return value naming pattern
    result["hcloud_storage_box_snapshot"] = result.pop(o.represent)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
