from __future__ import annotations

from unittest.mock import MagicMock

import pytest


@pytest.fixture()
def module():
    obj = MagicMock()
    obj.params = {
        "api_token": "dummy",
        "api_endpoint": "https://api.hetzner.cloud/v1",
    }
    return obj
