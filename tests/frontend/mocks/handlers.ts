import { setupServer } from "msw/node";
import { http, HttpResponse } from "msw";

const API_BASE = "http://localhost:8000/api/v1";

const profissionalFicticio = {
  id: "11111111-1111-1111-1111-111111111111",
  nome: "Dra. Alice",
  email: "alice@triagem.local",
  cargo: "MEDICO",
  ativo: true,
};

const pacienteFicticio = {
  id: "22222222-2222-2222-2222-222222222222",
  nome_completo: "Mariana Alves",
  data_nascimento: "1990-01-01",
  cpf: "11144477735",
  sexo: "F",
  contato_emergencia: "Mae - 11999999999",
  criado_em: "2024-01-01T00:00:00",
};

const triagemFicticia = {
  id: "33333333-3333-3333-3333-333333333333",
  paciente_id: pacienteFicticio.id,
  profissional_id: profissionalFicticio.id,
  sinais_vitais: {
    frequencia_cardiaca: 95,
    pressao_sistolica: 125,
    pressao_diastolica: 82,
    saturacao_o2: 96,
    temperatura: 40,
    frequencia_respiratoria: 20,
    glasgow: 15,
  },
  sintomas: [{ codigo: "febre", descricao: "Febre", peso: 0.7 }],
  queixa_principal: "Febre alta",
  nivel_calculado: "AMARELO",
  nivel_confirmado: null,
  justificativa: "Discriminadores ativados: avaliar_febre_alta.",
  discriminadores_ativados: ["avaliar_febre_alta"],
  confianca: 1,
  origem: "regras",
  confirmado_em: null,
  usado_em_treino: false,
  criado_em: "2024-01-01T00:00:00",
};

export function errorHandler(path: string, statusCode: number, detail: string) {
  return http.all(`${API_BASE}${path}`, () =>
    HttpResponse.json({ detail }, { status: statusCode }),
  );
}

export const handlers = [
  http.post(`${API_BASE}/auth/login`, () =>
    HttpResponse.json(
      {
        access_token: "access-token-fake",
        refresh_token: "refresh-token-fake",
        token_type: "bearer",
      },
      { status: 200 },
    ),
  ),
  http.post(`${API_BASE}/auth/registro`, () =>
    HttpResponse.json(profissionalFicticio, { status: 201 }),
  ),
  http.post(`${API_BASE}/auth/refresh`, () =>
    HttpResponse.json(
      {
        access_token: "access-token-novo",
        refresh_token: "refresh-token-novo",
        token_type: "bearer",
      },
      { status: 200 },
    ),
  ),
  http.get(`${API_BASE}/auth/me`, () =>
    HttpResponse.json(profissionalFicticio, { status: 200 }),
  ),
  http.get(`${API_BASE}/pacientes`, () =>
    HttpResponse.json(
      [
        pacienteFicticio,
        { ...pacienteFicticio, id: "44444444-4444-4444-4444-444444444444", nome_completo: "Carlos Menezes" },
        { ...pacienteFicticio, id: "55555555-5555-5555-5555-555555555555", nome_completo: "Aline Batista" },
      ],
      { status: 200 },
    ),
  ),
  http.get(`${API_BASE}/pacientes/:id`, ({ params }) =>
    HttpResponse.json({ ...pacienteFicticio, id: String(params.id) }, { status: 200 }),
  ),
  http.post(`${API_BASE}/triagens`, () =>
    HttpResponse.json(
      { id: "uuid-fake", criado_em: "2024-01-01T00:00:00" },
      { status: 201 },
    ),
  ),
  http.get(`${API_BASE}/triagens/:id`, ({ params }) =>
    HttpResponse.json({ ...triagemFicticia, id: String(params.id) }, { status: 200 }),
  ),
  http.post(`${API_BASE}/triagens/:id/confirmar`, ({ params }) =>
    HttpResponse.json(
      {
        ...triagemFicticia,
        id: String(params.id),
        nivel_confirmado: "AMARELO",
        confirmado_em: "2024-01-01T00:01:00",
      },
      { status: 200 },
    ),
  ),
  http.get(`${API_BASE}/triagens/paciente/:id`, () =>
    HttpResponse.json([triagemFicticia], { status: 200 }),
  ),
];

export const server = setupServer(...handlers);
