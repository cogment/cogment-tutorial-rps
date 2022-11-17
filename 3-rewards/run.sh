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

function _py_build() {
  _load_dot_env
  directory=$1
  cp "${ROOT_DIR}/data.proto" "${ROOT_DIR}/cogment.yaml" "${ROOT_DIR}/${directory}"
  cd "${ROOT_DIR}/${directory}"
  python -m venv .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate
  pip install -r requirements.txt
  .venv/bin/python -m cogment.generate
  deactivate
}

function _py_start() {
  _load_dot_env
  directory=$1
  cd "${ROOT_DIR}/${directory}"
  .venv/bin/python main.py
}

function _run_sequence() {
  commands=("$@")

  for command in "${commands[@]}"; do
    "${command}"
  done
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

function client_build() {
  _py_build client
}

function client_start() {
  _py_start client
}

function environment_build() {
  _py_build environment
}

function random_agent_build() {
  _py_build random_agent
}

function build() {
  _run_sequence client_build environment_build random_agent_build
}

function services_start() {
  _load_dot_env
  cogment launch "${ROOT_DIR}/services.yaml"
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
