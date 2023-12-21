# Copyright (c) 2019 Hetzner Cloud GmbH <info@hetzner-cloud.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations

DOCUMENTATION = """
name: hcloud
short_description: Ansible dynamic inventory plugin for the Hetzner Cloud.

description:
  - Reads inventories from the Hetzner Cloud API.
  - Uses a YAML configuration file that ends with C(hcloud.yml) or C(hcloud.yaml).

author:
  - Lukas Kaemmerling (@lkaemmerling)

requirements:
  - python-dateutil >= 2.7.5
  - requests >=2.20

extends_documentation_fragment:
  - constructed
  - inventory_cache

options:
  plugin:
    description: Mark this as an P(hetzner.hcloud.hcloud#inventory) inventory instance.
    required: true
    choices: [hcloud, hetzner.hcloud.hcloud]

  api_token:
    description:
      - The API Token for the Hetzner Cloud.
    type: str
    required: false # TODO: Mark as required once 'api_token_env' is removed.
    aliases: [token]
    env:
      - name: HCLOUD_TOKEN
  api_token_env:
    description:
      - Environment variable name to load the Hetzner Cloud API Token from.
    type: str
    default: HCLOUD_TOKEN
    aliases: [token_env]
    deprecated:
      why: The option is adding too much complexity, while the alternatives are preferred.
      collection_name: hetzner.hcloud
      version: 3.0.0
      alternatives: Use the P(ansible.builtin.env#lookup) lookup plugin instead.
  api_endpoint:
    description:
      - The API Endpoint for the Hetzner Cloud.
    type: str
    default: https://api.hetzner.cloud/v1
    env:
      - name: HCLOUD_ENDPOINT

  group:
    description: The group all servers are automatically added to.
    default: hcloud
    type: str
    required: false
  connect_with:
    description: |
      Connect to the server using the value from this field. This sets the C(ansible_host)
      variable to the value indicated, if that value is available. If you need further
      customization, like falling back to private ipv4 if the server has no public ipv4,
      you can use O(compose) top-level key.
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

  hostvars_prefix:
    description:
      - The prefix for host variables names coming from Hetzner Cloud.
    type: str
    version_added: 2.5.0
  hostvars_suffix:
    description:
      - The suffix for host variables names coming from Hetzner Cloud.
    type: str
    version_added: 2.5.0
"""

EXAMPLES = """
# Minimal example. 'HCLOUD_TOKEN' is exposed in environment.
plugin: hetzner.hcloud.hcloud

---
# Example with templated token, e.g. provided through extra vars.
plugin: hetzner.hcloud.hcloud
api_token: "{{ _vault_hetzner_cloud_token }}"

---
# Example with locations, types, status
plugin: hetzner.hcloud.hcloud
locations:
  - nbg1
types:
  - cx11
status:
  - running

---
# Group by a location with prefix e.g. "hcloud_location_nbg1"
# and image_os_flavor without prefix and separator e.g. "ubuntu"
# and status with prefix e.g. "server_status_running"
plugin: hetzner.hcloud.hcloud
keyed_groups:
  - key: location
    prefix: hcloud_location
  - key: image_os_flavor
    separator: ""
  - key: status
    prefix: server_status
"""

import os
import sys
from ipaddress import IPv6Network

from ansible.errors import AnsibleError
from ansible.inventory.manager import InventoryData
from ansible.module_utils.common.text.converters import to_native
from ansible.plugins.inventory import BaseInventoryPlugin, Cacheable, Constructable
from ansible.utils.display import Display

from ..module_utils.client import (
    Client,
    ClientException,
    client_check_required_lib,
    client_get_by_name_or_id,
)
from ..module_utils.vendor.hcloud import APIException
from ..module_utils.vendor.hcloud.networks import Network
from ..module_utils.vendor.hcloud.servers import Server
from ..module_utils.version import version

if sys.version_info >= (3, 11):
    # The typed dicts are only used to help development and we prefer not requiring
    # the additional typing-extensions dependency
    from typing import NotRequired, TypedDict

    class InventoryPrivateNetwork(TypedDict):
        id: int
        name: str
        ip: str

    class InventoryServer(TypedDict):
        id: int
        name: str
        status: str

        # Server Type
        type: str
        server_type: str
        architecture: str

        # Datacenter
        datacenter: str
        location: str

        # Labels
        labels: dict[str, str]

        # Network
        ipv4: NotRequired[str]
        ipv6: NotRequired[str]
        ipv6_network: NotRequired[str]
        ipv6_network_mask: NotRequired[str]
        private_ipv4: NotRequired[str]
        private_networks: list[InventoryPrivateNetwork]

        # Image
        image_id: int
        image_name: str
        image_os_flavor: str

        # Ansible
        ansible_host: str

else:
    InventoryServer = dict


def first_ipv6_address(network: str) -> str:
    """
    Return the first address for a ipv6 network.

    :param network: IPv6 Network.
    """
    return next(IPv6Network(network).hosts())


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):
    NAME = "hetzner.hcloud.hcloud"

    inventory: InventoryData
    display: Display

    client: Client

    network: Network | None

    def _configure_hcloud_client(self):
        # If api_token_env is not the default, print a deprecation warning and load the
        # environment variable.
        api_token_env = self.get_option("api_token_env")
        if api_token_env != "HCLOUD_TOKEN":
            self.display.deprecated(
                "The 'api_token_env' option is deprecated, please use the 'HCLOUD_TOKEN' "
                "environment variable or use the 'ansible.builtin.env' lookup instead.",
                version="3.0.0",
                collection_name="hetzner.hcloud",
            )
            if api_token_env in os.environ:
                self.set_option("api_token", os.environ.get(api_token_env))

        api_token = self.get_option("api_token")
        api_endpoint = self.get_option("api_endpoint")

        if api_token is None:  # TODO: Remove once I(api_token_env) is removed.
            raise AnsibleError(
                "No setting was provided for required configuration setting: "
                "plugin_type: inventory "
                "plugin: hetzner.hcloud.hcloud "
                "setting: api_token"
            )

        # Resolve template string
        api_token = self.templar.template(api_token)

        self.client = Client(
            token=api_token,
            api_endpoint=api_endpoint,
            application_name="ansible-inventory",
            application_version=version,
        )

        try:
            # Ensure the api token is valid
            self.client.locations.get_list()
        except APIException as exception:
            raise AnsibleError("Invalid Hetzner Cloud API Token.") from exception

    def _validate_options(self) -> None:
        if self.get_option("network"):
            network_param: str = self.get_option("network")
            network_param = self.templar.template(network_param)

            try:
                self.network = client_get_by_name_or_id(self.client, "networks", network_param)
            except (ClientException, APIException) as exception:
                raise AnsibleError(to_native(exception)) from exception

    def _fetch_servers(self) -> list[Server]:
        self._validate_options()

        get_servers_params = {}
        if self.get_option("label_selector"):
            get_servers_params["label_selector"] = self.get_option("label_selector")

        if self.get_option("status"):
            get_servers_params["status"] = self.get_option("status")

        servers = self.client.servers.get_all(**get_servers_params)

        if self.get_option("network"):
            servers = [s for s in servers if self.network.id in [p.network.id for p in s.private_net]]

        if self.get_option("locations"):
            locations: list[str] = self.get_option("locations")
            servers = [s for s in servers if s.datacenter.location.name in locations]

        if self.get_option("types"):
            server_types: list[str] = self.get_option("types")
            servers = [s for s in servers if s.server_type.name in server_types]

        if self.get_option("images"):
            images: list[str] = self.get_option("images")
            servers = [s for s in servers if s.image is not None and s.image.os_flavor in images]

        return servers

    def _build_inventory_server(self, server: Server) -> InventoryServer:
        server_dict: InventoryServer = {}
        server_dict["id"] = server.id
        server_dict["name"] = to_native(server.name)
        server_dict["status"] = to_native(server.status)

        # Server Type
        server_dict["type"] = to_native(server.server_type.name)
        server_dict["server_type"] = to_native(server.server_type.name)
        server_dict["architecture"] = to_native(server.server_type.architecture)

        # Network
        if server.public_net.ipv4:
            server_dict["ipv4"] = to_native(server.public_net.ipv4.ip)

        if server.public_net.ipv6:
            server_dict["ipv6"] = to_native(first_ipv6_address(server.public_net.ipv6.ip))
            server_dict["ipv6_network"] = to_native(server.public_net.ipv6.network)
            server_dict["ipv6_network_mask"] = to_native(server.public_net.ipv6.network_mask)

        server_dict["private_networks"] = [
            {"id": v.network.id, "name": to_native(v.network.name), "ip": to_native(v.ip)} for v in server.private_net
        ]

        if self.get_option("network"):
            for private_net in server.private_net:
                # Set private_ipv4 if user filtered for one network
                if private_net.network.id == self.network.id:
                    server_dict["private_ipv4"] = to_native(private_net.ip)
                    break

        # Datacenter
        server_dict["datacenter"] = to_native(server.datacenter.name)
        server_dict["location"] = to_native(server.datacenter.location.name)

        # Image
        if server.image is not None:
            server_dict["image_id"] = server.image.id
            server_dict["image_os_flavor"] = to_native(server.image.os_flavor)
            server_dict["image_name"] = to_native(server.image.name or server.image.description)

        # Labels
        server_dict["labels"] = dict(server.labels)

        try:
            server_dict["ansible_host"] = self._get_server_ansible_host(server)
        except AnsibleError as exception:
            # Log warning that for this host can not be connected to, using the
            # method specified in 'connect_with'. Users might use 'compose' to
            # override the connection method, or implement custom logic, so we
            # do not need to abort if nothing matched.
            self.display.v(f"[hcloud] {exception}", server.name)

        return server_dict

    def _get_server_ansible_host(self, server: Server):
        if self.get_option("connect_with") == "public_ipv4":
            if server.public_net.ipv4:
                return to_native(server.public_net.ipv4.ip)
            raise AnsibleError("Server has no public ipv4, but connect_with=public_ipv4 was specified")

        if self.get_option("connect_with") == "public_ipv6":
            if server.public_net.ipv6:
                return to_native(first_ipv6_address(server.public_net.ipv6.ip))
            raise AnsibleError("Server has no public ipv6, but connect_with=public_ipv6 was specified")

        if self.get_option("connect_with") == "hostname":
            # every server has a name, no need to guard this
            return to_native(server.name)

        if self.get_option("connect_with") == "ipv4_dns_ptr":
            if server.public_net.ipv4:
                return to_native(server.public_net.ipv4.dns_ptr)
            raise AnsibleError("Server has no public ipv4, but connect_with=ipv4_dns_ptr was specified")

        if self.get_option("connect_with") == "private_ipv4":
            if self.get_option("network"):
                for private_net in server.private_net:
                    if private_net.network.id == self.network.id:
                        return to_native(private_net.ip)

            else:
                raise AnsibleError("You can only connect via private IPv4 if you specify a network")

    def verify_file(self, path):
        """Return the possibly of a file being consumable by this plugin."""
        return super().verify_file(path) and path.endswith(("hcloud.yaml", "hcloud.yml"))

    def _get_cached_result(self, path, cache) -> tuple[list[InventoryServer], bool]:
        # false when refresh_cache or --flush-cache is used
        if not cache:
            return [], False

        # get the user-specified directive
        if not self.get_option("cache"):
            return [], False

        cache_key = self.get_cache_key(path)
        try:
            cached_result = self._cache[cache_key]
        except KeyError:
            # if cache expires or cache file doesn"t exist
            return [], False

        return cached_result, True

    def _update_cached_result(self, path, cache, result: list[InventoryServer]):
        if not self.get_option("cache"):
            return

        cache_key = self.get_cache_key(path)
        # We weren't explicitly told to flush the cache, and there's already a cache entry,
        # this means that the result we're being passed came from the cache.  As such we don't
        # want to "update" the cache as that could reset a TTL on the cache entry.
        if cache and cache_key in self._cache:
            return

        self._cache[cache_key] = result

    def parse(self, inventory, loader, path, cache=True):
        super().parse(inventory, loader, path, cache)

        try:
            client_check_required_lib()
        except ClientException as exception:
            raise AnsibleError(to_native(exception)) from exception

        # Allow using extra variables arguments as template variables (e.g.
        # '--extra-vars my_var=my_value')
        self.templar.available_variables = self._vars

        self._read_config_data(path)
        self._configure_hcloud_client()

        servers, cached = self._get_cached_result(path, cache)
        if not cached:
            with self.client.cached_session():
                servers = [self._build_inventory_server(s) for s in self._fetch_servers()]

        # Add a top group
        self.inventory.add_group(group=self.get_option("group"))

        hostvars_prefix = self.get_option("hostvars_prefix")
        hostvars_suffix = self.get_option("hostvars_suffix")

        for server in servers:
            self.inventory.add_host(server["name"], group=self.get_option("group"))
            for key, value in server.items():
                # Add hostvars prefix and suffix for variables coming from the Hetzner Cloud.
                if hostvars_prefix or hostvars_suffix:
                    if key not in ("ansible_host",):
                        if hostvars_prefix:
                            key = hostvars_prefix + key
                        if hostvars_suffix:
                            key = key + hostvars_suffix

                self.inventory.set_variable(server["name"], key, value)

            # Use constructed if applicable
            strict = self.get_option("strict")

            # Composed variables
            self._set_composite_vars(
                self.get_option("compose"),
                self.inventory.get_host(server["name"]).get_vars(),
                server["name"],
                strict=strict,
            )

            # Complex groups based on jinja2 conditionals, hosts that meet the conditional are added to group
            self._add_host_to_composed_groups(
                self.get_option("groups"),
                {},
                server["name"],
                strict=strict,
            )

            # Create groups based on variable values and add the corresponding hosts to it
            self._add_host_to_keyed_groups(
                self.get_option("keyed_groups"),
                {},
                server["name"],
                strict=strict,
            )

        self._update_cached_result(path, cache, servers)
