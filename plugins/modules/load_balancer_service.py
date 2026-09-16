#!/usr/bin/python

# Copyright: (c) 2020, Hetzner Cloud GmbH <info@hetzner-cloud.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import annotations

DOCUMENTATION = """
---
module: load_balancer_service

short_description: Create and manage the services of cloud Load Balancers on the Hetzner Cloud.


description:
    - Create, update and manage the services of cloud Load Balancers on the Hetzner Cloud.

author:
    - Lukas Kaemmerling (@LKaemmerling)
version_added: 0.1.0
options:
    load_balancer:
        description:
            - Name or ID of the Hetzner Cloud Load Balancer the service belongs to
        type: str
        required: true
    listen_port:
        description:
            - The port the service listens on, i.e. the port users can connect to.
        type: int
        required: true
    destination_port:
        description:
            - The port traffic is forwarded to, i.e. the port the targets are listening and accepting connections on.
            - Required if services does not exist and protocol is tcp.
        type: int
    protocol:
        description:
            - Protocol of the service.
            - Required if Load Balancer does not exist.
        type: str
        choices: [ http, https, tcp ]
    proxyprotocol:
        description:
            - Enable the PROXY protocol.
        type: bool
        default: False
    http:
        description:
            - Configuration for HTTP and HTTPS services
        type: dict
        suboptions:
            cookie_name:
                description:
                    - Name of the cookie which will be set when you enable sticky sessions
                type: str
            cookie_lifetime:
                description:
                    - Lifetime of the cookie which will be set when you enable sticky sessions, in seconds
                type: int
            certificates:
                description:
                    - List of Names or IDs of certificates
                type: list
                elements: str
            sticky_sessions:
                description:
                    - Enable or disable sticky_sessions
                type: bool
                default: False
            redirect_http:
                description:
                    - Redirect Traffic from Port 80 to Port 443, only available if protocol is https
                type: bool
                default: False
            timeout_idle:
                description:
                    - Idle timeout in seconds for HTTP connections. Must be between 30 and 300 seconds.
                type: int
    health_check:
        description:
            - Configuration for health checks
        type: dict
        suboptions:
            protocol:
                description:
                    - Protocol the health checks will be performed over
                type: str
                choices: [ http, https, tcp ]
            port:
                description:
                    - Port the health check will be performed on
                type: int
            interval:
                description:
                    - Interval of health checks, in seconds
                type: int
            timeout:
                description:
                    - Timeout of health checks, in seconds
                type: int
            retries:
                description:
                    - Number of retries until a target is marked as unhealthy
                type: int
            http:
                description:
                    - Additional Configuration of health checks with protocol http/https
                type: dict
                suboptions:
                    domain:
                        description:
                            - Domain we will set within the HTTP HOST header
                        type: str
                    path:
                        description:
                            - Path we will try to access
                        type: str
                    response:
                        description:
                            - Response we expect, if response is not within the health check response the target is unhealthy
                        type: str
                    status_codes:
                        description:
                            - List of HTTP status codes we expect to get when we perform the health check.
                        type: list
                        elements: str
                    tls:
                        description:
                            - Verify the TLS certificate, only available if health check protocol is https
                        type: bool
                        default: False
    state:
        description:
            - State of the Load Balancer.
        default: present
        choices: [ absent, present ]
        type: str
extends_documentation_fragment:
- hetzner.hcloud.hcloud
"""

EXAMPLES = """
- name: Create a basic Load Balancer service with Port 80
  hetzner.hcloud.load_balancer_service:
    load_balancer: my-load-balancer
    protocol: http
    listen_port: 80
    state: present

- name: Ensure the Load Balancer is absent (remove if needed)
  hetzner.hcloud.load_balancer_service:
    load_balancer: my-Load Balancer
    protocol: http
    listen_port: 80
    state: absent
"""

RETURN = """
hcloud_load_balancer_service:
    description: The Load Balancer service instance
    returned: Always
    type: dict
    contains:
        load_balancer:
            description: The name of the Load Balancer where the service belongs to
            returned: always
            type: str
            sample: my-load-balancer
        listen_port:
            description: The port the service listens on, i.e. the port users can connect to.
            returned: always
            type: int
            sample: 443
        protocol:
            description: Protocol of the service
            returned: always
            type: str
            sample: http
        destination_port:
            description:
               - The port traffic is forwarded to, i.e. the port the targets are listening and accepting connections on.
            returned: always
            type: int
            sample: 80
        proxyprotocol:
            description:
                - Enable the PROXY protocol.
            returned: always
            type: bool
            sample: false
        http:
            description: Configuration for HTTP and HTTPS services
            returned: always
            type: dict
            contains:
                cookie_name:
                    description: Name of the cookie which will be set when you enable sticky sessions
                    returned: always
                    type: str
                    sample: HCLBSTICKY
                cookie_lifetime:
                    description: Lifetime of the cookie which will be set when you enable sticky sessions, in seconds
                    returned: always
                    type: int
                    sample: 3600
                certificates:
                    description: List of Names or IDs of certificates
                    returned: always
                    type: list
                    elements: str
                sticky_sessions:
                    description: Enable or disable sticky_sessions
                    returned: always
                    type: bool
                    sample: true
                redirect_http:
                    description: Redirect Traffic from Port 80 to Port 443, only available if protocol is https
                    returned: always
                    type: bool
                    sample: false
                timeout_idle:
                    description: Idle timeout in seconds for HTTP connections.
                    returned: always
                    type: int
                    sample: 50
        health_check:
            description: Configuration for health checks
            returned: always
            type: dict
            contains:
                protocol:
                    description: Protocol the health checks will be performed over
                    returned: always
                    type: str
                    sample: http
                port:
                    description: Port the health check will be performed on
                    returned: always
                    type: int
                    sample: 80
                interval:
                    description: Interval of health checks, in seconds
                    returned: always
                    type: int
                    sample: 15
                timeout:
                    description: Timeout of health checks, in seconds
                    returned: always
                    type: int
                    sample: 10
                retries:
                    description: Number of retries until a target is marked as unhealthy
                    returned: always
                    type: int
                    sample: 3
                http:
                    description: Additional Configuration of health checks with protocol http/https
                    returned: always
                    type: dict
                    contains:
                        domain:
                            description: Domain we will set within the HTTP HOST header
                            returned: always
                            type: str
                            sample: example.com
                        path:
                            description: Path we will try to access
                            returned: always
                            type: str
                            sample: /
                        response:
                            description: Response we expect, if response is not within the health check response the target is unhealthy
                            returned: always
                            type: str
                        status_codes:
                            description: List of HTTP status codes we expect to get when we perform the health check.
                            returned: always
                            type: list
                            elements: str
                            sample: ["2??","3??"]
                        tls:
                            description: Verify the TLS certificate, only available if health check protocol is https
                            returned: always
                            type: bool
                            sample: false
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import _load_balancer_service
from ..module_utils._base import AnsibleHCloud
from ..module_utils._vendor.hcloud import APIException, HCloudException
from ..module_utils._vendor.hcloud.load_balancers import (
    BoundLoadBalancer,
    LoadBalancerHealthCheck,
    LoadBalancerHealthCheckHttp,
    LoadBalancerService,
    LoadBalancerServiceHttp,
)


class AnsibleHCloudLoadBalancerService(AnsibleHCloud):
    represent = "hcloud_load_balancer_service"

    hcloud_load_balancer: BoundLoadBalancer | None = None
    hcloud_load_balancer_service: LoadBalancerService | None = None

    def _prepare_result(self):
        return {
            "load_balancer": self.hcloud_load_balancer.name,
            **_load_balancer_service.prepare_result(self.hcloud_load_balancer_service),
        }

    def _fetch(self):
        self.hcloud_load_balancer = self._client_get_by_name_or_id(
            "load_balancers",
            self.module.params.get("load_balancer"),
        )

        for service in self.hcloud_load_balancer.services:
            if self.module.params.get("listen_port") == service.listen_port:
                self.hcloud_load_balancer_service = service

    def _make_service_http(
        self, params: dict, current: LoadBalancerServiceHttp | None
    ) -> tuple[LoadBalancerServiceHttp, bool]:
        changed = False
        result = LoadBalancerServiceHttp()
        if (wanted := params.get("cookie_name")) is not None:
            if current is None or current.cookie_name != wanted:
                result.cookie_name = wanted
                changed = True
        if (wanted := params.get("cookie_lifetime")) is not None:
            if current is None or current.cookie_lifetime != wanted:
                result.cookie_lifetime = wanted
                changed = True
        if (wanted := params.get("sticky_sessions")) is not None:
            if current is None or current.sticky_sessions != wanted:
                result.sticky_sessions = wanted
                changed = True
        if (wanted := params.get("redirect_http")) is not None:
            if current is None or current.redirect_http != wanted:
                result.redirect_http = wanted
                changed = True
        if (wanted := params.get("timeout_idle")) is not None:
            if current is None or current.timeout_idle != wanted:
                result.timeout_idle = wanted
                changed = True
        if (wanted := params.get("certificates")) is not None:
            wanted_certificates = [
                self._client_get_by_name_or_id(
                    "certificates",
                    id_or_name,
                )
                for id_or_name in wanted
            ]
            wanted_certificates_ids = sorted(o.id for o in wanted_certificates)
            current_certificates_ids = sorted(o.id for o in current.certificates or [])
            if current is None or current_certificates_ids != wanted_certificates_ids:
                result.certificates = wanted_certificates
                changed = True
        return result, changed

    def _make_service_health_check(
        self, params: dict, current: LoadBalancerHealthCheck
    ) -> tuple[LoadBalancerHealthCheck, bool]:
        changed = False
        result = LoadBalancerHealthCheck()
        if (wanted := params.get("protocol")) is not None:
            if current is None or current.protocol != wanted:
                result.protocol = wanted
                changed = True
        if (wanted := params.get("port")) is not None:
            if current is None or current.port != wanted:
                result.port = wanted
                changed = True
        if (wanted := params.get("interval")) is not None:
            if current is None or current.interval != wanted:
                result.interval = wanted
                changed = True
        if (wanted := params.get("timeout")) is not None:
            if current is None or current.timeout != wanted:
                result.timeout = wanted
                changed = True
        if (wanted := params.get("retries")) is not None:
            if current is None or current.retries != wanted:
                result.retries = wanted
                changed = True
        if (wanted := params.get("http")) is not None:
            wanted_http, changed_http = self._make_service_health_check_http(wanted, current and current.http)
            if current is None or changed_http:
                result.http = wanted_http
                changed = True
        return result, changed

    def _make_service_health_check_http(
        self, params: dict, current: LoadBalancerHealthCheckHttp | None
    ) -> tuple[LoadBalancerHealthCheckHttp, bool]:
        changed = False
        result = LoadBalancerHealthCheckHttp()
        if (wanted := params.get("domain")) is not None:
            if current is None or current.domain != wanted:
                result.domain = wanted
                changed = True
        if (wanted := params.get("path")) is not None:
            if current is None or current.path != wanted:
                result.path = wanted
                changed = True
        if (wanted := params.get("response")) is not None:
            if current is None or current.response != wanted:
                result.response = wanted
                changed = True
        if (wanted := params.get("status_codes")) is not None:
            if current is None or current.status_codes != wanted:
                result.status_codes = wanted
                changed = True
        if (wanted := params.get("tls")) is not None:
            if current is None or current.tls != wanted:
                result.tls = wanted
                changed = True
        return result, changed

    def _create(self):
        self.module.fail_on_missing_params(required_params=["protocol"])
        if self.module.params.get("protocol") == "tcp":
            self.module.fail_on_missing_params(required_params=["destination_port"])

        params = {
            "protocol": self.module.params.get("protocol"),
            "listen_port": self.module.params.get("listen_port"),
            "proxyprotocol": self.module.params.get("proxyprotocol"),
        }

        if value := self.module.params.get("destination_port"):
            params["destination_port"] = value

        if value := self.module.params.get("http"):
            params["http"], _ = self._make_service_http(value, None)

        if value := self.module.params.get("health_check"):
            params["health_check"], _ = self._make_service_health_check(value, None)

        if not self.module.check_mode:
            action = self.hcloud_load_balancer.add_service(LoadBalancerService(**params))
            action.wait_until_finished()

        self._mark_as_changed()
        self._fetch()

    def _update(self):
        changed = False

        params = {
            "listen_port": self.module.params.get("listen_port"),
        }

        if (wanted := self.module.params.get("destination_port")) is not None:
            if self.hcloud_load_balancer_service.destination_port != wanted:
                params["destination_port"] = wanted
                changed = True

        if (wanted := self.module.params.get("protocol")) is not None:
            if self.hcloud_load_balancer_service.protocol != wanted:
                params["protocol"] = wanted
                changed = True

        if (wanted := self.module.params.get("proxyprotocol")) is not None:
            if self.hcloud_load_balancer_service.proxyprotocol != wanted:
                params["proxyprotocol"] = wanted
                changed = True

        if (wanted := self.module.params.get("http")) is not None:
            wanted_http, changed_http = self._make_service_http(
                wanted,
                self.hcloud_load_balancer_service.http,
            )
            if changed_http:
                params["http"] = wanted_http
                changed = True

        if (wanted := self.module.params.get("health_check")) is not None:
            wanted_health_check, changed_health_check = self._make_service_health_check(
                wanted,
                self.hcloud_load_balancer_service.health_check,
            )
            if changed_health_check:
                params["health_check"] = wanted_health_check
                changed = True

        if changed and not self.module.check_mode:
            action = self.hcloud_load_balancer.update_service(LoadBalancerService(**params))
            action.wait_until_finished()
            self._fetch()

        if changed:
            self._mark_as_changed()

    def _delete(self):
        if not self.module.check_mode:
            action = self.hcloud_load_balancer.delete_service(self.hcloud_load_balancer_service)
            action.wait_until_finished()
        self._mark_as_changed()
        self.hcloud_load_balancer_service = None

    def present(self):
        try:
            self._fetch()
            if self.hcloud_load_balancer_service is None:
                self._create()
            else:
                self._update()

        except HCloudException as exception:
            self.fail_json_hcloud(exception)

    def absent(self):
        try:
            self._fetch()
            if self.hcloud_load_balancer_service is not None:
                self._delete()

        except APIException as exception:
            self.fail_json_hcloud(exception)

    @classmethod
    def define_module(cls):
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
                        cookie_name={"type": "str"},
                        cookie_lifetime={"type": "int"},
                        sticky_sessions={"type": "bool", "default": False},
                        redirect_http={"type": "bool", "default": False},
                        timeout_idle={"type": "int"},
                        certificates={"type": "list", "elements": "str"},
                    ),
                },
                health_check={
                    "type": "dict",
                    "options": dict(
                        protocol={
                            "type": "str",
                            "choices": ["http", "https", "tcp"],
                        },
                        port={"type": "int"},
                        interval={"type": "int"},
                        timeout={"type": "int"},
                        retries={"type": "int"},
                        http={
                            "type": "dict",
                            "options": dict(
                                domain={"type": "str"},
                                path={"type": "str"},
                                response={"type": "str"},
                                status_codes={"type": "list", "elements": "str"},
                                tls={"type": "bool", "default": False},
                            ),
                        },
                    ),
                },
                state={
                    "choices": ["absent", "present"],
                    "default": "present",
                },
                **super().base_module_arguments(),
            ),
            supports_check_mode=True,
        )


def main():
    module = AnsibleHCloudLoadBalancerService.define_module()

    hcloud = AnsibleHCloudLoadBalancerService(module)
    state = module.params.get("state")
    if state == "absent":
        hcloud.absent()
    elif state == "present":
        hcloud.present()

    module.exit_json(**hcloud.get_result())


if __name__ == "__main__":
    main()
