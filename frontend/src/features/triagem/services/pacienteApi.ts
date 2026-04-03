import type { Paciente, Sexo } from "@/shared/types";
import { http } from "@/shared/utils/httpClient";

export interface PacienteCreateInput {
  nome_completo: string;
  data_nascimento: string;
  cpf?: string | null;
  sexo: Sexo;
  contato_emergencia?: string | null;
}

export async function buscarPaciente(id: string): Promise<Paciente> {
  const { data } = await http.get<Paciente>(`/pacientes/${id}`);
  return data;
}

export async function listarPacientes(
  skip = 0,
  limit = 20,
): Promise<Paciente[]> {
  const { data } = await http.get<Paciente[]>("/pacientes", {
    params: { skip, limit },
  });
  return data;
}

export async function criarPaciente(
  dados: PacienteCreateInput,
): Promise<Paciente> {
  const { data } = await http.post<Paciente>("/pacientes", dados);
  return data;
}
