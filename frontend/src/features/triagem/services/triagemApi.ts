import type {
  RiscoNivel,
  TriagemCreatedResponse,
  TriagemInput,
  TriagemResult,
} from "@/shared/types";
import { http } from "@/shared/utils/httpClient";

function normalizarNivel(nivel: unknown): RiscoNivel {
  const valor = String(nivel ?? "").toUpperCase();
  if (
    valor === "VERMELHO" ||
    valor === "LARANJA" ||
    valor === "AMARELO" ||
    valor === "VERDE" ||
    valor === "AZUL"
  ) {
    return valor;
  }
  return "VERDE";
}

function normalizarTriagem(data: TriagemResult): TriagemResult {
  return {
    ...data,
    nivel_calculado: normalizarNivel(data.nivel_calculado),
    nivel_confirmado:
      data.nivel_confirmado === null
        ? null
        : normalizarNivel(data.nivel_confirmado),
  };
}

export async function classificar(
  dados: TriagemInput,
): Promise<TriagemCreatedResponse> {
  const { data } = await http.post<TriagemCreatedResponse>("/triagens", dados);
  return data;
}

export async function buscarTriagem(id: string): Promise<TriagemResult> {
  const { data } = await http.get<TriagemResult>(`/triagens/${id}`);
  return normalizarTriagem(data);
}

export async function confirmarTriagem(
  id: string,
  nivel: RiscoNivel,
): Promise<TriagemResult> {
  const { data } = await http.post<TriagemResult>(`/triagens/${id}/confirmar`, {
    nivel_confirmado: nivel.toLowerCase(),
  });
  return normalizarTriagem(data);
}

export async function listarPorPaciente(
  pacienteId: string,
): Promise<TriagemResult[]> {
  const { data } = await http.get<TriagemResult[]>(`/triagens/paciente/${pacienteId}`);
  return data.map(normalizarTriagem);
}
