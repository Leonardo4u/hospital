# Arquitetura do Triagem Inteligente

## Visão geral

```text
+-------------+      +--------+      +-------------------+      +------------+
| Navegador   | ---> | Nginx  | ---> | FastAPI Backend   | ---> | PostgreSQL |
| React/Vite  |      | Proxy  |      | API + Regras + DB |      | 16         |
+-------------+      +--------+      +-------------------+      +------------+
```

O sistema foi desenhado para suportar triagem clínica baseada no Protocolo de Manchester com separação explícita entre domínio, transporte HTTP, persistência e apresentação. O frontend opera como cliente leve, enquanto o backend concentra regras clínicas, auditoria e autenticação.

## ADRs

### ADR-001: Por que `Protocol` em vez de `ABC` para `ClassificationStrategy`

Optamos por `typing.Protocol` para permitir injeção por duck typing sem acoplamento hierárquico rígido. Isso reduz fricção para testes, estratégias híbridas futuras e adaptadores vindos de outras camadas.

### ADR-002: Por que CQS nos endpoints de triagem

`POST /triagens` retorna apenas identificador e timestamp porque escrita e leitura têm objetivos diferentes. Isso reduz payload, mantém o contrato previsível e preserva a possibilidade de leitura assíncrona do resultado completo.

### ADR-003: Por que `audit_log` é imutável em nível de banco

Auditoria clínica não pode depender apenas da aplicação. O bloqueio de `UPDATE` e `DELETE` por permissão do banco garante trilha de auditoria mais resistente a erro operacional e uso indevido.

### ADR-004: Por que pastas feature-based no frontend

A estrutura por feature reduz acoplamento transversal e facilita evolução do produto por fluxos clínicos. `auth` e `triagem` ficam autocontidos com domínio, serviços, hooks e componentes próprios.

### ADR-005: Por que ML é placeholder até 500 amostras

Sem base confirmada mínima, qualquer modelo estatístico introduziria falsa confiança clínica. O sistema permanece totalmente funcional via regras Manchester e só abre espaço para ML quando houver volume suficiente de exemplos confirmados.

## Primeiros passos para novo desenvolvedor

1. Clone o repositório e copie `.env.example` para `.env`.
2. Ajuste as variáveis mínimas de ambiente, especialmente `DATABASE_URL`, `SECRET_KEY` e `VITE_API_URL`.
3. Suba o stack com `docker-compose up --build`.
4. Execute `python scripts/seed.py` para popular dados iniciais.
5. Acesse frontend, autentique com o usuário admin e valide `GET /api/v1/health`.

## Variáveis de ambiente

| Variável | Tipo | Obrigatória | Exemplo | Uso |
| --- | --- | --- | --- | --- |
| `DATABASE_URL` | string | sim | `postgresql+asyncpg://triagem:senha@db:5432/triagem_db` | conexão principal do backend |
| `SECRET_KEY` | string | sim | `troque-por-segredo-longo` | assinatura JWT |
| `ALGORITHM` | string | não | `HS256` | algoritmo JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | int | não | `15` | validade do access token |
| `REFRESH_TOKEN_EXPIRE_DAYS` | int | não | `7` | validade do refresh token |
| `DEBUG` | bool | não | `false` | modo de desenvolvimento |
| `MIN_AMOSTRAS_ML` | int | não | `500` | limiar para ativação futura de ML |
| `ALLOWED_ORIGINS` | string CSV | não | `http://localhost,https://triagem.exemplo.com` | CORS do backend |
| `POSTGRES_DB` | string | sim | `triagem_db` | nome do banco |
| `POSTGRES_USER` | string | sim | `triagem` | usuário do banco |
| `POSTGRES_PASSWORD` | string | sim | `senha_aqui` | senha do banco |
| `VITE_API_URL` | string | sim | `http://localhost:8000/api/v1` | base URL do frontend |

## Fluxo de classificação

O profissional autentica no frontend, seleciona um paciente e informa sinais vitais, sintomas e queixa principal. O frontend valida ranges fisiológicos localmente e envia a triagem para o backend. O backend converte os dados para o domínio puro, classifica via motor Manchester, persiste a triagem, registra o `audit_log` e retorna apenas o identificador da nova triagem. Em seguida o frontend consulta o recurso completo, apresenta o risco calculado e permite confirmação profissional. Toda confirmação e eventual correção também são auditadas.
