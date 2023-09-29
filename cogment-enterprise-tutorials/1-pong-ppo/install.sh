#!/usr/bin/env bash

set -o errexit

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
COGMENT_VERSION="2.18.0"
COGMENT_ENTERPRISE_PY_SDK_VERSION="0.4.0"

# Check if the enterprise sdk archive is there
COGMENT_ENTERPRISE_PY_SDK_ARCHIVE="${ROOT_DIR}/cogment-enterprise-${COGMENT_ENTERPRISE_PY_SDK_VERSION}.tar.gz"
if [ ! -f "${COGMENT_ENTERPRISE_PY_SDK_ARCHIVE}" ]; then
  printf "Expected Cogment Enterprise Python SDK v%s couldn't be found at %s" "${COGMENT_ENTERPRISE_VERSION}" "${COGMENT_ENTERPRISE_PY_SDK_ARCHIVE}"
  exit 1
fi

# Create virtualenv
python3 -m venv "${ROOT_DIR}/.venv"

# Install cogment in the virtualenv
pushd "${ROOT_DIR}/.venv/bin"
curl --silent -L https://raw.githubusercontent.com/cogment/cogment/main/install.sh --output install-cogment.sh
chmod +x install-cogment.sh
./install-cogment.sh --version "${COGMENT_VERSION}" --skip-install --install-dir ./cogment
rm install-cogment.sh
popd

# Activate the venv
# shellcheck disable=SC1091
source "${ROOT_DIR}/.venv/bin/activate"

# Install python dependencies
pip install -r "${ROOT_DIR}/requirements.txt" "${COGMENT_ENTERPRISE_PY_SDK_ARCHIVE}"

# Run cogment code generation
pushd "${ROOT_DIR}"
python3 -m cogment.generate --spec=cogment.yaml --output=cog_settings.py
popd

# Accept the Atari ROM
AutoROM --accept-license

# deactivate the venv for now
deactivate
