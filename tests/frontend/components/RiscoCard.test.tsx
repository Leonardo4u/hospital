import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { RiscoCard } from "../../../frontend/src/features/triagem/components/RiscoCard";

const baseResultado = {
  id: "1",
  paciente_id: "p1",
  profissional_id: "pr1",
  sinais_vitais: {
    frequencia_cardiaca: 160,
    pressao_sistolica: 75,
    pressao_diastolica: 50,
    saturacao_o2: 84,
    temperatura: 36.5,
    frequencia_respiratoria: 28,
    glasgow: 6,
  },
  sintomas: [],
  queixa_principal: "Choque",
  nivel_calculado: "VERMELHO" as const,
  nivel_confirmado: null,
  justificativa: "Discriminadores ativados: avaliar_choque.",
  discriminadores_ativados: ["avaliar_choque"],
  confianca: 1,
  origem: "regras" as const,
  confirmado_em: null,
  usado_em_treino: false,
  criado_em: "2024-01-01T00:00:00",
};

describe("RiscoCard", () => {
  it("test_renderiza_nivel_vermelho_com_cor_correta", () => {
    render(<RiscoCard resultado={baseResultado} onConfirmar={vi.fn()} isConfirmando={false} />);
    expect(screen.getByText(/VERMELHO/i).closest("header")).toHaveStyle({ backgroundColor: "rgb(220, 38, 38)" });
  });

  it("test_renderiza_discriminadores_ativados", () => {
    render(<RiscoCard resultado={baseResultado} onConfirmar={vi.fn()} isConfirmando={false} />);
    expect(screen.getByText("avaliar_choque")).toBeVisible();
  });

  it("test_botoes_de_confirmacao_visiveis_antes_de_confirmar", () => {
    render(<RiscoCard resultado={baseResultado} onConfirmar={vi.fn()} isConfirmando={false} />);
    expect(screen.getAllByRole("button")).toHaveLength(5);
  });

  it("test_botoes_desabilitados_durante_confirmacao", () => {
    render(<RiscoCard resultado={baseResultado} onConfirmar={vi.fn()} isConfirmando={true} />);
    expect(screen.getAllByRole("button").every((button) => (button as HTMLButtonElement).disabled)).toBe(true);
  });

  it("test_nivel_confirmado_oculta_botoes", () => {
    render(<RiscoCard resultado={{ ...baseResultado, nivel_confirmado: "VERMELHO" }} onConfirmar={vi.fn()} isConfirmando={false} />);
    expect(screen.queryByRole("button")).toBeNull();
  });

  it("test_badge_corrigido_aparece_quando_niveis_divergem", () => {
    render(<RiscoCard resultado={{ ...baseResultado, nivel_calculado: "AZUL", nivel_confirmado: "VERMELHO" }} onConfirmar={vi.fn()} isConfirmando={false} />);
    expect(screen.getByText(/Corrigido pelo profissional/i)).toBeVisible();
  });

  it("test_role_status_presente_para_acessibilidade", () => {
    render(<RiscoCard resultado={baseResultado} onConfirmar={vi.fn()} isConfirmando={false} />);
    expect(screen.getByRole("status")).toBeInTheDocument();
  });

  it("test_clicar_botao_confirmar_chama_callback", () => {
    const onConfirmar = vi.fn();
    render(<RiscoCard resultado={baseResultado} onConfirmar={onConfirmar} isConfirmando={false} />);
    fireEvent.click(screen.getByRole("button", { name: /AMARELO/i }));
    expect(onConfirmar).toHaveBeenCalledWith("AMARELO");
  });
});
