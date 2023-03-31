#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Hetzner Cloud GmbH <info@hetzner-cloud.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: hcloud_load_balancer_type_info

short_description: Gather infos about the Hetzner Cloud Load Balancer types.


description:
    - Gather infos about your Hetzner Cloud Load Balancer types.

author:
    - Lukas Kaemmerling (@LKaemmerling)
version_added: 0.1.0
options:
    id:
        description:
            - The ID of the Load Balancer type you want to get.
        type: int
    name:
        description:
            - The name of the Load Balancer type you want to get.
        type: str
extends_documentation_fragment:
- hetzner.hcloud.hcloud

'''

EXAMPLES = """
- name: Gather hcloud Load Balancer type infos
  hcloud_load_balancer_type_info:
  register: output

- name: Print the gathered infos
  debug:
    var: output.hcloud_load_balancer_type_info
"""

RETURN = """
hcloud_load_balancer_type_info:
    description: The Load Balancer type infos as list
    returned: always
    type: complex
    contains:
        id:
            description: Numeric identifier of the Load Balancer type
            returned: always
            type: int
            sample: 1937415
        name:
            description: Name of the Load Balancer type
            returned: always
            type: str
            sample: lb11
        description:
            description: Description of the Load Balancer type
            returned: always
            type: str
            sample: LB11
        max_connections:
            description: Number of maximum simultaneous open connections
            returned: always
            type: int
            sample: 1
        max_services:
            description: Number of services a Load Balancer of this type can have
            returned: always
            type: int
            sample: 1
        max_targets:
            description: Number of targets a single Load Balancer can have
            returned: always
            type: int
            sample: 25
        max_assigned_certificates:
            description: Number of SSL Certificates that can be assigned to a single Load Balancer
            returned: always
            type: int
            sample: 5
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from ansible_collections.hetzner.hcloud.plugins.module_utils.hcloud import Hcloud


class AnsibleHcloudLoadBalancerTypeInfo(Hcloud):
    def __init__(self, module):
        Hcloud.__init__(self, module, "hcloud_load_balancer_type_info")
        self.hcloud_load_balancer_type_info = None

    def _prepare_result(self):
        tmp = []

        for load_balancer_type in self.hcloud_load_balancer_type_info:
            if load_balancer_type is not None:
                tmp.append({
                    "id": to_native(load_balancer_type.id),
                    "name": to_native(load_balancer_type.name),
                    "description": to_native(load_balancer_type.description),
                    "max_connections": load_balancer_type.max_connections,
                    "max_services": load_balancer_type.max_services,
                    "max_targets": load_balancer_type.max_targets,
                    "max_assigned_certificates": load_balancer_type.max_assigned_certificates
                })
        return tmp

    def get_load_balancer_types(self):
        try:
            if self.module.params.get("id") is not None:
                self.hcloud_load_balancer_type_info = [self.client.load_balancer_types.get_by_id(
                    self.module.params.get("id")
                )]
            elif self.module.params.get("name") is not None:
                self.hcloud_load_balancer_type_info = [self.client.load_balancer_types.get_by_name(
                    self.module.params.get("name")
                )]
            else:
                self.hcloud_load_balancer_type_info = self.client.load_balancer_types.get_all()

        except Exception as e:
            self.module.fail_json(msg=e.message)

    @staticmethod
    def define_module():
        return AnsibleModule(
            argument_spec=dict(
                id={"type": "int"},
                name={"type": "str"},
                **Hcloud.base_module_arguments()
            ),
            supports_check_mode=True,
        )


def main():
    module = AnsibleHcloudLoadBalancerTypeInfo.define_module()

    hcloud = AnsibleHcloudLoadBalancerTypeInfo(module)
    hcloud.get_load_balancer_types()
    result = hcloud.get_result()
    ansible_info = {
        'hcloud_load_balancer_type_info': result['hcloud_load_balancer_type_info']
    }
    module.exit_json(**ansible_info)


if __name__ == "__main__":
    main()
