import { describe, expect, it } from "vitest";

import {
  getNivelInfo,
  NIVEL_INFO,
  ordenarPorGravidade,
} from "../../../frontend/src/shared/types/manchester";

describe("manchester", () => {
  it("test_nivel_info_existe_para_todos_os_5_niveis", () => {
    expect(Object.keys(NIVEL_INFO)).toHaveLength(5);
  });

  it("test_vermelho_tem_tempo_maximo_null", () => {
    expect(NIVEL_INFO.VERMELHO.tempoMaximoMinutos).toBeNull();
  });

  it("test_azul_tem_tempo_240_minutos", () => {
    expect(NIVEL_INFO.AZUL.tempoMaximoMinutos).toBe(240);
  });

  it("test_ordenar_por_gravidade_vermelho_primeiro", () => {
    expect(ordenarPorGravidade(["AZUL", "VERMELHO"])[0]).toBe("VERMELHO");
  });

  it("test_ordenar_por_gravidade_azul_ultimo", () => {
    const lista = ordenarPorGravidade(["AZUL", "VERMELHO", "AMARELO"]);
    expect(lista.at(-1)).toBe("AZUL");
  });

  it("test_ordenar_lista_mista_retorna_ordem_correta", () => {
    expect(ordenarPorGravidade(["VERDE", "AMARELO", "VERMELHO", "AZUL"])).toEqual(["VERMELHO", "AMARELO", "VERDE", "AZUL"]);
  });

  it("test_get_nivel_info_retorna_cor_hex_valida", () => {
    const info = getNivelInfo("AMARELO");
    expect(info.cor.startsWith("#") && info.cor.length === 7).toBe(true);
  });
});
