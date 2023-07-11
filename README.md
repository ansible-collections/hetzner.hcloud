[![Build Status](https://dev.azure.com/ansible/hetzner.hcloud/_apis/build/status/CI?branchName=master)](https://dev.azure.com/ansible/hetzner.hcloud/_build?definitionId=35)
[![Codecov](https://img.shields.io/codecov/c/github/ansible-collections/hetzner.hcloud)](https://codecov.io/gh/ansible-collections/hetzner.hcloud)

# Ansible Collection: hetzner.hcloud

Ansible Hetzner Cloud Collection for controlling your Hetzner Cloud Resources.

### Python version compatibility

This collection depends on the [hcloud](https://github.com/hetznercloud/hcloud-python) library. Due to the [hcloud](https://github.com/hetznercloud/hcloud-python) Python Support Policy this collection requires Python 3.7 or greater.

## Release notes

See [here](https://github.com/ansible-collections/hetzner.hcloud/tree/master/CHANGELOG.rst).

### Release policy

The `main` branch is used for the development of the latest versions of the collections, and may contain breaking changes. The `stable-*` branches (e.g. `stable-1` for the `1.x.y` releases) are used to cut additional minor or patch releases if needed, but we do not provide official support for multiple versions of the collection.

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

1. Make sure your local `main` branch is in a clean state and is up to date.
2. Define a new version:
   ```sh
   export HCLOUD_VERSION=1.15.0
   ```
3. Create a release branch:
   ```sh
   git checkout -b "release-$HCLOUD_VERSION"
   ```
4. Generate the changelog for the new version, it should remove all fragments and change
   the `changelogs/changelog.yaml` and `CHANGELOG.rst`:
   ```sh
   antsibull-changelog release --version "$HCLOUD_VERSION"
   git add changelogs/changelog.yaml changelogs/fragments CHANGELOG.rst
   ```
5. Update the `version` in the ansible galaxy metadata file:
   ```sh
   sed -i "s/^version: .*/version: $HCLOUD_VERSION/" galaxy.yml
   git add galaxy.yml
   ```
6. Commit the changes:
   ```sh
   git commit -m "chore: prepare v$HCLOUD_VERSION"
   ```
7. Push the changes to Github, open a Pull Request and follow the process to get the PR merged into `main`.
8. Once the PR is merged, tag the release through the Github UI, after this the Github Actions will run and publish the collection to Ansible
   Galaxy.
