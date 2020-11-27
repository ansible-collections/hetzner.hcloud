#!/usr/bin/env bash

set -o pipefail -eux

declare -a args

IFS='/:' read -ra args <<< "$1"

ansible_version="${args[0]}"
script="${args[1]}"

function join {
    local IFS="$1";
    shift;
    echo "$*";
}

test="$(join / "${args[@]:1}")"
command -v python
python -V

function retry
{
    for repetition in 1 2 3; do
        set +e
        "$@"
        result=$?
        set -e
        if [ ${result} == 0 ]; then
            return ${result}
        fi
        echo "$@ -> ${result}"
    done
    echo "Command '$@' failed 3 times!"
    exit -1
}

command -v pip
pip --version
pip list --disable-pip-version-check
if [ "${ansible_version}" == "devel" ]; then
    retry pip install https://github.com/ansible/ansible/archive/devel.tar.gz --disable-pip-version-check
else
    retry pip install "https://github.com/ansible/ansible/archive/stable-${ansible_version}.tar.gz" --disable-pip-version-check
fi
export ANSIBLE_COLLECTIONS_PATHS="${HOME}/.ansible"
SHIPPABLE_RESULT_DIR="$(pwd)/shippable"
TEST_DIR="${ANSIBLE_COLLECTIONS_PATHS}/ansible_collections/hetzner/hcloud"
rm -rf  "${TEST_DIR}"
mkdir -p "${TEST_DIR}"
cp -r "." "${TEST_DIR}"
cd "${TEST_DIR}"

# STAR: HACK install dependencies
retry ansible-galaxy -vvv collection install community.general
retry ansible-galaxy -vvv collection install ansible.netcommon
retry ansible-galaxy -vvv collection install community.internal_test_tools
retry pip install netaddr --disable-pip-version-check
retry pip install hcloud
retry pip install rstcheck
# END: HACK

export PYTHONIOENCODING='utf-8'

if [ "${JOB_TRIGGERED_BY_NAME:-}" == "nightly-trigger" ]; then
    COMPLETE=yes
fi


if [ -n "${COMPLETE:-}" ]; then
    # disable change detection triggered by setting the COMPLETE environment variable to a non-empty value
    export CHANGED=""
elif [[ "${CI_COMMIT_MESSAGE}" =~ ci_complete ]]; then
    # disable change detection triggered by having 'ci_complete' in the latest commit message
    export CHANGED=""
else
    # enable change detection (default behavior)
    export CHANGED=""
fi


export UNSTABLE="--allow-unstable-changed"

# remove empty core/extras module directories from PRs created prior to the repo-merge
find plugins -type d -empty -print -delete

ansible-test env --dump --show --timeout "50" --color -v

group="${args[1]}"
echo $test
if [[ "${test}" =~ hcloud ]]; then
  group="${args[3]}"
  bash tests/utils/gitlab/integration.sh "shippable/hcloud/group${group}/"
else
  bash tests/utils/gitlab/sanity.sh "sanity/${group}"
fi
