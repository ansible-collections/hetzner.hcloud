# Changelog

## [2.5.0](https://github.com/ansible-collections/hetzner.hcloud/compare/2.4.1...2.5.0) (2024-02-02)


### Features

* add `hostvars_prefix` and `hostvars_suffix` options to inventory hostvars ([#423](https://github.com/ansible-collections/hetzner.hcloud/issues/423)) ([4e3f89a](https://github.com/ansible-collections/hetzner.hcloud/commit/4e3f89aed3be6f040e304521d69329c313616df5))
* allow forcing the deletion of firewalls that are still in use ([#447](https://github.com/ansible-collections/hetzner.hcloud/issues/447)) ([559d315](https://github.com/ansible-collections/hetzner.hcloud/commit/559d31561ad1e0fcf8dd14523bd3eb4262a8a3c1))
* improve firewall resources management ([#324](https://github.com/ansible-collections/hetzner.hcloud/issues/324)) ([2757fe7](https://github.com/ansible-collections/hetzner.hcloud/commit/2757fe745fcd80409290a453db72e9e6e4016f8f))
* replace `ansible.netcommon` utils with python3 `ipaddress` module ([#416](https://github.com/ansible-collections/hetzner.hcloud/issues/416)) ([4cfdf50](https://github.com/ansible-collections/hetzner.hcloud/commit/4cfdf50b26536c468705c729cdb48d4b2d421571))

## [2.4.1](https://github.com/ansible-collections/hetzner.hcloud/compare/2.4.0...2.4.1) (2023-11-27)


### Bug Fixes

* **inventory:** always use fresh cache on new cached session ([#404](https://github.com/ansible-collections/hetzner.hcloud/issues/404)) ([df7fa04](https://github.com/ansible-collections/hetzner.hcloud/commit/df7fa041494eb3609fcdbe65517a58a6396e0a84))

## [2.4.0](https://github.com/ansible-collections/hetzner.hcloud/compare/2.3.0...2.4.0) (2023-11-24)


### Features

* add `hetzner.hcloud.all` action group ([#396](https://github.com/ansible-collections/hetzner.hcloud/issues/396)) ([6581ed5](https://github.com/ansible-collections/hetzner.hcloud/commit/6581ed50db8fd7a3e7525cb364acd63fec256c3a))
* **inventory:** improve api options ([#397](https://github.com/ansible-collections/hetzner.hcloud/issues/397)) ([9905bd0](https://github.com/ansible-collections/hetzner.hcloud/commit/9905bd0e01ca5a21bb2db94f29a4c5276ffc638b))
* remove `hcloud_` prefix from all modules names ([#390](https://github.com/ansible-collections/hetzner.hcloud/issues/390)) ([933a162](https://github.com/ansible-collections/hetzner.hcloud/commit/933a16249bc224ee135fcf28a2ebb9ad34978d85))
* rename api_endpoint module argument ([#395](https://github.com/ansible-collections/hetzner.hcloud/issues/395)) ([7c9fbf8](https://github.com/ansible-collections/hetzner.hcloud/commit/7c9fbf85a734bc7884ff967680beb1fe422dc0ff))


### Bug Fixes

* **inventory:** improve performance ([#402](https://github.com/ansible-collections/hetzner.hcloud/issues/402)) ([f85d8f4](https://github.com/ansible-collections/hetzner.hcloud/commit/f85d8f4492f5c400dfcc4601f8212b6310f5c691))

## [2.3.0](https://github.com/ansible-collections/hetzner.hcloud/compare/2.2.0...2.3.0) (2023-11-07)

### Features

- add `created` field to server and server_info modules ([#381](https://github.com/ansible-collections/hetzner.hcloud/issues/381)) ([c3e4c0e](https://github.com/ansible-collections/hetzner.hcloud/commit/c3e4c0ea0a77bec26b83476af99d35078ed9cf6d))
- add server_types to datacenter info module ([#379](https://github.com/ansible-collections/hetzner.hcloud/issues/379)) ([084e04d](https://github.com/ansible-collections/hetzner.hcloud/commit/084e04d576798e7b49c5c3101803e7b8d2e80181))

## [2.2.0](https://github.com/ansible-collections/hetzner.hcloud/compare/2.1.2...2.2.0) (2023-10-23)

### Features

- add deprecation field to hcloud_iso_info ([#357](https://github.com/ansible-collections/hetzner.hcloud/issues/357)) ([76ef636](https://github.com/ansible-collections/hetzner.hcloud/commit/76ef636f07feb91daa91ecaa17619d10fea7d6e4))
- add load_balancer algorithm option ([#368](https://github.com/ansible-collections/hetzner.hcloud/issues/368)) ([a93dbaa](https://github.com/ansible-collections/hetzner.hcloud/commit/a93dbaa428a128555d71a9ef36a1a6c211e09952))
- allow selecting a resource using its ID ([#361](https://github.com/ansible-collections/hetzner.hcloud/issues/361)) ([5e425c5](https://github.com/ansible-collections/hetzner.hcloud/commit/5e425c56c2643f7c0c68b7c6feb8d3e098d4bcdb))

## [2.1.2](https://github.com/ansible-collections/hetzner.hcloud/compare/2.1.1...v2.1.2) (2023-10-05)

### Bug Fixes

- firewall port argument is required with udp or tcp ([#345](https://github.com/ansible-collections/hetzner.hcloud/issues/345)) ([76c1abf](https://github.com/ansible-collections/hetzner.hcloud/commit/76c1abf44764778aa6e11bae57df5ee5f69a947b))
- invalid field in load_balancer_service health_check.http return data ([#333](https://github.com/ansible-collections/hetzner.hcloud/issues/333)) ([fb35516](https://github.com/ansible-collections/hetzner.hcloud/commit/fb35516e7609fad4dd3fa75138dbc603f83d9aa0))

## Dev Changelog

> [!WARNING]
> For the user changelog, please check out [CHANGELOG.rst](../CHANGELOG.rst) instead.

This file contains a list of changes intended towards developers. It is auto-generated by release-please.

We would prefer to not generate this file, but disabling this is not supported currently: https://github.com/googleapis/release-please/issues/2007
