# Copyright: (c) 2019, Hetzner Cloud GmbH <info@hetzner-cloud.de>

# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)


import traceback
from typing import Any, Dict, Optional, Union

from ansible.module_utils.basic import (
    AnsibleModule as AnsibleModuleBase,
    env_fallback,
    missing_required_lib,
)
from ansible.module_utils.common.text.converters import to_native

from ..module_utils.vendor.hcloud import APIException, Client, HCloudException
from ..module_utils.vendor.hcloud.actions import ActionException
from .version import version

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


# Provide typing definitions to the AnsibleModule class
class AnsibleModule(AnsibleModuleBase):
    params: dict


class AnsibleHCloud:
    represent: str

    module: AnsibleModule

    def __init__(self, module: AnsibleModule):
        if not self.represent:
            raise NotImplementedError(f"represent property is not defined for {self.__class__.__name__}")

        self.module = module
        self.result = {"changed": False, self.represent: None}
        if not HAS_REQUESTS:
            module.fail_json(msg=missing_required_lib("requests"))
        if not HAS_DATEUTIL:
            module.fail_json(msg=missing_required_lib("python-dateutil"))
        self._build_client()

    def fail_json_hcloud(
        self,
        exception: HCloudException,
        msg: Optional[str] = None,
        params: Any = None,
        **kwargs,
    ) -> None:
        last_traceback = traceback.format_exc()

        failure = {}

        if params is not None:
            failure["params"] = params

        if isinstance(exception, APIException):
            failure["message"] = exception.message
            failure["code"] = exception.code
            failure["details"] = exception.details

        elif isinstance(exception, ActionException):
            failure["action"] = {k: getattr(exception.action, k) for k in exception.action.__slots__}

        exception_message = to_native(exception)
        if msg is not None:
            msg = f"{exception_message}: {msg}"
        else:
            msg = exception_message

        self.module.fail_json(msg=msg, exception=last_traceback, failure=failure, **kwargs)

    def _build_client(self) -> None:
        self.client = Client(
            token=self.module.params["api_token"],
            api_endpoint=self.module.params["endpoint"],
            application_name="ansible-module",
            application_version=version,
        )

    def _client_get_by_name_or_id(self, resource: str, param: Union[str, int]):
        """
        Get a resource by name, and if not found by its ID.

        :param resource: Name of the resource client that implements both `get_by_name` and `get_by_id` methods
        :param param: Name or ID of the resource to query
        """
        resource_client = getattr(self.client, resource)

        result = resource_client.get_by_name(param)
        if result is not None:
            return result

        # If the param is not a valid ID, prevent an unnecessary call to the API.
        try:
            int(param)
        except ValueError:
            self.module.fail_json(msg=f"resource ({resource.rstrip('s')}) does not exist: {param}")

        return resource_client.get_by_id(param)

    def _mark_as_changed(self) -> None:
        self.result["changed"] = True

    @classmethod
    def base_module_arguments(cls):
        return {
            "api_token": {
                "type": "str",
                "required": True,
                "fallback": (env_fallback, ["HCLOUD_TOKEN"]),
                "no_log": True,
            },
            "endpoint": {
                "type": "str",
                "default": "https://api.hetzner.cloud/v1",
            },
        }

    def _prepare_result(self) -> Dict[str, Any]:
        """Prepare the result for every module"""
        return {}

    def get_result(self) -> Dict[str, Any]:
        if getattr(self, self.represent) is not None:
            self.result[self.represent] = self._prepare_result()
        return self.result
