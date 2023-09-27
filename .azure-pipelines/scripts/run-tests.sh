#!/usr/bin/env bash
# Configure the test environment and run the tests.

set -o pipefail -eu

entry_point="$1"
entry_point_args="$2"
read -r -a coverage_branches <<< "$3"  # space separated list of branches to run code coverage on for scheduled builds

export COMMIT_MESSAGE
export COMPLETE
export COVERAGE
export IS_PULL_REQUEST

if [ "${SYSTEM_PULLREQUEST_TARGETBRANCH:-}" ]; then
  IS_PULL_REQUEST=true
  COMMIT_MESSAGE=$(git log --format=%B -n 1 HEAD^2)
else
  IS_PULL_REQUEST=false
  COMMIT_MESSAGE=$(git log --format=%B -n 1 HEAD)
fi

COMPLETE=false
COVERAGE=false

if [ "${BUILD_REASON}" = "Schedule" ]; then
  COMPLETE=true

  if printf '%s\n' "${coverage_branches[@]}" | grep -q "^${BUILD_SOURCEBRANCHNAME}$"; then
    COVERAGE=true
  fi
fi

"${entry_point}" "${entry_point_args}" 2>&1 | "$(dirname "$0")/time-command.py"
