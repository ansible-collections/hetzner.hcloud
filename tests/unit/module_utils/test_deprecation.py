from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest import mock

import pytest
from ansible_collections.hetzner.hcloud.plugins.module_utils.deprecation import (
    deprecated_server_type_warning,
)
from ansible_collections.hetzner.hcloud.plugins.module_utils.vendor.hcloud.locations import (
    BoundLocation,
)
from ansible_collections.hetzner.hcloud.plugins.module_utils.vendor.hcloud.server_types import (
    BoundServerType,
)

PAST = datetime.now(timezone.utc) - timedelta(days=14)
FUTURE = datetime.now(timezone.utc) + timedelta(days=14)

LOCATION_FSN = {
    "id": 1,
    "name": "fsn1",
}
LOCATION_NBG = {
    "id": 2,
    "name": "nbg1",
}
DEPRECATION_NONE = {
    "deprecation": None,
}
DEPRECATION_DEPRECATED = {
    "deprecation": {
        "announced": PAST.isoformat(),
        "unavailable_after": FUTURE.isoformat(),
    },
}
DEPRECATION_UNAVAILABLE = {
    "deprecation": {
        "announced": PAST.isoformat(),
        "unavailable_after": PAST.isoformat(),
    },
}


@pytest.mark.parametrize(
    ("server_type", "location", "calls"),
    [
        (
            BoundServerType(
                mock.Mock(),
                {"name": "cx22", "locations": []},
            ),
            BoundLocation(mock.Mock(), LOCATION_FSN),
            [],
        ),
        # - Deprecated (backward compatible)
        (
            BoundServerType(
                mock.Mock(),
                {"name": "cx22", **DEPRECATION_DEPRECATED},
            ),
            None,
            [
                mock.call(
                    "Server type cx22 is deprecated in all locations and will no longer "
                    f"be available for order as of {FUTURE.strftime('%Y-%m-%d')}. "
                    "Existing servers of that type will continue to work as before and "
                    "no action is required on your part."
                )
            ],
        ),
        # - Unavailable (backward compatible)
        (
            BoundServerType(
                mock.Mock(),
                {"name": "cx22", **DEPRECATION_UNAVAILABLE},
            ),
            None,
            [
                mock.call(
                    "Server type cx22 is unavailable in all locations and can no longer "
                    "be ordered. Existing servers of that type will continue to work as "
                    "before and no action is required on your part."
                )
            ],
        ),
        # - SOME locations are deprecated
        # - Given location is NOT deprecated
        (
            BoundServerType(
                mock.Mock(),
                {
                    "name": "cx22",
                    "locations": [
                        {**LOCATION_FSN, **DEPRECATION_NONE},
                        {**LOCATION_NBG, **DEPRECATION_DEPRECATED},
                    ],
                },
            ),
            BoundLocation(mock.Mock(), LOCATION_FSN),
            [],
        ),
        # - SOME locations are deprecated
        # - Given location is deprecated
        (
            BoundServerType(
                mock.Mock(),
                {
                    "name": "cx22",
                    "locations": [
                        {**LOCATION_FSN, **DEPRECATION_NONE},
                        {**LOCATION_NBG, **DEPRECATION_DEPRECATED},
                    ],
                },
            ),
            BoundLocation(mock.Mock(), LOCATION_NBG),
            [
                mock.call(
                    "Server type cx22 is deprecated in nbg1 and will no longer be available "
                    f"for order as of {FUTURE.strftime('%Y-%m-%d')}. Existing servers of "
                    "that type will continue to work as before and no action is required "
                    "on your part."
                )
            ],
        ),
        # - SOME locations are unavailable
        # - Given location is unavailable
        (
            BoundServerType(
                mock.Mock(),
                {
                    "name": "cx22",
                    "locations": [
                        {**LOCATION_FSN, **DEPRECATION_NONE},
                        {**LOCATION_NBG, **DEPRECATION_UNAVAILABLE},
                    ],
                },
            ),
            BoundLocation(mock.Mock(), LOCATION_NBG),
            [
                mock.call(
                    "Server type cx22 is unavailable in nbg1 and can no longer be ordered. "
                    "Existing servers of that type will continue to work as before and no "
                    "action is required on your part."
                )
            ],
        ),
        # - SOME locations are deprecated
        # - Location is not given
        (
            BoundServerType(
                mock.Mock(),
                {
                    "name": "cx22",
                    "locations": [
                        {**LOCATION_FSN, **DEPRECATION_NONE},
                        {**LOCATION_NBG, **DEPRECATION_DEPRECATED},
                    ],
                },
            ),
            None,
            [],
        ),
        # - SOME locations are unavailable
        # - Location is not given
        (
            BoundServerType(
                mock.Mock(),
                {
                    "name": "cx22",
                    "locations": [
                        {**LOCATION_FSN, **DEPRECATION_NONE},
                        {**LOCATION_NBG, **DEPRECATION_UNAVAILABLE},
                    ],
                },
            ),
            None,
            [],
        ),
        # - SOME locations are deprecated
        # - SOME locations are unavailable
        # - Location is not given
        (
            BoundServerType(
                mock.Mock(),
                {
                    "name": "cx22",
                    "locations": [
                        {**LOCATION_FSN, **DEPRECATION_DEPRECATED},
                        {**LOCATION_NBG, **DEPRECATION_UNAVAILABLE},
                    ],
                },
            ),
            None,
            [
                mock.call(
                    "Server type cx22 is deprecated in all locations (fsn1,nbg1) and "
                    "can no longer be ordered in some locations (nbg1). Existing servers"
                    " of that type will continue to work as before and no action is "
                    "required on your part."
                )
            ],
        ),
        # - ALL locations are deprecated
        # - Location is not given
        (
            BoundServerType(
                mock.Mock(),
                {
                    "name": "cx22",
                    "locations": [
                        {**LOCATION_FSN, **DEPRECATION_DEPRECATED},
                        {**LOCATION_NBG, **DEPRECATION_DEPRECATED},
                    ],
                },
            ),
            None,
            [
                mock.call(
                    "Server type cx22 is deprecated in all locations (fsn1,nbg1) and "
                    "will no longer be available for order. Existing servers of that "
                    "type will continue to work as before and no action is required on "
                    "your part."
                )
            ],
        ),
        # - ALL locations are unavailable
        # - Location is not given
        (
            BoundServerType(
                mock.Mock(),
                {
                    "name": "cx22",
                    "locations": [
                        {**LOCATION_FSN, **DEPRECATION_UNAVAILABLE},
                        {**LOCATION_NBG, **DEPRECATION_UNAVAILABLE},
                    ],
                },
            ),
            None,
            [
                mock.call(
                    "Server type cx22 is unavailable in all locations (fsn1,nbg1) and "
                    "can no longer be ordered. Existing servers of that type will "
                    "continue to work as before and no action is required on your part."
                )
            ],
        ),
    ],
)
def test_deprecated_server_type_warning(server_type, location, calls):
    m = mock.Mock()
    deprecated_server_type_warning(m, server_type, location)
    m.warn.assert_has_calls(calls)
