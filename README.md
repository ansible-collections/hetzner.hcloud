[![Build Status](https://dev.azure.com/ansible/hetzner.hcloud/_apis/build/status/CI?branchName=master)](https://dev.azure.com/ansible/hetzner.hcloud/_build?definitionId=35)
[![Codecov](https://img.shields.io/codecov/c/github/ansible-collections/hetzner.hcloud)](https://codecov.io/gh/ansible-collections/hetzner.hcloud)

Ansible Collection: hetzner.hcloud
=================================================

Ansible Hetzner Cloud Collection for controlling your Hetzner Cloud Resources.

## Release notes

See [here](https://github.com/ansible-collections/hetzner.hcloud/tree/master/CHANGELOG.rst).

## Documentation

The documentation for all modules are available through `ansible-doc`.

Sample: `ansible-doc hetzner.hcloud.hcloud_server` shows the documentation for the `hcloud_server` module.

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
ansible-test integration --color --local  -vvv hcloud_server // Executed all integration tests for hcloud_server module
```

## Releasing a new version

### Generating changelog from fragments

1. Check if the changelog fragments are available (there should be files in `changelogs/fragments`)
2. Run `antsibull-changelog release --version <version>`, it should remove all fragments and change
   the `changelogs/changlog.yaml` and `CHANGELOG.rst`
3. Push the changes to the main branch
4. Tag the release through the Github UI, after this the Github Actions will run and publish the collection to Ansible
   Galaxy
