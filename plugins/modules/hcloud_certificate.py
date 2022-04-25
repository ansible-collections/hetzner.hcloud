#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Hetzner Cloud GmbH <info@hetzner-cloud.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: hcloud_certificate

short_description: Create and manage certificates on the Hetzner Cloud.


description:
    - Create, update and manage certificates on the Hetzner Cloud.

author:
    - Lukas Kaemmerling (@lkaemmerling)

options:
    id:
        description:
            - The ID of the Hetzner Cloud certificate to manage.
            - Only required if no certificate I(name) is given
        type: int
    name:
        description:
            - The Name of the Hetzner Cloud certificate to manage.
            - Only required if no certificate I(id) is given or a certificate does not exist.
        type: str
    labels:
        description:
            - User-defined labels (key-value pairs)
        type: dict
    certificate:
        description:
            - Certificate and chain in PEM format, in order so that each record directly certifies the one preceding.
            - Required if certificate does not exist.
        type: str
    private_key:
        description:
            - Certificate key in PEM format.
            - Required if certificate does not exist.
        type: str
    domain_names:
        description:
            - Certificate key in PEM format.
            - Required if certificate does not exist.
        type: list
        elements: str
    type:
        description:
            - Choose between uploading a Certificate in PEM format or requesting a managed Let's Encrypt Certificate.
        default: uploaded
        choices: [ uploaded, managed ]
        type: str
    state:
        description:
            - State of the certificate.
        default: present
        choices: [ absent, present ]
        type: str
extends_documentation_fragment:
- hetzner.hcloud.hcloud

'''

EXAMPLES = """
- name: Create a basic certificate
  hcloud_certificate:
    name: my-certificate
    certificate: "ssh-rsa AAAjjk76kgf...Xt"
    private_key: "ssh-rsa AAAjjk76kgf...Xt"
    state: present

- name: Create a certificate with labels
  hcloud_certificate:
    name: my-certificate
    certificate: "ssh-rsa AAAjjk76kgf...Xt"
    private_key: "ssh-rsa AAAjjk76kgf...Xt"
    labels:
        key: value
        mylabel: 123
    state: present

- name: Ensure the certificate is absent (remove if needed)
  hcloud_certificate:
    name: my-certificate
    state: absent
"""

RETURN = """
hcloud_certificate:
    description: The certificate instance
    returned: Always
    type: complex
    contains:
        id:
            description: Numeric identifier of the certificate
            returned: always
            type: int
            sample: 1937415
        name:
            description: Name of the certificate
            returned: always
            type: str
            sample: my website cert
        fingerprint:
            description: Fingerprint of the certificate
            returned: always
            type: str
            sample: "03:c7:55:9b:2a:d1:04:17:09:f6:d0:7f:18:34:63:d4:3e:5f"
        certificate:
            description: Certificate and chain in PEM format
            returned: always
            type: str
            sample: "-----BEGIN CERTIFICATE-----..."
        domain_names:
            description: List of Domains and Subdomains covered by the Certificate
            returned: always
            type: dict
        not_valid_before:
            description: Point in time when the Certificate becomes valid (in ISO-8601 format)
            returned: always
            type: str
        not_valid_after:
            description: Point in time when the Certificate stops being valid (in ISO-8601 format)
            returned: always
            type: str
        labels:
            description: User-defined labels (key-value pairs)
            returned: always
            type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from ansible_collections.hetzner.hcloud.plugins.module_utils.hcloud import Hcloud

try:
    from hcloud.certificates.domain import Certificate
    from hcloud.certificates.domain import Server
    from hcloud import APIException
except ImportError:
    APIException = None


class AnsibleHcloudCertificate(Hcloud):
    def __init__(self, module):
        Hcloud.__init__(self, module, "hcloud_certificate")
        self.hcloud_certificate = None

    def _prepare_result(self):
        return {
            "id": to_native(self.hcloud_certificate.id),
            "name": to_native(self.hcloud_certificate.name),
            "type": to_native(self.hcloud_certificate.type),
            "fingerprint": to_native(self.hcloud_certificate.fingerprint),
            "certificate": to_native(self.hcloud_certificate.certificate),
            "not_valid_before": to_native(self.hcloud_certificate.not_valid_before),
            "not_valid_after": to_native(self.hcloud_certificate.not_valid_after),
            "domain_names": [to_native(domain) for domain in self.hcloud_certificate.domain_names],
            "labels": self.hcloud_certificate.labels
        }

    def _get_certificate(self):
        try:
            if self.module.params.get("id") is not None:
                self.hcloud_certificate = self.client.certificates.get_by_id(
                    self.module.params.get("id")
                )
            elif self.module.params.get("name") is not None:
                self.hcloud_certificate = self.client.certificates.get_by_name(
                    self.module.params.get("name")
                )

        except Exception as e:
            self.module.fail_json(msg=e.message)

    def _create_certificate(self):
        self.module.fail_on_missing_params(
            required_params=["name"]
        )

        params = {
            "name": self.module.params.get("name"),
            "labels": self.module.params.get("labels")
        }
        if self.module.params.get('type') == 'uploaded':
            self.module.fail_on_missing_params(
                required_params=["certificate", "private_key"]
            )
            params["certificate"] = self.module.params.get("certificate")
            params["private_key"] = self.module.params.get("private_key")
            if not self.module.check_mode:
                try:
                    self.client.certificates.create(**params)
                except Exception as e:
                    self.module.fail_json(msg=e.message)
        else:
            self.module.fail_on_missing_params(
                required_params=["domain_names"]
            )
            params["domain_names"] = self.module.params.get("domain_names")
            if not self.module.check_mode:
                try:
                    resp = self.client.certificates.create_managed(**params)
                    resp.action.wait_until_finished(max_retries=1000)
                except Exception as e:
                    self.module.fail_json(msg=e.message)

        self._mark_as_changed()
        self._get_certificate()

    def _update_certificate(self):
        try:
            name = self.module.params.get("name")
            if name is not None and self.hcloud_certificate.name != name:
                self.module.fail_on_missing_params(
                    required_params=["id"]
                )
                if not self.module.check_mode:
                    self.hcloud_certificate.update(name=name)
                self._mark_as_changed()

            labels = self.module.params.get("labels")
            if labels is not None and self.hcloud_certificate.labels != labels:
                if not self.module.check_mode:
                    self.hcloud_certificate.update(labels=labels)
                self._mark_as_changed()
        except Exception as e:
            self.module.fail_json(msg=e.message)
        self._get_certificate()

    def present_certificate(self):
        self._get_certificate()
        if self.hcloud_certificate is None:
            self._create_certificate()
        else:
            self._update_certificate()

    def delete_certificate(self):
        self._get_certificate()
        if self.hcloud_certificate is not None:
            if not self.module.check_mode:
                try:
                    self.client.certificates.delete(self.hcloud_certificate)
                except Exception as e:
                    self.module.fail_json(msg=e.message)
            self._mark_as_changed()
        self.hcloud_certificate = None

    @staticmethod
    def define_module():
        return AnsibleModule(
            argument_spec=dict(
                id={"type": "int"},
                name={"type": "str"},
                type={
                    "choices": ["uploaded", "managed"],
                    "default": "uploaded",
                },
                domain_names={"type": "list", "elements": "str", "default": []},
                certificate={"type": "str"},
                private_key={"type": "str", "no_log": True},
                labels={"type": "dict"},
                state={
                    "choices": ["absent", "present"],
                    "default": "present",
                },
                **Hcloud.base_module_arguments()
            ),
            required_one_of=[['id', 'name']],
            required_if=[['state', 'present', ['name']]],
            supports_check_mode=True,
        )


def main():
    module = AnsibleHcloudCertificate.define_module()

    hcloud = AnsibleHcloudCertificate(module)
    state = module.params.get("state")
    if state == "absent":
        hcloud.delete_certificate()
    elif state == "present":
        hcloud.present_certificate()

    module.exit_json(**hcloud.get_result())


if __name__ == "__main__":
    main()
