#!/usr/bin/env bash

target="$1"

HCLOUD_TOKEN=$(cat hcloud_token.txt)
changed_all_target="shippable/${cloud}/smoketest/"

echo "[default]
hcloud_api_token=${HCLOUD_TOKEN}
" >> $(pwd)/tests/integration/cloud-config-hcloud.ini
# shellcheck disable=SC2086
export SHIPPABLE="true"
export SHIPPABLE_BUILD_NUMBER="gl-$(cat prefix.txt)"
export SHIPPABLE_JOB_NUMBER="$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 2 | head -n 1)"
ansible-test integration --color --local -vv "${target}" ${COVERAGE:+"$COVERAGE"} ${CHANGED:+"$CHANGED"} ${UNSTABLE:+"$UNSTABLE"}
