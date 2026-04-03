import { useEffect, useMemo, useState } from "react";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import type {
  Paciente,
  RiscoNivel,
  SinaisVitaisInput,
  SintomaInput,
  TriagemResult,
} from "@/shared/types";

import {
  validarQueixaPrincipal,
  validarSinaisVitais,
} from "../domain/validacaoClinica";
import * as triagemApi from "../services/triagemApi";

const SINAIS_VITAIS_PADRAO: SinaisVitaisInput = {
  frequencia_cardiaca: 78,
  pressao_sistolica: 120,
  pressao_diastolica: 80,
  saturacao_o2: 98,
  temperatura: 36.7,
  frequencia_respiratoria: 16,
  glasgow: 15,
};

function normalizarSinaisVitais(
  estadoAtual: Partial<SinaisVitaisInput>,
): Partial<SinaisVitaisInput> {
  const normalizado: Partial<SinaisVitaisInput> = { ...estadoAtual };

  (Object.keys(SINAIS_VITAIS_PADRAO) as (keyof SinaisVitaisInput)[]).forEach((campo) => {
    const valor = estadoAtual[campo];
    if (typeof valor !== "number" || Number.isNaN(valor) || valor <= 0) {
      normalizado[campo] = SINAIS_VITAIS_PADRAO[campo];
    }
  });

  return normalizado;
}

function extrairMensagemErro(error: unknown): string | null {
  if (typeof error === "object" && error !== null && "response" in error) {
    const response = (error as { response?: { data?: { detail?: unknown } } }).response;
    const detail = response?.data?.detail;
    if (typeof detail === "string") {
      return detail;
    }
  }

  return null;
}

export function useTriagem(pacienteIdHistorico?: string) {
  const queryClient = useQueryClient();
  const [pacienteSelecionado, setPacienteSelecionado] = useState<Paciente | null>(null);
  const [sinaisVitais, setSinaisVitaisState] = useState<Partial<SinaisVitaisInput>>(SINAIS_VITAIS_PADRAO);
  const [sintomasSelecionados, setSintomasSelecionados] = useState<SintomaInput[]>([]);
  const [queixaPrincipal, setQueixaPrincipal] = useState("");
  const [errosValidacao, setErrosValidacao] = useState<Record<string, string>>({});
  const [triagemRealizadaId, setTriagemRealizadaId] = useState<string | null>(null);

  useEffect(() => {
    setSinaisVitaisState((estadoAtual) => normalizarSinaisVitais(estadoAtual));
  }, []);

  const resultadoTriagemQuery = useQuery({
    queryKey: ["triagem", triagemRealizadaId],
    queryFn: () => triagemApi.buscarTriagem(triagemRealizadaId as string),
    enabled: triagemRealizadaId !== null,
  });

  const historicoPacienteQuery = useQuery({
    queryKey: ["triagens", "paciente", pacienteIdHistorico],
    queryFn: () => triagemApi.listarPorPaciente(pacienteIdHistorico as string),
    enabled: pacienteIdHistorico !== undefined && pacienteIdHistorico.length > 0,
  });

  const classificarMutation = useMutation({
    mutationFn: () =>
      triagemApi.classificar({
        paciente_id: pacienteSelecionado?.id ?? "",
        sinais_vitais: sinaisVitais as SinaisVitaisInput,
        sintomas: sintomasSelecionados,
        queixa_principal: queixaPrincipal.trim(),
      }),
    onSuccess: (data) => {
      setTriagemRealizadaId(data.id);
    },
  });

  const confirmarMutation = useMutation({
    mutationFn: (nivel: RiscoNivel) =>
      triagemApi.confirmarTriagem(triagemRealizadaId as string, nivel),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["triagem", triagemRealizadaId] });
      if (pacienteSelecionado !== null) {
        await queryClient.invalidateQueries({
          queryKey: ["triagens", "paciente", pacienteSelecionado.id],
        });
      }
    },
  });

  return useMemo(
    () => ({
      pacienteSelecionado,
      sinaisVitais,
      sintomasSelecionados,
      queixaPrincipal,
      errosValidacao,
      triagemRealizadaId,
      resultadoTriagem: resultadoTriagemQuery.data as TriagemResult | undefined,
      historicoPaciente: historicoPacienteQuery.data ?? [],
      erroServidor:
        extrairMensagemErro(classificarMutation.error) ??
        extrairMensagemErro(confirmarMutation.error) ??
        extrairMensagemErro(resultadoTriagemQuery.error) ??
        extrairMensagemErro(historicoPacienteQuery.error),
      classificar: () => {
        const erros = validarSinaisVitais(sinaisVitais);
        const erroQueixa = validarQueixaPrincipal(queixaPrincipal);
        if (erroQueixa !== null) {
          erros.queixaPrincipal = erroQueixa;
        }
        if (pacienteSelecionado === null) {
          erros.paciente = "Selecione um paciente para continuar.";
        }
        if (Object.keys(erros).length > 0) {
          setErrosValidacao(erros);
          return;
        }

        setErrosValidacao({});
        classificarMutation.mutate();
      },
      confirmar: (nivel: RiscoNivel) => {
        if (triagemRealizadaId === null) {
          return;
        }
        confirmarMutation.mutate(nivel);
      },
      setSinaisVitais: (campo: keyof SinaisVitaisInput, valor: number | undefined) => {
        setSinaisVitaisState((estadoAtual) => ({
          ...(valor === undefined || Number.isNaN(valor)
            ? Object.fromEntries(
                Object.entries(estadoAtual).filter(([chave]) => chave !== campo),
              )
            : {
                ...estadoAtual,
                [campo]: valor,
              }),
        }));
        setErrosValidacao((estadoAtual) => {
          const proximo = { ...estadoAtual };
          delete proximo[campo];
          return proximo;
        });
      },
      toggleSintoma: (sintoma: SintomaInput) => {
        setSintomasSelecionados((estadoAtual) =>
          estadoAtual.some((item) => item.codigo === sintoma.codigo)
            ? estadoAtual.filter((item) => item.codigo !== sintoma.codigo)
            : [...estadoAtual, sintoma],
        );
      },
      selecionarPaciente: (paciente: Paciente) => {
        setPacienteSelecionado(paciente);
        setErrosValidacao((estadoAtual) => {
          const proximo = { ...estadoAtual };
          delete proximo.paciente;
          return proximo;
        });
      },
      setQueixaPrincipal: (valor: string) => {
        setQueixaPrincipal(valor);
        setErrosValidacao((estadoAtual) => {
          const proximo = { ...estadoAtual };
          delete proximo.queixaPrincipal;
          return proximo;
        });
      },
      resetar: () => {
        setPacienteSelecionado(null);
        setSinaisVitaisState(SINAIS_VITAIS_PADRAO);
        setSintomasSelecionados([]);
        setQueixaPrincipal("");
        setErrosValidacao({});
        setTriagemRealizadaId(null);
      },
      isLoading:
        classificarMutation.isPending ||
        confirmarMutation.isPending ||
        resultadoTriagemQuery.isLoading ||
        historicoPacienteQuery.isLoading,
    }),
    [
      classificarMutation,
      confirmarMutation,
      errosValidacao,
      historicoPacienteQuery.data,
      historicoPacienteQuery.error,
      historicoPacienteQuery.isLoading,
      pacienteSelecionado,
      queryClient,
      queixaPrincipal,
      resultadoTriagemQuery.data,
      resultadoTriagemQuery.error,
      resultadoTriagemQuery.isLoading,
      sinaisVitais,
      sintomasSelecionados,
      triagemRealizadaId,
    ],
  );
}
