
[![Build Status](https://dev.azure.com/ansible/hetzner.hcloud/_apis/build/status/CI?branchName=master)](https://dev.azure.com/ansible/hetzner.hcloud/_build?definitionId=35)
[![Codecov](https://img.shields.io/codecov/c/github/ansible-collections/hetzner.hcloud)](https://codecov.io/gh/ansible-collections/hetzner.hcloud)

Ansible Collection: hetzner.hcloud
=================================================

Ansible Hetzner Cloud Collection for controlling your Hetzner Cloud Resources.

## Release notes

See [here](https://github.com/ansible-collections/hetzner.hcloud/tree/master/CHANGELOG.rst).


## Publishing New Version


TBD	Basic instructions without release branches:

1. Create `changelogs/fragments/<version>.yml` with `release_summary:` section (which must be a string, not a list).
2. Run `antsibull-changelog release --collection-flatmap yes`
3. Make sure `CHANGELOG.rst` and `changelogs/changelog.yaml` are added to git, and the deleted fragments have been removed.
4. Tag the commit with `<version>`. Push changes and tag to the main repository.
