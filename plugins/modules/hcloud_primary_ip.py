#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Hetzner Cloud GmbH <info@hetzner-cloud.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: hcloud_primary_ip

short_description: Create and manage cloud Primary IPs on the Hetzner Cloud.


description:
    - Create, update and manage cloud Primary IPs on the Hetzner Cloud.

author:
    - Lukas Kaemmerling (@lkaemmerling)
version_added: 1.8.0
options:
    id:
        description:
            - The ID of the Hetzner Cloud Primary IPs to manage.
            - Only required if no Primary IP I(name) is given.
        type: int
    name:
        description:
            - The Name of the Hetzner Cloud Primary IPs to manage.
            - Only required if no Primary IP I(id) is given or a Primary IP does not exist.
        type: str
    datacenter:
        description:
            - Home Location of the Hetzner Cloud Primary IP.
            - Required if no I(server) is given and Primary IP does not exist.
        type: str
    type:
        description:
            - Type of the Primary IP.
            - Required if Primary IP does not exist
        choices: [ ipv4, ipv6 ]
        type: str
    auto_delete:
        description:
            - Delete this Primary IP when the resource it is assigned to is deleted
        type: bool
        default: no
    delete_protection:
        description:
            - Protect the Primary IP for deletion.
        type: bool
    labels:
        description:
            - User-defined labels (key-value pairs).
        type: dict
    state:
        description:
            - State of the Primary IP.
        default: present
        choices: [ absent, present ]
        type: str

requirements:
  - hcloud-python >= 1.9.0

extends_documentation_fragment:
- hetzner.hcloud.hcloud

'''

EXAMPLES = """
- name: Create a basic IPv4 Primary IP
  hcloud_primary_ip:
    name: my-primary-ip
    datacenter: fsn1-dc14
    type: ipv4
    state: present
- name: Create a basic IPv6 Primary IP
  hcloud_primary_ip:
    name: my-primary-ip
    datacenter: fsn1-dc14
    type: ipv6
    state: present
- name: Primary IP should be absent
  hcloud_primary_ip:
    name: my-primary-ip
    state: absent
"""

RETURN = """
hcloud_primary_ip:
    description: The Primary IP instance
    returned: Always
    type: complex
    contains:
        id:
            description: ID of the Primary IP
            type: int
            returned: Always
            sample: 12345
        name:
            description: Name of the Primary IP
            type: str
            returned: Always
            sample: my-primary-ip
        ip:
            description: IP Address of the Primary IP
            type: str
            returned: Always
            sample: 116.203.104.109
        type:
            description: Type of the Primary IP
            type: str
            returned: Always
            sample: ipv4
        datacenter:
            description: Name of the datacenter of the Primary IP
            type: str
            returned: Always
            sample: fsn1-dc14
        delete_protection:
            description: True if Primary IP is protected for deletion
            type: bool
            returned: always
            sample: false
        labels:
            description: User-defined labels (key-value pairs)
            type: dict
            returned: Always
            sample:
                key: value
                mylabel: 123
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from ansible_collections.hetzner.hcloud.plugins.module_utils.hcloud import Hcloud


class AnsibleHcloudPrimaryIP(Hcloud):
    def __init__(self, module):
        Hcloud.__init__(self, module, "hcloud_primary_ip")
        self.hcloud_primary_ip = None

    def _prepare_result(self):
        return {
            "id": to_native(self.hcloud_primary_ip.id),
            "name": to_native(self.hcloud_primary_ip.name),
            "ip": to_native(self.hcloud_primary_ip.ip),
            "type": to_native(self.hcloud_primary_ip.type),
            "datacenter": to_native(self.hcloud_primary_ip.datacenter.name),
            "labels": self.hcloud_primary_ip.labels,
            "delete_protection": self.hcloud_primary_ip.protection["delete"],
        }

    def _get_primary_ip(self):
        try:
            if self.module.params.get("id") is not None:
                self.hcloud_primary_ip = self.client.primary_ips.get_by_id(
                    self.module.params.get("id")
                )
            else:
                self.hcloud_primary_ip = self.client.primary_ips.get_by_name(
                    self.module.params.get("name")
                )
        except Exception as e:
            self.module.fail_json(msg=e.message)

    def _create_primary_ip(self):
        self.module.fail_on_missing_params(
            required_params=["type", "datacenter"]
        )
        try:
            params = {
                "type": self.module.params.get("type"),
                "name": self.module.params.get("name"),
                "datacenter": self.client.datacenters.get_by_name(
                    self.module.params.get("datacenter")
                )
            }

            if self.module.params.get("labels") is not None:
                params["labels"] = self.module.params.get("labels")
            if not self.module.check_mode:
                resp = self.client.primary_ips.create(**params)
                self.hcloud_primary_ip = resp.primary_ip

                delete_protection = self.module.params.get("delete_protection")
                if delete_protection is not None:
                    self.hcloud_primary_ip.change_protection(delete=delete_protection).wait_until_finished()
        except Exception as e:
            self.module.fail_json(msg=e)
        self._mark_as_changed()
        self._get_primary_ip()

    def _update_primary_ip(self):
        try:
            labels = self.module.params.get("labels")
            if labels is not None and labels != self.hcloud_primary_ip.labels:
                if not self.module.check_mode:
                    self.hcloud_primary_ip.update(labels=labels)
                self._mark_as_changed()

            delete_protection = self.module.params.get("delete_protection")
            if delete_protection is not None and delete_protection != self.hcloud_primary_ip.protection["delete"]:
                if not self.module.check_mode:
                    self.hcloud_primary_ip.change_protection(delete=delete_protection).wait_until_finished()
                self._mark_as_changed()

            self._get_primary_ip()
        except Exception as e:
            self.module.fail_json(msg=e.message)

    def present_primary_ip(self):
        self._get_primary_ip()
        if self.hcloud_primary_ip is None:
            self._create_primary_ip()
        else:
            self._update_primary_ip()

    def delete_primary_ip(self):
        try:
            self._get_primary_ip()
            if self.hcloud_primary_ip is not None:
                if not self.module.check_mode:
                    self.client.primary_ips.delete(self.hcloud_primary_ip)
                self._mark_as_changed()
            self.hcloud_primary_ip = None
        except Exception as e:
            self.module.fail_json(msg=e.message)

    @staticmethod
    def define_module():
        return AnsibleModule(
            argument_spec=dict(
                id={"type": "int"},
                name={"type": "str"},
                datacenter={"type": "str"},
                auto_delete={"type": "bool", "default": False},
                type={"choices": ["ipv4", "ipv6"]},
                labels={"type": "dict"},
                delete_protection={"type": "bool"},
                state={
                    "choices": ["absent", "present"],
                    "default": "present",
                },
                **Hcloud.base_module_arguments()
            ),
            required_one_of=[['id', 'name']],
            supports_check_mode=True,
        )


def main():
    module = AnsibleHcloudPrimaryIP.define_module()

    hcloud = AnsibleHcloudPrimaryIP(module)
    state = module.params["state"]
    if state == "absent":
        hcloud.delete_primary_ip()
    elif state == "present":
        hcloud.present_primary_ip()

    module.exit_json(**hcloud.get_result())


if __name__ == "__main__":
    main()
