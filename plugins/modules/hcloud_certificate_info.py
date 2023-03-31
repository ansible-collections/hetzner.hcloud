#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Hetzner Cloud GmbH <info@hetzner-cloud.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: hcloud_certificate_info
short_description: Gather infos about your Hetzner Cloud certificates.
description:
    - Gather facts about your Hetzner Cloud certificates.
author:
    - Lukas Kaemmerling (@LKaemmerling)
options:
    id:
        description:
            - The ID of the certificate you want to get.
        type: int
    name:
        description:
            - The name of the certificate you want to get.
        type: str
    label_selector:
        description:
            - The label selector for the certificate you want to get.
        type: str
extends_documentation_fragment:
- hetzner.hcloud.hcloud

'''

EXAMPLES = """
- name: Gather hcloud certificate infos
  hcloud_certificate_info:
  register: output
- name: Print the gathered infos
  debug:
    var: output.hcloud_certificate_info
"""

RETURN = """
hcloud_certificate_info:
    description: The certificate instances
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


class AnsibleHcloudCertificateInfo(Hcloud):
    def __init__(self, module):
        Hcloud.__init__(self, module, "hcloud_certificate_info")
        self.hcloud_certificate_info = None

    def _prepare_result(self):
        certificates = []

        for certificate in self.hcloud_certificate_info:
            if certificate:
                certificates.append({
                    "id": to_native(certificate.id),
                    "name": to_native(certificate.name),
                    "fingerprint": to_native(certificate.fingerprint),
                    "certificate": to_native(certificate.certificate),
                    "not_valid_before": to_native(certificate.not_valid_before),
                    "not_valid_after": to_native(certificate.not_valid_after),
                    "domain_names": [to_native(domain) for domain in certificate.domain_names],
                    "labels": certificate.labels
                })
        return certificates

    def get_certificates(self):
        try:
            if self.module.params.get("id") is not None:
                self.hcloud_certificate_info = [self.client.certificates.get_by_id(
                    self.module.params.get("id")
                )]
            elif self.module.params.get("name") is not None:
                self.hcloud_certificate_info = [self.client.certificates.get_by_name(
                    self.module.params.get("name")
                )]
            elif self.module.params.get("label_selector") is not None:
                self.hcloud_certificate_info = self.client.certificates.get_all(
                    label_selector=self.module.params.get("label_selector"))
            else:
                self.hcloud_certificate_info = self.client.certificates.get_all()

        except Exception as e:
            self.module.fail_json(msg=e.message)

    @staticmethod
    def define_module():
        return AnsibleModule(
            argument_spec=dict(
                id={"type": "int"},
                name={"type": "str"},
                label_selector={"type": "str"},
                **Hcloud.base_module_arguments()
            ),
            supports_check_mode=True,
        )


def main():
    module = AnsibleHcloudCertificateInfo.define_module()

    hcloud = AnsibleHcloudCertificateInfo(module)
    hcloud.get_certificates()
    result = hcloud.get_result()

    ansible_info = {
        'hcloud_certificate_info': result['hcloud_certificate_info']
    }
    module.exit_json(**ansible_info)


if __name__ == "__main__":
    main()
