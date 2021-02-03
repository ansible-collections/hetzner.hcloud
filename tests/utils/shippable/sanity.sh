#!/usr/bin/env bash

set -o pipefail -eux

declare -a args
IFS='/:' read -ra args <<< "$1"

group="${args[1]}"

if [ "${BASE_BRANCH:-}" ]; then
    base_branch="origin/${BASE_BRANCH}"
else
    base_branch=""
fi

if [ "${group}" == "extra" ]; then
    # ansible-galaxy -vvv collection install community.internal_test_tools
    git clone --single-branch --depth 1 https://github.com/ansible-collections/community.internal_test_tools.git ../../community/internal_test_tools

    ../internal_test_tools/tools/run.py --color
    exit
fi

# shellcheck disable=SC2086
ansible-test sanity --color -v --junit ${COVERAGE:+"$COVERAGE"} ${CHANGED:+"$CHANGED"} \
    --docker --base-branch "${base_branch}" \
    --allow-disabled
