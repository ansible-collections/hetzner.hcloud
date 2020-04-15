#!/usr/bin/env bash

set -o pipefail -eux

cloud="hcloud"
python="3.8"

target="cloud/hcloud"

stage="prod"

changed_all_target="shippable/${cloud}/smoketest/"

# shellcheck disable=SC2086
ansible-test integration --color -v "${target}" ${COVERAGE:+"$COVERAGE"} ${CHANGED:+"$CHANGED"} ${UNSTABLE:+"$UNSTABLE"} --changed-all-target "${changed_all_target}"
