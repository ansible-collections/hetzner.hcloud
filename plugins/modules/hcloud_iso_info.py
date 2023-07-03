#!/usr/bin/python

# Copyright: (c) 2022, Patrice Le Guyader
# heavily inspired by the work of @LKaemmerling
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = """
---
module: hcloud_iso_info

short_description: Gather infos about the Hetzner Cloud ISO list.

description:
    - Gather infos about the Hetzner Cloud ISO list.

author:
    - Patrice Le Guyader (@patlegu)
    - Lukas Kaemmerling (@LKaemmerling)

options:
    id:
        description:
            - The ID of the ISO image you want to get.
        type: int
    name:
        description:
            - The name of the ISO you want to get.
        type: str
    architecture:
        description:
            - Filter ISOs with compatible architecture.
        type: str
        choices: [x86, arm]
    include_architecture_wildcard:
        description:
            - Include ISOs with wildcard architecture (architecture is null).
            - Works only if architecture filter is specified.
        type: bool

extends_documentation_fragment:
    - hetzner.hcloud.hcloud
"""

EXAMPLES = """
- name: Gather hcloud ISO type infos
  hcloud_iso_info:
  register: output

- name: Print the gathered infos
  debug:
    var: output.hcloud_iso_info
"""

RETURN = """
hcloud_iso_info:
    description: The ISO type infos as list
    returned: always
    type: complex
    contains:
        id:
            description: ID of the ISO
            returned: always
            type: int
            sample: 22110
        name:
            description: Unique identifier of the ISO. Only set for public ISOs
            returned: always
            type: str
            sample: debian-12.0.0-amd64-netinst.iso
        description:
            description: Description of the ISO
            returned: always
            type: str
            sample: Debian 12.0 (amd64/netinstall)
        architecture:
            description: >
                Type of cpu architecture this ISO is compatible with.
                None indicates no restriction on the architecture (wildcard).
            returned: when supported
            type: str
            sample: x86
        type:
            description: Type of the ISO, can be one of `public`, `private`.
            returned: always
            type: str
            sample: public
        deprecated:
            description: >
                ISO 8601 timestamp of deprecation, None if ISO is still available.
                After the deprecation time it will no longer be possible to attach the
                ISO to servers.
            returned: always
            type: str
            sample: "2024-12-01T00:00:00+00:00"
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native
from ansible_collections.hetzner.hcloud.plugins.module_utils.hcloud import Hcloud


class AnsibleHcloudIsoInfo(Hcloud):
    def __init__(self, module):
        Hcloud.__init__(self, module, "hcloud_iso_info")
        self.hcloud_iso_info = None

    def _prepare_result(self):
        tmp = []

        for iso_info in self.hcloud_iso_info:
            if iso_info is None:
                continue

            tmp.append(
                {
                    "id": to_native(iso_info.id),
                    "name": to_native(iso_info.name),
                    "description": to_native(iso_info.description),
                    "type": iso_info.type,
                    "architecture": iso_info.architecture,
                    "deprecated": iso_info.deprecated,
                }
            )

        return tmp

    def get_iso_infos(self):
        try:
            if self.module.params.get("id") is not None:
                self.hcloud_iso_info = [self.client.isos.get_by_id(self.module.params.get("id"))]
            elif self.module.params.get("name") is not None:
                self.hcloud_iso_info = [self.client.isos.get_by_name(self.module.params.get("name"))]
            else:
                self.hcloud_iso_info = self.client.isos.get_all(
                    architecture=self.module.params.get("architecture"),
                    include_wildcard_architecture=self.module.params.get("include_wildcard_architecture"),
                )

        except Exception as e:
            self.module.fail_json(msg=e.message)

    @staticmethod
    def define_module():
        return AnsibleModule(
            argument_spec=dict(
                id={"type": "int"},
                name={"type": "str"},
                architecture={"type": "str", "choices": ["x86", "arm"]},
                include_architecture_wildcard={"type": "bool"},
                **Hcloud.base_module_arguments(),
            ),
            supports_check_mode=True,
        )


def main():
    module = AnsibleHcloudIsoInfo.define_module()
    hcloud = AnsibleHcloudIsoInfo(module)
    hcloud.get_iso_infos()
    result = hcloud.get_result()
    ansible_info = {"hcloud_iso_info": result["hcloud_iso_info"]}
    module.exit_json(**ansible_info)


if __name__ == "__main__":
    main()
