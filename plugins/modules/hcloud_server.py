#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Hetzner Cloud GmbH <info@hetzner-cloud.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: hcloud_server

short_description: Create and manage cloud servers on the Hetzner Cloud.


description:
    - Create, update and manage cloud servers on the Hetzner Cloud.

author:
    - Lukas Kaemmerling (@LKaemmerling)

options:
    id:
        description:
            - The ID of the Hetzner Cloud server to manage.
            - Only required if no server I(name) is given
        type: int
    name:
        description:
            - The Name of the Hetzner Cloud server to manage.
            - Only required if no server I(id) is given or a server does not exist.
        type: str
    server_type:
        description:
            - The Server Type of the Hetzner Cloud server to manage.
            - Required if server does not exist.
        type: str
    ssh_keys:
        description:
            - List of SSH key names
            - The key names correspond to the SSH keys configured for your
              Hetzner Cloud account access.
        type: list
        elements: str
    volumes:
        description:
            - List of Volumes IDs that should be attached to the server on server creation.
        type: list
        elements: str
    firewalls:
        description:
            - List of Firewall IDs that should be attached to the server on server creation.
        type: list
        elements: str
    image:
        description:
            - Image the server should be created from.
            - Required if server does not exist.
        type: str
    location:
        description:
            - Location of Server.
            - Required if no I(datacenter) is given and server does not exist.
        type: str
    datacenter:
        description:
            - Datacenter of Server.
            - Required of no I(location) is given and server does not exist.
        type: str
    backups:
        description:
            - Enable or disable Backups for the given Server.
        type: bool
    upgrade_disk:
        description:
            - Resize the disk size, when resizing a server.
            - If you want to downgrade the server later, this value should be False.
        type: bool
        default: no
    enable_ipv4:
        description:
            - Enables the public ipv4 address
        type: bool
        default: yes
    enable_ipv6:
        description:
            - Enables the public ipv6 address
        type: bool
        default: yes
    ipv4:
        description:
            - ID of the ipv4 Primary IP to use. If omitted and enable_ipv4 is true, a new ipv4 Primary IP will automatically be created
        type: str
    ipv6:
        description:
            - ID of the ipv6 Primary IP to use. If omitted and enable_ipv6 is true, a new ipv6 Primary IP will automatically be created.
        type: str
    private_networks:
        description:
            - List of private networks the server is attached to (name or ID)
            - If None, private networks are left as they are (e.g. if previously added by hcloud_server_network),
              if it has any other value (including []), only those networks are attached to the server.
        type: list
        elements: str
    force_upgrade:
        description:
            - Deprecated
            - Force the upgrade of the server.
            - Power off the server if it is running on upgrade.
        type: bool
        default: no
    force:
        description:
            - Force the update of the server.
            - May power off the server if update.
        type: bool
        default: no
    allow_deprecated_image:
        description:
            - Allows the creation of servers with deprecated images.
        type: bool
        default: no
    user_data:
        description:
            - User Data to be passed to the server on creation.
            - Only used if server does not exist.
        type: str
    rescue_mode:
        description:
            - Add the Hetzner rescue system type you want the server to be booted into.
        type: str
    labels:
        description:
            - User-defined labels (key-value pairs).
        type: dict
    delete_protection:
        description:
            - Protect the Server for deletion.
            - Needs to be the same as I(rebuild_protection).
        type: bool
    rebuild_protection:
        description:
            - Protect the Server for rebuild.
            - Needs to be the same as I(delete_protection).
        type: bool
    placement_group:
        description:
            - Placement Group of the server.
        type: str
    state:
        description:
            - State of the server.
        default: present
        choices: [ absent, present, restarted, started, stopped, rebuild ]
        type: str
extends_documentation_fragment:
- hetzner.hcloud.hcloud

'''

EXAMPLES = """
- name: Create a basic server
  hcloud_server:
    name: my-server
    server_type: cx11
    image: ubuntu-18.04
    state: present

- name: Create a basic server with ssh key
  hcloud_server:
    name: my-server
    server_type: cx11
    image: ubuntu-18.04
    location: fsn1
    ssh_keys:
      - me@myorganisation
    state: present

- name: Resize an existing server
  hcloud_server:
    name: my-server
    server_type: cx21
    upgrade_disk: yes
    state: present

- name: Ensure the server is absent (remove if needed)
  hcloud_server:
    name: my-server
    state: absent

- name: Ensure the server is started
  hcloud_server:
    name: my-server
    state: started

- name: Ensure the server is stopped
  hcloud_server:
    name: my-server
    state: stopped

- name: Ensure the server is restarted
  hcloud_server:
    name: my-server
    state: restarted

- name: Ensure the server is will be booted in rescue mode and therefore restarted
  hcloud_server:
    name: my-server
    rescue_mode: linux64
    state: restarted

- name: Ensure the server is rebuild
  hcloud_server:
    name: my-server
    image: ubuntu-18.04
    state: rebuild

- name: Add server to placement group
  hcloud_server:
    name: my-server
    placement_group: my-placement-group
    force: True
    state: present

- name: Remove server from placement group
  hcloud_server:
    name: my-server
    placement_group: null
    state: present

- name: Add server with private network only
  hcloud_server:
    name: my-server
    enable_ipv4: false
    enable_ipv6: false
    private_networks:
      - my-network
      - 4711
    state: present
"""

RETURN = """
hcloud_server:
    description: The server instance
    returned: Always
    type: complex
    contains:
        id:
            description: Numeric identifier of the server
            returned: always
            type: int
            sample: 1937415
        name:
            description: Name of the server
            returned: always
            type: str
            sample: my-server
        status:
            description: Status of the server
            returned: always
            type: str
            sample: running
        server_type:
            description: Name of the server type of the server
            returned: always
            type: str
            sample: cx11
        ipv4_address:
            description: Public IPv4 address of the server
            returned: always
            type: str
            sample: 116.203.104.109
        ipv6:
            description: IPv6 network of the server
            returned: always
            type: str
            sample: 2a01:4f8:1c1c:c140::/64
        private_networks:
            description: List of private networks the server is attached to (name or ID)
            returned: always
            type: list
            elements: str
            sample: ['my-network', 'another-network', '4711']
        private_networks_info:
            description: List of private networks the server is attached to (dict with name and ip)
            returned: always
            type: list
            elements: dict
            sample: [{'name': 'my-network', 'ip': '192.168.1.1'}, {'name': 'another-network', 'ip': '10.185.50.40'}]
        location:
            description: Name of the location of the server
            returned: always
            type: str
            sample: fsn1
        placement_group:
            description: Placement Group of the server
            type: str
            returned: always
            sample: 4711
            version_added: "1.5.0"
        datacenter:
            description: Name of the datacenter of the server
            returned: always
            type: str
            sample: fsn1-dc14
        rescue_enabled:
            description: True if rescue mode is enabled, Server will then boot into rescue system on next reboot
            returned: always
            type: bool
            sample: false
        backup_window:
            description: Time window (UTC) in which the backup will run, or null if the backups are not enabled
            returned: always
            type: bool
            sample: 22-02
        labels:
            description: User-defined labels (key-value pairs)
            returned: always
            type: dict
        delete_protection:
            description: True if server is protected for deletion
            type: bool
            returned: always
            sample: false
            version_added: "0.1.0"
        rebuild_protection:
            description: True if server is protected for rebuild
            type: bool
            returned: always
            sample: false
            version_added: "0.1.0"
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from ansible_collections.hetzner.hcloud.plugins.module_utils.hcloud import Hcloud
from datetime import timedelta

try:
    from hcloud.volumes.domain import Volume
    from hcloud.ssh_keys.domain import SSHKey
    from hcloud.servers.domain import Server, ServerCreatePublicNetwork
    from hcloud.firewalls.domain import FirewallResource
except ImportError:
    Volume = None
    SSHKey = None
    Server = None
    ServerCreatePublicNetwork = None
    FirewallResource = None


class AnsibleHcloudServer(Hcloud):
    def __init__(self, module):
        Hcloud.__init__(self, module, "hcloud_server")
        self.hcloud_server = None

    def _prepare_result(self):
        image = None if self.hcloud_server.image is None else to_native(self.hcloud_server.image.name)
        placement_group = None if self.hcloud_server.placement_group is None else to_native(
            self.hcloud_server.placement_group.name)
        ipv4_address = None if self.hcloud_server.public_net.ipv4 is None else to_native(
            self.hcloud_server.public_net.ipv4.ip)
        ipv6 = None if self.hcloud_server.public_net.ipv6 is None else to_native(self.hcloud_server.public_net.ipv6.ip)
        backup_window = None if self.hcloud_server.backup_window is None else to_native(self.hcloud_server.backup_window)
        return {
            "id": to_native(self.hcloud_server.id),
            "name": to_native(self.hcloud_server.name),
            "ipv4_address": ipv4_address,
            "ipv6": ipv6,
            "private_networks": [to_native(net.network.name) for net in self.hcloud_server.private_net],
            "private_networks_info": [{"name": to_native(net.network.name), "ip": net.ip} for net in self.hcloud_server.private_net],
            "image": image,
            "server_type": to_native(self.hcloud_server.server_type.name),
            "datacenter": to_native(self.hcloud_server.datacenter.name),
            "location": to_native(self.hcloud_server.datacenter.location.name),
            "placement_group": placement_group,
            "rescue_enabled": self.hcloud_server.rescue_enabled,
            "backup_window": backup_window,
            "labels": self.hcloud_server.labels,
            "delete_protection": self.hcloud_server.protection["delete"],
            "rebuild_protection": self.hcloud_server.protection["rebuild"],
            "status": to_native(self.hcloud_server.status),
        }

    def _get_server(self):
        try:
            if self.module.params.get("id") is not None:
                self.hcloud_server = self.client.servers.get_by_id(
                    self.module.params.get("id")
                )
            else:
                self.hcloud_server = self.client.servers.get_by_name(
                    self.module.params.get("name")
                )
        except Exception as e:
            self.module.fail_json(msg=e.message)

    def _create_server(self):
        self.module.fail_on_missing_params(
            required_params=["name", "server_type", "image"]
        )

        server_type = self._get_server_type()

        params = {
            "name": self.module.params.get("name"),
            "server_type": server_type,
            "user_data": self.module.params.get("user_data"),
            "labels": self.module.params.get("labels"),
            "image": self._get_image(server_type),
            "placement_group": self._get_placement_group(),
            "public_net": ServerCreatePublicNetwork(
                enable_ipv4=self.module.params.get("enable_ipv4"),
                enable_ipv6=self.module.params.get("enable_ipv6")
            )
        }

        if self.module.params.get("ipv4") is not None:
            p = self.client.primary_ips.get_by_name(self.module.params.get("ipv4"))
            if not p:
                p = self.client.primary_ips.get_by_id(self.module.params.get("ipv4"))
            params["public_net"].ipv4 = p

        if self.module.params.get("ipv6") is not None:
            p = self.client.primary_ips.get_by_name(self.module.params.get("ipv6"))
            if not p:
                p = self.client.primary_ips.get_by_id(self.module.params.get("ipv6"))
            params["public_net"].ipv6 = p

        if self.module.params.get("private_networks") is not None:
            _networks = []
            for network_name_or_id in self.module.params.get("private_networks"):
                _networks.append(
                    self.client.networks.get_by_name(network_name_or_id)
                    or self.client.networks.get_by_id(network_name_or_id)
                )
            params["networks"] = _networks

        if self.module.params.get("ssh_keys") is not None:
            params["ssh_keys"] = [
                SSHKey(name=ssh_key_name)
                for ssh_key_name in self.module.params.get("ssh_keys")
            ]

        if self.module.params.get("volumes") is not None:
            params["volumes"] = [
                Volume(id=volume_id) for volume_id in self.module.params.get("volumes")
            ]
        if self.module.params.get("firewalls") is not None:
            params["firewalls"] = []
            for fw in self.module.params.get("firewalls"):
                f = self.client.firewalls.get_by_name(fw)
                if f is not None:
                    # When firewall name is not available look for id instead
                    params["firewalls"].append(f)
                else:
                    params["firewalls"].append(self.client.firewalls.get_by_id(fw))

        if self.module.params.get("location") is None and self.module.params.get("datacenter") is None:
            # When not given, the API will choose the location.
            params["location"] = None
            params["datacenter"] = None
        elif self.module.params.get("location") is not None and self.module.params.get("datacenter") is None:
            params["location"] = self.client.locations.get_by_name(
                self.module.params.get("location")
            )
        elif self.module.params.get("location") is None and self.module.params.get("datacenter") is not None:
            params["datacenter"] = self.client.datacenters.get_by_name(
                self.module.params.get("datacenter")
            )

        if self.module.params.get("state") == "stopped":
            params["start_after_create"] = False
        if not self.module.check_mode:
            try:
                resp = self.client.servers.create(**params)
                self.result["root_password"] = resp.root_password
                resp.action.wait_until_finished(max_retries=1000)
                [action.wait_until_finished() for action in resp.next_actions]

                rescue_mode = self.module.params.get("rescue_mode")
                if rescue_mode:
                    self._get_server()
                    self._set_rescue_mode(rescue_mode)

                backups = self.module.params.get("backups")
                if backups:
                    self._get_server()
                    self.hcloud_server.enable_backup().wait_until_finished()

                delete_protection = self.module.params.get("delete_protection")
                rebuild_protection = self.module.params.get("rebuild_protection")
                if delete_protection is not None and rebuild_protection is not None:
                    self._get_server()
                    self.hcloud_server.change_protection(delete=delete_protection,
                                                         rebuild=rebuild_protection).wait_until_finished()
            except Exception as e:
                self.module.fail_json(msg=e.message)
        self._mark_as_changed()
        self._get_server()

    def _get_image(self, server_type):
        image_resp = self.client.images.get_list(name=self.module.params.get("image"), architecture=server_type.architecture, include_deprecated=True)
        images = getattr(image_resp, 'images')
        image = None
        if images is not None and len(images) > 0:
            # If image name is not available look for id instead
            image = images[0]
        else:
            try:
                image = self.client.images.get_by_id(self.module.params.get("image"))
            except Exception:
                self.module.fail_json(msg="Image %s was not found" % self.module.params.get('image'))
        if image.deprecated is not None:
            available_until = image.deprecated + timedelta(days=90)
            if self.module.params.get("allow_deprecated_image"):
                self.module.warn(
                    "You try to use a deprecated image. The image %s will continue to be available until %s.") % (
                    image.name, available_until.strftime('%Y-%m-%d'))
            else:
                self.module.fail_json(
                    msg=("You try to use a deprecated image. The image %s will continue to be available until %s." +
                         " If you want to use this image use allow_deprecated_image=yes."
                         ) % (image.name, available_until.strftime('%Y-%m-%d')))
        return image

    def _get_server_type(self):
        server_type = self.client.server_types.get_by_name(
            self.module.params.get("server_type")
        )
        if server_type is None:
            try:
                server_type = self.client.server_types.get_by_id(self.module.params.get("server_type"))
            except Exception:
                self.module.fail_json(msg="server_type %s was not found" % self.module.params.get('server_type'))

        return server_type

    def _get_placement_group(self):
        if self.module.params.get("placement_group") is None:
            return None

        placement_group = self.client.placement_groups.get_by_name(
            self.module.params.get("placement_group")
        )
        if placement_group is None:
            try:
                placement_group = self.client.placement_groups.get_by_id(self.module.params.get("placement_group"))
            except Exception:
                self.module.fail_json(
                    msg="placement_group %s was not found" % self.module.params.get("placement_group"))

        return placement_group

    def _get_primary_ip(self, field):
        if self.module.params.get(field) is None:
            return None

        primary_ip = self.client.primary_ips.get_by_name(
            self.module.params.get(field)
        )
        if primary_ip is None:
            try:
                primary_ip = self.client.primary_ips.get_by_id(self.module.params.get(field))
            except Exception as e:
                self.module.fail_json(
                    msg="primary_ip %s was not found" % self.module.params.get(field))

        return primary_ip

    def _update_server(self):
        if "force_upgrade" in self.module.params:
            self.module.warn("force_upgrade is deprecated, use force instead")

        try:
            previous_server_status = self.hcloud_server.status

            rescue_mode = self.module.params.get("rescue_mode")
            if rescue_mode and self.hcloud_server.rescue_enabled is False:
                if not self.module.check_mode:
                    self._set_rescue_mode(rescue_mode)
                self._mark_as_changed()
            elif not rescue_mode and self.hcloud_server.rescue_enabled is True:
                if not self.module.check_mode:
                    self.hcloud_server.disable_rescue().wait_until_finished()
                self._mark_as_changed()

            backups = self.module.params.get("backups")
            if backups and self.hcloud_server.backup_window is None:
                if not self.module.check_mode:
                    self.hcloud_server.enable_backup().wait_until_finished()
                self._mark_as_changed()
            elif backups is not None and not backups and self.hcloud_server.backup_window is not None:
                if not self.module.check_mode:
                    self.hcloud_server.disable_backup().wait_until_finished()
                self._mark_as_changed()

            labels = self.module.params.get("labels")
            if labels is not None and labels != self.hcloud_server.labels:
                if not self.module.check_mode:
                    self.hcloud_server.update(labels=labels)
                self._mark_as_changed()

            wanted_firewalls = self.module.params.get("firewalls")
            if wanted_firewalls is not None:
                # Removing existing but not wanted firewalls
                for current_firewall in self.hcloud_server.public_net.firewalls:
                    if current_firewall.firewall.name not in wanted_firewalls:
                        self._mark_as_changed()
                        if not self.module.check_mode:
                            r = FirewallResource(type="server", server=self.hcloud_server)
                            actions = self.client.firewalls.remove_from_resources(current_firewall.firewall, [r])
                            for a in actions:
                                a.wait_until_finished()

                # Adding wanted firewalls that doesn't exist yet
                for fname in wanted_firewalls:
                    found = False
                    for f in self.hcloud_server.public_net.firewalls:
                        if f.firewall.name == fname:
                            found = True
                            break

                    if not found:
                        self._mark_as_changed()
                        if not self.module.check_mode:
                            fw = self.client.firewalls.get_by_name(fname)
                            if fw is None:
                                self.module.fail_json(msg="firewall %s was not found" % fname)
                            r = FirewallResource(type="server", server=self.hcloud_server)
                            actions = self.client.firewalls.apply_to_resources(fw, [r])
                            for a in actions:
                                a.wait_until_finished()

            if "placement_group" in self.module.params:
                if self.module.params["placement_group"] is None and self.hcloud_server.placement_group is not None:
                    if not self.module.check_mode:
                        self.hcloud_server.remove_from_placement_group().wait_until_finished()
                    self._mark_as_changed()
                else:
                    placement_group = self._get_placement_group()
                    if (
                            placement_group is not None and
                            (
                                self.hcloud_server.placement_group is None or
                                self.hcloud_server.placement_group.id != placement_group.id
                            )
                    ):
                        self.stop_server_if_forced()
                        if not self.module.check_mode:
                            self.hcloud_server.add_to_placement_group(placement_group).wait_until_finished()
                        self._mark_as_changed()

            if "ipv4" in self.module.params:
                if (
                        self.module.params["ipv4"] is None and
                        self.hcloud_server.public_net.primary_ipv4 is not None and
                        not self.module.params.get("enable_ipv4")
                ):
                    self.stop_server_if_forced()
                    if not self.module.check_mode:
                        self.hcloud_server.public_net.primary_ipv4.unassign().wait_until_finished()
                    self._mark_as_changed()
                else:
                    primary_ip = self._get_primary_ip("ipv4")
                    if (
                            primary_ip is not None and
                            (
                                self.hcloud_server.public_net.primary_ipv4 is None or
                                self.hcloud_server.public_net.primary_ipv4.id != primary_ip.id
                            )
                    ):
                        self.stop_server_if_forced()
                        if not self.module.check_mode:
                            if self.hcloud_server.public_net.primary_ipv4:
                                self.hcloud_server.public_net.primary_ipv4.unassign().wait_until_finished()
                            primary_ip.assign(self.hcloud_server.id, "server").wait_until_finished()
                        self._mark_as_changed()
            if "ipv6" in self.module.params:
                if (
                        (self.module.params["ipv6"] is None or self.module.params["ipv6"] == "") and
                        self.hcloud_server.public_net.primary_ipv6 is not None and
                        not self.module.params.get("enable_ipv6")
                ):
                    self.stop_server_if_forced()
                    if not self.module.check_mode:
                        self.hcloud_server.public_net.primary_ipv6.unassign().wait_until_finished()
                    self._mark_as_changed()
                else:
                    primary_ip = self._get_primary_ip("ipv6")
                    if (
                            primary_ip is not None and
                            (
                                self.hcloud_server.public_net.primary_ipv6 is None or
                                self.hcloud_server.public_net.primary_ipv6.id != primary_ip.id
                            )
                    ):
                        self.stop_server_if_forced()
                        if not self.module.check_mode:
                            if self.hcloud_server.public_net.primary_ipv6 is not None:
                                self.hcloud_server.public_net.primary_ipv6.unassign().wait_until_finished()
                            primary_ip.assign(self.hcloud_server.id, "server").wait_until_finished()
                        self._mark_as_changed()
            if "private_networks" in self.module.params and self.module.params["private_networks"] is not None:
                if not bool(self.module.params["private_networks"]):
                    # This handles None, "" and []
                    networks_target = {}
                else:
                    _networks = {}
                    for network_name_or_id in self.module.params.get("private_networks"):
                        _found_network = self.client.networks.get_by_name(network_name_or_id) \
                            or self.client.networks.get_by_id(network_name_or_id)
                        _networks.update(
                            {_found_network.id: _found_network}
                        )
                    networks_target = _networks
                networks_is = dict()
                for p_network in self.hcloud_server.private_net:
                    networks_is.update({p_network.network.id: p_network.network})
                for network_id in set(list(networks_is) + list(networks_target)):
                    if network_id in networks_is and network_id not in networks_target:
                        self.stop_server_if_forced()
                        if not self.module.check_mode:
                            self.hcloud_server.detach_from_network(networks_is[network_id]).wait_until_finished()
                        self._mark_as_changed()
                    elif network_id in networks_target and network_id not in networks_is:
                        self.stop_server_if_forced()
                        if not self.module.check_mode:
                            self.hcloud_server.attach_to_network(networks_target[network_id]).wait_until_finished()
                        self._mark_as_changed()

            server_type = self.module.params.get("server_type")
            if server_type is not None and self.hcloud_server.server_type.name != server_type:
                self.stop_server_if_forced()

                timeout = 100
                if self.module.params.get("upgrade_disk"):
                    timeout = (
                        1000
                    )  # When we upgrade the disk to the resize progress takes some more time.
                if not self.module.check_mode:
                    self.hcloud_server.change_type(
                        server_type=self._get_server_type(),
                        upgrade_disk=self.module.params.get("upgrade_disk"),
                    ).wait_until_finished(timeout)
                self._mark_as_changed()

            if (
                    not self.module.check_mode and
                    (
                        (
                            self.module.params.get("state") == "present" and
                            previous_server_status == Server.STATUS_RUNNING
                        ) or
                        self.module.params.get("state") == "started"
                    )
            ):
                self.start_server()

            delete_protection = self.module.params.get("delete_protection")
            rebuild_protection = self.module.params.get("rebuild_protection")
            if (delete_protection is not None and rebuild_protection is not None) and (
                    delete_protection != self.hcloud_server.protection["delete"] or rebuild_protection !=
                    self.hcloud_server.protection["rebuild"]):
                if not self.module.check_mode:
                    self.hcloud_server.change_protection(delete=delete_protection,
                                                         rebuild=rebuild_protection).wait_until_finished()
                self._mark_as_changed()
            self._get_server()
        except Exception as e:
            self.module.fail_json(msg=e)

    def _set_rescue_mode(self, rescue_mode):
        if self.module.params.get("ssh_keys"):
            resp = self.hcloud_server.enable_rescue(type=rescue_mode,
                                                    ssh_keys=[self.client.ssh_keys.get_by_name(ssh_key_name).id
                                                              for
                                                              ssh_key_name in
                                                              self.module.params.get("ssh_keys")])
        else:
            resp = self.hcloud_server.enable_rescue(type=rescue_mode)
        resp.action.wait_until_finished()
        self.result["root_password"] = resp.root_password

    def start_server(self):
        try:
            if self.hcloud_server:
                if self.hcloud_server.status != Server.STATUS_RUNNING:
                    if not self.module.check_mode:
                        self.client.servers.power_on(self.hcloud_server).wait_until_finished()
                    self._mark_as_changed()
                self._get_server()
        except Exception as e:
            self.module.fail_json(msg=e.message)

    def stop_server(self):
        try:
            if self.hcloud_server:
                if self.hcloud_server.status != Server.STATUS_OFF:
                    if not self.module.check_mode:
                        self.client.servers.power_off(self.hcloud_server).wait_until_finished()
                    self._mark_as_changed()
                self._get_server()
        except Exception as e:
            self.module.fail_json(msg=e.message)

    def stop_server_if_forced(self):
        previous_server_status = self.hcloud_server.status
        if previous_server_status == Server.STATUS_RUNNING and not self.module.check_mode:
            if (
                    self.module.params.get("force_upgrade") or
                    self.module.params.get("force") or
                    self.module.params.get("state") == "stopped"
            ):
                self.stop_server()  # Only stopped server can be upgraded
                return previous_server_status
            else:
                self.module.warn(
                    "You can not upgrade a running instance %s. You need to stop the instance or use force=yes."
                    % self.hcloud_server.name
                )

        return None

    def rebuild_server(self):
        self.module.fail_on_missing_params(
            required_params=["image"]
        )
        try:
            if not self.module.check_mode:
                image = self._get_image(self.hcloud_server.server_type)
                self.client.servers.rebuild(self.hcloud_server, image).wait_until_finished(1000)  # When we rebuild the server progress takes some more time.
            self._mark_as_changed()

            self._get_server()
        except Exception as e:
            self.module.fail_json(msg=e.message)

    def present_server(self):
        self._get_server()
        if self.hcloud_server is None:
            self._create_server()
        else:
            self._update_server()

    def delete_server(self):
        try:
            self._get_server()
            if self.hcloud_server is not None:
                if not self.module.check_mode:
                    self.client.servers.delete(self.hcloud_server).wait_until_finished()
                self._mark_as_changed()
            self.hcloud_server = None
        except Exception as e:
            self.module.fail_json(msg=e.message)

    @staticmethod
    def define_module():
        return AnsibleModule(
            argument_spec=dict(
                id={"type": "int"},
                name={"type": "str"},
                image={"type": "str"},
                server_type={"type": "str"},
                location={"type": "str"},
                datacenter={"type": "str"},
                user_data={"type": "str"},
                ssh_keys={"type": "list", "elements": "str", "no_log": False},
                volumes={"type": "list", "elements": "str"},
                firewalls={"type": "list", "elements": "str"},
                labels={"type": "dict"},
                backups={"type": "bool"},
                upgrade_disk={"type": "bool", "default": False},
                enable_ipv4={"type": "bool", "default": True},
                enable_ipv6={"type": "bool", "default": True},
                ipv4={"type": "str"},
                ipv6={"type": "str"},
                private_networks={"type": "list", "elements": "str", "default": None},
                force={"type": "bool", "default": False},
                force_upgrade={"type": "bool", "default": False},
                allow_deprecated_image={"type": "bool", "default": False},
                rescue_mode={"type": "str"},
                delete_protection={"type": "bool"},
                rebuild_protection={"type": "bool"},
                placement_group={"type": "str"},
                state={
                    "choices": ["absent", "present", "restarted", "started", "stopped", "rebuild"],
                    "default": "present",
                },
                **Hcloud.base_module_arguments()
            ),
            required_one_of=[['id', 'name']],
            mutually_exclusive=[["location", "datacenter"]],
            required_together=[["delete_protection", "rebuild_protection"]],
            supports_check_mode=True,
        )


def main():
    module = AnsibleHcloudServer.define_module()

    hcloud = AnsibleHcloudServer(module)
    state = module.params.get("state")
    if state == "absent":
        hcloud.delete_server()
    elif state == "present":
        hcloud.present_server()
    elif state == "started":
        hcloud.present_server()
        hcloud.start_server()
    elif state == "stopped":
        hcloud.present_server()
        hcloud.stop_server()
    elif state == "restarted":
        hcloud.present_server()
        hcloud.stop_server()
        hcloud.start_server()
    elif state == "rebuild":
        hcloud.present_server()
        hcloud.rebuild_server()

    module.exit_json(**hcloud.get_result())


if __name__ == "__main__":
    main()
