#!/usr/bin/python

# Copyright: (c) 2022, Hetzner Cloud GmbH <info@hetzner-cloud.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import annotations

DOCUMENTATION = """
---
module: primary_ip

short_description: Create and manage cloud Primary IPs on the Hetzner Cloud.


description:
    - Create, update and manage cloud Primary IPs on the Hetzner Cloud.
    - To manage the DNS pointer of a Primary IP, use the M(hetzner.hcloud.rdns) module.

author:
    - Lukas Kaemmerling (@lkaemmerling)
version_added: 1.8.0
options:
    id:
        description:
            - The ID of the Hetzner Cloud Primary IPs to manage.
            - Only required if no Primary IP O(name) is given.
        type: int
    name:
        description:
            - The Name of the Hetzner Cloud Primary IPs to manage.
            - Only required if no Primary IP O(id) is given or a Primary IP does not exist.
        type: str
    location:
        description:
            - ID or name of the Location the Hetzner Cloud Primary IP will be bound to.
            - Required if no O(server) or O(datacenter) is given and Primary IP does not exist.
        type: str
    datacenter:
        description:
            - B(Deprecated:) The O(datacenter) argument is deprecated and will be removed
              after 1 July 2026. Please use the O(location) argument instead.
              See https://docs.hetzner.cloud/changelog#2025-12-16-phasing-out-datacenters.
            - Home Location of the Hetzner Cloud Primary IP.
            - Required if no O(server) or O(location) is given and Primary IP does not exist.
        type: str
    server:
        description:
            - Name or ID of the Hetzner Cloud Server the Primary IP should be assigned to.
            - The Primary IP cannot be assigned to a running server.
            - Required if no O(datacenter) is given and the Primary IP does not exist.
            - Use C(null) to unassign the Primary IP from the server.
        type: str
    type:
        description:
            - Type of the Primary IP.
            - Required if Primary IP does not exist
        choices: [ ipv4, ipv6 ]
        type: str
    auto_delete:
        description:
            - Delete the Primary IP when the resource it is assigned to is deleted.
        type: bool
        default: false
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

extends_documentation_fragment:
- hetzner.hcloud.hcloud
"""

EXAMPLES = """
- name: Create a IPv4 Primary IP
  hetzner.hcloud.primary_ip:
    name: my-primary-ip
    location: fsn1
    type: ipv4
    state: present

- name: Create a IPv6 Primary IP
  hetzner.hcloud.primary_ip:
    name: my-primary-ip
    location: fsn1
    type: ipv6
    state: present

- name: Delete a Primary IP
  hetzner.hcloud.primary_ip:
    name: my-primary-ip
    state: absent

- name: Ensure the server is stopped
  hetzner.hcloud.server:
    name: my-server
    state: stopped
- name: Create a Primary IP attached to a Server
  hetzner.hcloud.primary_ip:
    name: my-primary-ip
    server: my-server
    type: ipv4
    state: present
- name: Ensure the server is started
  hetzner.hcloud.server:
    name: my-server
    state: started

- name: Unassign a Primary IP from a Server
  hetzner.hcloud.primary_ip:
    name: my-primary-ip
    type: ipv4
    server: null
    state: present
"""

RETURN = """
hcloud_primary_ip:
    description: The Primary IP instance
    returned: Always
    type: dict
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
        location:
            description: Name of the Location of the Primary IP
            type: str
            returned: Always
            sample: fsn1
        datacenter:
            description: |
                Name of the datacenter of the Primary IP

                B(Deprecated:) The RV(hcloud_primary_ip.datacenter) value is deprecated and will be removed
                after 1 July 2026. Please use the RV(hcloud_primary_ip.location) value instead.
                See https://docs.hetzner.cloud/changelog#2025-12-16-phasing-out-datacenters.
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
        assignee_id:
            description: ID of the resource the Primary IP is assigned to, null if it is not assigned.
            type: int
            returned: always
            sample: 1937415
        assignee_type:
            description: Resource type the Primary IP can be assigned to.
            type: str
            returned: always
            sample: server
        auto_delete:
            description: Delete the Primary IP when the resource it is assigned to is deleted.
            type: bool
            returned: always
            sample: false
"""

from typing import TYPE_CHECKING

from ..module_utils import _primary_ip
from ..module_utils._base import AnsibleHCloud, AnsibleModule
from ..module_utils._vendor.hcloud import HCloudException
from ..module_utils._vendor.hcloud.primary_ips import BoundPrimaryIP

if TYPE_CHECKING:
    from ..module_utils._vendor.hcloud.servers import BoundServer


class AnsiblePrimaryIP(AnsibleHCloud):
    represent = "primary_ip"

    primary_ip: BoundPrimaryIP | None = None

    def _prepare_result(self):
        if self.primary_ip is None:
            return {}
        return _primary_ip.prepare_result(self.primary_ip)

    def _get(self):
        if (value := self.module.params.get("id")) is not None:
            self.primary_ip = self.client.primary_ips.get_by_id(value)
        elif (value := self.module.params.get("name")) is not None:
            self.primary_ip = self.client.primary_ips.get_by_name(value)

    def _create(self):
        self.fail_on_invalid_params(
            required=["name", "type"],
            required_one_of=[["server", "location", "datacenter"]],
        )
        params = {
            "name": self.module.params.get("name"),
            "type": self.module.params.get("type"),
        }

        if (value := self.module.params.get("location")) is not None:
            params["location"] = self._client_get_by_name_or_id("locations", value)
        elif (value := self.module.params.get("datacenter")) is not None:
            self.module.warn(
                "The `datacenter` argument is deprecated and will be removed "
                "after 1 July 2026. Please use the `location` argument instead. "
                "See https://docs.hetzner.cloud/changelog#2025-12-16-phasing-out-datacenters."
            )
            # Backward compatible datacenter argument.
            # datacenter hel1-dc2 => location hel1
            # pylint: disable=disallowed-name
            part1, _, _ = str(value).partition("-")
            params["location"] = self.client.locations.get_by_name(part1)
        elif (value := self.module.params.get("server")) is not None:
            server: BoundServer = self._client_get_by_name_or_id("servers", value)
            params["assignee_id"] = server.id

        if (value := self.module.params.get("auto_delete")) is not None:
            params["auto_delete"] = value

        if (value := self.module.params.get("labels")) is not None:
            params["labels"] = value

        if not self.module.check_mode:
            resp = self.client.primary_ips.create(**params)
            if resp.action is not None:
                resp.action.wait_until_finished()
            self.primary_ip = resp.primary_ip
        self._mark_as_changed()

        if (value := self.module.params.get("delete_protection")) is not None:
            if not self.module.check_mode:
                action = self.primary_ip.change_protection(delete=value)
                action.wait_until_finished()
            self._mark_as_changed()

        if not self.module.check_mode:
            self.primary_ip.reload()

    def _update(self):
        need_reload = False

        if (value := self.module.params.get("delete_protection")) is not None:
            if value != self.primary_ip.protection["delete"]:
                if not self.module.check_mode:
                    action = self.primary_ip.change_protection(delete=value)
                    action.wait_until_finished()
                    need_reload = True
                self._mark_as_changed()

        if self.module.param_is_defined("server"):
            if (value := self.module.params.get("server")) is not None:
                server: BoundServer = self._client_get_by_name_or_id("servers", value)

                if self.primary_ip.assignee_id is None or self.primary_ip.assignee_id != server.id:
                    if self.primary_ip.assignee_id is not None:
                        if not self.module.check_mode:
                            action = self.primary_ip.unassign()
                            action.wait_until_finished()
                            need_reload = True
                        self._mark_as_changed()

                    if not self.module.check_mode:
                        action = self.primary_ip.assign(server.id, "server")
                        action.wait_until_finished()
                        need_reload = True
                    self._mark_as_changed()
            else:
                if self.primary_ip.assignee_id is not None:
                    if not self.module.check_mode:
                        action = self.primary_ip.unassign()
                        action.wait_until_finished()
                        need_reload = True
                    self._mark_as_changed()

        params = {}

        if (value := self.module.params.get("auto_delete")) is not None:
            if value != self.primary_ip.auto_delete:
                params["auto_delete"] = value
                self._mark_as_changed()

        if (value := self.module.params.get("labels")) is not None:
            if value != self.primary_ip.labels:
                params["labels"] = value
                self._mark_as_changed()

        if params or need_reload:
            if not self.module.check_mode:
                self.primary_ip = self.primary_ip.update(**params)

    def _delete(self):
        if self.primary_ip.assignee_id is not None:
            if not self.module.check_mode:
                action = self.primary_ip.unassign()
                action.wait_until_finished()
            self._mark_as_changed()

        if not self.module.check_mode:
            self.primary_ip.delete()
        self.primary_ip = None
        self._mark_as_changed()

    def present(self):
        try:
            self._get()
            if self.primary_ip is None:
                self._create()
            else:
                self._update()
        except HCloudException as exception:
            self.fail_json_hcloud(exception)

    def delete(self):
        try:
            self._get()
            if self.primary_ip is not None:
                self._delete()
        except HCloudException as exception:
            self.fail_json_hcloud(exception)

    @classmethod
    def define_module(cls):
        return AnsibleModule(
            argument_spec=dict(
                id={"type": "int"},
                name={"type": "str"},
                location={"type": "str"},
                datacenter={
                    "type": "str",
                    "removed_at_date": "2026-07-01",
                    "removed_from_collection": "hetzner.hcloud",
                },
                server={"type": "str"},
                auto_delete={"type": "bool", "default": False},
                type={"choices": ["ipv4", "ipv6"]},
                labels={"type": "dict"},
                delete_protection={"type": "bool"},
                state={
                    "choices": ["absent", "present"],
                    "default": "present",
                },
                **super().base_module_arguments(),
            ),
            required_one_of=[["id", "name"]],
            supports_check_mode=True,
        )


def main():
    o = AnsiblePrimaryIP(AnsiblePrimaryIP.define_module())

    match o.module.params["state"]:
        case "absent":
            o.delete()
        case "present":
            o.present()

    result = o.get_result()
    result["hcloud_primary_ip"] = result.pop(o.represent)

    o.module.exit_json(**result)


if __name__ == "__main__":
    main()
