import { getNivelInfo, NIVEL_INFO, ordenarPorGravidade } from "@/shared/types";
import type { RiscoNivel, TriagemResult } from "@/shared/types";

interface RiscoCardProps {
  resultado: TriagemResult;
  onConfirmar: (nivel: RiscoNivel) => void;
  isConfirmando: boolean;
}

const NIVEIS_ORDENADOS = ordenarPorGravidade([
  "AZUL",
  "VERDE",
  "AMARELO",
  "LARANJA",
  "VERMELHO",
]);

export function RiscoCard({
  resultado,
  onConfirmar,
  isConfirmando,
}: RiscoCardProps) {
  const info = getNivelInfo(resultado.nivel_calculado);
  const confirmadoInfo = resultado.nivel_confirmado
    ? getNivelInfo(resultado.nivel_confirmado)
    : null;

  return (
    <article
      role="status"
      aria-live="polite"
      className="overflow-hidden rounded-[2rem] border border-slate-200 bg-white shadow-lg"
    >
      <header
        className="px-6 py-6"
        style={{ backgroundColor: info.cor, color: info.corTexto }}
      >
        <p className="text-sm uppercase tracking-[0.35em] opacity-90">
          Classificacao calculada
        </p>
        <h2 className="mt-3 font-serif text-4xl">
          {resultado.nivel_calculado} - {info.label}
        </h2>
        <p className="mt-3 text-sm font-medium opacity-90">
          {info.tempoMaximoMinutos === null
            ? "Atendimento imediato"
            : `Tempo maximo recomendado: ${info.tempoMaximoMinutos} minutos`}
        </p>
      </header>

      <div className="space-y-6 px-6 py-6">
        <section className="space-y-2">
          <h3 className="text-sm font-semibold uppercase tracking-[0.25em] text-slate-500">
            Justificativa
          </h3>
          <p className="rounded-3xl bg-slate-50 p-4 text-slate-700">
            {resultado.justificativa}
          </p>
        </section>

        <section className="space-y-3">
          <h3 className="text-sm font-semibold uppercase tracking-[0.25em] text-slate-500">
            Discriminadores ativados
          </h3>
          <div className="flex flex-wrap gap-2">
            {resultado.discriminadores_ativados.map((item) => (
              <span
                key={item}
                className="rounded-full bg-slate-900 px-3 py-2 text-xs font-semibold text-white"
              >
                {item}
              </span>
            ))}
          </div>
        </section>

        <section className="space-y-4">
          <h3 className="text-sm font-semibold uppercase tracking-[0.25em] text-slate-500">
            Confirmar classificacao
          </h3>

          {resultado.nivel_confirmado === null ? (
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
              {NIVEIS_ORDENADOS.map((nivel) => {
                const nivelInfo = NIVEL_INFO[nivel];
                const sugerido = resultado.nivel_calculado === nivel;

                return (
                  <button
                    key={nivel}
                    type="button"
                    disabled={isConfirmando}
                    onClick={() => onConfirmar(nivel)}
                    className={`rounded-3xl border-2 px-4 py-4 text-left transition disabled:cursor-not-allowed disabled:opacity-60 ${
                      sugerido ? "border-slate-900 shadow-md" : "border-transparent"
                    }`}
                    style={{
                      backgroundColor: nivelInfo.cor,
                      color: nivelInfo.corTexto,
                    }}
                  >
                    <p className="text-xs uppercase tracking-[0.3em] opacity-80">
                      {sugerido ? "Sugerido" : "Confirmar"}
                    </p>
                    <p className="mt-2 text-lg font-bold">{nivel}</p>
                    <p className="text-sm opacity-90">{nivelInfo.label}</p>
                  </button>
                );
              })}
            </div>
          ) : (
            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
              <div className="flex flex-wrap items-center gap-3">
                <span className="rounded-full bg-emerald-600 px-3 py-1 text-xs font-semibold text-white">
                  Confirmado
                </span>
                <span
                  className="rounded-full px-3 py-1 text-sm font-semibold"
                  style={{
                    backgroundColor: confirmadoInfo?.cor,
                    color: confirmadoInfo?.corTexto,
                  }}
                >
                  {resultado.nivel_confirmado}
                </span>
                {resultado.nivel_confirmado !== resultado.nivel_calculado ? (
                  <span className="rounded-full bg-amber-400 px-3 py-1 text-xs font-semibold text-slate-900">
                    Corrigido pelo profissional
                  </span>
                ) : null}
              </div>
            </div>
          )}

          {isConfirmando ? (
            <div className="flex items-center gap-3 text-sm text-slate-500">
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-300 border-t-slate-800" />
              Confirmando classificacao...
            </div>
          ) : null}
        </section>
      </div>
    </article>
  );
}
