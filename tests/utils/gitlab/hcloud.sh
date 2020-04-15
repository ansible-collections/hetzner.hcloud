#!/usr/bin/env bash

set -o pipefail -eux

cloud="hcloud"
python="3.8"

target="cloud/hcloud/"

changed_all_target="shippable/${cloud}/smoketest/"
ls -la
echo "[default]
hcloud_api_token=${HCLOUD_TOKEN}
" >> /usr/local/lib/python3.8/site-packages/ansible_test/config/cloud-config-hcloud.ini
# shellcheck disable=SC2086
ansible-test integration --color --local -v "${target}" ${COVERAGE:+"$COVERAGE"} ${CHANGED:+"$CHANGED"} ${UNSTABLE:+"$UNSTABLE"}
