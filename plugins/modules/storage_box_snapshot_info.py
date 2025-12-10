#!/usr/bin/python

# Copyright: (c) 2025, Hetzner Cloud GmbH <info@hetzner-cloud.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import annotations

DOCUMENTATION = """
---
module: storage_box_snapshot_info

short_description: Gather infos about Hetzner Storage Box Snapshots.

description:
    - Gather infos about Hetzner Storage Box Snapshots.
    - See the L(Storage Boxes API documentation,https://docs.hetzner.cloud/reference/hetzner#storage-boxes) for more details.
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
            - ID of the Storage Box Snapshot to get.
            - If the ID is invalid, the module will fail.
        type: int
    name:
        description:
            - Name of the Storage Box Snapshot to get.
        type: str
    label_selector:
        description:
            - Label selector to filter the Storage Box Snapshots to get.
        type: str

extends_documentation_fragment:
  - hetzner.hcloud.hcloud
"""

EXAMPLES = """
- name: Gather all Storage Box Snapshots
  hetzner.hcloud.storage_box_snapshot_info:
    storage_box: my-storage-box
  register: output

- name: Gather Storage Box Snapshots by label
  hetzner.hcloud.storage_box_snapshot_info:
    storage_box: my-storage-box
    label_selector: key=value
  register: output

- name: Gather Storage Box Snapshot by id
  hetzner.hcloud.storage_box_snapshot_info:
    storage_box: 497436
    id: 405920
  register: output

- name: Gather Storage Box Snapshot by name
  hetzner.hcloud.storage_box_snapshot_info:
    storage_box: my-storage-box
    name: 2025-02-12T11-35-19
  register: output

- name: Print the gathered infos
  debug:
    var: output.hcloud_storage_box_snapshot_info
"""

RETURN = """
hcloud_storage_box_snapshot_info:
    description: List of Storage Box Snapshots.
    returned: always
    type: list
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


class AnsibleStorageBoxSnapshotInfo(AnsibleHCloud):
    represent = "storage_box_snapshots"

    storage_box: BoundStorageBox | None = None
    storage_box_snapshots: list[BoundStorageBoxSnapshot] | None = None

    def __init__(self, module: AnsibleModule):
        storage_box_experimental_warning(module)
        super().__init__(module)

    def _prepare_result(self):
        result = []

        for o in self.storage_box_snapshots or []:
            if o is not None:
                result.append(storage_box_snapshot.prepare_result(o))
        return result

    def fetch(self):
        try:
            self.storage_box = storage_box.get(
                self.client.storage_boxes,
                self.module.params.get("storage_box"),
            )

            if (id_ := self.module.params.get("id")) is not None:
                self.storage_box_snapshots = [self.storage_box.get_snapshot_by_id(id_)]
            elif (name := self.module.params.get("name")) is not None:
                self.storage_box_snapshots = [self.storage_box.get_snapshot_by_name(name)]
            else:
                params = {}
                if (value := self.module.params.get("label_selector")) is not None:
                    params["label_selector"] = value
                self.storage_box_snapshots = self.storage_box.get_snapshot_all(**params)

        except HCloudException as exception:
            self.fail_json_hcloud(exception)

    @classmethod
    def define_module(cls):
        return AnsibleModule(
            argument_spec=dict(
                storage_box={"type": "str", "required": True},
                id={"type": "int"},
                name={"type": "str"},
                label_selector={"type": "str"},
                **super().base_module_arguments(),
            ),
            supports_check_mode=True,
        )


def main():
    module = AnsibleStorageBoxSnapshotInfo.define_module()
    o = AnsibleStorageBoxSnapshotInfo(module)

    o.fetch()
    result = o.get_result()

    # Legacy return value naming pattern
    result["hcloud_storage_box_snapshot_info"] = result.pop(o.represent)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
