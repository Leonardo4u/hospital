import { describe, expect, it, vi } from "vitest";

import {
  calcularIdade,
  classificarAlertaSinais,
  validarSinaisVitais,
} from "../../../frontend/src/features/triagem/domain/validacaoClinica";

describe("validarSinaisVitais", () => {
  it("test_objeto_vazio_retorna_todos_os_campos_como_erro", () => {
    expect(Object.keys(validarSinaisVitais({}))).toHaveLength(7);
  });

  it("test_dados_validos_retorna_objeto_vazio", () => {
    expect(validarSinaisVitais({
      frequencia_cardiaca: 75,
      pressao_sistolica: 120,
      pressao_diastolica: 80,
      saturacao_o2: 98,
      temperatura: 36.5,
      frequencia_respiratoria: 16,
      glasgow: 15,
    })).toEqual({});
  });

  it("test_fc_limite_inferior_valido", () => {
    expect(validarSinaisVitais({ frequencia_cardiaca: 20 }).frequencia_cardiaca).toBeUndefined();
  });

  it("test_fc_abaixo_do_limite_retorna_erro", () => {
    expect(validarSinaisVitais({ frequencia_cardiaca: 19 }).frequencia_cardiaca).toBeDefined();
  });

  it("test_fc_limite_superior_valido", () => {
    expect(validarSinaisVitais({ frequencia_cardiaca: 300 }).frequencia_cardiaca).toBeUndefined();
  });

  it("test_fc_acima_do_limite_retorna_erro", () => {
    expect(validarSinaisVitais({ frequencia_cardiaca: 301 }).frequencia_cardiaca).toBeDefined();
  });

  it("test_multiplos_erros_retornam_todos_simultaneamente", () => {
    const erros = validarSinaisVitais({ frequencia_cardiaca: -1, glasgow: 20 });
    expect(Object.keys(erros)).toEqual(expect.arrayContaining(["frequencia_cardiaca", "glasgow"]));
  });

  it("test_erro_contem_unidade_de_medida", () => {
    expect(validarSinaisVitais({ frequencia_cardiaca: -1 }).frequencia_cardiaca).toContain("bpm");
  });
});

describe("classificarAlertaSinais", () => {
  const base = {
    frequencia_cardiaca: 75,
    pressao_sistolica: 120,
    pressao_diastolica: 80,
    saturacao_o2: 98,
    temperatura: 36.5,
    frequencia_respiratoria: 16,
    glasgow: 15,
  };

  it("test_spo2_88_retorna_alerta_critico", () => {
    expect(classificarAlertaSinais({ ...base, saturacao_o2: 88 })).toContainEqual({ campo: "saturacao_o2", alerta: "critico" });
  });

  it("test_spo2_93_retorna_alerta_atencao", () => {
    expect(classificarAlertaSinais({ ...base, saturacao_o2: 93 })).toContainEqual({ campo: "saturacao_o2", alerta: "atencao" });
  });

  it("test_fc_160_retorna_alerta_critico", () => {
    expect(classificarAlertaSinais({ ...base, frequencia_cardiaca: 160 })).toContainEqual({ campo: "frequencia_cardiaca", alerta: "critico" });
  });

  it("test_fc_105_retorna_alerta_atencao", () => {
    expect(classificarAlertaSinais({ ...base, frequencia_cardiaca: 105 })).toContainEqual({ campo: "frequencia_cardiaca", alerta: "atencao" });
  });

  it("test_vitais_normais_retorna_lista_vazia", () => {
    expect(classificarAlertaSinais(base)).toEqual([]);
  });

  it("test_glasgow_7_retorna_critico", () => {
    expect(classificarAlertaSinais({ ...base, glasgow: 7 })).toContainEqual({ campo: "glasgow", alerta: "critico" });
  });

  it("test_temperatura_41_2_retorna_critico", () => {
    expect(classificarAlertaSinais({ ...base, temperatura: 41.2 })).toContainEqual({ campo: "temperatura", alerta: "critico" });
  });
});

describe("calcularIdade", () => {
  it("test_data_hoje_menos_30_anos_retorna_30", () => {
    const hoje = new Date();
    const data = `${hoje.getFullYear() - 30}-${String(hoje.getMonth() + 1).padStart(2, "0")}-${String(hoje.getDate()).padStart(2, "0")}`;
    expect(calcularIdade(data)).toBe(30);
  });

  it("test_aniversario_ainda_nao_ocorreu_retorna_idade_menos_1", () => {
    const hoje = new Date();
    const proximoMes = hoje.getMonth() === 11 ? 1 : hoje.getMonth() + 2;
    const ano = hoje.getMonth() === 11 ? hoje.getFullYear() - 29 : hoje.getFullYear() - 30;
    const data = `${ano}-${String(proximoMes).padStart(2, "0")}-01`;
    expect(calcularIdade(data)).toBeGreaterThanOrEqual(29);
  });

  it("test_data_nascimento_hoje_retorna_0", () => {
    const hoje = new Date();
    const data = `${hoje.getFullYear()}-${String(hoje.getMonth() + 1).padStart(2, "0")}-${String(hoje.getDate()).padStart(2, "0")}`;
    expect(calcularIdade(data)).toBe(0);
  });
});
