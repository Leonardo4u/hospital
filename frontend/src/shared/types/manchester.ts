export type RiscoNivel = "VERMELHO" | "LARANJA" | "AMARELO" | "VERDE" | "AZUL";

export interface NivelInfo {
  cor: `#${string}`;
  corTexto: `#${string}`;
  label: string;
  tempoMaximoMinutos: number | null;
  descricao: string;
}

export const NIVEL_INFO: Record<RiscoNivel, NivelInfo> = {
  VERMELHO: {
    cor: "#DC2626",
    corTexto: "#FFFFFF",
    label: "Emergência",
    tempoMaximoMinutos: null,
    descricao: "Atendimento imediato por risco iminente à vida.",
  },
  LARANJA: {
    cor: "#EA580C",
    corTexto: "#FFFFFF",
    label: "Muito Urgente",
    tempoMaximoMinutos: 10,
    descricao: "Necessita avaliação rápida por alta prioridade clínica.",
  },
  AMARELO: {
    cor: "#CA8A04",
    corTexto: "#111827",
    label: "Urgente",
    tempoMaximoMinutos: 60,
    descricao: "Demanda cuidado prioritário, sem instabilidade imediata.",
  },
  VERDE: {
    cor: "#16A34A",
    corTexto: "#FFFFFF",
    label: "Pouco Urgente",
    tempoMaximoMinutos: 120,
    descricao: "Quadro estável com menor probabilidade de deterioração rápida.",
  },
  AZUL: {
    cor: "#2563EB",
    corTexto: "#FFFFFF",
    label: "Não Urgente",
    tempoMaximoMinutos: 240,
    descricao: "Casos de baixa gravidade adequados para fluxo ambulatorial.",
  },
};

const ORDEM_GRAVIDADE: Record<RiscoNivel, number> = {
  VERMELHO: 0,
  LARANJA: 1,
  AMARELO: 2,
  VERDE: 3,
  AZUL: 4,
};

export function getNivelInfo(nivel: RiscoNivel): NivelInfo {
  return NIVEL_INFO[nivel];
}

export function ordenarPorGravidade(niveis: RiscoNivel[]): RiscoNivel[] {
  return [...niveis].sort((a, b) => ORDEM_GRAVIDADE[a] - ORDEM_GRAVIDADE[b]);
}
