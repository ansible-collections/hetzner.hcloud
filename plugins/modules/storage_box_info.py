#!/usr/bin/python

# Copyright: (c) 2025, Hetzner Cloud GmbH <info@hetzner-cloud.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import annotations

DOCUMENTATION = """
---
module: storage_box_info

short_description: Gather infos about Hetzner Storage Boxes.

description:
    - Gather infos about Hetzner Storage Boxes.
    - See the L(Storage Boxes API documentation,https://docs.hetzner.cloud/reference/hetzner#storage-boxes) for more details.
    - B(Experimental:) Storage Box support is experimental, breaking changes may occur within minor releases.
      See https://github.com/ansible-collections/hetzner.hcloud/issues/756 for more details.

author:
    - Jonas Lammler (@jooola)

options:
    id:
        description:
            - ID of the Storage Box to get.
            - If the ID is invalid, the module will fail.
        type: int
    name:
        description:
            - Name of the Storage Box to get.
        type: str
    label_selector:
        description:
            - Label selector to filter the Storage Boxes to get.
        type: str

extends_documentation_fragment:
  - hetzner.hcloud.hcloud
"""

EXAMPLES = """
- name: Gather all Storage Boxes
  hetzner.hcloud.storage_box_info:
  register: output
- name: Print the gathered infos
  debug:
    var: output.hcloud_storage_box_info

- name: Gather Storage Boxes by label
  hetzner.hcloud.storage_box_info:
    label_selector: env=prod
  register: output
- name: Print the gathered infos
  debug:
    var: output.hcloud_storage_box_info

- name: Gather a Storage Box by name
  hetzner.hcloud.storage_box_info:
    name: backups
  register: output
- name: Print the gathered infos
  debug:
    var: output.hcloud_storage_box_info[0]

- name: Gather a Storage Box by id
  hetzner.hcloud.storage_box_info:
    name: 12345
  register: output
- name: Print the gathered infos
  debug:
    var: output.hcloud_storage_box_info[0]
"""

RETURN = """
hcloud_storage_box_info:
    description: List of Storage Boxes.
    returned: always
    type: list
    elements: dict
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

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import storage_box
from ..module_utils.experimental import storage_box_experimental_warning
from ..module_utils.hcloud import AnsibleHCloud
from ..module_utils.vendor.hcloud import HCloudException
from ..module_utils.vendor.hcloud.storage_boxes import (
    BoundStorageBox,
)


class AnsibleStorageBox(AnsibleHCloud):
    represent = "storage_box"

    storage_box: list[BoundStorageBox] | None = None

    def __init__(self, module: AnsibleModule):
        storage_box_experimental_warning(module)
        super().__init__(module)

    def _prepare_result(self):
        result = []
        for o in self.storage_box or []:
            if o is not None:
                result.append(storage_box.prepare_result(o))

        return result

    def fetch(self):
        try:
            if (id_ := self.module.params.get("id")) is not None:
                self.storage_box = [self.client.storage_boxes.get_by_id(id_)]
            elif (name := self.module.params.get("name")) is not None:
                self.storage_box = [self.client.storage_boxes.get_by_name(name)]
            else:
                params = {}
                if (label_selector := self.module.params.get("label_selector")) is not None:
                    params["label_selector"] = label_selector
                self.storage_box = self.client.storage_boxes.get_all(**params)

        except HCloudException as exception:
            self.fail_json_hcloud(exception)

    @classmethod
    def define_module(cls):
        return AnsibleModule(
            argument_spec=dict(
                id={"type": "int"},
                name={"type": "str"},
                label_selector={"type": "str"},
                **super().base_module_arguments(),
            ),
            supports_check_mode=True,
        )


def main():
    module = AnsibleStorageBox.define_module()
    o = AnsibleStorageBox(module)

    o.fetch()
    result = o.get_result()

    # Legacy return value naming pattern
    result["hcloud_storage_box_info"] = result.pop(o.represent)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
