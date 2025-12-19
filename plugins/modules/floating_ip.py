#!/usr/bin/python

# Copyright: (c) 2019, Hetzner Cloud GmbH <info@hetzner-cloud.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import annotations

DOCUMENTATION = """
---
module: floating_ip

short_description: Create and manage cloud Floating IPs on the Hetzner Cloud.


description:
    - Create, update and manage cloud Floating IPs on the Hetzner Cloud.
    - To manage the DNS pointer of a Floating IP, use the M(hetzner.hcloud.rdns) module.

author:
    - Lukas Kaemmerling (@lkaemmerling)
version_added: 0.1.0
options:
    id:
        description:
            - The ID of the Hetzner Cloud Floating IPs to manage.
            - Only required if no Floating IP I(name) is given.
        type: int
    name:
        description:
            - The Name of the Hetzner Cloud Floating IPs to manage.
            - Only required if no Floating IP I(id) is given or a Floating IP does not exist.
        type: str
    description:
        description:
            - The Description of the Hetzner Cloud Floating IPs.
        type: str
    home_location:
        description:
            - Home Location of the Hetzner Cloud Floating IP.
            - Required if no I(server) is given and Floating IP does not exist.
        type: str
    server:
        description:
            - Server Name the Floating IP should be assigned to.
            - Required if no I(home_location) is given and Floating IP does not exist.
        type: str
    type:
        description:
            - Type of the Floating IP.
            - Required if Floating IP does not exist
        choices: [ ipv4, ipv6 ]
        type: str
    force:
        description:
            - Force the assignment or deletion of the Floating IP.
        type: bool
    delete_protection:
        description:
            - Protect the Floating IP for deletion.
        type: bool
    labels:
        description:
            - User-defined labels (key-value pairs).
        type: dict
    state:
        description:
            - State of the Floating IP.
        default: present
        choices: [ absent, present ]
        type: str

extends_documentation_fragment:
- hetzner.hcloud.hcloud
"""

EXAMPLES = """
- name: Create a basic IPv4 Floating IP
  hetzner.hcloud.floating_ip:
    name: my-floating-ip
    home_location: fsn1
    type: ipv4
    state: present
- name: Create a basic IPv6 Floating IP
  hetzner.hcloud.floating_ip:
    name: my-floating-ip
    home_location: fsn1
    type: ipv6
    state: present
- name: Assign a Floating IP to a server
  hetzner.hcloud.floating_ip:
    name: my-floating-ip
    server: 1234
    state: present
- name: Assign a Floating IP to another server
  hetzner.hcloud.floating_ip:
    name: my-floating-ip
    server: 1234
    force: true
    state: present
- name: Floating IP should be absent
  hetzner.hcloud.floating_ip:
    name: my-floating-ip
    state: absent
"""

RETURN = """
hcloud_floating_ip:
    description: The Floating IP instance
    returned: Always
    type: dict
    contains:
        id:
            description: ID of the Floating IP
            type: int
            returned: Always
            sample: 12345
        name:
            description: Name of the Floating IP
            type: str
            returned: Always
            sample: my-floating-ip
        description:
            description: Description of the Floating IP
            type: str
            returned: Always
            sample: my-floating-ip
        ip:
            description: IP Address of the Floating IP
            type: str
            returned: Always
            sample: 116.203.104.109
        type:
            description: Type of the Floating IP
            type: str
            returned: Always
            sample: ipv4
        home_location:
            description: Name of the home location of the Floating IP
            type: str
            returned: Always
            sample: fsn1
        server:
            description: Name of the server the Floating IP is assigned to.
            type: str
            returned: Always
            sample: "my-server"
        delete_protection:
            description: True if Floating IP is protected for deletion
            type: bool
            returned: always
            sample: false
            version_added: "0.1.0"
        labels:
            description: User-defined labels (key-value pairs)
            type: dict
            returned: Always
            sample:
                key: value
                mylabel: 123
"""

from ..module_utils import _floating_ip
from ..module_utils._base import AnsibleHCloud, AnsibleModule
from ..module_utils._vendor.hcloud import HCloudException
from ..module_utils._vendor.hcloud.floating_ips import BoundFloatingIP


class AnsibleFloatingIP(AnsibleHCloud):
    represent = "floating_ip"

    floating_ip: BoundFloatingIP | None = None

    def _prepare_result(self):
        if self.floating_ip is None:
            return {}
        return _floating_ip.prepare_result(self.floating_ip)

    def _get(self):
        if (value := self.module.params.get("id")) is not None:
            self.floating_ip = self.client.floating_ips.get_by_id(value)
        elif (value := self.module.params.get("name")) is not None:
            self.floating_ip = self.client.floating_ips.get_by_name(value)

    def _create(self):
        self.fail_on_invalid_params(
            required=["name", "type"],
            required_one_of=[["home_location", "server"]],
        )

        params = {
            "name": self.module.params.get("name"),
            "type": self.module.params.get("type"),
        }

        if (value := self.module.params.get("home_location")) is not None:
            params["home_location"] = self.client.locations.get_by_name(value)
        elif (value := self.module.params.get("server")) is not None:
            params["server"] = self.client.servers.get_by_name(value)
        else:
            self.module.fail_json(msg="one of the following is required: home_location, server")

        if (value := self.module.params.get("description")) is not None:
            params["description"] = value

        if (value := self.module.params.get("labels")) is not None:
            params["labels"] = value

        if not self.module.check_mode:
            resp = self.client.floating_ips.create(**params)
            self.floating_ip = resp.floating_ip
            if resp.action is not None:
                resp.action.wait_until_finished()
        self._mark_as_changed()

        if (value := self.module.params.get("delete_protection")) is not None:
            if not self.module.check_mode:
                action = self.floating_ip.change_protection(delete=value)
                action.wait_until_finished()
            self._mark_as_changed()

        if not self.module.check_mode:
            self.floating_ip.reload()

    def _update(self):
        need_reload = False

        if (value := self.module.params.get("delete_protection")) is not None:
            if value != self.floating_ip.protection["delete"]:
                if not self.module.check_mode:
                    action = self.floating_ip.change_protection(delete=value)
                    action.wait_until_finished()
                    need_reload = True
                self._mark_as_changed()

        if (value := self.module.params.get("server")) is not None:
            if self.floating_ip.server is not None:
                if value != self.floating_ip.server.name:
                    if self.module.params.get("force"):
                        if not self.module.check_mode:
                            action = self.floating_ip.assign(self.client.servers.get_by_name(value))
                            action.wait_until_finished()
                            need_reload = True
                        self._mark_as_changed()
                    else:
                        self.module.warn(
                            "Floating IP is already assigned to another server "
                            f"{self.floating_ip.server.name}. You need to "
                            "unassign the Floating IP or use force=true."
                        )

            else:  # self.floating_ip.server is None
                if not self.module.check_mode:
                    action = self.floating_ip.assign(self.client.servers.get_by_name(value))
                    action.wait_until_finished()
                    need_reload = True
                self._mark_as_changed()

        else:  # value is None
            if self.floating_ip.server is not None:
                if not self.module.check_mode:
                    action = self.floating_ip.unassign()
                    action.wait_until_finished()
                    need_reload = True
                self._mark_as_changed()

        params = {}

        if (value := self.module.params.get("labels")) is not None:
            if value != self.floating_ip.labels:
                params["labels"] = value
                self._mark_as_changed()

        if (value := self.module.params.get("description")) is not None:
            if value != self.floating_ip.description:
                params["description"] = value
                self._mark_as_changed()

        if params or need_reload:
            if not self.module.check_mode:
                self.floating_ip = self.floating_ip.update(**params)

    def _delete(self):
        if self.floating_ip.server is not None:
            if self.module.params.get("force"):
                if not self.module.check_mode:
                    action = self.floating_ip.unassign()
                    action.wait_until_finished()

                    self.floating_ip.delete()
                self._mark_as_changed()
            else:
                self.module.warn(
                    "Floating IP is currently assigned to server "
                    f"{self.floating_ip.server.name}. You need to "
                    "unassign the Floating IP or use force=true."
                )
        else:
            if not self.module.check_mode:
                self.floating_ip.delete()
            self._mark_as_changed()

        self.floating_ip = None

    def present(self):
        try:
            self._get()
            if self.floating_ip is None:
                self._create()
            else:
                self._update()
        except HCloudException as exception:
            self.fail_json_hcloud(exception)

    def delete(self):
        try:
            self._get()
            if self.floating_ip is not None:
                self._delete()
        except HCloudException as exception:
            self.fail_json_hcloud(exception)

    @classmethod
    def define_module(cls):
        return AnsibleModule(
            argument_spec=dict(
                id={"type": "int"},
                name={"type": "str"},
                description={"type": "str"},
                server={"type": "str"},
                home_location={"type": "str"},
                force={"type": "bool"},
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
            mutually_exclusive=[["home_location", "server"]],
            supports_check_mode=True,
        )


def main():
    o = AnsibleFloatingIP(AnsibleFloatingIP.define_module())

    match o.module.params["state"]:
        case "absent":
            o.delete()
        case "present":
            o.present()

    result = o.get_result()
    result["hcloud_floating_ip"] = result.pop(o.represent)

    o.module.exit_json(**result)


if __name__ == "__main__":
    main()
