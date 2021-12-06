#!/usr/bin/env bash

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

set -o errexit

for d in "$ROOT_DIR"/*-*/; do
  (
    cd "$d" || exit
    printf "\n******** TESTING \"%s\" ********\n\n" "$d"
    cogment run build
    cogment run start &
    sleep 20
    cogment run client &
    sleep 10
    cogment run stop
    sleep 10
    docker-compose kill
  )
done
