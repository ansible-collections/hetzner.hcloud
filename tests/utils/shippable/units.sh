#!/usr/bin/env bash

set -o pipefail -eux

declare -a args
IFS='/:' read -ra args <<< "$1"

python_version="${args[1]}"

ansible-test env --timeout 30 --color -v

# shellcheck disable=SC2086
ansible-test units --color -v \
    --docker default \
    --python "$python_version" \
    ${COVERAGE:+"$COVERAGE"} \
    ${CHANGED:+"$CHANGED"}
