#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Hetzner Cloud GmbH <info@hetzner-cloud.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: hcloud_rdns

short_description: Create and manage reverse DNS entries on the Hetzner Cloud.


description:
    - Create, update and delete reverse DNS entries on the Hetzner Cloud.

author:
    - Lukas Kaemmerling (@lkaemmerling)

options:
    server:
        description:
            - The name of the Hetzner Cloud server you want to add the reverse DNS entry to.
        type: str
    floating_ip:
        description:
            - The name of the Hetzner Cloud Floating IP you want to add the reverse DNS entry to.
        type: str
    primary_ip:
        description:
            - The name of the Hetzner Cloud Primary IP you want to add the reverse DNS entry to.
        type: str
    load_balancer:
        description:
            - The name of the Hetzner Cloud Load Balancer you want to add the reverse DNS entry to.
        type: str
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
  hcloud_rdns:
    server: my-server
    ip_address: 123.123.123.123
    dns_ptr: example.com
    state: present

- name: Create a reverse DNS entry for a Floating IP
  hcloud_rdns:
    floating_ip: my-floating-ip
    ip_address: 123.123.123.123
    dns_ptr: example.com
    state: present

- name: Create a reverse DNS entry for a Primary IP
  hcloud_rdns:
    primary_ip: my-primary-ip
    ip_address: 123.123.123.123
    dns_ptr: example.com
    state: present

- name: Create a reverse DNS entry for a Load Balancer
  hcloud_rdns:
    load_balancer: my-load-balancer
    ip_address: 123.123.123.123
    dns_ptr: example.com
    state: present

- name: Ensure the reverse DNS entry is absent (remove if needed)
  hcloud_rdns:
    server: my-server
    ip_address: 123.123.123.123
    dns_ptr: example.com
    state: absent
"""

RETURN = """
hcloud_rdns:
    description: The reverse DNS entry
    returned: always
    type: complex
    contains:
        server:
            description: Name of the server
            type: str
            returned: always
            sample: my-server
        floating_ip:
            description: Name of the Floating IP
            type: str
            returned: always
            sample: my-floating-ip
        primary_ip:
            description: Name of the Primary IP
            type: str
            returned: always
            sample: my-primary-ip
        load_balancer:
            description: Name of the Load Balancer
            type: str
            returned: always
            sample: my-load-balancer
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


class AnsibleHcloudReverseDNS(Hcloud):
    def __init__(self, module):
        Hcloud.__init__(self, module, "hcloud_rdns")
        self.hcloud_resource = None
        self.hcloud_rdns = None

    def _prepare_result(self):
        result = {
            "server": None,
            "floating_ip": None,
            "load_balancer": None,
            "ip_address": to_native(self.hcloud_rdns["ip_address"]),
            "dns_ptr": to_native(self.hcloud_rdns["dns_ptr"]),
        }

        if self.module.params.get("server"):
            result["server"] = to_native(self.hcloud_resource.name)
        elif self.module.params.get("floating_ip"):
            result["floating_ip"] = to_native(self.hcloud_resource.name)
        elif self.module.params.get("load_balancer"):
            result["load_balancer"] = to_native(self.hcloud_resource.name)
        elif self.module.params.get("primary_ip"):
            result["primary_ip"] = to_native(self.hcloud_resource.name)
        return result

    def _get_resource(self):
        try:
            if self.module.params.get("server"):
                self.hcloud_resource = self.client.servers.get_by_name(
                    self.module.params.get("server")
                )
                if self.hcloud_resource is None:
                    self.module.fail_json(msg="The selected server does not exist")
            elif self.module.params.get("floating_ip"):
                self.hcloud_resource = self.client.floating_ips.get_by_name(
                    self.module.params.get("floating_ip")
                )
                if self.hcloud_resource is None:
                    self.module.fail_json(msg="The selected Floating IP does not exist")
            elif self.module.params.get("primary_ip"):
                self.hcloud_resource = self.client.primary_ips.get_by_name(
                    self.module.params.get("primary_ip")
                )
                if self.hcloud_resource is None:
                    self.module.fail_json(msg="The selected Floating IP does not exist")
            elif self.module.params.get("load_balancer"):
                self.hcloud_resource = self.client.load_balancers.get_by_name(
                    self.module.params.get("load_balancer")
                )
                if self.hcloud_resource is None:
                    self.module.fail_json(msg="The selected Load Balancer does not exist")
        except Exception as e:
            self.module.fail_json(msg=e.message)

    def _get_rdns(self):
        ip_address = self.module.params.get("ip_address")
        if utils.validate_ip_address(ip_address):
            if self.module.params.get("server"):
                if self.hcloud_resource.public_net.ipv4.ip == ip_address:
                    self.hcloud_rdns = {
                        "ip_address": self.hcloud_resource.public_net.ipv4.ip,
                        "dns_ptr": self.hcloud_resource.public_net.ipv4.dns_ptr,
                    }
                else:
                    self.module.fail_json(msg="The selected server does not have this IP address")
            elif self.module.params.get("floating_ip"):
                if self.hcloud_resource.ip == ip_address:
                    self.hcloud_rdns = {
                        "ip_address": self.hcloud_resource.ip,
                        "dns_ptr": self.hcloud_resource.dns_ptr[0]["dns_ptr"],
                    }
                else:
                    self.module.fail_json(msg="The selected Floating IP does not have this IP address")
            elif self.module.params.get("primary_ip"):
                if self.hcloud_resource.ip == ip_address:
                    self.hcloud_rdns = {
                        "ip_address": self.hcloud_resource.ip,
                        "dns_ptr": self.hcloud_resource.dns_ptr[0]["dns_ptr"],
                    }
                else:
                    self.module.fail_json(msg="The selected Primary IP does not have this IP address")
            elif self.module.params.get("load_balancer"):
                if self.hcloud_resource.public_net.ipv4.ip == ip_address:
                    self.hcloud_rdns = {
                        "ip_address": self.hcloud_resource.public_net.ipv4.ip,
                        "dns_ptr": self.hcloud_resource.public_net.ipv4.dns_ptr,
                    }
                else:
                    self.module.fail_json(msg="The selected Load Balancer does not have this IP address")

        elif utils.validate_ip_v6_address(ip_address):
            if self.module.params.get("server"):
                for ipv6_address_dns_ptr in self.hcloud_resource.public_net.ipv6.dns_ptr:
                    if ipv6_address_dns_ptr["ip"] == ip_address:
                        self.hcloud_rdns = {
                            "ip_address": ipv6_address_dns_ptr["ip"],
                            "dns_ptr": ipv6_address_dns_ptr["dns_ptr"],
                        }
            elif self.module.params.get("floating_ip"):
                for ipv6_address_dns_ptr in self.hcloud_resource.dns_ptr:
                    if ipv6_address_dns_ptr["ip"] == ip_address:
                        self.hcloud_rdns = {
                            "ip_address": ipv6_address_dns_ptr["ip"],
                            "dns_ptr": ipv6_address_dns_ptr["dns_ptr"],
                        }
            elif self.module.params.get("primary_ip"):
                for ipv6_address_dns_ptr in self.hcloud_resource.dns_ptr:
                    if ipv6_address_dns_ptr["ip"] == ip_address:
                        self.hcloud_rdns = {
                            "ip_address": ipv6_address_dns_ptr["ip"],
                            "dns_ptr": ipv6_address_dns_ptr["dns_ptr"],
                        }
            elif self.module.params.get("load_balancer"):
                for ipv6_address_dns_ptr in self.hcloud_resource.public_net.ipv6.dns_ptr:
                    if ipv6_address_dns_ptr["ip"] == ip_address:
                        self.hcloud_rdns = {
                            "ip_address": ipv6_address_dns_ptr["ip"],
                            "dns_ptr": ipv6_address_dns_ptr["dns_ptr"],
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
            try:
                self.hcloud_resource.change_dns_ptr(**params).wait_until_finished()
            except Exception as e:
                self.module.fail_json(msg=e.message)
        self._mark_as_changed()
        self._get_resource()
        self._get_rdns()

    def _update_rdns(self):
        dns_ptr = self.module.params.get("dns_ptr")
        if dns_ptr != self.hcloud_rdns["dns_ptr"]:
            params = {
                "ip": self.module.params.get("ip_address"),
                "dns_ptr": dns_ptr,
            }

            if not self.module.check_mode:
                try:
                    self.hcloud_resource.change_dns_ptr(**params).wait_until_finished()
                except Exception as e:
                    self.module.fail_json(msg=e.message)
            self._mark_as_changed()
            self._get_resource()
            self._get_rdns()

    def present_rdns(self):
        self._get_resource()
        self._get_rdns()
        if self.hcloud_rdns is None:
            self._create_rdns()
        else:
            self._update_rdns()

    def delete_rdns(self):
        self._get_resource()
        self._get_rdns()
        if self.hcloud_rdns is not None:
            if not self.module.check_mode:
                try:
                    self.hcloud_resource.change_dns_ptr(ip=self.hcloud_rdns['ip_address'], dns_ptr=None)
                except Exception as e:
                    self.module.fail_json(msg=e.message)
            self._mark_as_changed()
        self.hcloud_rdns = None

    @staticmethod
    def define_module():
        return AnsibleModule(
            argument_spec=dict(
                server={"type": "str"},
                floating_ip={"type": "str"},
                load_balancer={"type": "str"},
                primary_ip={"type": "str"},
                ip_address={"type": "str", "required": True},
                dns_ptr={"type": "str"},
                state={
                    "choices": ["absent", "present"],
                    "default": "present",
                },
                **Hcloud.base_module_arguments()
            ),
            required_one_of=[['server', 'floating_ip', 'load_balancer', 'primary_ip']],
            mutually_exclusive=[["server", "floating_ip", 'load_balancer', 'primary_ip']],
            supports_check_mode=True,
        )


def main():
    module = AnsibleHcloudReverseDNS.define_module()

    hcloud = AnsibleHcloudReverseDNS(module)
    state = module.params["state"]
    if state == "absent":
        hcloud.delete_rdns()
    elif state == "present":
        hcloud.present_rdns()

    module.exit_json(**hcloud.get_result())


if __name__ == "__main__":
    main()
