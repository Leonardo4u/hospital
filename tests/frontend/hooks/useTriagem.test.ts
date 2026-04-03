import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, act } from "@testing-library/react";
import React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { useTriagem } from "../../../frontend/src/features/triagem/hooks/useTriagem";
import * as triagemApi from "../../../frontend/src/features/triagem/services/triagemApi";

vi.mock("../../../frontend/src/features/triagem/services/triagemApi", () => ({
  classificar: vi.fn(),
  buscarTriagem: vi.fn(),
  confirmarTriagem: vi.fn(),
  listarPorPaciente: vi.fn(),
}));

function wrapper({ children }: { children: React.ReactNode }) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return React.createElement(QueryClientProvider, { client }, children);
}

afterEach(() => {
  vi.clearAllMocks();
});

describe("useTriagem", () => {
  it("test_classificar_com_dados_invalidos_nao_chama_api", () => {
    const { result } = renderHook(() => useTriagem(), { wrapper });
    act(() => {
      result.current.classificar();
    });
    expect(triagemApi.classificar).not.toHaveBeenCalled();
  });

  it("test_classificar_com_dados_validos_chama_api", async () => {
    vi.mocked(triagemApi.classificar).mockResolvedValue({ id: "triagem-1", criado_em: "2024-01-01T00:00:00" });
    const { result } = renderHook(() => useTriagem(), { wrapper });
    act(() => {
      result.current.selecionarPaciente({ id: "p1", nome_completo: "Paciente", data_nascimento: "1990-01-01", cpf: null, sexo: "F", contato_emergencia: null, criado_em: "2024-01-01T00:00:00" });
      result.current.setSinaisVitais("glasgow", 15);
      result.current.setSinaisVitais("frequencia_cardiaca", 80);
      result.current.setSinaisVitais("pressao_sistolica", 120);
      result.current.setSinaisVitais("pressao_diastolica", 80);
      result.current.setSinaisVitais("saturacao_o2", 98);
      result.current.setSinaisVitais("temperatura", 36.5);
      result.current.setSinaisVitais("frequencia_respiratoria", 16);
      result.current.setQueixaPrincipal("Dor leve");
    });
    await act(async () => {
      result.current.classificar();
    });
    expect(triagemApi.classificar).toHaveBeenCalled();
  });

  it("test_classificar_seta_triagem_realizada_id", async () => {
    vi.mocked(triagemApi.classificar).mockResolvedValue({ id: "triagem-1", criado_em: "2024-01-01T00:00:00" });
    const { result } = renderHook(() => useTriagem(), { wrapper });
    act(() => {
      result.current.selecionarPaciente({ id: "p1", nome_completo: "Paciente", data_nascimento: "1990-01-01", cpf: null, sexo: "F", contato_emergencia: null, criado_em: "2024-01-01T00:00:00" });
      result.current.setSinaisVitais("glasgow", 15);
      result.current.setSinaisVitais("frequencia_cardiaca", 80);
      result.current.setSinaisVitais("pressao_sistolica", 120);
      result.current.setSinaisVitais("pressao_diastolica", 80);
      result.current.setSinaisVitais("saturacao_o2", 98);
      result.current.setSinaisVitais("temperatura", 36.5);
      result.current.setSinaisVitais("frequencia_respiratoria", 16);
      result.current.setQueixaPrincipal("Dor leve");
    });
    await act(async () => {
      result.current.classificar();
    });
    expect(result.current.triagemRealizadaId).toBe("triagem-1");
  });

  it("test_toggle_sintoma_adiciona_quando_ausente", () => {
    const { result } = renderHook(() => useTriagem(), { wrapper });
    act(() => {
      result.current.toggleSintoma({ codigo: "febre", descricao: "Febre", peso: 0.7 });
    });
    expect(result.current.sintomasSelecionados).toHaveLength(1);
  });

  it("test_toggle_sintoma_remove_quando_presente", () => {
    const { result } = renderHook(() => useTriagem(), { wrapper });
    act(() => {
      result.current.toggleSintoma({ codigo: "febre", descricao: "Febre", peso: 0.7 });
      result.current.toggleSintoma({ codigo: "febre", descricao: "Febre", peso: 0.7 });
    });
    expect(result.current.sintomasSelecionados).toHaveLength(0);
  });

  it("test_resetar_limpa_todo_o_estado", () => {
    const { result } = renderHook(() => useTriagem(), { wrapper });
    act(() => {
      result.current.toggleSintoma({ codigo: "febre", descricao: "Febre", peso: 0.7 });
      result.current.setSinaisVitais("glasgow", 15);
      result.current.setQueixaPrincipal("Dor");
      result.current.resetar();
    });
    expect(result.current.sinaisVitais).toEqual({});
    expect(result.current.sintomasSelecionados).toEqual([]);
    expect(result.current.triagemRealizadaId).toBeNull();
  });

  it("test_set_sinais_vitais_limpa_erro_do_campo", () => {
    const { result } = renderHook(() => useTriagem(), { wrapper });
    act(() => {
      result.current.classificar();
      result.current.setSinaisVitais("frequencia_cardiaca", 80);
    });
    expect(result.current.errosValidacao.frequencia_cardiaca).toBeUndefined();
  });
});
