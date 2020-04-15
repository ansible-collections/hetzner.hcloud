#!/usr/bin/env bash

set -o pipefail -eux

cloud="hcloud"
python="3.8"

target="cloud/hcloud"

stage="prod"

changed_all_target="shippable/${cloud}/smoketest/"

if ! ansible-test integration "${changed_all_target}" --list-targets > /dev/null 2>&1; then
    # no smoketest tests are available for this cloud
    changed_all_target="none"
fi

# shellcheck disable=SC2086
ansible-test integration --color -v --retry-on-error "${target}" ${COVERAGE:+"$COVERAGE"} ${CHANGED:+"$CHANGED"} ${UNSTABLE:+"$UNSTABLE"} \
    --remote-terminate always --remote-stage "${stage}" --changed-all-target "${changed_all_target}"
