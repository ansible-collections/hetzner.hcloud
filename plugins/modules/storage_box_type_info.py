#!/usr/bin/python

# Copyright: (c) 2025, Hetzner Cloud GmbH <info@hetzner-cloud.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import annotations

DOCUMENTATION = """
---
module: storage_box_type_info

short_description: Gather infos about Hetzner Storage Box Types.

description:
    - Gather infos about available Hetzner Storage Box Types.
    - See the L(Storage Box Types documentation,https://docs.hetzner.cloud/reference/hetzner#storage-box-types) for more details.
    - B(Experimental:) Storage Box support is experimental, breaking changes may occur within minor releases.
      See https://github.com/ansible-collections/hetzner.hcloud/issues/756 for more details.

author:
    - Jonas Lammler (@jooola)

options:
    id:
        description:
            - ID of the Storage Box Type to get.
            - If the ID is invalid, the module will fail.
        type: int
    name:
        description:
            - Name of the Storage Box Type to get.
        type: str

extends_documentation_fragment:
  - hetzner.hcloud.hcloud
"""

EXAMPLES = """
- name: Gather Storage Box Types infos
  hetzner.hcloud.storage_box_type_info:
  register: output

- name: Print the gathered infos
  debug:
    var: output.hcloud_storage_box_type_info
"""

RETURN = """
hcloud_storage_box_type_info:
    description: List of Storage Box Types.
    returned: always
    type: list
    contains:
        id:
            description: ID of the Storage Box Type.
            returned: success
            type: int
            sample: 1937415
        name:
            description: Name of the Storage Box Type.
            returned: success
            type: str
            sample: bx21
        description:
            description: Description of the Storage Box Type.
            returned: success
            type: str
            sample: BX21
        snapshot_limit:
            description: Maximum number of allowed manual snapshots.
            returned: success
            type: int
            sample: 10
        automatic_snapshot_limit:
            description: Maximum number of snapshots created automatically by a snapshot plan.
            returned: success
            type: int
            sample: 10
        subaccounts_limit:
            description: Maximum number of subaccounts.
            returned: success
            type: int
            sample: 200
        size:
            description: Available storage in bytes.
            returned: success
            type: int
            sample: 1099511627776
        deprecation:
            description: Deprecation details about the Storage Box Type.
            returned: when deprecated
            type: dict
            contains:
                announced:
                    description: Date when the deprecation was announced.
                    returned: success
                    type: str
                    sample: "2025-06-02T00:00:00Z"
                unavailable_after:
                    description: |
                      Date when the resource will stop being available.

                      The resource will be removed from the list endpoint, but details
                      about the resource can be fetched using its ID.
                    returned: success
                    type: str
                    sample: "2025-09-02T00:00:00Z"
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils.experimental import storage_box_experimental_warning
from ..module_utils.hcloud import AnsibleHCloud
from ..module_utils.vendor.hcloud import HCloudException
from ..module_utils.vendor.hcloud.storage_box_types import BoundStorageBoxType


class AnsibleStorageBoxTypeInfo(AnsibleHCloud):
    represent = "storage_box_types"

    storage_box_types: list[BoundStorageBoxType] | None = None

    def __init__(self, module: AnsibleModule):
        storage_box_experimental_warning(module)
        super().__init__(module)

    def _prepare_result(self):
        result = []

        for o in self.storage_box_types or []:
            if o is None:
                continue

            result.append(
                {
                    "id": o.id,
                    "name": o.name,
                    "description": o.description,
                    "snapshot_limit": o.snapshot_limit,
                    "automatic_snapshot_limit": o.automatic_snapshot_limit,
                    "subaccounts_limit": o.subaccounts_limit,
                    "size": o.size,
                    "deprecation": (
                        {
                            "announced": o.deprecation.announced.isoformat(),
                            "unavailable_after": o.deprecation.unavailable_after.isoformat(),
                        }
                        if o.deprecation is not None
                        else None
                    ),
                }
            )
        return result

    def fetch(self):
        try:
            if (id_ := self.module.params.get("id")) is not None:
                self.storage_box_types = [self.client.storage_box_types.get_by_id(id_)]
            elif (name := self.module.params.get("name")) is not None:
                self.storage_box_types = [self.client.storage_box_types.get_by_name(name)]
            else:
                self.storage_box_types = self.client.storage_box_types.get_all()

        except HCloudException as exception:
            self.fail_json_hcloud(exception)

    @classmethod
    def define_module(cls):
        return AnsibleModule(
            argument_spec=dict(
                id={"type": "int"},
                name={"type": "str"},
                **super().base_module_arguments(),
            ),
            supports_check_mode=True,
        )


def main():
    module = AnsibleStorageBoxTypeInfo.define_module()
    o = AnsibleStorageBoxTypeInfo(module)

    o.fetch()
    result = o.get_result()

    # Legacy return value naming pattern
    result["hcloud_storage_box_type_info"] = result.pop(o.represent)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
