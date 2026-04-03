import { useMemo, useState } from "react";

import type { SintomaInput } from "@/shared/types";

import { SINTOMAS_CATALOGADOS } from "../domain/sintomasDB";

interface SintomaSeletorProps {
  selecionados: SintomaInput[];
  onToggle: (sintoma: SintomaInput) => void;
}

export function SintomaSeletor({
  selecionados,
  onToggle,
}: SintomaSeletorProps) {
  const [busca, setBusca] = useState("");

  const sintomasFiltrados = useMemo(() => {
    const termo = busca.trim().toLowerCase();
    if (termo.length === 0) {
      return SINTOMAS_CATALOGADOS;
    }

    return SINTOMAS_CATALOGADOS.filter((sintoma) =>
      sintoma.descricao.toLowerCase().includes(termo),
    );
  }, [busca]);

  return (
    <section className="space-y-5">
      <div>
        <h2 className="font-serif text-2xl text-slate-900">Sintomas associados</h2>
        <p className="text-sm text-slate-500">
          Selecione os sintomas observados ou relatados pelo paciente.
        </p>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium text-slate-700" htmlFor="busca-sintoma">
          Buscar sintoma
        </label>
        <input
          id="busca-sintoma"
          type="text"
          value={busca}
          onChange={(event) => setBusca(event.target.value)}
          placeholder="Ex.: dor, febre, dispneia"
          className="w-full rounded-2xl border border-slate-300 px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
        />
      </div>

      <div className="space-y-3">
        <p className="text-sm font-medium text-slate-700">Selecionados</p>
        <div className="flex min-h-14 flex-wrap gap-2 rounded-3xl border border-slate-200 bg-slate-50 p-3">
          {selecionados.length === 0 ? (
            <span className="text-sm text-slate-500">
              Nenhum sintoma selecionado ainda.
            </span>
          ) : (
            selecionados.map((sintoma) => (
              <button
                key={sintoma.codigo}
                type="button"
                aria-pressed="true"
                onClick={() => onToggle(sintoma)}
                className="rounded-full bg-blue-600 px-3 py-2 text-sm font-medium text-white"
              >
                ✓ {sintoma.descricao}
              </button>
            ))
          )}
        </div>
      </div>

      <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
        {sintomasFiltrados.map((sintoma) => {
          const ativo = selecionados.some((item) => item.codigo === sintoma.codigo);

          return (
            <button
              key={sintoma.codigo}
              type="button"
              aria-pressed={ativo}
              onClick={() => onToggle(sintoma)}
              className={`rounded-2xl border px-4 py-3 text-left transition ${
                ativo
                  ? "border-blue-600 bg-blue-50 text-blue-800"
                  : "border-slate-200 bg-white text-slate-700 hover:border-slate-300 hover:bg-slate-50"
              }`}
            >
              <span className="text-sm font-medium">{sintoma.descricao}</span>
            </button>
          );
        })}
      </div>
    </section>
  );
}
