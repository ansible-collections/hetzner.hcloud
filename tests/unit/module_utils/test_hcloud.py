from __future__ import annotations

import traceback
from datetime import datetime, timezone
from unittest.mock import MagicMock

from ansible_collections.hetzner.hcloud.plugins.module_utils.hcloud import AnsibleHCloud
from ansible_collections.hetzner.hcloud.plugins.module_utils.vendor.hcloud import (
    APIException,
)
from ansible_collections.hetzner.hcloud.plugins.module_utils.vendor.hcloud.actions import (
    Action,
    ActionException,
    ActionFailedException,
    ActionTimeoutException,
)


def test_hcloud_fail_json_hcloud():
    module = MagicMock()
    module.params = {
        "api_token": "fake_token",
        "api_endpoint": "https://api.hetzner.cloud/v1",
    }
    AnsibleHCloud.represent = "hcloud_test"
    hcloud = AnsibleHCloud(module)

    try:
        raise APIException(
            code="invalid_input",
            message="invalid input in fields 'server', 'home_location'",
            details={
                "fields": [
                    {"messages": ["either server or home_location must be provided"], "name": "server"},
                    {"messages": ["either server or home_location must be provided"], "name": "home_location"},
                ]
            },
        )
    except APIException as exception:
        hcloud.fail_json_hcloud(exception)

        module.fail_json.assert_called_with(
            msg="invalid input in fields 'server', 'home_location'",
            exception=traceback.format_exc(),
            failure={
                "message": "invalid input in fields 'server', 'home_location'",
                "code": "invalid_input",
                "details": {
                    "fields": [
                        {"messages": ["either server or home_location must be provided"], "name": "server"},
                        {"messages": ["either server or home_location must be provided"], "name": "home_location"},
                    ]
                },
            },
        )

    try:
        raise ActionFailedException(
            action=Action(
                **{
                    "id": 1084730887,
                    "command": "change_server_type",
                    "status": "error",
                    "progress": 100,
                    "resources": [{"id": 34574042, "type": "server"}],
                    "error": {"code": "server_does_not_exist_anymore", "message": "Server does not exist anymore"},
                    "started": "2023-07-06T14:52:42+00:00",
                    "finished": "2023-07-06T14:53:08+00:00",
                }
            )
        )
    except ActionException as exception:
        hcloud.fail_json_hcloud(exception)

        module.fail_json.assert_called_with(
            msg="The pending action failed: Server does not exist anymore",
            exception=traceback.format_exc(),
            failure={
                "action": {
                    "id": 1084730887,
                    "command": "change_server_type",
                    "status": "error",
                    "progress": 100,
                    "resources": [{"id": 34574042, "type": "server"}],
                    "error": {"code": "server_does_not_exist_anymore", "message": "Server does not exist anymore"},
                    "started": datetime(2023, 7, 6, 14, 52, 42, tzinfo=timezone.utc),
                    "finished": datetime(2023, 7, 6, 14, 53, 8, tzinfo=timezone.utc),
                }
            },
        )

    try:
        raise ActionTimeoutException(
            action=Action(
                **{
                    "id": 1084659545,
                    "command": "create_server",
                    "status": "running",
                    "progress": 50,
                    "started": "2023-07-06T13:58:38+00:00",
                    "finished": None,
                    "resources": [{"id": 34572291, "type": "server"}],
                    "error": None,
                }
            )
        )
    except ActionException as exception:
        hcloud.fail_json_hcloud(exception)

        module.fail_json.assert_called_with(
            msg="The pending action timed out",
            exception=traceback.format_exc(),
            failure={
                "action": {
                    "id": 1084659545,
                    "command": "create_server",
                    "status": "running",
                    "progress": 50,
                    "resources": [{"id": 34572291, "type": "server"}],
                    "error": None,
                    "started": datetime(2023, 7, 6, 13, 58, 38, tzinfo=timezone.utc),
                    "finished": None,
                }
            },
        )
