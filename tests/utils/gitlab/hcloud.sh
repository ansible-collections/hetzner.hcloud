#!/usr/bin/env bash

set -o pipefail -eux

cloud="hcloud"
python="3.8"

target="cloud/hcloud"

changed_all_target="shippable/${cloud}/smoketest/"
ls -la
# shellcheck disable=SC2086
ansible-test integration --color --local -v "${target}" ${COVERAGE:+"$COVERAGE"} ${CHANGED:+"$CHANGED"} ${UNSTABLE:+"$UNSTABLE"} --changed-all-target "${changed_all_target}"
