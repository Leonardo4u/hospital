import { describe, expect, it } from "vitest";

import {
  calcularIdade,
  classificarAlertaSinais,
  validarSinaisVitais,
} from "../../../frontend/src/features/triagem/domain/validacaoClinica";

describe("validacaoClinica", () => {
  it("test_sinais_vitais_validos_retorna_objeto_vazio", () => {
    expect(
      validarSinaisVitais({
        frequencia_cardiaca: 80,
        pressao_sistolica: 120,
        pressao_diastolica: 80,
        saturacao_o2: 98,
        temperatura: 36.7,
        frequencia_respiratoria: 16,
        glasgow: 15,
      }),
    ).toEqual({});
  });

  it("test_fc_fora_do_range_retorna_erro_no_campo_correto", () => {
    const resultado = validarSinaisVitais({ frequencia_cardiaca: 10 });

    expect(resultado.frequencia_cardiaca).toContain("20");
  });

  it("test_glasgow_invalido_retorna_erro", () => {
    const resultado = validarSinaisVitais({ glasgow: 20 });

    expect(resultado.glasgow).toBeDefined();
  });

  it("test_multiplos_campos_invalidos_retornam_todos_os_erros", () => {
    const resultado = validarSinaisVitais({
      frequencia_cardiaca: 10,
      saturacao_o2: 20,
      glasgow: 20,
    });

    expect(Object.keys(resultado)).toEqual(
      expect.arrayContaining(["frequencia_cardiaca", "saturacao_o2", "glasgow"]),
    );
  });

  it("test_alerta_critico_spo2_abaixo_de_90", () => {
    const alertas = classificarAlertaSinais({
      frequencia_cardiaca: 90,
      pressao_sistolica: 120,
      pressao_diastolica: 80,
      saturacao_o2: 88,
      temperatura: 36.8,
      frequencia_respiratoria: 16,
      glasgow: 15,
    });

    expect(alertas).toContainEqual({ campo: "saturacao_o2", alerta: "critico" });
  });

  it("test_alerta_atencao_fc_acima_de_100", () => {
    const alertas = classificarAlertaSinais({
      frequencia_cardiaca: 110,
      pressao_sistolica: 120,
      pressao_diastolica: 80,
      saturacao_o2: 98,
      temperatura: 36.8,
      frequencia_respiratoria: 16,
      glasgow: 15,
    });

    expect(alertas).toContainEqual({ campo: "frequencia_cardiaca", alerta: "atencao" });
  });

  it("test_calcular_idade_retorna_anos_completos", () => {
    const hoje = new Date();
    const aniversarioJaPassou = `${hoje.getFullYear() - 30}-01-01`;

    expect(calcularIdade(aniversarioJaPassou)).toBeGreaterThanOrEqual(30);
  });
});
