#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Patrice Le Guyader
# heavily inspired by the work of @LKaemmerling
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: hcloud_isos_info

short_description: Gather infos about the Hetzner Cloud isos list.


description:
    - Gather infos about the Hetzner Cloud isos list.

author:
    - Patrice Le Guyader (@patlegu)
    - Lukas Kaemmerling (@LKaemmerling)

options:
    id:
        description:
            - The ID of the iso image you want to get.
        type: int
    name:
        description:
            - The description of the iso you want to get.
        type: str
extends_documentation_fragment:
- hetzner.hcloud.hcloud

'''

EXAMPLES = """
- name: Gather hcloud isos type infos
  hcloud_isos_info:
  register: output

- name: Print the gathered infos
  debug:
    var: output.hcloud_isos_info
"""

RETURN = """
hcloud_isos_info:
    description: The isos type infos as list
    returned: always
    type: complex
    contains:
        id:
            description: ID of the ISO
            returned: always
            type: int
            sample: 1937415
        name:
            description: Unique identifier of the ISO. Only set for public ISOs
            returned: always
            type: str
            sample: fsn1
        description:
            description: DDescription of the ISO
            returned: always
            type: str
            sample: Falkenstein DC Park 1
        type:
            description: Type of the ISO. Choices: `public`, `private`
            returned: always
            type: str
            sample: 1
        deprecated:
            description: ISO 8601 timestamp of deprecation, None if ISO is still available. After the deprecation time it will no longer be possible to attach the ISO to servers.
            returned: always
            type: datetime, None
            sample: 1
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from ansible_collections.hetzner.hcloud.plugins.module_utils.hcloud import Hcloud

try:
    from hcloud import APIException
except ImportError:
    APIException = None


class AnsibleHcloudIsosInfo(Hcloud):
    def __init__(self, module):
        Hcloud.__init__(self, module, "hcloud_isos_info")
        self.hcloud_isos_info = None

    def _prepare_result(self):
        tmp = []

        for iso_info in self.hcloud_isos_info:
            if iso_info is not None:
                tmp.append({
                    "id": to_native(iso_info.id),
                    "name": to_native(iso_info.name),
                    "description": to_native(iso_info.description),
                    "type": iso_info.type,
                    "deprecated": iso_info.deprecated
                })
        return tmp

    def get_isos_infos(self):
        try:
            if self.module.params.get("id") is not None:
                self.hcloud_isos_info = [self.client.isos.get_by_id(
                    self.module.params.get("id")
                )]
            elif self.module.params.get("name") is not None:
                self.hcloud_isos_info = [self.client.isos.get_by_name(
                    self.module.params.get("name")
                )]
            else:
                self.hcloud_isos_info = self.client.isos.get_all()

        except Exception as e:
            self.module.fail_json(msg=e.message)

    @staticmethod
    def define_module():
        return AnsibleModule(
            argument_spec=dict(
                id={"type": "int"},
                name={"type": "str"},
                **Hcloud.base_module_arguments()
            ),
            supports_check_mode=True,
        )


def main():
    module = AnsibleHcloudIsosInfo.define_module()
    hcloud = AnsibleHcloudIsosInfo(module)
    hcloud.get_isos_infos()
    result = hcloud.get_result()
    ansible_info = {
        'hcloud_isos_info': result['hcloud_isos_info']
    }
    module.exit_json(**ansible_info)

if __name__ == "__main__":
    main()
