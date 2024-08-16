from __future__ import annotations

import pytest

from plugins.filter.all import load_balancer_status


def _lb_target_server(status: str) -> dict:
    return {"type": "server", "health_status": [{"status": status}]}


def _lb_target_label_selector(status: str) -> dict:
    return {"type": "label_selector", "targets": [_lb_target_server(status)]}


LOAD_BALANCER_STATUS_TEST_CASES = (
    ({"targets": [{"type": "server", "health_status": []}]}, "unknown"),
    ({"targets": [{"type": "server", "health_status": [{}]}]}, "unknown"),
    ({"targets": [_lb_target_server("healthy")]}, "healthy"),
    ({"targets": [_lb_target_server("unhealthy")]}, "unhealthy"),
    ({"targets": [_lb_target_server("unknown")]}, "unknown"),
    ({"targets": [_lb_target_label_selector("healthy"), _lb_target_server("healthy")]}, "healthy"),
    ({"targets": [_lb_target_label_selector("healthy"), _lb_target_server("unhealthy")]}, "unhealthy"),
    ({"targets": [_lb_target_label_selector("healthy"), _lb_target_server("unknown")]}, "unknown"),
    ({"targets": [_lb_target_label_selector("unhealthy"), _lb_target_server("healthy")]}, "unhealthy"),
    ({"targets": [_lb_target_label_selector("unhealthy"), _lb_target_server("unhealthy")]}, "unhealthy"),
    ({"targets": [_lb_target_label_selector("unhealthy"), _lb_target_server("unknown")]}, "unhealthy"),
    ({"targets": [_lb_target_label_selector("unknown"), _lb_target_server("healthy")]}, "unknown"),
    ({"targets": [_lb_target_label_selector("unknown"), _lb_target_server("unhealthy")]}, "unhealthy"),
    ({"targets": [_lb_target_label_selector("unknown"), _lb_target_server("unknown")]}, "unknown"),
    ({"targets": [_lb_target_server("healthy"), _lb_target_label_selector("healthy")]}, "healthy"),
    ({"targets": [_lb_target_server("healthy"), _lb_target_label_selector("unhealthy")]}, "unhealthy"),
    ({"targets": [_lb_target_server("healthy"), _lb_target_label_selector("unknown")]}, "unknown"),
    ({"targets": [_lb_target_server("unhealthy"), _lb_target_label_selector("healthy")]}, "unhealthy"),
    ({"targets": [_lb_target_server("unhealthy"), _lb_target_label_selector("unhealthy")]}, "unhealthy"),
    ({"targets": [_lb_target_server("unhealthy"), _lb_target_label_selector("unknown")]}, "unhealthy"),
    ({"targets": [_lb_target_server("unknown"), _lb_target_label_selector("healthy")]}, "unknown"),
    ({"targets": [_lb_target_server("unknown"), _lb_target_label_selector("unhealthy")]}, "unhealthy"),
    ({"targets": [_lb_target_server("unknown"), _lb_target_label_selector("unknown")]}, "unknown"),
)


@pytest.mark.parametrize(("value", "expected"), LOAD_BALANCER_STATUS_TEST_CASES)
def test_load_balancer_status(value, expected):
    assert expected == load_balancer_status(value)
