# Note that this module util is **PRIVATE** to the collection. It can have breaking changes at any time.
# Do not use this from other collections or standalone plugins/modules!

from __future__ import annotations

from ipaddress import ip_interface


def normalize_ip(value: str) -> str:
    return str(ip_interface(value))
