#!/usr/bin/python

# Copyright: (c) 2019, Hetzner Cloud GmbH <info@hetzner-cloud.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = """
---
module: hcloud_server_type_info

short_description: Gather infos about the Hetzner Cloud server types.


description:
    - Gather infos about your Hetzner Cloud server types.
    - This module was called C(hcloud_server_type_facts) before Ansible 2.9, returning C(ansible_facts) and C(hcloud_server_type_facts).
      Note that the M(hetzner.hcloud.hcloud_server_type_info) module no longer returns C(ansible_facts) and the value was renamed to C(hcloud_server_type_info)!

author:
    - Lukas Kaemmerling (@LKaemmerling)

options:
    id:
        description:
            - The ID of the server type you want to get.
        type: int
    name:
        description:
            - The name of the server type you want to get.
        type: str
extends_documentation_fragment:
- hetzner.hcloud.hcloud

"""

EXAMPLES = """
- name: Gather hcloud server type infos
  hcloud_server_type_info:
  register: output

- name: Print the gathered infos
  debug:
    var: output.hcloud_server_type_info
"""

RETURN = """
hcloud_server_type_info:
    description: The server type infos as list
    returned: always
    type: complex
    contains:
        id:
            description: Numeric identifier of the server type
            returned: always
            type: int
            sample: 1937415
        name:
            description: Name of the server type
            returned: always
            type: str
            sample: fsn1
        description:
            description: Detail description of the server type
            returned: always
            type: str
            sample: Falkenstein DC Park 1
        cores:
            description: Number of cpu cores a server of this type will have
            returned: always
            type: int
            sample: 1
        memory:
            description: Memory a server of this type will have in GB
            returned: always
            type: int
            sample: 1
        disk:
            description: Disk size a server of this type will have in GB
            returned: always
            type: int
            sample: 25
        storage_type:
            description: Type of server boot drive
            returned: always
            type: str
            sample: local
        cpu_type:
            description: Type of cpu
            returned: always
            type: str
            sample: shared
        architecture:
            description: Architecture of cpu
            returned: always
            type: str
            sample: x86
        included_traffic:
            description: Free traffic per month in bytes
            returned: always
            type: int
            sample: 21990232555520
        deprecation:
            description: |
              Describes if, when & how the resources was deprecated.
              If this field is set to None the resource is not deprecated. If it has a value, it is considered deprecated.
            returned: success
            type: dict
            contains:
                announced:
                    description: Date of when the deprecation was announced.
                    returned: success
                    type: str
                    sample: "2021-11-09T09:00:00+00:00"
                unavailable_after:
                    description: |
                      After the time in this field, the resource will not be available from the general listing
                      endpoint of the resource type, and it can not be used in new resources. For example, if this is
                      an image, you can not create new servers with this image after the mentioned date.
                    returned: success
                    type: str
                    sample: "2021-12-01T00:00:00+00:00"

"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native
from ansible_collections.hetzner.hcloud.plugins.module_utils.hcloud import Hcloud


class AnsibleHcloudServerTypeInfo(Hcloud):
    def __init__(self, module):
        Hcloud.__init__(self, module, "hcloud_server_type_info")
        self.hcloud_server_type_info = None

    def _prepare_result(self):
        tmp = []

        for server_type in self.hcloud_server_type_info:
            if server_type is not None:
                tmp.append(
                    {
                        "id": to_native(server_type.id),
                        "name": to_native(server_type.name),
                        "description": to_native(server_type.description),
                        "cores": server_type.cores,
                        "memory": server_type.memory,
                        "disk": server_type.disk,
                        "storage_type": to_native(server_type.storage_type),
                        "cpu_type": to_native(server_type.cpu_type),
                        "architecture": to_native(server_type.architecture),
                        "included_traffic": server_type.included_traffic,
                        "deprecation": {
                            "announced": server_type.deprecation.announced.isoformat(),
                            "unavailable_after": server_type.deprecation.unavailable_after.isoformat(),
                        }
                        if server_type.deprecation is not None
                        else None,
                    }
                )
        return tmp

    def get_server_types(self):
        try:
            if self.module.params.get("id") is not None:
                self.hcloud_server_type_info = [self.client.server_types.get_by_id(self.module.params.get("id"))]
            elif self.module.params.get("name") is not None:
                self.hcloud_server_type_info = [self.client.server_types.get_by_name(self.module.params.get("name"))]
            else:
                self.hcloud_server_type_info = self.client.server_types.get_all()

        except Exception as e:
            self.module.fail_json(msg=e.message)

    @staticmethod
    def define_module():
        return AnsibleModule(
            argument_spec=dict(
                id={"type": "int"},
                name={"type": "str"},
                **Hcloud.base_module_arguments(),
            ),
            supports_check_mode=True,
        )


def main():
    module = AnsibleHcloudServerTypeInfo.define_module()

    is_old_facts = module._name == "hcloud_server_type_facts"
    if is_old_facts:
        module.deprecate(
            "The 'hcloud_server_type_facts' module has been renamed to 'hcloud_server_type_info', "
            "and the renamed one no longer returns ansible_facts",
            version="2.0.0",
            collection_name="hetzner.hcloud",
        )

    hcloud = AnsibleHcloudServerTypeInfo(module)
    hcloud.get_server_types()
    result = hcloud.get_result()
    if is_old_facts:
        ansible_info = {
            "hcloud_server_type_facts": result["hcloud_server_type_info"],
            # We keep the key with a naming mistake below to prevent a breaking changes.
            # The entire module will be removed in v2.0.0
            "hcloud_server_type_info": result["hcloud_server_type_info"],
        }
        module.exit_json(ansible_facts=ansible_info)
    else:
        ansible_info = {"hcloud_server_type_info": result["hcloud_server_type_info"]}
        module.exit_json(**ansible_info)


if __name__ == "__main__":
    main()
