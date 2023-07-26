#!/usr/bin/python

# Copyright: (c) 2019, Hetzner Cloud GmbH <info@hetzner-cloud.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = """
---
module: hcloud_floating_ip_info

short_description: Gather infos about the Hetzner Cloud Floating IPs.

description:
    - Gather facts about your Hetzner Cloud Floating IPs.

author:
    - Lukas Kaemmerling (@LKaemmerling)

options:
    id:
        description:
            - The ID of the Floating IP you want to get.
        type: int
    label_selector:
        description:
            - The label selector for the Floating IP you want to get.
        type: str
extends_documentation_fragment:
- hetzner.hcloud.hcloud

"""

EXAMPLES = """
- name: Gather hcloud Floating ip infos
  hetzner.hcloud.hcloud_floating_ip_info:
  register: output
- name: Print the gathered infos
  debug:
    var: output
"""

RETURN = """
hcloud_floating_ip_info:
    description: The Floating ip infos as list
    returned: always
    type: complex
    contains:
        id:
            description: Numeric identifier of the Floating IP
            returned: always
            type: int
            sample: 1937415
        name:
            description: Name of the Floating IP
            returned: Always
            type: str
            sample: my-floating-ip
            version_added: "0.1.0"
        description:
            description: Description of the Floating IP
            returned: always
            type: str
            sample: Falkenstein DC 8
        ip:
            description: IP address of the Floating IP
            returned: always
            type: str
            sample: 131.232.99.1
        type:
            description: Type of the Floating IP
            returned: always
            type: str
            sample: ipv4
        server:
            description: Name of the server where the Floating IP is assigned to.
            returned: always
            type: str
            sample: my-server
        home_location:
            description: Location the Floating IP was created in
            returned: always
            type: str
            sample: fsn1
        delete_protection:
            description: True if the Floating IP is protected for deletion
            returned: always
            type: bool
            version_added: "0.1.0"
        labels:
            description: User-defined labels (key-value pairs)
            returned: always
            type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native

from ..module_utils.hcloud import AnsibleHCloud
from ..module_utils.vendor.hcloud import HCloudException


class AnsibleHcloudFloatingIPInfo(AnsibleHCloud):
    def __init__(self, module):
        super().__init__(module, "hcloud_floating_ip_info")
        self.hcloud_floating_ip_info = None

    def _prepare_result(self):
        tmp = []

        for floating_ip in self.hcloud_floating_ip_info:
            if floating_ip is not None:
                server_name = None
                if floating_ip.server is not None:
                    server_name = floating_ip.server.name
                tmp.append(
                    {
                        "id": to_native(floating_ip.id),
                        "name": to_native(floating_ip.name),
                        "description": to_native(floating_ip.description),
                        "ip": to_native(floating_ip.ip),
                        "type": to_native(floating_ip.type),
                        "server": to_native(server_name),
                        "home_location": to_native(floating_ip.home_location.name),
                        "labels": floating_ip.labels,
                        "delete_protection": floating_ip.protection["delete"],
                    }
                )

        return tmp

    def get_floating_ips(self):
        try:
            if self.module.params.get("id") is not None:
                self.hcloud_floating_ip_info = [self.client.floating_ips.get_by_id(self.module.params.get("id"))]
            elif self.module.params.get("label_selector") is not None:
                self.hcloud_floating_ip_info = self.client.floating_ips.get_all(
                    label_selector=self.module.params.get("label_selector")
                )
            else:
                self.hcloud_floating_ip_info = self.client.floating_ips.get_all()

        except HCloudException as e:
            self.fail_json_hcloud(e)

    @classmethod
    def define_module(cls):
        return AnsibleModule(
            argument_spec=dict(
                id={"type": "int"},
                label_selector={"type": "str"},
                **super().base_module_arguments(),
            ),
            supports_check_mode=True,
        )


def main():
    module = AnsibleHcloudFloatingIPInfo.define_module()
    hcloud = AnsibleHcloudFloatingIPInfo(module)

    hcloud.get_floating_ips()
    result = hcloud.get_result()

    ansible_info = {"hcloud_floating_ip_info": result["hcloud_floating_ip_info"]}
    module.exit_json(**ansible_info)


if __name__ == "__main__":
    main()
