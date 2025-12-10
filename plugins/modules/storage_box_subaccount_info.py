#!/usr/bin/python

# Copyright: (c) 2025, Hetzner Cloud GmbH <info@hetzner-cloud.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import annotations

DOCUMENTATION = """
---
module: storage_box_subaccount_info

short_description: Gather infos about Hetzner Storage Box Subaccounts.

description:
    - Gather infos about Hetzner Storage Box Subaccounts.
    - See the L(Storage Box Subaccounts API documentation,https://docs.hetzner.cloud/reference/hetzner#storage-box-subaccounts) for more details.
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
            - ID of the Storage Box Subaccount to get.
            - If the ID is invalid, the module will fail.
        type: int
    name:
        description:
            - Name of the Storage Box Subaccount to get.
        type: str
    label_selector:
        description:
            - Label selector to filter the Storage Box Subaccounts to get.
        type: str

extends_documentation_fragment:
  - hetzner.hcloud.hcloud
"""

EXAMPLES = """
- name: Gather all Storage Box Subaccounts
  hetzner.hcloud.storage_box_subaccount_info:
  register: output

- name: Gather Storage Box Subaccounts by label
  hetzner.hcloud.storage_box_subaccount_info:
    label_selector: env=prod
  register: output

- name: Gather a Storage Box Subaccount by name
  hetzner.hcloud.storage_box_subaccount_info:
    name: subaccount1
  register: output

- name: Gather a Storage Box Subaccount by id
  hetzner.hcloud.storage_box_subaccount_info:
    name: 12345
  register: output

- name: Print the gathered infos
  debug:
    var: output.hcloud_storage_box_subaccount_info
"""

RETURN = """
hcloud_storage_box_subaccount_info:
    description: List of Storage Box Subaccounts.
    returned: always
    type: list
    elements: dict
    contains:
        storage_box:
            description: ID of the parent Storage Box.
            returned: always
            type: int
            sample: 514605
        id:
            description: ID of the Storage Box Subaccount.
            returned: always
            type: int
            sample: 158045
        name:
            description: Name of the Storage Box Subaccount.
            returned: always
            type: str
            sample: subaccount1
        description:
            description: Description of the Storage Box Subaccount.
            returned: always
            type: str
            sample: backups from subaccount1
        home_directory:
            description: Home directory of the Storage Box Subaccount.
            returned: always
            type: str
            sample: backups/subaccount1
        username:
            description: Username of the Storage Box Subaccount.
            returned: always
            type: str
            sample: u514605-sub1
        server:
            description: FQDN of the Storage Box Subaccount.
            returned: always
            type: str
            sample: u514605-sub1.your-storagebox.de
        access_settings:
            description: Access settings of the Storage Box Subaccount.
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
                readonly:
                    description: Whether the Subaccount is read-only.
                    returned: always
                    type: bool
                    sample: false
        labels:
            description: User-defined labels (key-value pairs) of the Storage Box Subaccount.
            returned: always
            type: dict
            sample:
                env: prod
        created:
            description: Point in time when the Storage Box Subaccount was created (in RFC3339 format).
            returned: always
            type: str
            sample: "2025-12-03T13:47:47Z"
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import storage_box, storage_box_subaccount
from ..module_utils.experimental import storage_box_experimental_warning
from ..module_utils.hcloud import AnsibleHCloud
from ..module_utils.storage_box_subaccount import NAME_LABEL_KEY
from ..module_utils.vendor.hcloud import HCloudException
from ..module_utils.vendor.hcloud.storage_boxes import (
    BoundStorageBox,
    BoundStorageBoxSubaccount,
)


class AnsibleStorageBoxSubaccountInfo(AnsibleHCloud):
    represent = "storage_box_subaccounts"

    storage_box: BoundStorageBox | None = None
    storage_box_subaccounts: list[BoundStorageBoxSubaccount] | None = None

    def __init__(self, module: AnsibleModule):
        storage_box_experimental_warning(module)
        super().__init__(module)

    def _prepare_result(self):
        result = []

        for o in self.storage_box_subaccounts or []:
            if o is not None:
                # Workaround the missing name property
                # Get the name of the resource from the labels
                name = o.labels.pop(NAME_LABEL_KEY)

                result.append(storage_box_subaccount.prepare_result(o, name))
        return result

    def fetch(self):
        try:
            self.storage_box = storage_box.get(
                self.client.storage_boxes,
                self.module.params.get("storage_box"),
            )

            if (value := self.module.params.get("id")) is not None:
                self.storage_box_subaccounts = [self.storage_box.get_subaccount_by_id(value)]
            elif (value := self.module.params.get("name")) is not None:
                self.storage_box_subaccounts = [storage_box_subaccount.get_by_name(self.storage_box, value)]
            else:
                params = {}
                if (value := self.module.params.get("label_selector")) is not None:
                    params["label_selector"] = value
                self.storage_box_subaccounts = self.storage_box.get_subaccount_all(**params)

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
    module = AnsibleStorageBoxSubaccountInfo.define_module()
    o = AnsibleStorageBoxSubaccountInfo(module)

    o.fetch()
    result = o.get_result()

    # Legacy return value naming pattern
    result["hcloud_storage_box_subaccount_info"] = result.pop(o.represent)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
