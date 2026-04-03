import { useEffect, useMemo, useState } from "react";

import type { SinaisVitaisInput } from "@/shared/types";

import { classificarAlertaSinais, validarQueixaPrincipal, validarSinaisVitais } from "../domain/validacaoClinica";
import { BodyMap } from "./BodyMap";
import { RiscoCard } from "./RiscoCard";
import { SeletorPaciente } from "./SeletorPaciente";
import { SinaisVitaisForm } from "./SinaisVitaisForm";
import { SintomaSeletor } from "./SintomaSeletor";
import { useTriagem } from "../hooks/useTriagem";

const STEPS = ["Paciente", "Sinais Vitais", "Localizacao", "Resultado"] as const;

export function TriagemWizard() {
  const {
    classificar,
    confirmar,
    erroServidor,
    errosValidacao,
    isLoading,
    pacienteSelecionado,
    queixaPrincipal,
    resetar,
    resultadoTriagem,
    selecionarPaciente,
    setQueixaPrincipal,
    setSinaisVitais,
    sinaisVitais,
    sintomasSelecionados,
    toggleSintoma,
  } = useTriagem();
  const [stepAtual, setStepAtual] = useState(1);
  const [regioesSelecionadas, setRegioesSelecionadas] = useState<string[]>([]);

  useEffect(() => {
    if (resultadoTriagem !== undefined) {
      setStepAtual(4);
    }
  }, [resultadoTriagem]);

  const alertas = useMemo(() => {
    const camposObrigatorios: (keyof SinaisVitaisInput)[] = [
      "frequencia_cardiaca",
      "pressao_sistolica",
      "pressao_diastolica",
      "saturacao_o2",
      "temperatura",
      "frequencia_respiratoria",
      "glasgow",
    ];

    if (camposObrigatorios.some((campo) => sinaisVitais[campo] === undefined)) {
      return [];
    }

    return classificarAlertaSinais(sinaisVitais as SinaisVitaisInput);
  }, [sinaisVitais]);

  const podeAvancar = useMemo(() => {
    if (stepAtual === 1) {
      return pacienteSelecionado !== null;
    }

    if (stepAtual === 2) {
      return Object.keys(validarSinaisVitais(sinaisVitais)).length === 0;
    }

    if (stepAtual === 3) {
      return validarQueixaPrincipal(queixaPrincipal) === null;
    }

    return false;
  }, [pacienteSelecionado, queixaPrincipal, sinaisVitais, stepAtual]);

  const handleToggleRegiao = (regiao: string) => {
    setRegioesSelecionadas((estadoAtual) =>
      estadoAtual.includes(regiao)
        ? estadoAtual.filter((item) => item !== regiao)
        : [...estadoAtual, regiao],
    );
  };

  const handleAvancar = () => {
    if (stepAtual === 3) {
      classificar();
      return;
    }

    if (podeAvancar) {
      setStepAtual((valorAtual) => Math.min(valorAtual + 1, 4));
    }
  };

  const handleNovaTriagem = () => {
    resetar();
    setRegioesSelecionadas([]);
    setStepAtual(1);
  };

  return (
    <section className="space-y-6">
      <div className="rounded-[2rem] border border-slate-200 bg-white p-5 shadow-sm">
        <div className="mb-4 flex items-center justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-slate-500">
              Fluxo assistencial
            </p>
            <h1 className="mt-2 font-serif text-3xl text-slate-900">
              Triagem Manchester
            </h1>
          </div>
          <span className="rounded-full bg-slate-900 px-4 py-2 text-sm font-semibold text-white">
            Etapa {stepAtual} de 4
          </span>
        </div>

        <div className="grid gap-3 md:grid-cols-4">
          {STEPS.map((step, index) => {
            const numero = index + 1;
            const ativo = numero === stepAtual;
            const concluido = numero < stepAtual;

            return (
              <div
                key={step}
                className={`rounded-2xl border px-4 py-3 text-sm font-medium ${
                  ativo
                    ? "border-blue-600 bg-blue-50 text-blue-800"
                    : concluido
                      ? "border-emerald-300 bg-emerald-50 text-emerald-700"
                      : "border-slate-200 bg-slate-50 text-slate-500"
                }`}
              >
                {numero}. {step}
              </div>
            );
          })}
        </div>
      </div>

      {stepAtual === 1 ? (
        <SeletorPaciente
          onSelecionar={selecionarPaciente}
          pacienteSelecionado={pacienteSelecionado}
        />
      ) : null}

      {stepAtual === 2 ? (
        <div className="space-y-8">
          <SinaisVitaisForm
            valores={sinaisVitais}
            erros={errosValidacao}
            alertas={alertas}
            onChange={setSinaisVitais}
          />
          <SintomaSeletor
            selecionados={sintomasSelecionados}
            onToggle={toggleSintoma}
          />
        </div>
      ) : null}

      {stepAtual === 3 ? (
        <div className="space-y-8">
          <BodyMap
            regioesSelecionadas={regioesSelecionadas}
            onToggleRegiao={handleToggleRegiao}
          />

          <section className="space-y-3 rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
            <div>
              <h2 className="font-serif text-2xl text-slate-900">Queixa principal</h2>
              <p className="text-sm text-slate-500">
                Descreva a principal queixa em termos objetivos e clinicos.
              </p>
            </div>

            <textarea
              value={queixaPrincipal}
              onChange={(event) => {
                const texto = event.target.value;
                const prefixo =
                  regioesSelecionadas.length > 0
                    ? `[${regioesSelecionadas.join(", ")}] `
                    : "";
                setQueixaPrincipal(prefixo + texto.replace(/^\[[^\]]+\]\s*/, ""));
              }}
              rows={5}
              className="w-full rounded-3xl border border-slate-300 px-4 py-4 text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              placeholder="Ex.: Dor toracica em aperto com irradiacao para membro superior esquerdo."
            />

            {errosValidacao.queixaPrincipal ? (
              <p className="text-sm text-red-600">{errosValidacao.queixaPrincipal}</p>
            ) : null}
          </section>
        </div>
      ) : null}

      {stepAtual === 4 && resultadoTriagem !== undefined ? (
        <div className="space-y-4">
          <RiscoCard
            resultado={resultadoTriagem}
            onConfirmar={confirmar}
            isConfirmando={isLoading}
          />
          <button
            type="button"
            onClick={handleNovaTriagem}
            className="rounded-2xl border border-slate-300 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:border-blue-400 hover:text-blue-700"
          >
            Nova Triagem
          </button>
        </div>
      ) : null}

      {erroServidor !== null ? (
        <div className="rounded-3xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {erroServidor}
        </div>
      ) : null}

      {stepAtual < 4 ? (
        <div className="flex items-center justify-between gap-4">
          <button
            type="button"
            onClick={() => setStepAtual((valorAtual) => Math.max(valorAtual - 1, 1))}
            disabled={stepAtual === 1}
            className="rounded-2xl border border-slate-300 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-slate-400 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Voltar
          </button>

          <button
            type="button"
            onClick={handleAvancar}
            disabled={!podeAvancar || isLoading}
            className="rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
          >
            {stepAtual === 3 ? "Classificar" : "Avancar"}
          </button>
        </div>
      ) : null}
    </section>
  );
}
