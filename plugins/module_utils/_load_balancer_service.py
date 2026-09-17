# Note that this module util is **PRIVATE** to the collection. It can have breaking changes at any time.
# Do not use this from other collections or standalone plugins/modules!

from __future__ import annotations

from ._vendor.hcloud.load_balancers import (
    LoadBalancerHealthCheck,
    LoadBalancerHealthCheckHttp,
    LoadBalancerService,
    LoadBalancerServiceHttp,
)


def prepare_result(o: LoadBalancerService) -> dict:
    return {
        "listen_port": o.listen_port,
        "protocol": o.protocol,
        "destination_port": o.destination_port,
        "proxyprotocol": o.proxyprotocol,
        "http": prepare_http_result(o.http) if o.protocol in ("http", "https") and o.http is not None else None,
        "health_check": prepare_health_check_result(o.health_check) if o.health_check is not None else None,
    }


def prepare_http_result(o: LoadBalancerServiceHttp) -> dict:
    return {
        "cookie_name": o.cookie_name,
        "cookie_lifetime": o.cookie_lifetime,
        "redirect_http": o.redirect_http,
        "sticky_sessions": o.sticky_sessions,
        "timeout_idle": o.timeout_idle,
        "certificates": [certificate.name for certificate in o.certificates or []],
    }


def prepare_health_check_result(o: LoadBalancerHealthCheck) -> dict:
    return {
        "protocol": o.protocol,
        "port": o.port,
        "interval": o.interval,
        "timeout": o.timeout,
        "retries": o.retries,
        "http": (
            prepare_health_check_http_result(o.http)
            if (o.protocol in ("http", "https") and o.http is not None)
            else None
        ),
    }


def prepare_health_check_http_result(o: LoadBalancerHealthCheckHttp) -> dict:
    return {
        "domain": o.domain,
        "path": o.path,
        "response": o.response,
        "status_codes": o.status_codes or [],
        "tls": o.tls,
    }
