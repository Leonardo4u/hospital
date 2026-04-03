# Runbook Operacional

## Verificar saúde do sistema

1. Verifique os containers com `docker ps`.
2. Consulte `GET /api/v1/health`.
3. Em caso de degradação, confira logs do backend e latência do banco.

Exemplo:

```bash
curl http://localhost/api/v1/health
docker ps
```

## Aplicar migrations em produção sem downtime

1. Gere a migration com `./scripts/create_migration.sh "nome_da_change"`.
2. Revise o SQL gerado.
3. Faça deploy da nova imagem.
4. Execute `docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm backend alembic upgrade head`.
5. Só depois promova o tráfego para os containers novos.

## Backup e restore do PostgreSQL

### Backup

```bash
docker exec -t <container_db> pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > backup.sql
```

### Restore

```bash
cat backup.sql | docker exec -i <container_db> psql -U "$POSTGRES_USER" "$POSTGRES_DB"
```

## Treinar o modelo ML ao atingir 500 amostras

Quando `GET /metrics/triagem` mostrar `amostras_disponiveis_ml >= 500`, execute:

```bash
python ml/scripts/train.py --data-source database --output ml/trained_models/model.joblib
```

Enquanto esse script for placeholder, o fluxo oficial continua sendo Manchester puro.

## Rotacionar o `SECRET_KEY`

1. Gere uma nova chave aleatória com pelo menos 64 caracteres.
2. Atualize a variável `SECRET_KEY` no gerenciador de segredos.
3. Programe uma janela curta de troca, pois tokens emitidos anteriormente serão invalidados.
4. Reinicie backend e nginx.
5. Force novo login dos usuários se necessário.
6. Verifique `/health` e um login manual após a rotação.

## Troubleshooting

### Banco lento

- Verifique CPU e I/O do host.
- Inspecione conexões ativas com `pg_stat_activity`.
- Revise índices e consultas agregadas de `/metrics/triagem`.

### Classificador falhando

- Consulte `/api/v1/health`.
- Verifique logs estruturados para `request_id`, `exc_type` e `exc_message`.
- Revalide variáveis de ambiente e integridade do módulo de classificação.

### Frontend com tela branca

- Confira `VITE_API_URL`.
- Abra o console do navegador para erros de bundle.
- Verifique se o `try_files` do Nginx está servindo `index.html`.

## Contatos e escalação

- Nível 1: suporte operacional
- Nível 2: time backend
- Nível 3: DBA e responsável técnico clínico
- Canal de incidente: preencher conforme operação real
