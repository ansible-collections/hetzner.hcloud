from __future__ import annotations

from ansible_collections.hetzner.hcloud.plugins.module_utils.client import (
    exponential_backoff_poll_interval,
)


def test_exponential_backoff_poll_interval():
    poll_interval = exponential_backoff_poll_interval(base=1.0, multiplier=2, cap=5.0, jitter=0.0)
    poll_max_retries = 25

    results = [poll_interval(i) for i in range(poll_max_retries)]
    assert sum(results) == 117.0
    assert results[:6] == [1.0, 2.0, 4.0, 5.0, 5.0, 5.0]
