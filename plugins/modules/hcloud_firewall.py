#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Hetzner Cloud GmbH <info@hetzner-cloud.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: hcloud_firewall

short_description: Create and manage firewalls on the Hetzner Cloud.


description:
    - Create, update and manage firewalls on the Hetzner Cloud.

author:
    - Lukas Kaemmerling (@lkaemmerling)

options:
    id:
        description:
            - The ID of the Hetzner Cloud firewall to manage.
            - Only required if no firewall I(name) is given
        type: int
    name:
        description:
            - The Name of the Hetzner Cloud firewall to manage.
            - Only required if no firewall I(id) is given, or a firewall does not exist.
        type: str
    labels:
        description:
            - User-defined labels (key-value pairs)
        type: dict
    rules:
        description:
            - List of rules the firewall should contain.
        type: list
        elements: dict
        suboptions:
            direction:
                description:
                    - The direction of the firewall rule.
                type: str
                choices: [ in, out ]
            port:
                description:
                    - The port of the firewall rule.
                type: str
            protocol:
                description:
                    - The protocol of the firewall rule.
                type: str
                choices: [ icmp, tcp, udp, esp, gre ]
            source_ips:
                description:
                    - List of CIDRs that are allowed within this rule
                type: list
                elements: str
                default: [ ]
            destination_ips:
                description:
                    - List of CIDRs that are allowed within this rule
                type: list
                elements: str
                default: [ ]
            description:
                description:
                    - User defined description of this rule.
                type: str
    state:
        description:
            - State of the firewall.
        default: present
        choices: [ absent, present ]
        type: str
extends_documentation_fragment:
- hetzner.hcloud.hcloud
'''

EXAMPLES = """
- name: Create a basic firewall
  hcloud_firewall:
    name: my-firewall
    state: present

- name: Create a firewall with rules
  hcloud_firewall:
    name: my-firewall
    rules:
       - direction: in
         protocol: icmp
         source_ips:
           - 0.0.0.0/0
           - ::/0
         description: allow icmp in
    state: present

- name: Create a firewall with labels
  hcloud_firewall:
    name: my-firewall
    labels:
        key: value
        mylabel: 123
    state: present

- name: Ensure the firewall is absent (remove if needed)
  hcloud_firewall:
    name: my-firewall
    state: absent
"""

RETURN = """
hcloud_firewall:
    description: The firewall instance
    returned: Always
    type: complex
    contains:
        id:
            description: Numeric identifier of the firewall
            returned: always
            type: int
            sample: 1937415
        name:
            description: Name of the firewall
            returned: always
            type: str
            sample: my firewall
        rules:
            description: List of Rules within this Firewall
            returned: always
            type: complex
            contains:
                direction:
                    description: Direction of the Firewall Rule
                    type: str
                    returned: always
                    sample: in
                protocol:
                    description: Protocol of the Firewall Rule
                    type: str
                    returned: always
                    sample: icmp
                port:
                    description: Port of the Firewall Rule, None/Null if protocol is icmp
                    type: str
                    returned: always
                    sample: in
                source_ips:
                    description: Source IPs of the Firewall
                    type: list
                    elements: str
                    returned: always
                destination_ips:
                    description: Source IPs of the Firewall
                    type: list
                    elements: str
                    returned: always
                description:
                    description: User defined description of the Firewall Rule
                    type: str
                    returned: always
        labels:
            description: User-defined labels (key-value pairs)
            returned: always
            type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from ansible_collections.hetzner.hcloud.plugins.module_utils.hcloud import Hcloud
import time

try:
    from hcloud.firewalls.domain import FirewallRule
    from hcloud import APIException
except ImportError:
    APIException = None
    FirewallRule = None


class AnsibleHcloudFirewall(Hcloud):
    def __init__(self, module):
        Hcloud.__init__(self, module, "hcloud_firewall")
        self.hcloud_firewall = None

    def _prepare_result(self):
        return {
            "id": to_native(self.hcloud_firewall.id),
            "name": to_native(self.hcloud_firewall.name),
            "rules": [self._prepare_result_rule(rule) for rule in self.hcloud_firewall.rules],
            "labels": self.hcloud_firewall.labels
        }

    def _prepare_result_rule(self, rule):
        return {
            "direction": rule.direction,
            "protocol": to_native(rule.protocol),
            "port": to_native(rule.port) if rule.port is not None else None,
            "source_ips": [to_native(cidr) for cidr in rule.source_ips],
            "destination_ips": [to_native(cidr) for cidr in rule.destination_ips],
            "description": to_native(rule.description) if rule.description is not None else None,
        }

    def _get_firewall(self):
        try:
            if self.module.params.get("id") is not None:
                self.hcloud_firewall = self.client.firewalls.get_by_id(
                    self.module.params.get("id")
                )
            elif self.module.params.get("name") is not None:
                self.hcloud_firewall = self.client.firewalls.get_by_name(
                    self.module.params.get("name")
                )

        except Exception as e:
            self.module.fail_json(msg=e.message)

    def _create_firewall(self):
        self.module.fail_on_missing_params(
            required_params=["name"]
        )
        params = {
            "name": self.module.params.get("name"),
            "labels": self.module.params.get("labels")
        }
        rules = self.module.params.get("rules")
        if rules is not None:
            params["rules"] = [
                FirewallRule(
                    direction=rule["direction"],
                    protocol=rule["protocol"],
                    source_ips=rule["source_ips"] if rule["source_ips"] is not None else [],
                    destination_ips=rule["destination_ips"] if rule["destination_ips"] is not None else [],
                    port=rule["port"],
                    description=rule["description"],
                )
                for rule in rules
            ]
        if not self.module.check_mode:
            try:
                self.client.firewalls.create(**params)
            except Exception as e:
                self.module.fail_json(msg=e.message, **params)
        self._mark_as_changed()
        self._get_firewall()

    def _update_firewall(self):
        name = self.module.params.get("name")
        if name is not None and self.hcloud_firewall.name != name:
            self.module.fail_on_missing_params(
                required_params=["id"]
            )
            if not self.module.check_mode:
                self.hcloud_firewall.update(name=name)
            self._mark_as_changed()

        labels = self.module.params.get("labels")
        if labels is not None and self.hcloud_firewall.labels != labels:
            if not self.module.check_mode:
                self.hcloud_firewall.update(labels=labels)
            self._mark_as_changed()

        rules = self.module.params.get("rules")
        if rules is not None and rules != [self._prepare_result_rule(rule) for rule in self.hcloud_firewall.rules]:
            if not self.module.check_mode:
                new_rules = [
                    FirewallRule(
                        direction=rule["direction"],
                        protocol=rule["protocol"],
                        source_ips=rule["source_ips"] if rule["source_ips"] is not None else [],
                        destination_ips=rule["destination_ips"] if rule["destination_ips"] is not None else [],
                        port=rule["port"],
                        description=rule["description"],
                    )
                    for rule in rules
                ]
                self.hcloud_firewall.set_rules(new_rules)
            self._mark_as_changed()
        self._get_firewall()

    def present_firewall(self):
        self._get_firewall()
        if self.hcloud_firewall is None:
            self._create_firewall()
        else:
            self._update_firewall()

    def delete_firewall(self):
        self._get_firewall()
        if self.hcloud_firewall is not None:
            if not self.module.check_mode:
                retry_count = 0
                while retry_count < 10:
                    try:
                        self.client.firewalls.delete(self.hcloud_firewall)
                        break
                    except APIException as e:
                        if "is still in use" in e.message:
                            retry_count = retry_count + 1
                            time.sleep(0.5 * retry_count)
                        else:
                            self.module.fail_json(msg=e.message)
                    except Exception as e:
                        self.module.fail_json(msg=e.message)
            self._mark_as_changed()
        self.hcloud_firewall = None

    @staticmethod
    def define_module():
        return AnsibleModule(
            argument_spec=dict(
                id={"type": "int"},
                name={"type": "str"},
                rules=dict(
                    type="list",
                    elements="dict",
                    options=dict(
                        direction={"type": "str", "choices": ["in", "out"]},
                        protocol={"type": "str", "choices": ["icmp", "udp", "tcp", "esp", "gre"]},
                        port={"type": "str"},
                        source_ips={"type": "list", "elements": "str", "default": []},
                        destination_ips={"type": "list", "elements": "str", "default": []},
                        description={"type": "str"},
                    ),
                    required_together=[["direction", "protocol"]],
                ),
                labels={"type": "dict"},
                state={
                    "choices": ["absent", "present"],
                    "default": "present",
                },
                **Hcloud.base_module_arguments()
            ),
            required_one_of=[['id', 'name']],
            required_if=[['state', 'present', ['name']]],
            supports_check_mode=True,
        )


def main():
    module = AnsibleHcloudFirewall.define_module()

    hcloud = AnsibleHcloudFirewall(module)
    state = module.params.get("state")
    if state == "absent":
        hcloud.delete_firewall()
    elif state == "present":
        hcloud.present_firewall()

    module.exit_json(**hcloud.get_result())


if __name__ == "__main__":
    main()
