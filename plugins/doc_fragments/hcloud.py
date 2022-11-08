# -*- coding: utf-8 -*-
# Copyright: (c) 2019, Hetzner Cloud GmbH <info@hetzner-cloud.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = '''
options:
    api_token:
        description:
            - This is the API Token for the Hetzner Cloud.
            - You can also set this option by using the environment variable HCLOUD_TOKEN
        required: True
        type: str
    endpoint:
        description:
            - This is the API Endpoint for the Hetzner Cloud.
        default: https://api.hetzner.cloud/v1
        type: str
requirements:
  - hcloud-python >= 1.0.0
seealso:
- name: Documentation for Hetzner Cloud API
  description: Complete reference for the Hetzner Cloud API.
  link: https://docs.hetzner.cloud/
'''
