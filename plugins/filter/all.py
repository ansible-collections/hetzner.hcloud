from __future__ import annotations

from typing import Literal

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common.text.converters import to_native


# pylint: disable=unused-argument
def load_balancer_status(load_balancer: dict, *args, **kwargs) -> Literal["unknown", "unhealthy", "healthy"]:
    """
    Return the status of a Load Balancer based on its targets.
    """
    try:
        result = "healthy"
        for target in load_balancer["targets"]:
            target_health_status = target.get("health_status")

            # Report missing health status as unknown
            if not target_health_status:
                result = "unknown"
                continue

            for health_status in target_health_status:
                status = health_status.get("status")
                if status == "healthy":
                    continue

                if status in (None, "unknown"):
                    result = "unknown"
                    continue

                if status == "unhealthy":
                    return "unhealthy"

        return result
    except Exception as exc:
        raise AnsibleFilterError(f"load_balancer_status - {to_native(exc)}", orig_exc=exc) from exc


class FilterModule:
    """
    Hetzner Cloud filters.
    """

    def filters(self):
        return {
            "load_balancer_status": load_balancer_status,
        }
