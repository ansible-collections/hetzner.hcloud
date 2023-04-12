# Copyright (c) 2019 Hetzner Cloud GmbH <info@hetzner-cloud.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
    name: hcloud
    author:
      - Lukas Kaemmerling (@lkaemmerling)
    short_description: Ansible dynamic inventory plugin for the Hetzner Cloud.
    requirements:
        - python >= 3.5
        - hcloud-python >= 1.0.0
    description:
        - Reads inventories from the Hetzner Cloud API.
        - Uses a YAML configuration file that ends with hcloud.(yml|yaml).
    extends_documentation_fragment:
        - constructed
    options:
        plugin:
            description: marks this as an instance of the "hcloud" plugin
            required: true
            choices: ["hcloud", "hetzner.hcloud.hcloud"]
        token:
            description: The Hetzner Cloud API Token.
            required: false
        group:
            description: The group all servers are automatically added to.
            default: hcloud
            type: str
            required: false
        token_env:
            description: Environment variable to load the Hetzner Cloud API Token from.
            default: HCLOUD_TOKEN
            type: str
            required: false
        connect_with:
            description: |
              Connect to the server using the value from this field. This sets the `ansible_host`
              variable to the value indicated, if that value is available. If you need further
              customization, like falling back to private ipv4 if the server has no public ipv4,
              you can use `compose` top-level key.
            default: public_ipv4
            type: str
            choices:
                - public_ipv4
                - public_ipv6
                - hostname
                - ipv4_dns_ptr
                - private_ipv4
        locations:
          description: Populate inventory with instances in this location.
          default: []
          type: list
          elements: str
          required: false
        types:
          description: Populate inventory with instances with this type.
          default: []
          type: list
          elements: str
          required: false
        images:
          description: Populate inventory with instances with this image name, only available for system images.
          default: []
          type: list
          elements: str
          required: false
        label_selector:
          description: Populate inventory with instances with this label.
          default: ""
          type: str
          required: false
        network:
          description: Populate inventory with instances which are attached to this network name or ID.
          default: ""
          type: str
          required: false
        status:
          description: Populate inventory with instances with this status.
          default: []
          type: list
          elements: str
          required: false
'''

EXAMPLES = r"""
# Minimal example. `HCLOUD_TOKEN` is exposed in environment.
plugin: hcloud

# Example with templated token, e.g. provided through extra vars.
plugin: hcloud
token: "{{ hetzner_apitoken }}"

# Example with locations, types, status and token
plugin: hcloud
token: foobar
locations:
  - nbg1
types:
  - cx11
status:
  - running

# Group by a location with prefix e.g. "hcloud_location_nbg1"
# and image_os_flavor without prefix and separator e.g. "ubuntu"
# and status with prefix e.g. "server_status_running"
plugin: hcloud
keyed_groups:
  - key: location
    prefix: hcloud_location
  - key: image_os_flavor
    separator: ""
  - key: status
    prefix: server_status
"""

import os
from ansible.errors import AnsibleError
from ansible.module_utils._text import to_native
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable
from ansible.release import __version__
from ipaddress import IPv6Network

try:
    from hcloud import hcloud
    from hcloud import APIException
    HAS_HCLOUD = True
except ImportError:
    HAS_HCLOUD = False


class InventoryModule(BaseInventoryPlugin, Constructable):
    NAME = 'hetzner.hcloud.hcloud'

    def _configure_hcloud_client(self):
        self.token_env = self.get_option("token_env")
        self.templar.available_variables = self._vars
        self.api_token = self.templar.template(self.get_option("token"), fail_on_undefined=False) or os.getenv(self.token_env)
        if self.api_token is None:
            raise AnsibleError(
                "Please specify a token, via the option token, via environment variable HCLOUD_TOKEN "
                "or via custom environment variable set by token_env option."
            )

        self.endpoint = os.getenv("HCLOUD_ENDPOINT") or "https://api.hetzner.cloud/v1"

        self.client = hcloud.Client(token=self.api_token,
                                    api_endpoint=self.endpoint,
                                    application_name="ansible-inventory",
                                    application_version=__version__)

    def _test_hcloud_token(self):
        try:
            # We test the API Token against the location API, because this is the API with the smallest result
            # and not controllable from the customer.
            self.client.locations.get_all()
        except APIException:
            raise AnsibleError("Invalid Hetzner Cloud API Token.")

    def _get_servers(self):
        if len(self.get_option("label_selector")) > 0:
            self.servers = self.client.servers.get_all(label_selector=self.get_option("label_selector"))
        else:
            self.servers = self.client.servers.get_all()

    def _filter_servers(self):
        if self.get_option("network"):
            network = self.templar.template(self.get_option("network"), fail_on_undefined=False) or self.get_option("network")
            try:
                self.network = self.client.networks.get_by_name(network)
                if self.network is None:
                    self.network = self.client.networks.get_by_id(network)
            except APIException:
                raise AnsibleError(
                    "The given network is not found.")

            tmp = []
            for server in self.servers:
                for server_private_network in server.private_net:
                    if server_private_network.network.id == self.network.id:
                        tmp.append(server)
            self.servers = tmp

        if self.get_option("locations"):
            tmp = []
            for server in self.servers:
                if server.datacenter.location.name in self.get_option("locations"):
                    tmp.append(server)
            self.servers = tmp

        if self.get_option("types"):
            tmp = []
            for server in self.servers:
                if server.server_type.name in self.get_option("types"):
                    tmp.append(server)
            self.servers = tmp

        if self.get_option("images"):
            tmp = []
            for server in self.servers:
                if server.image is not None and server.image.os_flavor in self.get_option("images"):
                    tmp.append(server)
            self.servers = tmp

        if self.get_option("status"):
            tmp = []
            for server in self.servers:
                if server.status in self.get_option("status"):
                    tmp.append(server)
            self.servers = tmp

    def _set_server_attributes(self, server):
        self.inventory.set_variable(server.name, "id", to_native(server.id))
        self.inventory.set_variable(server.name, "name", to_native(server.name))
        self.inventory.set_variable(server.name, "status", to_native(server.status))
        self.inventory.set_variable(server.name, "type", to_native(server.server_type.name))
        self.inventory.set_variable(server.name, "architecture", to_native(server.server_type.architecture))

        # Network
        if server.public_net.ipv4:
            self.inventory.set_variable(server.name, "ipv4", to_native(server.public_net.ipv4.ip))

        if server.public_net.ipv6:
            self.inventory.set_variable(server.name, "ipv6_network", to_native(server.public_net.ipv6.network))
            self.inventory.set_variable(server.name, "ipv6_network_mask", to_native(server.public_net.ipv6.network_mask))
            self.inventory.set_variable(server.name, "ipv6", to_native(self._first_ipv6_address(server.public_net.ipv6.ip)))

        self.inventory.set_variable(
            server.name,
            "private_networks",
            [
                {"name": n.network.name, "id": n.network.id, "ip": n.ip}
                for n in server.private_net
            ],
        )

        if self.get_option("network"):
            for server_private_network in server.private_net:
                # Set private_ipv4 if user filtered for one network
                if server_private_network.network.id == self.network.id:
                    self.inventory.set_variable(server.name, "private_ipv4", to_native(server_private_network.ip))

        try:
            self.inventory.set_variable(server.name, "ansible_host", self._get_server_ansible_host(server))
        except AnsibleError as e:
            # Log warning that for this host can not be connected to, using the
            # method specified in `connect_with`. Users might use `compose` to
            # override the connection method, or implement custom logic, so we
            # do not need to abort if nothing matched.
            self.display.v("[hcloud] %s" % e, server.name)

        # Server Type
        if server.server_type is not None:
            self.inventory.set_variable(server.name, "server_type", to_native(server.server_type.name))

        # Datacenter
        self.inventory.set_variable(server.name, "datacenter", to_native(server.datacenter.name))
        self.inventory.set_variable(server.name, "location", to_native(server.datacenter.location.name))

        # Image
        if server.image is not None:
            self.inventory.set_variable(server.name, "image_id", to_native(server.image.id))
            self.inventory.set_variable(server.name, "image_os_flavor", to_native(server.image.os_flavor))
            if server.image.name is not None:
                self.inventory.set_variable(server.name, "image_name", to_native(server.image.name))
            else:
                self.inventory.set_variable(server.name, "image_name", to_native(server.image.description))
        else:
            self.inventory.set_variable(server.name, "image_id", to_native("No Image ID found"))
            self.inventory.set_variable(server.name, "image_name", to_native("No Image Name found"))
            self.inventory.set_variable(server.name, "image_os_flavor", to_native("No Image OS Flavor found"))

        # Labels
        self.inventory.set_variable(server.name, "labels", dict(server.labels))

    def _get_server_ansible_host(self, server):
        if self.get_option("connect_with") == "public_ipv4":
            if server.public_net.ipv4:
                return to_native(server.public_net.ipv4.ip)
            else:
                raise AnsibleError("Server has no public ipv4, but connect_with=public_ipv4 was specified")

        if self.get_option("connect_with") == "public_ipv6":
            if server.public_net.ipv6:
                return to_native(self._first_ipv6_address(server.public_net.ipv6.ip))
            else:
                raise AnsibleError("Server has no public ipv6, but connect_with=public_ipv6 was specified")

        elif self.get_option("connect_with") == "hostname":
            # every server has a name, no need to guard this
            return to_native(server.name)

        elif self.get_option("connect_with") == "ipv4_dns_ptr":
            if server.public_net.ipv4:
                return to_native(server.public_net.ipv4.dns_ptr)
            else:
                raise AnsibleError("Server has no public ipv4, but connect_with=ipv4_dns_ptr was specified")

        elif self.get_option("connect_with") == "private_ipv4":
            if self.get_option("network"):
                for server_private_network in server.private_net:
                    if server_private_network.network.id == self.network.id:
                        return to_native(server_private_network.ip)

            else:
                raise AnsibleError(
                    "You can only connect via private IPv4 if you specify a network")

    def _first_ipv6_address(self, network):
        return next(IPv6Network(network).hosts())

    def verify_file(self, path):
        """Return the possibly of a file being consumable by this plugin."""
        return (
            super(InventoryModule, self).verify_file(path) and
            path.endswith(("hcloud.yaml", "hcloud.yml"))
        )

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path, cache)

        if not HAS_HCLOUD:
            raise AnsibleError("The Hetzner Cloud dynamic inventory plugin requires hcloud-python.")

        self._read_config_data(path)
        self._configure_hcloud_client()
        self._test_hcloud_token()
        self._get_servers()
        self._filter_servers()

        # Add a top group
        self.inventory.add_group(group=self.get_option("group"))

        for server in self.servers:
            self.inventory.add_host(server.name, group=self.get_option("group"))
            self._set_server_attributes(server)

            # Use constructed if applicable
            strict = self.get_option('strict')

            # Composed variables
            self._set_composite_vars(self.get_option('compose'), self.inventory.get_host(server.name).get_vars(), server.name, strict=strict)

            # Complex groups based on jinja2 conditionals, hosts that meet the conditional are added to group
            self._add_host_to_composed_groups(self.get_option('groups'), {}, server.name, strict=strict)

            # Create groups based on variable values and add the corresponding hosts to it
            self._add_host_to_keyed_groups(self.get_option('keyed_groups'), {}, server.name, strict=strict)
