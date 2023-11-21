[![Galaxy version](https://img.shields.io/badge/dynamic/json?label=galaxy&prefix=v&url=https://galaxy.ansible.com/api/v3/plugin/ansible/content/published/collections/index/hetzner/hcloud/&query=highest_version.version)](https://galaxy.ansible.com/ui/repo/published/hetzner/hcloud)
[![GitHub version](https://img.shields.io/github/v/release/ansible-collections/hetzner.hcloud)](https://github.com/ansible-collections/hetzner.hcloud/releases)
[![Build Status](https://dev.azure.com/ansible/hetzner.hcloud/_apis/build/status/ci?branchName=main)](https://dev.azure.com/ansible/hetzner.hcloud/_build?definitionId=35)
[![Codecov](https://img.shields.io/codecov/c/github/ansible-collections/hetzner.hcloud)](https://codecov.io/gh/ansible-collections/hetzner.hcloud)

# Ansible Collection: hetzner.hcloud

Ansible Hetzner Cloud Collection for controlling your Hetzner Cloud Resources.

### Python version compatibility

This collection depends on the [hcloud](https://github.com/hetznercloud/hcloud-python) library. Due to the [hcloud](https://github.com/hetznercloud/hcloud-python) Python Support Policy this collection requires Python 3.8 or greater.

## Release notes

See [here](https://github.com/ansible-collections/hetzner.hcloud/tree/master/CHANGELOG.rst).

### Release policy

The `main` branch is used for the development of the latest versions of the collections, and may contain breaking changes. The `stable-*` branches (e.g. `stable-1` for the `1.x.y` releases) are used to cut additional minor or patch releases if needed, but we do not provide official support for multiple versions of the collection.

## Documentation

The documentation for all modules are available through `ansible-doc`.

Sample: `ansible-doc hetzner.hcloud.server` shows the documentation for the `server` module.

For all modules that were part of Ansible directly (before Ansible 2.11) we also have the documentation published in the
Ansible documentation: https://docs.ansible.com/ansible/latest/collections/hetzner/hcloud/

# Development

## Requirements

You should place the collection (clone the repository) into the Ansible collection path. Normally this
is `~/.ansible/collections/ansible_collections/<namespace>/<collection`, so for our collection it would
be: `~/.ansible/collections/ansible_collections/hetzner/hcloud`.

```
git clone git@github.com:ansible-collections/hetzner.hcloud.git ~/.ansible/collections/ansible_collections/hetzner/hcloud
```

After this you just need `ansible` installed.

## Testing

Testing is done via `ansible-test`. Make sure to have a `cloud-config-hcloud.ini` file in `tests/integration` which
contains the hcloud API token:

```
[default]
hcloud_api_token=<token>
```

After this you should be able to use `ansible-test integration` to perform the integration tests for a specific module.
Sample:

```
ansible-test integration --color --local  -vvv hetzner.hcloud.server // Executed all integration tests for server module
```

## Releasing a new version

If there are releasable changes, `release-please` will open a PR on GitHub with the proposed version. When this PR is merged, `release-please` will tag the release.
