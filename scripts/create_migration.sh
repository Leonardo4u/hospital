#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Uso: ./create_migration.sh \"nome_da_migration\""
  exit 1
fi

if [[ -z "${VIRTUAL_ENV:-}" ]] && ! command -v poetry >/dev/null 2>&1; then
  echo "Ative um virtualenv ou um ambiente Poetry antes de criar a migration."
  exit 1
fi

SAIDA="$(alembic revision --autogenerate -m "$1")"
echo "$SAIDA"
echo "$SAIDA" | grep -Eo 'versions/[^ ]+\.py' || true
