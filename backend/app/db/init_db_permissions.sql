-- Requisito clinico: audit_log deve ser imutavel no nivel do banco.
-- Este script deve ser executado manualmente pelo DBA apos a criacao do schema.

CREATE ROLE triagem_app WITH LOGIN PASSWORD 'trocar_em_execucao_controlada';

GRANT USAGE ON SCHEMA public TO triagem_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO triagem_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO triagem_app;

REVOKE UPDATE, DELETE ON TABLE audit_logs FROM triagem_app;
GRANT SELECT, INSERT ON TABLE audit_logs TO triagem_app;
