#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] iniciando aplicacao backend..."

if ! /app/scripts/apply_migrations.sh; then
  echo "[entrypoint] erro ao aplicar migrations. Encerrando container."
  exit 1
fi

exec "$@"
