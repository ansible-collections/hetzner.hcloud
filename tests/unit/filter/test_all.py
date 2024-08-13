from __future__ import annotations

import pytest

from plugins.filter.all import load_balancer_status

LOAD_BALANCER_STATUS_TEST_CASES = (
    ({"targets": [{"health_status": []}]}, "unknown"),
    ({"targets": [{"health_status": [{}]}]}, "unknown"),
    ({"targets": [{"health_status": [{"status": "unknown"}]}]}, "unknown"),
    ({"targets": [{"health_status": [{"status": "unhealthy"}]}]}, "unhealthy"),
    ({"targets": [{"health_status": [{"status": "healthy"}]}]}, "healthy"),
    (
        {
            "targets": [
                {"health_status": [{"status": "healthy"}]},
                {"health_status": [{"status": "healthy"}]},
            ]
        },
        "healthy",
    ),
    (
        {
            "targets": [
                {"health_status": [{"status": "healthy"}, {"status": "unhealthy"}]},
                {"health_status": [{"status": "healthy"}, {"status": "unknown"}]},
            ]
        },
        "unhealthy",
    ),
    (
        {
            "targets": [
                {"health_status": [{"status": "healthy"}]},
                {"health_status": [{"status": "unhealthy"}]},
            ]
        },
        "unhealthy",
    ),
)


@pytest.mark.parametrize(("value", "expected"), LOAD_BALANCER_STATUS_TEST_CASES)
def test_load_balancer_status(value, expected):
    assert expected == load_balancer_status(value)
