#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Hetzner Cloud GmbH <info@hetzner-cloud.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: hcloud_load_balancer_target

short_description: Manage Hetzner Cloud Load Balancer targets


description:
    - Create and delete Hetzner Cloud Load Balancer targets

author:
    - Lukas Kaemmerling (@lkaemmerling)
version_added: 0.1.0
options:
    type:
        description:
            - The type of the target.
        type: str
        choices: [ server ]
        required: true
    load_balancer:
        description:
            - The name of the Hetzner Cloud Load Balancer.
        type: str
        required: true
    server:
        description:
            - The name of the Hetzner Cloud Server.
            - Required if I(type) is server
        type: str
    use_private_ip:
        description:
            - Route the traffic over the private IP of the Load Balancer through a Hetzner Cloud Network.
            - Load Balancer needs to be attached to a network. See M(hetzner.hcloud.hcloud.hcloud_load_balancer_network)
        type: bool
    state:
        description:
            - State of the load_balancer_network.
        default: present
        choices: [ absent, present ]
        type: str

requirements:
  - hcloud-python >= 1.8.1

extends_documentation_fragment:
- hetzner.hcloud.hcloud

'''

EXAMPLES = """
- name: Create a server Load Balancer target
  hcloud_load_balancer_target:
    type: server
    load_balancer: my-LoadBalancer
    server: my-server
    state: present

- name: Ensure the Load Balancer target is absent (remove if needed)
  hcloud_load_balancer_target:
    type: server
    load_balancer: my-LoadBalancer
    server: my-server
    state: absent
"""

RETURN = """
hcloud_load_balancer_target:
    description: The relationship between a Load Balancer and a network
    returned: always
    type: complex
    contains:
        type:
            description: Type of the Load Balancer Target
            type: str
            returned: always
            sample: server
        load_balancer:
            description: Name of the Load Balancer
            type: str
            returned: always
            sample: my-LoadBalancer
        server:
            description: Name of the Server
            type: str
            returned: if I(type) is server
            sample: my-server
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from ansible_collections.hetzner.hcloud.plugins.module_utils.hcloud import Hcloud

try:
    from hcloud import APIException
    from hcloud.load_balancers.domain import LoadBalancerTarget
except ImportError:
    APIException = None


class AnsibleHcloudLoadBalancerTarget(Hcloud):
    def __init__(self, module):
        super(AnsibleHcloudLoadBalancerTarget, self).__init__(module, "hcloud_load_balancer_target")
        self.hcloud_load_balancer = None
        self.hcloud_load_balancer_target = None
        self.hcloud_server = None

    def _prepare_result(self):
        return {
            "type": to_native(self.hcloud_load_balancer_target.type),
            "load_balancer": to_native(self.hcloud_load_balancer.name),
            "server": to_native(self.hcloud_server.name) if self.hcloud_server else None,
        }

    def _get_load_balancer_and_target(self):
        try:
            self.hcloud_load_balancer = self.client.load_balancers.get_by_name(self.module.params.get("load_balancer"))
            if self.module.params.get("type") == "server":
                self.hcloud_server = self.client.servers.get_by_name(self.module.params.get("server"))
            self.hcloud_load_balancer_target = None
        except APIException as e:
            self.module.fail_json(msg=e.message)

    def _get_load_balancer_target(self):
        for target in self.hcloud_load_balancer.targets:
            if self.module.params.get("type") == "server":
                if target.server.id == self.hcloud_server.id:
                    self.hcloud_load_balancer_target = target

    def _create_load_balancer_target(self):
        params = {
            "target": None
        }

        if self.module.params.get("type") == "server":
            self.module.fail_on_missing_params(
                required_params=["server"]
            )
            params["target"] = LoadBalancerTarget(type=self.module.params.get("type"), server=self.hcloud_server,
                                                  use_private_ip=self.module.params.get("use_private_ip"))
        if not self.module.check_mode:
            try:
                self.hcloud_load_balancer.add_target(**params).wait_until_finished()
            except APIException as e:
                self.module.fail_json(msg=e.message)

        self._mark_as_changed()
        self._get_load_balancer_and_target()
        self._get_load_balancer_target()

    def present_load_balancer_target(self):
        self._get_load_balancer_and_target()
        self._get_load_balancer_target()
        if self.hcloud_load_balancer_target is None:
            self._create_load_balancer_target()

    def delete_load_balancer_target(self):
        self._get_load_balancer_and_target()
        self._get_load_balancer_target()
        if self.hcloud_load_balancer_target is not None and self.hcloud_load_balancer is not None:
            if not self.module.check_mode:
                target = None
                if self.module.params.get("type") == "server":
                    target = LoadBalancerTarget(type=self.module.params.get("type"),
                                                server=self.hcloud_server,
                                                use_private_ip=self.module.params.get("use_private_ip"))
                self.hcloud_load_balancer.remove_target(target).wait_until_finished()
            self._mark_as_changed()
        self.hcloud_load_balancer_target = None

    @staticmethod
    def define_module():
        return AnsibleModule(
            argument_spec=dict(
                type={"type": "str", "required": True, "choices": ["server"]},
                load_balancer={"type": "str", "required": True},
                server={"type": "str"},
                use_private_ip={"type": "bool", "default": False},
                state={
                    "choices": ["absent", "present"],
                    "default": "present",
                },
                **Hcloud.base_module_arguments()
            ),
            supports_check_mode=True,
        )


def main():
    module = AnsibleHcloudLoadBalancerTarget.define_module()

    hcloud = AnsibleHcloudLoadBalancerTarget(module)
    state = module.params["state"]
    if state == "absent":
        hcloud.delete_load_balancer_target()
    elif state == "present":
        hcloud.present_load_balancer_target()

    module.exit_json(**hcloud.get_result())


if __name__ == "__main__":
    main()
