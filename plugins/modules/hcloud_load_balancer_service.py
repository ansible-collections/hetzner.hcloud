#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Hetzner Cloud GmbH <info@hetzner-cloud.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: hcloud_load_balancer_service

short_description: Create and manage the services of cloud Load Balancers on the Hetzner Cloud.


description:
    - Create, update and manage the services of cloud Load Balancers on the Hetzner Cloud.

author:
    - Lukas Kaemmerling (@LKaemmerling)

options:
    load_balancer:
        description:
            - The ID of the Hetzner Cloud Load Balancer to manage.
        type: int
    listen_port:
        description:
            - The Name of the Hetzner Cloud Load Balancer to manage.
        type: str
    load_balancer_type:
        description:
            - The Load Balancer Type of the Hetzner Cloud Load Balancer to manage.
            - Required if Load Balancer does not exists.
        type: str
    location:
        description:
            - Location of Load Balancer.
            - Required if no I(network_zone) is given and Load Balancer does not exists.
        type: str
    network_zone:
        description:
            - Network Zone of Load Balancer.
            - Required of no I(location) is given and Load Balancer does not exists.
        type: str
    labels:
        description:
            - User-defined labels (key-value pairs).
        type: dict
    disable_public_interface:
        description:
            - Disables the public interface.
        type: bool
        default: False
    delete_protection:
        description:
            - Protect the Load Balancer for deletion.
        type: bool
    state:
        description:
            - State of the Load Balancer.
        default: present
        choices: [ absent, present ]
        type: str
extends_documentation_fragment:
- hetzner.hcloud.hcloud

requirements:
  - hcloud-python >= 1.8.0
'''

EXAMPLES = """
- name: Create a basic Load Balancer
  hcloud_load_balancer_service:
    name: my-Load Balancer
    load_balancer_type: lb11
    location: fsn1
    state: present

- name: Ensure the Load Balancer is absent (remove if needed)
  hcloud_load_balancer_service:
    name: my-Load Balancer
    state: absent

"""

RETURN = """
hcloud_load_balancer_service:
    description: The Load Balancer instance
    returned: Always
    type: complex
    contains:
        id:
            description: Numeric identifier of the Load Balancer
            returned: always
            type: int
            sample: 1937415
        name:
            description: Name of the Load Balancer
            returned: always
            type: str
            sample: my-Load-Balancer
        status:
            description: Status of the Load Balancer
            returned: always
            type: str
            sample: running
        load_balancer_type:
            description: Name of the Load Balancer type of the Load Balancer
            returned: always
            type: str
            sample: cx11
        ipv4_address:
            description: Public IPv4 address of the Load Balancer
            returned: always
            type: str
            sample: 116.203.104.109
        ipv6_address:
            description: Public IPv6 address of the Load Balancer
            returned: always
            type: str
            sample: 2a01:4f8:1c1c:c140::1
        location:
            description: Name of the location of the Load Balancer
            returned: always
            type: str
            sample: fsn1
        labels:
            description: User-defined labels (key-value pairs)
            returned: always
            type: dict
        delete_protection:
            description: True if Load Balancer is protected for deletion
            type: bool
            returned: always
            sample: false
        disable_public_interface:
            description: True if Load Balancer public interface is disabled
            type: bool
            returned: always
            sample: false
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from ansible_collections.hetzner.hcloud.plugins.module_utils.hcloud import Hcloud

try:
    from hcloud.load_balancers.domain import LoadBalancer, LoadBalancerService, LoadBalancerServiceHttp, \
        LoadBalancerServiceHealthCheck, LoadBalancerServiceHealthCheckHttp
    from hcloud import APIException
except ImportError:
    pass


class AnsibleHcloudLoadBalancerService(Hcloud):
    def __init__(self, module):
        Hcloud.__init__(self, module, "hcloud_load_balancer_service")
        self.hcloud_load_balancer = None
        self.hcloud_load_balancer_service = None

    def _prepare_result(self):
        return {
            "load_balancer": to_native(self.hcloud_load_balancer.name),
            "protocol": to_native(self.hcloud_load_balancer_service.protocol),
            "listen_port": self.hcloud_load_balancer_service.listen_port,
            "destination_port": self.hcloud_load_balancer_service.destination_port,
            "proxyprotocol": self.hcloud_load_balancer_service.proxyprotocol,
        }

    def _get_load_balancer(self):
        try:
            self.hcloud_load_balancer = self.client.load_balancers.get_by_name(
                self.module.params.get("load_balancer")
            )
            self._get_load_balancer_service()
        except APIException as e:
            self.module.fail_json(msg=e.message)

    def _create_load_balancer_service(self):

        self.module.fail_on_missing_params(
            required_params=["protocol"]
        )
        if self.module.params.get("protocol") == "tcp":
            self.module.fail_on_missing_params(
                required_params=["destination_port"]
            )

        params = {
            "protocol": self.module.params.get("protocol"),
            "listen_port": self.module.params.get("listen_port"),
            "proxyprotocol": self.module.params.get("proxyprotocol")
        }

        if self.module.params.get("destination_port"):
            params["destination_port"] = self.module.params.get("destination_port")

        if self.module.params.get("http"):
            params["http"] = self.__get_service_http(http_arg=self.module.params.get("http"))

        if self.module.params.get("health_check"):
            params["health_check"] = self.__get_service_health_checks(
                health_check=self.module.params.get("health_check"))

        if not self.module.check_mode:
            try:
                self.hcloud_load_balancer.add_service(LoadBalancerService(**params)).wait_until_finished(
                    max_retries=1000)
            except APIException as e:
                self.module.fail_json(msg=e.message)
        self._mark_as_changed()
        self._get_load_balancer()
        self._get_load_balancer_service()

    def __get_service_http(self, http_arg):
        service_http = LoadBalancerServiceHttp(certificates=[])
        if http_arg.get("cookie_name") is not None:
            service_http.cookie_name = http_arg.get("cookie_name")
        if http_arg.get("cookie_lifetime") is not None:
            service_http.cookie_lifetime = http_arg.get("cookie_lifetime")
        if http_arg.get("sticky_sessions") is not None:
            service_http.sticky_sessions = http_arg.get("sticky_sessions")
        if http_arg.get("redirect_http") is not None:
            service_http.redirect_http = http_arg.get("redirect_http")
        if http_arg.get("certificates") is not None:
            certificates = http_arg.get("certificates")
            if certificates is not None:
                for certificate in certificates:
                    hcloud_cert = None
                    try:
                        try:
                            hcloud_cert = self.client.certificates.get_by_name(
                                certificate
                            )
                        except APIException:
                            hcloud_cert = self.client.certificates.get_by_id(
                                certificate
                            )
                    except APIException as e:
                        self.module.fail_json(msg=e.message)
                    service_http.certificates.append(hcloud_cert)

        return service_http

    def __get_service_health_checks(self, health_check):
        service_health_check = LoadBalancerServiceHealthCheck()
        if health_check.get("protocol") is not None:
            service_health_check.protocol = health_check.get("protocol")
        if health_check.get("port") is not None:
            service_health_check.port = health_check.get("port")
        if health_check.get("interval") is not None:
            service_health_check.interval = health_check.get("interval")
        if health_check.get("timeout") is not None:
            service_health_check.timeout = health_check.get("timeout")
        if health_check.get("retries") is not None:
            service_health_check.retries = health_check.get("retries")
        if health_check.get("http") is not None:
            health_check_http = health_check.get("http")
            service_health_check.http = LoadBalancerServiceHealthCheckHttp()
            if health_check_http.get("domain") is not None:
                service_health_check.http.domain = health_check_http.get("domain")
            if health_check_http.get("path") is not None:
                service_health_check.http.path = health_check_http.get("path")
            if health_check_http.get("response") is not None:
                service_health_check.http.response = health_check_http.get("response")
            if health_check_http.get("status_codes") is not None:
                service_health_check.http.status_codes = health_check_http.get("status_codes")
            if health_check_http.get("tls") is not None:
                service_health_check.http.tls = health_check_http.get("tls")

        return service_health_check

    def _update_load_balancer_service(self):
        try:
            params = {
                "listen_port": self.module.params.get("listen_port"),
            }

            if self.module.params.get("destination_port"):
                params["destination_port"] = self.module.params.get("destination_port")

            if self.module.params.get("protocol"):
                params["protocol"] = self.module.params.get("protocol")

            if self.module.params.get("proxyprotocol"):
                params["proxyprotocol"] = self.module.params.get("proxyprotocol")

            if self.module.params.get("http"):
                params["http"] = self.__get_service_http(http_arg=self.module.params.get("http"))

            if self.module.params.get("health_check"):
                params["health_check"] = self.__get_service_health_checks(
                    health_check=self.module.params.get("health_check"))

            if not self.module.check_mode:
                self.hcloud_load_balancer.update_service(LoadBalancerService(**params)).wait_until_finished(
                    max_retries=1000)
            self._mark_as_changed()
        except APIException as e:
            self.module.fail_json(msg=e.message)
        self._get_load_balancer()

    def _get_load_balancer_service(self):
        for service in self.hcloud_load_balancer.services:
            if self.module.params.get("listen_port") == service.listen_port:
                self.hcloud_load_balancer_service = service

    def present_load_balancer_service(self):
        self._get_load_balancer()
        if self.hcloud_load_balancer_service is None:
            self._create_load_balancer_service()
        else:
            self._update_load_balancer_service()

    def delete_load_balancer_service(self):
        try:
            self._get_load_balancer()
            if self.hcloud_load_balancer_service is not None:
                if not self.module.check_mode:
                    self.hcloud_load_balancer.delete_service(self.hcloud_load_balancer_service).wait_until_finished(
                        max_retries=1000)
                self._mark_as_changed()
            self.hcloud_load_balancer_service = None
        except APIException as e:
            self.module.fail_json(msg=e.message)

    @staticmethod
    def define_module():
        return AnsibleModule(
            argument_spec=dict(
                load_balancer={"type": "str", "required": True},
                listen_port={"type": "int", "required": True},
                destination_port={"type": "int"},
                protocol={
                    "type": "str",
                    "choices": ["http", "https", "tcp"],
                },
                proxyprotocol={"type": "bool", "default": False},
                http={
                    "type": "dict",
                    "options": dict(
                        cookie_name={
                            "type": "str"
                        },
                        cookie_lifetime={
                            "type": "int"
                        },
                        sticky_sessions={
                            "type": "bool",
                            "default": False
                        },
                        redirect_http={
                            "type": "bool",
                            "default": False
                        },
                        certificates={
                            "type": "list",
                            "elements": "str"
                        },

                    )
                },
                health_check={
                    "type": "dict",
                    "options": dict(
                        protocol={
                            "type": "str",
                            "choices": ["http", "https", "tcp"],
                        },
                        port={
                            "type": "int"
                        },
                        interval={
                            "type": "int"
                        },
                        timeout={
                            "type": "int"
                        },
                        retries={
                            "type": "int"
                        },
                        http={
                            "type": "dict",
                            "options": dict(
                                domain={
                                    "type": "str"
                                },
                                path={
                                    "type": "str"
                                },
                                response={
                                    "type": "str"
                                },
                                status_codes={
                                    "type": "list",
                                    "elements": "str"
                                },
                                tls={
                                    "type": "bool",
                                    "default": False
                                },
                            )
                        }
                    )

                },
                state={
                    "choices": ["absent", "present"],
                    "default": "present",
                },
                **Hcloud.base_module_arguments()
            ),
            supports_check_mode=True,
        )


def main():
    module = AnsibleHcloudLoadBalancerService.define_module()

    hcloud = AnsibleHcloudLoadBalancerService(module)
    state = module.params.get("state")
    if state == "absent":
        hcloud.delete_load_balancer_service()
    elif state == "present":
        hcloud.present_load_balancer_service()

    module.exit_json(**hcloud.get_result())


if __name__ == "__main__":
    main()
