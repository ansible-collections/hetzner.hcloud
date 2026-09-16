# Note that this module util is **PRIVATE** to the collection. It can have breaking changes at any time.
# Do not use this from other collections or standalone plugins/modules!

from __future__ import annotations

from ._client import client_resource_not_found
from ._vendor.hcloud.networks import BoundNetwork, NetworksClient


def get(client: NetworksClient, param: str | int) -> BoundNetwork:
    """
    Get a Bound Network either by ID or name.

    If the given parameter is an ID, return a partial Bound Network to reduce the amount
    of API requests.
    """
    try:
        return BoundNetwork(
            client,
            data={"id": int(param)},
            complete=False,
        )
    except ValueError:  # param is not an id
        result = client.get_by_name(param)
        if result is None:
            # pylint: disable=raise-missing-from
            raise client_resource_not_found("network", param)
        return result
