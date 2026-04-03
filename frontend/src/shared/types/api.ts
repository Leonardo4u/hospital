import type { RiscoNivel } from "./manchester";

export type Cargo = "MEDICO" | "ENFERMEIRO" | "TECNICO";
export type Sexo = "M" | "F" | "OUTRO";
export type OrigemClassificacao = "regras" | "ml" | "hibrido";

export interface Profissional {
  id: string;
  nome: string;
  email: string;
  cargo: Cargo;
  ativo: boolean;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Paciente {
  id: string;
  nome_completo: string;
  data_nascimento: string;
  cpf: string | null;
  sexo: Sexo;
  contato_emergencia: string | null;
  criado_em: string;
}

export interface SinaisVitaisInput {
  frequencia_cardiaca: number;
  pressao_sistolica: number;
  pressao_diastolica: number;
  saturacao_o2: number;
  temperatura: number;
  frequencia_respiratoria: number;
  glasgow: number;
}

export interface SintomaInput {
  codigo: string;
  descricao: string;
  peso: number;
}

export interface TriagemInput {
  paciente_id: string;
  sinais_vitais: SinaisVitaisInput;
  sintomas: SintomaInput[];
  queixa_principal: string;
}

export interface TriagemCreatedResponse {
  id: string;
  criado_em: string;
}

export interface TriagemResult {
  id: string;
  paciente_id: string;
  profissional_id: string;
  sinais_vitais: SinaisVitaisInput;
  sintomas: SintomaInput[];
  queixa_principal: string;
  nivel_calculado: RiscoNivel;
  nivel_confirmado: RiscoNivel | null;
  justificativa: string;
  discriminadores_ativados: string[];
  confianca: number;
  origem: OrigemClassificacao;
  confirmado_em: string | null;
  usado_em_treino: boolean;
  criado_em: string;
}

export interface ApiError {
  detail: string | { msg: string; type: string }[];
}
