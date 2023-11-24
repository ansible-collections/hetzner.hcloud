# Copyright: (c) 2023, Hetzner Cloud GmbH <info@hetzner-cloud.de>

from __future__ import annotations

from ansible.module_utils.basic import missing_required_lib

from .vendor.hcloud import APIException, Client

HAS_REQUESTS = True
HAS_DATEUTIL = True

try:
    import requests  # pylint: disable=unused-import
except ImportError:
    HAS_REQUESTS = False

try:
    import dateutil  # pylint: disable=unused-import
except ImportError:
    HAS_DATEUTIL = False


class ClientException(Exception):
    """An error related to the client occurred."""


def client_check_required_lib():
    if not HAS_REQUESTS:
        raise ClientException(missing_required_lib("requests"))
    if not HAS_DATEUTIL:
        raise ClientException(missing_required_lib("python-dateutil"))


def _client_resource_not_found(resource: str, param: str | int):
    return ClientException(f"resource ({resource.rstrip('s')}) does not exist: {param}")


def client_get_by_name_or_id(client: Client, resource: str, param: str | int):
    """
    Get a resource by name, and if not found by its ID.

    :param client: Client to use to make the call
    :param resource: Name of the resource client that implements both `get_by_name` and `get_by_id` methods
    :param param: Name or ID of the resource to query
    """
    resource_client = getattr(client, resource)

    result = resource_client.get_by_name(param)
    if result is not None:
        return result

    # If the param is not a valid ID, prevent an unnecessary call to the API.
    try:
        int(param)
    except ValueError as exception:
        raise _client_resource_not_found(resource, param) from exception

    try:
        return resource_client.get_by_id(param)
    except APIException as exception:
        if exception.code == "not_found":
            raise _client_resource_not_found(resource, param) from exception
        raise exception
