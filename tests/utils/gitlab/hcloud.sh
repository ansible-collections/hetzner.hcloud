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
export HOSTNAME="gitlab-$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 10 | head -n 1)"
ansible-test integration --color --docker --python "${python}" -v "${target}" ${COVERAGE:+"$COVERAGE"} ${CHANGED:+"$CHANGED"} ${UNSTABLE:+"$UNSTABLE"}
