import { useMemo } from "react";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import type { Paciente } from "@/shared/types";

import * as pacienteApi from "../services/pacienteApi";

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

export function usePaciente(pacienteId?: string) {
  const queryClient = useQueryClient();

  const pacienteQuery = useQuery({
    queryKey: ["paciente", pacienteId],
    queryFn: () => pacienteApi.buscarPaciente(pacienteId as string),
    enabled: pacienteId !== undefined && pacienteId.length > 0,
  });

  const pacientesQuery = useQuery({
    queryKey: ["pacientes", 0, 20],
    queryFn: () => pacienteApi.listarPacientes(),
  });

  const criarMutation = useMutation({
    mutationFn: (dados: pacienteApi.PacienteCreateInput) => pacienteApi.criarPaciente(dados),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["pacientes"] });
    },
  });

  return useMemo(
    () => ({
      paciente: pacienteQuery.data as Paciente | undefined,
      isLoading:
        pacienteQuery.isLoading ||
        pacientesQuery.isLoading ||
        criarMutation.isPending,
      erro:
        extrairMensagemErro(pacienteQuery.error) ??
        extrairMensagemErro(pacientesQuery.error) ??
        extrairMensagemErro(criarMutation.error),
      pacientes: pacientesQuery.data ?? [],
      criarPaciente: async (dados: pacienteApi.PacienteCreateInput) =>
        criarMutation.mutateAsync(dados),
    }),
    [
      criarMutation,
      pacienteQuery.data,
      pacienteQuery.error,
      pacienteQuery.isLoading,
      pacientesQuery.data,
      pacientesQuery.error,
      pacientesQuery.isLoading,
    ],
  );
}
