# Triagem Inteligente

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-orange)

O Triagem Inteligente é um sistema de triagem hospitalar baseado no Protocolo de Manchester, desenhado para apoiar o fluxo clínico desde a recepção do paciente até a confirmação profissional do nível de risco. O backend aplica regras clínicas auditáveis, enquanto o frontend oferece uma experiência operacional focada em rapidez, clareza e segurança.

O sistema foi pensado para equipes assistenciais que precisam registrar sinais vitais, sintomas, localização da queixa e decisão clínica com rastreabilidade completa. Cada classificação gera auditoria obrigatória e prepara o terreno para futura evolução com suporte híbrido entre regras e ML.

Manchester foi escolhido por ser um protocolo amplamente conhecido no contexto hospitalar, com foco em priorização por risco e tempo-resposta. Isso torna o produto mais aderente à prática clínica real e reduz ambiguidades no atendimento inicial.

## Pré-requisitos

- Docker 24+
- Docker Compose v2

## Início rápido

```bash
git clone <repo>
cp .env.example .env
docker-compose up --build
python scripts/seed.py
```

## URLs após subir

- Frontend: `http://localhost:5173`
- API Docs: `http://localhost:8000/docs` (apenas com `DEBUG=true`)
- Health check: `http://localhost:8000/api/v1/health`

## Credenciais do seed

- `admin@triagem.local`
- `Admin@2024`

## Documentação complementar

- [Arquitetura](docs/ARCHITECTURE.md)
- [Runbook Operacional](docs/RUNBOOK.md)

## Contribuição

### Rodar testes

```bash
python -m pytest
```

### Criar migration

```bash
./scripts/create_migration.sh "nome_da_migration"
```

### Lint

```bash
python -m compileall backend
```
