import type { SinaisVitaisInput } from "@/shared/types";

type AlertLevel = "critico" | "atencao";

interface AlertaSinal {
  campo: keyof SinaisVitaisInput;
  alerta: AlertLevel;
}

function validarNumero(
  valor: number | undefined,
  minimo: number,
  maximo: number,
  mensagem: string,
): string | null {
  if (valor === undefined || Number.isNaN(valor)) {
    return mensagem;
  }

  if (valor < minimo || valor > maximo) {
    return mensagem;
  }

  return null;
}

export function validarSinaisVitais(
  dados: Partial<SinaisVitaisInput>,
): Record<string, string> {
  const erros: Record<string, string> = {};

  const regras: Array<[keyof SinaisVitaisInput, string | null]> = [
    [
      "frequencia_cardiaca",
      validarNumero(
        dados.frequencia_cardiaca,
        20,
        300,
        "Frequencia cardiaca deve estar entre 20 e 300 bpm.",
      ),
    ],
    [
      "pressao_sistolica",
      validarNumero(
        dados.pressao_sistolica,
        40,
        300,
        "Pressao sistolica deve estar entre 40 e 300 mmHg.",
      ),
    ],
    [
      "pressao_diastolica",
      validarNumero(
        dados.pressao_diastolica,
        20,
        200,
        "Pressao diastolica deve estar entre 20 e 200 mmHg.",
      ),
    ],
    [
      "saturacao_o2",
      validarNumero(
        dados.saturacao_o2,
        50,
        100,
        "Saturacao de O2 deve estar entre 50 e 100%.",
      ),
    ],
    [
      "temperatura",
      validarNumero(
        dados.temperatura,
        28,
        45,
        "Temperatura deve estar entre 28 e 45 C.",
      ),
    ],
    [
      "frequencia_respiratoria",
      validarNumero(
        dados.frequencia_respiratoria,
        4,
        60,
        "Frequencia respiratoria deve estar entre 4 e 60 irpm.",
      ),
    ],
    [
      "glasgow",
      validarNumero(dados.glasgow, 3, 15, "Glasgow deve estar entre 3 e 15."),
    ],
  ];

  for (const [campo, erro] of regras) {
    if (erro !== null) {
      erros[campo] = erro;
    }
  }

  return erros;
}

export function validarQueixaPrincipal(queixa: string): string | null {
  const valor = queixa.trim();
  if (valor.length < 3) {
    return "Queixa principal deve ter ao menos 3 caracteres.";
  }
  if (valor.length > 500) {
    return "Queixa principal deve ter no maximo 500 caracteres.";
  }
  return null;
}

export function calcularIdade(dataNascimento: string): number {
  const nascimento = new Date(dataNascimento);
  const hoje = new Date();
  let idade = hoje.getFullYear() - nascimento.getFullYear();
  const aniversarioAindaNaoOcorreu =
    hoje.getMonth() < nascimento.getMonth() ||
    (hoje.getMonth() === nascimento.getMonth() && hoje.getDate() < nascimento.getDate());

  if (aniversarioAindaNaoOcorreu) {
    idade -= 1;
  }

  return idade;
}

export function classificarAlertaSinais(sinais: SinaisVitaisInput): AlertaSinal[] {
  const alertas: AlertaSinal[] = [];

  const adicionarSeNecessario = (
    campo: keyof SinaisVitaisInput,
    alerta: AlertLevel,
    condicao: boolean,
  ): void => {
    if (condicao) {
      alertas.push({ campo, alerta });
    }
  };

  adicionarSeNecessario(
    "frequencia_cardiaca",
    "critico",
    sinais.frequencia_cardiaca > 150 || sinais.frequencia_cardiaca < 40,
  );
  adicionarSeNecessario(
    "saturacao_o2",
    "critico",
    sinais.saturacao_o2 < 90,
  );
  adicionarSeNecessario(
    "pressao_sistolica",
    "critico",
    sinais.pressao_sistolica < 80 || sinais.pressao_sistolica > 200,
  );
  adicionarSeNecessario("glasgow", "critico", sinais.glasgow < 8);
  adicionarSeNecessario(
    "temperatura",
    "critico",
    sinais.temperatura > 41 || sinais.temperatura < 35,
  );

  adicionarSeNecessario(
    "frequencia_cardiaca",
    "atencao",
    !alertas.some((alerta) => alerta.campo === "frequencia_cardiaca") &&
      (sinais.frequencia_cardiaca > 100 || sinais.frequencia_cardiaca < 60),
  );
  adicionarSeNecessario(
    "saturacao_o2",
    "atencao",
    !alertas.some((alerta) => alerta.campo === "saturacao_o2") && sinais.saturacao_o2 < 95,
  );
  adicionarSeNecessario(
    "pressao_sistolica",
    "atencao",
    !alertas.some((alerta) => alerta.campo === "pressao_sistolica") &&
      sinais.pressao_sistolica > 160,
  );
  adicionarSeNecessario(
    "glasgow",
    "atencao",
    !alertas.some((alerta) => alerta.campo === "glasgow") && sinais.glasgow < 13,
  );
  adicionarSeNecessario(
    "temperatura",
    "atencao",
    !alertas.some((alerta) => alerta.campo === "temperatura") && sinais.temperatura > 38.5,
  );

  return alertas;
}
