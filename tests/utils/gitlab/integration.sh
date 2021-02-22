#!/usr/bin/env bash

target="$1"

HCLOUD_TOKEN=$(cat hcloud_token.txt)
# shellcheck disable=SC2034,SC2154
changed_all_target="shippable/${cloud}/smoketest/"

# shellcheck disable=SC2046
echo "[default]
hcloud_api_token=${HCLOUD_TOKEN}
" >> $(pwd)/tests/integration/cloud-config-hcloud.ini
export SHIPPABLE="true"

# shellcheck disable=SC2155
export SHIPPABLE_BUILD_NUMBER="gl-$(cat prefix.txt)"

# shellcheck disable=SC2155,SC2002
export SHIPPABLE_JOB_NUMBER="$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 2 | head -n 1)"
ansible-test integration --color --local -vv "${target}" ${COVERAGE:+"$COVERAGE"} ${CHANGED:+"$CHANGED"} ${UNSTABLE:+"$UNSTABLE"}
