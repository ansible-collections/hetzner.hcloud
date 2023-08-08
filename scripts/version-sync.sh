#!/usr/bin/env bash

# Sync the collection version variable based on the version in the galaxy.yml file.

galaxy_version="$(grep '^version:' galaxy.yml | cut -d ' ' -f 2)"

sed --in-place "s|version = .*|version = \"$galaxy_version\"|" plugins/module_utils/version.py
