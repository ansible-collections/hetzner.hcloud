#!/usr/bin/env bash

set -o pipefail -eux

error() {
  echo >&2 "error: $*"
  exit 1
}

retry() {
  local exit_code=1

  for _ in 1 2 3; do
    set +e
    "$@"
    exit_code=$?
    set -e
    if [ $exit_code == 0 ]; then
      return $exit_code
    fi
  done

  echo "Command '$*' failed 3 times!"
  exit $exit_code
}

declare -a entry_point_args
IFS='/:' read -ra entry_point_args <<< "$1"

# Explode entry point args, for example '2.16/integration/3.10/2' or '2.16/sanity'
ansible_version="${entry_point_args[0]}"
test_name="${entry_point_args[1]}"
python_version="${entry_point_args[2]:-}"
test_group="${entry_point_args[3]:-}"

export PYTHONIOENCODING="utf-8"
export PIP_DISABLE_PIP_VERSION_CHECK=true
export PIP_NO_WARN_SCRIPT_LOCATION=false # Negative options are a bit weird: https://pip.pypa.io/en/stable/topics/configuration/#boolean-options
export ANSIBLE_COLLECTIONS_PATH="$PWD/../.."

command -v python
python -V

command -v pip
pip --version
pip list

if [ "$ansible_version" == "devel" ]; then
  pip install "https://github.com/ansible/ansible/archive/devel.tar.gz"
else
  pip install "https://github.com/ansible/ansible/archive/stable-$ansible_version.tar.gz"
fi
command -v ansible
ansible --version

# Prepare coverage args
if $COVERAGE; then
  coverage_args="--coverage"
elif [[ "$COMMIT_MESSAGE" =~ ci_coverage ]]; then
  coverage_args="--coverage"
else
  coverage_args="--coverage-check"
fi

# Prepare changed args
if $COMPLETE; then
  changed_args=""
elif [[ "$COMMIT_MESSAGE" =~ ci_complete ]]; then
  changed_args=""
else
  changed_args="--changed"
fi

# Prepare unstable args
if $IS_PULL_REQUEST; then
  unstable_args="--allow-unstable-changed"
else
  unstable_args=""
fi

# Install dependencies
pip install rstcheck

# Ensure we can write other collections to this dir
sudo chown "$(whoami)" "$ANSIBLE_COLLECTIONS_PATH"

pip install -r tests/integration/requirements.txt -c tests/constraints.txt
ansible-galaxy -vvv collection install -r tests/requirements.yml

# Dump env and set timeout
timeout=45
if $COVERAGE; then
  timeout=60
fi

ansible-test env --color -v --dump --show --timeout "$timeout"

# Run tests
case "$test_name" in
  sanity)
    # shellcheck disable=SC2086
    ansible-test sanity --color -v \
      --exclude plugins/module_utils/vendor/ \
      --exclude scripts/ \
      --exclude tests/utils/ \
      --docker default \
      --junit \
      $coverage_args \
      $changed_args \
      --allow-disabled
    ;;

  units)
    # shellcheck disable=SC2086
    ansible-test units --color -v \
      --docker default \
      --python "$python_version" \
      $coverage_args \
      $changed_args
    ;;

  integration)
    # shellcheck disable=SC2086
    ansible-test integration --color -v \
      --remote-terminate always \
      --remote-stage prod \
      --docker default \
      --python "$python_version" \
      --retry-on-error \
      $coverage_args \
      $changed_args \
      --changed-all-target none \
      --changed-all-mode include \
      $unstable_args \
      "azp/group$test_group/"
    ;;

  *)
    error "found invalid test_name: $test_name"
    ;;
esac
