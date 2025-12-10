#!/usr/bin/python

# Copyright: (c) 2025, Hetzner Cloud GmbH <info@hetzner-cloud.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import annotations

DOCUMENTATION = """
---
module: storage_box_subaccount

short_description: Create and manage Storage Box Subaccounts in Hetzner.

description:
    - Create, update and delete Storage Box Subaccounts in Hetzner.
    - See the L(Storage Box Subaccounts API documentation,https://docs.hetzner.cloud/reference/hetzner#storage-box-subaccounts) for more details.
    - B(Experimental:) Storage Box support is experimental, breaking changes may occur within minor releases.
      See https://github.com/ansible-collections/hetzner.hcloud/issues/756 for more details.

author:
    - Jonas Lammler (@jooola)

options:
    storage_box:
        description:
            - ID or Name of the parent Storage Box.
            - Using the ID is preferred, to reduce the amount of API requests.
        type: str
        required: true
    id:
        description:
            - ID of the Storage Box Subaccount to manage.
            - Required if no Storage Box Subaccount O(name) is given.
            - If the ID is invalid, the module will fail.
        type: int
    name:
        description:
            - Name of the Storage Box Subaccount to manage.
            - Required if no Storage Box Subaccount O(id) is given.
            - Required if the Storage Box Subaccount does not exist.
            - Because the API resource does not have this property, the name is stored
              in the Storage Box Subaccount labels. This ensures that the module is
              idempotent, and removes the need to use different module arguments for
              create and update.
        type: str
    password:
        description:
            - Password for the Storage Box Subaccount.
            - Required if the Storage Box Subaccount does not exist or when O(state=reset_password).
        type: str
    home_directory:
        description:
            - Home directory of the Storage Box Subaccount.
            - Required if the Storage Box Subaccount does not exist.
        type: str
    access_settings:
        description:
            - Access settings of the Storage Box Subaccount.
        type: dict
        suboptions:
            reachable_externally:
                description:
                    - Whether access from outside the Hetzner network is allowed.
                type: bool
                default: false
            samba_enabled:
                description:
                    - Whether the Samba subsystem is enabled.
                type: bool
                default: false
            ssh_enabled:
                description:
                    - Whether the SSH subsystem is enabled.
                type: bool
                default: false
            webdav_enabled:
                description:
                    - Whether the WebDAV subsystem is enabled.
                type: bool
                default: false
            readonly:
                description:
                    - Whether the Subaccount is read-only.
                type: bool
                default: false
    description:
        description:
            - Description of the Storage Box Subaccount.
        type: str
    labels:
        description:
            - User-defined labels (key-value pairs) for the Storage Box Subaccount.
        type: dict
    state:
        description:
            - State of the Storage Box Subaccount.
            - C(reset_password) is not idempotent.
        default: present
        choices: [absent, present, reset_password]
        type: str

extends_documentation_fragment:
  - hetzner.hcloud.hcloud
"""

EXAMPLES = """
- name: Create a Storage Box Subaccount
  hetzner.hcloud.storage_box_subaccount:
    storage_box: my-storage-box
    name: subaccount1
    home_directory: backups/subaccount1
    password: secret
    access_settings:
      reachable_externally: false
      ssh_enabled: true
      samba_enabled: false
      webdav_enabled: false
      readonly: false
    labels:
      env: prod
    state: present

- name: Reset a Storage Box Subaccount password
  hetzner.hcloud.storage_box_subaccount:
    storage_box: my-storage-box
    name: subaccount1
    password: secret
    state: reset_password

- name: Delete a Storage Box Subaccount by name
  hetzner.hcloud.storage_box_subaccount:
    storage_box: my-storage-box
    name: subaccount1
    state: absent

- name: Delete a Storage Box Subaccount by id
  hetzner.hcloud.storage_box_subaccount:
    storage_box: 497436
    id: 158045
    state: absent
"""

RETURN = """
hcloud_storage_box_subaccount:
    description: Details about the Storage Box Subaccount.
    returned: always
    type: dict
    contains:
        storage_box:
            description: ID of the parent Storage Box.
            returned: always
            type: int
            sample: 497436
        id:
            description: ID of the Storage Box Subaccount.
            returned: always
            type: int
            sample: 158045
        name:
            description: Name of the Storage Box Subaccount.
            returned: always
            type: str
            sample: subaccount1
        description:
            description: Description of the Storage Box Subaccount.
            returned: always
            type: str
            sample: backups from subaccount1
        home_directory:
            description: Home directory of the Storage Box Subaccount.
            returned: always
            type: str
            sample: backups/subaccount1
        username:
            description: Username of the Storage Box Subaccount.
            returned: always
            type: str
            sample: u514605-sub1
        server:
            description: FQDN of the Storage Box Subaccount.
            returned: always
            type: str
            sample: u514605-sub1.your-storagebox.de
        access_settings:
            description: Access settings of the Storage Box Subaccount.
            returned: always
            type: dict
            contains:
                reachable_externally:
                    description: Whether access from outside the Hetzner network is allowed.
                    returned: always
                    type: bool
                    sample: false
                samba_enabled:
                    description: Whether the Samba subsystem is enabled.
                    returned: always
                    type: bool
                    sample: false
                ssh_enabled:
                    description: Whether the SSH subsystem is enabled.
                    returned: always
                    type: bool
                    sample: true
                webdav_enabled:
                    description: Whether the WebDAV subsystem is enabled.
                    returned: always
                    type: bool
                    sample: false
                readonly:
                    description: Whether the Subaccount is read-only.
                    returned: always
                    type: bool
                    sample: false
        labels:
            description: User-defined labels (key-value pairs) of the Storage Box Subaccount.
            returned: always
            type: dict
            sample:
                env: prod
        created:
            description: Point in time when the Storage Box Subaccount was created (in RFC3339 format).
            returned: always
            type: str
            sample: "2025-12-03T13:47:47Z"
"""

import string

from ..module_utils import storage_box, storage_box_subaccount
from ..module_utils.client import client_resource_not_found
from ..module_utils.experimental import storage_box_experimental_warning
from ..module_utils.hcloud import AnsibleHCloud, AnsibleModule
from ..module_utils.storage_box_subaccount import NAME_LABEL_KEY
from ..module_utils.vendor.hcloud import HCloudException
from ..module_utils.vendor.hcloud.storage_boxes import (
    BoundStorageBox,
    BoundStorageBoxSubaccount,
    StorageBoxSubaccountAccessSettings,
)


class AnsibleStorageBoxSubaccount(AnsibleHCloud):
    represent = "storage_box_subaccount"

    storage_box: BoundStorageBox | None = None
    storage_box_subaccount: BoundStorageBoxSubaccount | None = None
    storage_box_subaccount_name: str | None = None

    def __init__(self, module: AnsibleModule):
        storage_box_experimental_warning(module)
        super().__init__(module)

    def _prepare_result(self):
        if self.storage_box_subaccount is None:
            return {}
        return storage_box_subaccount.prepare_result(self.storage_box_subaccount, self.storage_box_subaccount_name)

    def _fetch(self):
        self.storage_box = storage_box.get(self.client.storage_boxes, self.module.params.get("storage_box"))

        if (value := self.module.params.get("id")) is not None:
            self.storage_box_subaccount = self.storage_box.get_subaccount_by_id(value)
        elif (value := self.module.params.get("name")) is not None:
            self.storage_box_subaccount = storage_box_subaccount.get_by_name(self.storage_box, value)

        # Workaround the missing name property
        # Get the name of the resource from the labels
        if self.storage_box_subaccount is not None:
            self.storage_box_subaccount_name = self.storage_box_subaccount.labels.pop(NAME_LABEL_KEY)

    def _create(self):
        self.fail_on_invalid_params(
            required=["name", "home_directory", "password"],
        )
        params = {
            "home_directory": self.module.params.get("home_directory"),
            "password": self.module.params.get("password"),
        }

        if (value := self.module.params.get("description")) is not None:
            params["description"] = value

        if (value := self.module.params.get("labels")) is not None:
            params["labels"] = value

        if (value := self.module.params.get("access_settings")) is not None:
            params["access_settings"] = StorageBoxSubaccountAccessSettings.from_dict(value)

        # Workaround the missing name property
        # Save the name of the resource in the labels
        if "labels" not in params:
            params["labels"] = {}
        params["labels"][NAME_LABEL_KEY] = self.module.params.get("name")

        if not self.module.check_mode:
            resp = self.storage_box.create_subaccount(**params)
            self.storage_box_subaccount = resp.subaccount
            resp.action.wait_until_finished()

            self.storage_box_subaccount.reload()
            self.storage_box_subaccount_name = self.storage_box_subaccount.labels.pop(NAME_LABEL_KEY)

        self._mark_as_changed()

    def _update(self):
        need_reload = False

        if (value := self.module.params.get("home_directory")) is not None:
            if self.storage_box_subaccount.home_directory != value:
                if not self.module.check_mode:
                    action = self.storage_box_subaccount.change_home_directory(value)
                    action.wait_until_finished()
                    need_reload = True
                self._mark_as_changed()

        if (value := self.module.params.get("access_settings")) is not None:
            access_settings = StorageBoxSubaccountAccessSettings.from_dict(value)
            if self.storage_box_subaccount.access_settings.to_payload() != access_settings.to_payload():
                if not self.module.check_mode:
                    action = self.storage_box_subaccount.update_access_settings(access_settings)
                    action.wait_until_finished()
                    need_reload = True
                self._mark_as_changed()

        params = {}
        if (value := self.module.params.get("description")) is not None:
            if value != self.storage_box_subaccount.description:
                params["description"] = value
                self._mark_as_changed()

        if (value := self.module.params.get("labels")) is not None:
            if value != self.storage_box_subaccount.labels:
                params["labels"] = value
                self._mark_as_changed()

                # Workaround the missing name property
                # Preserve resource name in the labels, name update happens below
                params["labels"][NAME_LABEL_KEY] = self.storage_box_subaccount_name

        # Workaround the missing name property
        # Update resource name in the labels
        if (value := self.module.params.get("name")) is not None:
            if value != self.storage_box_subaccount_name:
                self.fail_on_invalid_params(required=["id"])
                if "labels" not in params:
                    params["labels"] = self.storage_box_subaccount.labels
                params["labels"][NAME_LABEL_KEY] = value
                self._mark_as_changed()

        # Update only if params holds changes or actions were triggered
        if params or need_reload:
            if not self.module.check_mode:
                self.storage_box_subaccount = self.storage_box_subaccount.update(**params)
                self.storage_box_subaccount_name = self.storage_box_subaccount.labels.pop(NAME_LABEL_KEY)

    def _delete(self):
        if not self.module.check_mode:
            resp = self.storage_box_subaccount.delete()
            resp.action.wait_until_finished()

        self.storage_box_subaccount = None
        self._mark_as_changed()

    def present(self):
        try:
            self._fetch()
            if self.storage_box_subaccount is None:
                self._create()
            else:
                self._update()

        except HCloudException as exception:
            self.fail_json_hcloud(exception)

    def absent(self):
        try:
            self._fetch()
            if self.storage_box_subaccount is None:
                return
            self._delete()

        except HCloudException as exception:
            self.fail_json_hcloud(exception)

    def reset_password(self):
        self.fail_on_invalid_params(
            required=["password"],
        )
        try:
            self._fetch()
            if self.storage_box_subaccount is None:
                raise client_resource_not_found(
                    "storage box",
                    self.module.params.get("id") or self.module.params.get("name"),
                )
            if not self.module.check_mode:
                action = self.storage_box_subaccount.reset_password(self.module.params.get("password"))
                action.wait_until_finished()

            self._mark_as_changed()

        except HCloudException as exception:
            self.fail_json_hcloud(exception)

    @classmethod
    def define_module(cls):
        return AnsibleModule(
            argument_spec=dict(
                storage_box={"type": "str", "required": True},
                id={"type": "int"},
                name={"type": "str"},
                home_directory={"type": "str"},
                password={"type": "str", "no_log": True},
                description={"type": "str"},
                labels={"type": "dict"},
                access_settings={
                    "type": "dict",
                    "options": dict(
                        reachable_externally={"type": "bool", "default": False},
                        samba_enabled={"type": "bool", "default": False},
                        ssh_enabled={"type": "bool", "default": False},
                        webdav_enabled={"type": "bool", "default": False},
                        readonly={"type": "bool", "default": False},
                    ),
                },
                state={
                    "choices": ["absent", "present", "reset_password"],
                    "default": "present",
                },
                **super().base_module_arguments(),
            ),
            required_one_of=[["id", "name"]],
            supports_check_mode=True,
        )


def main():
    module = AnsibleStorageBoxSubaccount.define_module()
    o = AnsibleStorageBoxSubaccount(module)

    # Workaround the missing name property
    # Validate name
    if (value := module.params.get("name")) is not None:
        if len(value) < 1:
            module.fail_json(f"name '{value}' must be at least 1 character long")

        allowed_chars = string.ascii_letters + string.digits + "-"
        has_letters = False
        for c in value:
            if c in string.ascii_letters:
                has_letters = True
            if c in allowed_chars:
                continue
            module.fail_json(f"name '{value}' must only have allowed characters: {allowed_chars}")
        if not has_letters:
            module.fail_json(f"name '{value}' must contain at least one letter")

    match module.params.get("state"):
        case "reset_password":
            o.reset_password()
        case "absent":
            o.absent()
        case _:
            o.present()

    result = o.get_result()

    # Legacy return value naming pattern
    result["hcloud_storage_box_subaccount"] = result.pop(o.represent)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
