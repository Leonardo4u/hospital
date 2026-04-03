#!/usr/bin/env bash
set -euo pipefail

timestamp() {
  date +"%Y-%m-%dT%H:%M:%S%z"
}

DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-triagem_db}"
DB_USER="${POSTGRES_USER:-triagem}"

for tentativa in $(seq 1 30); do
  echo "[$(timestamp)] aguardando banco (${tentativa}/30)..."
  if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" >/dev/null 2>&1; then
    echo "[$(timestamp)] banco acessivel, aplicando migrations..."
    alembic upgrade head
    echo "[$(timestamp)] migrations aplicadas com sucesso."
    exit 0
  fi
  sleep 2
done

echo "[$(timestamp)] falha: banco nao acessivel apos 30 tentativas."
exit 1
