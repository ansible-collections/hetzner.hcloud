from __future__ import annotations

from ipaddress import ip_interface


def normalize_ip(value: str) -> str:
    return str(ip_interface(value))
