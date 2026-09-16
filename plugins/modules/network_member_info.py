#!/usr/bin/python

# Copyright: (c) 2026, Hetzner Cloud GmbH <info@hetzner-cloud.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import annotations

DOCUMENTATION = """
---
module: network_member_info

short_description: Gather info about your Hetzner Cloud Network Members.

description:
    - Gather info about your Hetzner Cloud Network Members.

author:
    - Jonas Lammler (@jooola)

options:
    network:
        description:
            - ID or Name of the Network to list the members of.
            - Using the ID is preferred, to reduce the amount of API requests.
        type: str
        required: true
    type:
        description:
            - Filter members by type. May be used multiple times.
        type: list
        elements: str
        choices: [server, load_balancer]
    status:
        description:
            - Filter members by status. May be used multiple times.
        type: list
        elements: str
        choices: [ok, attaching, detaching, updating, error]
    subnet:
        description:
            - Filter members by subnet. May be used multiple times.
        type: list
        elements: str

extends_documentation_fragment:
    - hetzner.hcloud.hcloud
"""

EXAMPLES = """
- name: Gather Network Member infos
  hetzner.hcloud.network_member_info:
    type: [server, load_balancer]
    status: [ok, attaching, detaching, updating, error]
    subnet: [10.0.1.0/24]
  register: output

- name: Print the gathered infos
  debug:
    var: output.hcloud_network_member_info
"""

RETURN = """
hcloud_network_member_info:
    description: Network Members infos as list.
    returned: always
    type: list
    contains:
        id:
            description: ID of the Resource attached to the Network.
            returned: always
            type: int
            sample: 1937415
        type:
            description: Type of the Resource attached to the Network.
            returned: always
            type: str
            sample: server
        ip:
            description: IP address of the Resource within the Network.
            returned: always
            type: str
            sample: 10.0.1.2
        alias_ips:
            description: Additional IP addresses of the Resource within the Network.
            returned: always
            type: list
            elements: str
            sample: [10.0.1.4, 10.0.1.7]
        subnet:
            description: IP range of the subnet the Resource is attached to.
            returned: always
            type: str
            sample: 10.0.1.0/24
        status:
            description: Status of the Resource within the Network.
            returned: always
            type: str
            sample: ok
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import _network, _network_member
from ..module_utils._base import AnsibleHCloud
from ..module_utils._vendor.hcloud import HCloudException
from ..module_utils._vendor.hcloud.networks import BoundNetwork, NetworkMember


class AnsibleNetworkMemberInfo(AnsibleHCloud):
    represent = "network_members"

    network: BoundNetwork | None = None
    network_members: list[NetworkMember] | None = None

    def _prepare_result(self):
        result = []

        for o in self.network_members or []:
            if o is not None:
                result.append(_network_member.prepare_result(o))
        return result

    def fetch(self):
        try:
            self.network = _network.get(
                self.client.networks,
                self.module.params.get("network"),
            )

            params = {}
            if (value := self.module.params.get("type")) is not None:
                params["type"] = value
            if (value := self.module.params.get("status")) is not None:
                params["status"] = value
            if (value := self.module.params.get("subnet")) is not None:
                params["status"] = value

            self.network_members = self.network.get_member_all(**params)

        except HCloudException as exception:
            self.fail_json_hcloud(exception)

    @classmethod
    def define_module(cls):
        return AnsibleModule(
            argument_spec=dict(
                network={"type": "str", "required": True},
                type={
                    "type": "list",
                    "elements": "str",
                    "choices": ["server", "load_balancer"],
                },
                status={
                    "type": "list",
                    "elements": "str",
                    "choices": ["ok", "attaching", "detaching", "updating", "error"],
                },
                subnet={
                    "type": "list",
                    "elements": "str",
                },
                **super().base_module_arguments(),
            ),
            supports_check_mode=True,
        )


def main():
    module = AnsibleNetworkMemberInfo.define_module()
    o = AnsibleNetworkMemberInfo(module)

    o.fetch()
    result = o.get_result()

    # Legacy return value naming pattern
    result["hcloud_network_member_info"] = result.pop(o.represent)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
