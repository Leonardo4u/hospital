import { useMemo } from "react";

import { getNivelInfo } from "@/shared/types";

import { usePaciente } from "../hooks/usePaciente";
import { useTriagem } from "../hooks/useTriagem";

interface HistoricoTriagemProps {
  pacienteId: string;
}

export function HistoricoTriagem({ pacienteId }: HistoricoTriagemProps) {
  const { paciente, isLoading: isLoadingPaciente } = usePaciente(pacienteId);
  const { historicoPaciente, isLoading } = useTriagem(pacienteId);

  const triagensOrdenadas = useMemo(
    () =>
      [...historicoPaciente].sort(
        (a, b) =>
          new Date(b.criado_em).getTime() - new Date(a.criado_em).getTime(),
      ),
    [historicoPaciente],
  );

  if (isLoading || isLoadingPaciente) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 3 }).map((_, index) => (
          <div
            key={index}
            className="h-20 animate-pulse rounded-3xl bg-slate-200"
          />
        ))}
      </div>
    );
  }

  if (triagensOrdenadas.length === 0) {
    return (
      <div className="rounded-[2rem] border border-dashed border-slate-300 bg-slate-50 px-5 py-6 text-sm text-slate-500">
        Nenhuma triagem registrada para este paciente
      </div>
    );
  }

  return (
    <section className="space-y-4">
      <div>
        <h2 className="font-serif text-2xl text-slate-900">Historico de triagens</h2>
        <p className="text-sm text-slate-500">
          {paciente ? `Ultimos registros de ${paciente.nome_completo}.` : "Registros recentes do paciente selecionado."}
        </p>
      </div>

      <div className="space-y-3">
        {triagensOrdenadas.map((triagem) => {
          const nivelInfo = getNivelInfo(triagem.nivel_calculado);

          return (
            <article
              key={triagem.id}
              className="rounded-[2rem] border border-slate-200 bg-white p-4 shadow-sm"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm text-slate-500">
                    {new Date(triagem.criado_em).toLocaleString("pt-BR")}
                  </p>
                  <p className="mt-2 font-medium text-slate-900">
                    {triagem.queixa_principal}
                  </p>
                </div>

                <span
                  className="rounded-full px-3 py-1 text-xs font-semibold"
                  style={{
                    backgroundColor: nivelInfo.cor,
                    color: nivelInfo.corTexto,
                  }}
                >
                  {triagem.nivel_calculado}
                </span>
              </div>

              {triagem.nivel_confirmado ? (
                <p className="mt-3 text-xs font-semibold uppercase tracking-[0.25em] text-emerald-700">
                  Confirmado
                </p>
              ) : null}
            </article>
          );
        })}
      </div>
    </section>
  );
}
