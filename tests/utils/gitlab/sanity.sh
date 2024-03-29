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
  ../internal_test_tools/tools/run.py --color
  exit
fi

case "${group}" in
  1) options=(--skip-test pylint --skip-test ansible-doc --skip-test validate-modules) ;;
  2) options=(--test ansible-doc --test validate-modules)                            ;;
  3) options=(--test pylint plugins/modules/)         ;;
  4) options=(--test pylint --exclude plugins/modules/) ;;
esac

# allow collection migration sanity tests for groups 3 and 4 to pass without updating this script during migration
network_path="lib/ansible/modules/network/"

if [ -d "${network_path}" ]; then
  if [ "${group}" -eq 3 ]; then
    options+=(--exclude "${network_path}")
  elif [ "${group}" -eq 4 ]; then
    options+=("${network_path}")
  fi
fi

pip install pycodestyle
pip install yamllint
pip install voluptuous
pip install pylint==2.5.3
# shellcheck disable=SC2086
ansible-test sanity --color -v --junit ${COVERAGE:+"$COVERAGE"} ${CHANGED:+"$CHANGED"} \
  --base-branch "${base_branch}" \
  --exclude plugins/module_utils/vendor/ \
  --exclude scripts/ \
  --exclude tests/utils/ \
  "${options[@]}" --allow-disabled
