#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: hcloud_floating_ip_rdns

short_description: Create and manage reverse DNS entries on the Hetzner Cloud.


description:
    - Create, update and delete reverse DNS entries on the Hetzner Cloud.

author:
    - Lukas Kaemmerling (@lkaemmerling)

options:
    name:
        description:
            - The name of the Floating IP you want to add the reverse DNS entry to.
        type: str
        required: true
    ip_address:
        description:
            - The IP address that should point to I(dns_ptr).
        type: str
        required: true
    dns_ptr:
        description:
            - The DNS address the I(ip_address) should resolve to.
            - Omit the param to reset the reverse DNS entry to the default value.
        type: str
    state:
        description:
            - State of the reverse DNS entry.
        default: present
        choices: [ absent, present ]
        type: str

requirements:
  - hcloud-python >= 1.3.0

extends_documentation_fragment:
- hetzner.hcloud.hcloud

'''

EXAMPLES = """
- name: Create a reverse DNS entry for a server
  hcloud_floating_ip_rdns:
    name: my-ip
    ip_address: 123.123.123.123
    dns_ptr: example.com
    state: present

- name: Ensure the reverse DNS entry is absent (remove if needed)
  hcloud_floating_ip_rdns:
    name: my-ip
    ip_address: 123.123.123.123
    dns_ptr: example.com
    state: absent
"""

RETURN = """
hcloud_floating_ip_rdns:
    description: The reverse DNS entry
    returned: always
    type: complex
    contains:
        name:
            description: Name of the server
            type: str
            returned: always
            sample: my-server
        ip_address:
            description: The IP address that point to the DNS ptr
            type: str
            returned: always
            sample: 123.123.123.123
        dns_ptr:
            description: The DNS that resolves to the IP
            type: str
            returned: always
            sample: example.com
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from ansible_collections.hetzner.hcloud.plugins.module_utils.hcloud import Hcloud
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils

try:
    from hcloud import APIException
except ImportError:
    APIException = None


class AnsibleHcloudFloatingIPReverseDNS(Hcloud):
    def __init__(self, module):
        super(AnsibleHcloudFloatingIPReverseDNS, self).__init__(module, "hcloud_floating_ip_rdns")
        self.hcloud_floating_ip = None
        self.hcloud_floating_ip_rdns = None

    def _prepare_result(self):
        return {
            "name": to_native(self.hcloud_floating_ip.name),
            "ip_address": to_native(self.hcloud_floating_ip_rdns["ip_address"]),
            "dns_ptr": to_native(self.hcloud_floating_ip_rdns["dns_ptr"]),
        }

    def _get_floating_ip(self):
        try:
            self.hcloud_floating_ip = self.client.floating_ips.get_by_name(
                self.module.params.get("name")
            )
        except APIException as e:
            self.module.fail_json(msg=e.message)

    def _get_rdns(self):
        ip_address = self.module.params.get("ip_address")
        if utils.validate_ip_address(ip_address) or utils.validate_ip_v6_address(ip_address):
            for ptr in self.hcloud_floating_ip.dns_ptr:
                if ptr["ip"] == ip_address:
                    self.hcloud_floating_ip_rdns = {
                        "ip_address": ptr["ip"],
                        "dns_ptr": ptr["dns_ptr"],
                    }
        else:
            self.module.fail_json(msg="The given IP address is not valid")

    def _create_rdns(self):
        self.module.fail_on_missing_params(
            required_params=["dns_ptr"]
        )
        params = {
            "ip": self.module.params.get("ip_address"),
            "dns_ptr": self.module.params.get("dns_ptr"),
        }

        if not self.module.check_mode:
            self.client.floating_ips.change_dns_ptr(self.hcloud_floating_ip, **params).wait_until_finished()

        self._mark_as_changed()
        self._get_floating_ip()
        self._get_rdns()

    def _update_rdns(self):
        dns_ptr = self.module.params.get("dns_ptr")
        if dns_ptr != self.hcloud_floating_ip_rdns["dns_ptr"]:
            ip = self.module.params.get("ip_address")
            if not self.module.check_mode:
                self.client.floating_ips.change_dns_ptr(self.hcloud_floating_ip, ip=ip, dns_ptr=dns_ptr).wait_until_finished()

            self._mark_as_changed()
            self._get_floating_ip()
            self._get_rdns()

    def present_rdns(self):
        self._get_floating_ip()
        self._get_rdns()
        if self.hcloud_floating_ip_rdns is None:
            self._create_rdns()
        else:
            self._update_rdns()

    def delete_rdns(self):
        self._get_floating_ip()
        self._get_rdns()
        if self.hcloud_floating_ip_rdns is not None:
            if not self.module.check_mode:
                self.client.floating_ips.change_dns_ptr(self.hcloud_floating_ip, ip=self.hcloud_floating_ip_rdns['ip_address'], dns_ptr=None).wait_until_finished()
            self._mark_as_changed()
        self.hcloud_floating_ip_rdns = None

    @staticmethod
    def define_module():
        return AnsibleModule(
            argument_spec=dict(
                name={"type": "str", "required": True},
                ip_address={"type": "str", "required": True},
                dns_ptr={"type": "str"},
                state={
                    "choices": ["absent", "present"],
                    "default": "present",
                },
                **Hcloud.base_module_arguments()
            ),
            supports_check_mode=True,
        )


def main():
    module = AnsibleHcloudFloatingIPReverseDNS.define_module()

    hcloud = AnsibleHcloudFloatingIPReverseDNS(module)
    state = module.params["state"]
    if state == "absent":
        hcloud.delete_rdns()
    elif state == "present":
        hcloud.present_rdns()

    module.exit_json(**hcloud.get_result())


if __name__ == "__main__":
    main()
