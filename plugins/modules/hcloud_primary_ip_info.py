#!/usr/bin/python

# Copyright: (c) 2019, Hetzner Cloud GmbH <info@hetzner-cloud.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = """
---
module: hcloud_primary_ip_info

short_description: Gather infos about the Hetzner Cloud Primary IPs.

description:
    - Gather facts about your Hetzner Cloud Primary IPs.

author:
    - Lukas Kaemmerling (@LKaemmerling)
    - Kevin Castner (@kcastner)

options:
    id:
        description:
            - The ID of the Primary IP you want to get.
        type: int
    name:
        description:
            - The name for the Primary IP you want to get.
        type: str
    label_selector:
        description:
            - The label selector for the Primary IP you want to get.
        type: str
extends_documentation_fragment:
- hetzner.hcloud.hcloud

"""

EXAMPLES = """
- name: Gather hcloud Primary IP infos
  hcloud_primary_ip_info:
  register: output

- name: Gather hcloud Primary IP infos by id
  hcloud_primary_ip_info:
    id: 673954
  register: output

- name: Gather hcloud Primary IP infos by name
  hcloud_primary_ip_info:
    name: srv1-v4
  register: output

- name: Gather hcloud Primary IP infos by label
  hcloud_primary_ip_info:
    label_selector: srv03-ips
  register: output

- name: Print the gathered infos
  debug:
    var: output

"""

RETURN = """
hcloud_primary_ip_info:
    description: The Primary IP infos as list
    returned: always
    type: complex
    contains:
        id:
            description: Numeric identifier of the Primary IP
            returned: always
            type: int
            sample: 1937415
        name:
            description: Name of the Primary IP
            returned: always
            type: str
            sample: my-primary-ip
        ip:
            description: IP address of the Primary IP
            returned: always
            type: str
            sample: 131.232.99.1
        type:
            description: Type of the Primary IP
            returned: always
            type: str
            sample: ipv4
        assignee_id:
            description: Numeric identifier of the ressource where the Primary IP is assigned to.
            returned: always
            type: int
            sample: 19584637
        assignee_type:
            description: Name of the type where the Primary IP is assigned to.
            returned: always
            type: str
            sample: server
        home_location:
            description: Location with datacenter where the Primary IP was created in
            returned: always
            type: str
            sample: fsn1-dc1
        dns_ptr:
            description: Shows the DNS PTR Record for Primary IP.
            returned: always
            type: str
            sample: srv01.example.com
        labels:
            description: User-defined labels (key-value pairs)
            returned: always
            type: dict
        delete_protection:
            description: True if the Primary IP is protected for deletion
            returned: always
            type: bool
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native
from ansible_collections.hetzner.hcloud.plugins.module_utils.hcloud import Hcloud


class AnsibleHcloudPrimaryIPInfo(Hcloud):
    def __init__(self, module):
        Hcloud.__init__(self, module, "hcloud_primary_ip_info")
        self.hcloud_primary_ip_info = None

    def _prepare_result(self):
        tmp = []

        for primary_ip in self.hcloud_primary_ip_info:
            if primary_ip is not None:
                dns_ptr = None
                if len(primary_ip.dns_ptr) > 0:
                    dns_ptr = primary_ip.dns_ptr[0]["dns_ptr"]
                tmp.append(
                    {
                        "id": to_native(primary_ip.id),
                        "name": to_native(primary_ip.name),
                        "ip": to_native(primary_ip.ip),
                        "type": to_native(primary_ip.type),
                        "assignee_id": (
                            to_native(primary_ip.assignee_id) if primary_ip.assignee_id is not None else None
                        ),
                        "assignee_type": to_native(primary_ip.assignee_type),
                        "home_location": to_native(primary_ip.datacenter.name),
                        "dns_ptr": to_native(dns_ptr) if dns_ptr is not None else None,
                        "labels": primary_ip.labels,
                        "delete_protection": primary_ip.protection["delete"],
                    }
                )

        return tmp

    def get_primary_ips(self):
        try:
            if self.module.params.get("id") is not None:
                self.hcloud_primary_ip_info = [self.client.primary_ips.get_by_id(self.module.params.get("id"))]
            elif self.module.params.get("name") is not None:
                self.hcloud_primary_ip_info = [self.client.primary_ips.get_by_name(self.module.params.get("name"))]
            elif self.module.params.get("label_selector") is not None:
                self.hcloud_primary_ip_info = self.client.primary_ips.get_all(
                    label_selector=self.module.params.get("label_selector")
                )
            else:
                self.hcloud_primary_ip_info = self.client.primary_ips.get_all()

        except Exception as e:
            self.module.fail_json(msg=e.message)

    @staticmethod
    def define_module():
        return AnsibleModule(
            argument_spec=dict(
                id={"type": "int"},
                label_selector={"type": "str"},
                name={"type": "str"},
                **Hcloud.base_module_arguments()
            ),
            supports_check_mode=True,
        )


def main():
    module = AnsibleHcloudPrimaryIPInfo.define_module()

    hcloud = AnsibleHcloudPrimaryIPInfo(module)

    hcloud.get_primary_ips()
    result = hcloud.get_result()

    ansible_info = {"hcloud_primary_ip_info": result["hcloud_primary_ip_info"]}
    module.exit_json(**ansible_info)


if __name__ == "__main__":
    main()
