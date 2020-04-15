#!/usr/bin/env bash

cloud="hcloud"
python="3.8"

target="cloud/hcloud/"
HCLOUD_TOKEN= $(cat hcloud_token.txt)
changed_all_target="shippable/${cloud}/smoketest/"
ls -la
echo "[default]
hcloud_api_token=${HCLOUD_TOKEN}
" >> $(pwd)/tests/integration/cloud-config-hcloud.ini
# shellcheck disable=SC2086
ansible-test integration --color --local -v "${target}" ${COVERAGE:+"$COVERAGE"} ${CHANGED:+"$CHANGED"} ${UNSTABLE:+"$UNSTABLE"}
