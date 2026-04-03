import http from "../../../shared/utils/httpClient";
import type { Cargo, Profissional, TokenResponse } from "../../../shared/types";

export interface RegistroInput {
  nome: string;
  email: string;
  senha: string;
  crm?: string;
  cargo: Cargo;
}

export async function login(email: string, senha: string): Promise<TokenResponse> {
  const { data } = await http.post<TokenResponse>("/auth/login", { email, senha });
  return data;
}

export async function registro(dados: RegistroInput): Promise<Profissional> {
  const { data } = await http.post<Profissional>("/auth/registro", dados);
  return data;
}

export async function refresh(refreshToken: string): Promise<TokenResponse> {
  const { data } = await http.post<TokenResponse>("/auth/refresh", {
    refresh_token: refreshToken,
  });
  return data;
}
