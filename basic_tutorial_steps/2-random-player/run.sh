#!/usr/bin/env bash

# This script acts as a command "menu" for this cogment project.
# - You can list the available commands using `./run.sh commands`
# - You can add a command as a bash function in this file

set -o errexit

ROOT_DIR=$(cd "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
RUN_SCRIPT="./$(basename -- "${BASH_SOURCE[0]}")"

### PRIVATE SUPPORT FUNCTIONS ###

function _load_dot_env() {
  cd "${ROOT_DIR}"
  if [ -f ".env" ]; then
    set -o allexport
    # shellcheck disable=SC1091
    source ".env"
    set +o allexport
  fi
}

### GENERIC PUBLIC COMMANDS ###

function commands() {
  all_commands=$(declare -F | awk '{print $NF}' | sort | grep -Ev "^_")
  for command in "${all_commands[@]}"; do
    if [[ ! ("${command}" =~ ^_.*) ]]; then
      printf "%s\n" "${command}"
    fi
  done
}

### PROJECT SPECIFIC PUBLIC COMMANDS ###

function install() {
  _load_dot_env

  # Create virtualenv
  python -m venv .venv

  # Install cogment in the virtualenv
  pushd "${ROOT_DIR}/.venv/bin"
  curl --silent -L https://raw.githubusercontent.com/cogment/cogment/main/install.sh --output install-cogment.sh
  chmod +x install-cogment.sh
  ./install-cogment.sh --version "${COGMENT_VERSION}" --skip-install --install-dir ./cogment
  rm install-cogment.sh
  popd

  # Activate the venv
  # shellcheck disable=SC1091
  source .venv/bin/activate

  # Install python dependencies
  pip install -r requirements.txt

  # Run cogment code generation
  python3 -m cogment.generate --spec=cogment.yaml --output=cog_settings.py

  deactivate
}

function services_start() {
  _load_dot_env
  # shellcheck disable=SC1091
  source .venv/bin/activate
  cogment launch "${ROOT_DIR}/launch.yaml"
  deactivate
}

function trial_runner_start() {
  _load_dot_env
  # shellcheck disable=SC1091
  source .venv/bin/activate
  python3 -m trial_runner.main
  deactivate
}

### MAIN SCRIPT ###

available_commands=$(commands)
command=$1
if [[ "${available_commands[*]}" = *"$1"* ]]; then
  shift
  ${command} "$@"
else
  printf "Unknown command [%s]\n" "${command}"
  printf "Available commands are:\n%s\n" "${available_commands[*]}"
  exit 1
fi
