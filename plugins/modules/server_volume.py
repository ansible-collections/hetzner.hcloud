#!/usr/bin/python

# Copyright: (c) 2025, Hetzner Cloud GmbH <info@hetzner-cloud.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import annotations

DOCUMENTATION = """
---
module: server_volume

short_description: Manage the relationship between Hetzner Cloud volumes and servers


description:
    - Attach and Detach volumes from Hetzner Cloud servers

author:
    - Amirhossein Shaerpour (@shaerpour)

options:
    volume:
        description:
            - Name of the volume
        type: str
        required: true
    server:
        description:
            - Server name where volume will be assigned to
        type: str
        required: true
    state:
        description:
            - State of the volume
            - Attach to server
            - Detach from server
        type: str
        default: present
        choices: [ present, absent ]
    automount:
        description:
            - Automatically mount the volume to server.
        type: bool
        default: False

extends_documentation_fragment:
- hetzner.hcloud.hcloud
"""

EXAMPLES = """
- name: Attach my-volume to my-server
  hetzner.hcloud.server_volume:
    volume: my-volume
    server: my-server

- name: Detach my-volume from my-server
  hetzner.hcloud.server_volume:
    volume: my-volume
    server: my-server
    state: detached

- name: Attach my-volume using id to my-server with automount enabled
  hetzner.hcloud.server_volume:
    volume: "123456"
    server: my-server
    state: attached
    automount: true
"""

RETURN = """
hcloud_server_volume:
    description: Attach or Detach external volume of a server
    returned: always
    type: complex
    contains:
        volume:
            description: Name of the Volume
            type: str
            returned: always
            sample: my-volume
        server:
            description: Name of the Server
            type: str
            returned: always
            sample: my-server
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils.hcloud import AnsibleHCloud
from ..module_utils.vendor.hcloud import HCloudException
from ..module_utils.vendor.hcloud.servers import BoundServer
from ..module_utils.vendor.hcloud.volumes import BoundVolume


class AnsibleHCloudServerVolume(AnsibleHCloud):
    represent = "hcloud_server_volume"

    hcloud_server: BoundServer | None = None
    hcloud_server_volume: BoundVolume | None = None

    def _prepare_result(self):
        return {
            "volume": self.hcloud_server_volume.name,
            "server": self.hcloud_server.name,
        }

    def _get_server_and_volume(self):
        try:
            self.hcloud_server_volume = self._client_get_by_name_or_id("volumes", self.module.params.get("volume"))

            self.hcloud_server = self._client_get_by_name_or_id(
                "servers",
                self.module.params.get("server"),
            )
        except HCloudException as exception:
            self.fail_json_hcloud(exception)

    def attach_volume(self):
        try:
            self._get_server_and_volume()
            server_name = self.module.params.get("server")
            server = self.client.servers.get_by_name(server_name)
            if self.hcloud_server_volume.server is None or self.hcloud_server.name != server.name:
                if not self.module.check_mode:
                    automount = self.module.params.get("automount", False)
                    action = self.hcloud_server_volume.attach(server=server, automount=automount)
                    action.wait_until_finished()
                self._mark_as_changed()
        except HCloudException as exception:
            self.fail_json_hcloud(exception)

    def detach_volume(self):
        try:
            self._get_server_and_volume()
            if self.hcloud_server_volume.server is not None:
                if not self.module.check_mode:
                    action = self.hcloud_server_volume.detach()
                    action.wait_until_finished()
                self._mark_as_changed()
        except HCloudException as exception:
            self.fail_json_hcloud(exception)

    @classmethod
    def define_module(cls):
        return AnsibleModule(
            argument_spec=dict(
                volume={"type": "str", "required": True},
                server={"type": "str", "required": True},
                automount={"type": "bool", "default": False},
                state={
                    "choices": ["present", "absent"],
                    "default": "present",
                },
                **super().base_module_arguments(),
            ),
            supports_check_mode=True,
        )


def main():
    module = AnsibleHCloudServerVolume.define_module()

    hcloud = AnsibleHCloudServerVolume(module)
    state = module.params["state"]
    if state == "present":
        hcloud.attach_volume()
    elif state == "absent":
        hcloud.detach_volume()

    module.exit_json(**hcloud.get_result())


if __name__ == "__main__":
    main()
