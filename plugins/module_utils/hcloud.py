# Copyright: (c) 2019, Hetzner Cloud GmbH <info@hetzner-cloud.de>

# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)


import traceback

from ansible.module_utils.basic import env_fallback, missing_required_lib
from ansible.module_utils.common.text.converters import to_native

from ..module_utils.vendor import hcloud
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


class AnsibleHCloud:
    def __init__(self, module, represent):
        self.module = module
        self.represent = represent
        self.result = {"changed": False, self.represent: None}
        if not HAS_REQUESTS:
            module.fail_json(msg=missing_required_lib("requests"))
        if not HAS_DATEUTIL:
            module.fail_json(msg=missing_required_lib("python-dateutil"))
        self._build_client()

    def fail_json_hcloud(self, exception, msg=None, params=None, **kwargs):
        last_traceback = traceback.format_exc()

        failure = {}

        if params is not None:
            failure["params"] = params

        if isinstance(exception, hcloud.APIException):
            failure["message"] = exception.message
            failure["code"] = exception.code
            failure["details"] = exception.details

        elif isinstance(exception, hcloud.actions.domain.ActionException):
            failure["action"] = {k: getattr(exception.action, k) for k in exception.action.__slots__}

        exception_message = to_native(exception)
        if msg is not None:
            msg = f"{exception_message}: {msg}"
        else:
            msg = exception_message

        self.module.fail_json(msg=msg, exception=last_traceback, failure=failure, **kwargs)

    def _build_client(self):
        self.client = hcloud.Client(
            token=self.module.params["api_token"],
            api_endpoint=self.module.params["endpoint"],
            application_name="ansible-module",
            application_version=version,
        )

    def _mark_as_changed(self):
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
            "endpoint": {"type": "str", "default": "https://api.hetzner.cloud/v1"},
        }

    def _prepare_result(self):
        """Prepare the result for every module

        :return: dict
        """
        return {}

    def get_result(self):
        if getattr(self, self.represent) is not None:
            self.result[self.represent] = self._prepare_result()
        return self.result
