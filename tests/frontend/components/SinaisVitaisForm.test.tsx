import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { SinaisVitaisForm } from "../../../frontend/src/features/triagem/components/SinaisVitaisForm";

const valores = {
  frequencia_cardiaca: 75,
  pressao_sistolica: 120,
  pressao_diastolica: 80,
  saturacao_o2: 98,
  temperatura: 36.5,
  frequencia_respiratoria: 16,
  glasgow: 15,
};

describe("SinaisVitaisForm", () => {
  it("test_renderiza_todos_os_7_campos", () => {
    render(<SinaisVitaisForm valores={valores} erros={{}} alertas={[]} onChange={vi.fn()} />);
    expect(screen.getAllByRole("spinbutton")).toHaveLength(7);
  });

  it("test_exibe_erro_abaixo_do_campo_correto", () => {
    render(<SinaisVitaisForm valores={valores} erros={{ frequencia_cardiaca: "Valor invalido" }} alertas={[]} onChange={vi.fn()} />);
    expect(screen.getByText("Valor invalido")).toBeVisible();
  });

  it("test_exibe_badge_critico_quando_alerta_critico", () => {
    render(<SinaisVitaisForm valores={valores} erros={{}} alertas={[{ campo: "frequencia_cardiaca", alerta: "critico" }]} onChange={vi.fn()} />);
    expect(screen.getByText("Critico")).toBeVisible();
  });

  it("test_exibe_badge_atencao_quando_alerta_atencao", () => {
    render(<SinaisVitaisForm valores={valores} erros={{}} alertas={[{ campo: "frequencia_cardiaca", alerta: "atencao" }]} onChange={vi.fn()} />);
    expect(screen.getByText("Atencao")).toBeVisible();
  });

  it("test_erro_tem_prioridade_sobre_alerta", () => {
    render(<SinaisVitaisForm valores={valores} erros={{ frequencia_cardiaca: "Valor invalido" }} alertas={[{ campo: "frequencia_cardiaca", alerta: "critico" }]} onChange={vi.fn()} />);
    expect(screen.queryByText("Critico")).toBeNull();
  });

  it("test_chama_onchange_com_campo_e_valor_corretos", () => {
    const onChange = vi.fn();
    render(<SinaisVitaisForm valores={valores} erros={{}} alertas={[]} onChange={onChange} />);
    fireEvent.change(screen.getByLabelText(/Frequencia cardiaca/i), { target: { value: "80" } });
    expect(onChange).toHaveBeenCalledWith("frequencia_cardiaca", 80);
  });
});
