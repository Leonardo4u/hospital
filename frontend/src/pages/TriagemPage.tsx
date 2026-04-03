import { useMemo, useState } from "react";

import { HistoricoTriagem, TriagemWizard, usePaciente } from "@/features/triagem";

export default function TriagemPage() {
  const { pacientes } = usePaciente();
  const [buscaHistorico, setBuscaHistorico] = useState("");
  const [pacienteHistoricoId, setPacienteHistoricoId] = useState<string | null>(null);
  const [drawerAberto, setDrawerAberto] = useState(false);

  const pacientesFiltrados = useMemo(() => {
    const termo = buscaHistorico.trim().toLowerCase();
    if (termo.length === 0) {
      return pacientes.slice(0, 6);
    }

    return pacientes
      .filter((paciente) =>
        paciente.nome_completo.toLowerCase().includes(termo),
      )
      .slice(0, 6);
  }, [buscaHistorico, pacientes]);

  const historicoSidebar = (
    <aside className="space-y-5 rounded-[2rem] border border-slate-200 bg-white p-5 shadow-sm">
      <div>
        <p className="text-xs uppercase tracking-[0.3em] text-slate-500">
          Historico rapido
        </p>
        <h2 className="mt-2 font-serif text-2xl text-slate-900">
          Pacientes recentes
        </h2>
      </div>

      <div className="space-y-2">
        <label
          className="text-sm font-medium text-slate-700"
          htmlFor="busca-historico-paciente"
        >
          Buscar paciente
        </label>
        <input
          id="busca-historico-paciente"
          type="text"
          value={buscaHistorico}
          onChange={(event) => setBuscaHistorico(event.target.value)}
          placeholder="Nome do paciente"
          className="w-full rounded-2xl border border-slate-300 px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
        />
      </div>

      <div className="space-y-2">
        {pacientesFiltrados.map((paciente) => (
          <button
            key={paciente.id}
            type="button"
            onClick={() => {
              setPacienteHistoricoId(paciente.id);
              setDrawerAberto(false);
            }}
            className={`w-full rounded-2xl border px-4 py-3 text-left transition ${
              pacienteHistoricoId === paciente.id
                ? "border-blue-500 bg-blue-50"
                : "border-slate-200 bg-slate-50 hover:border-slate-300"
            }`}
          >
            <p className="font-medium text-slate-900">{paciente.nome_completo}</p>
            <p className="text-sm text-slate-500">{paciente.data_nascimento}</p>
          </button>
        ))}
      </div>

      {pacienteHistoricoId ? (
        <HistoricoTriagem pacienteId={pacienteHistoricoId} />
      ) : (
        <div className="rounded-3xl border border-dashed border-slate-300 bg-slate-50 px-4 py-5 text-sm text-slate-500">
          Selecione um paciente para visualizar o historico.
        </div>
      )}
    </aside>
  );

  return (
    <main className="min-h-screen bg-[linear-gradient(180deg,#EFF6FF_0%,#F8FAFC_35%,#E2E8F0_100%)] px-4 py-6 md:px-6 xl:px-10">
      <div className="mx-auto max-w-[1600px] space-y-6">
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-slate-500">
              Triagem Inteligente
            </p>
            <h1 className="mt-2 font-serif text-4xl text-slate-900">
              Atendimento e classificacao clinica
            </h1>
          </div>

          <button
            type="button"
            onClick={() => setDrawerAberto(true)}
            className="rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm font-semibold text-slate-700 shadow-sm lg:hidden"
          >
            Ver historico
          </button>
        </div>

        <div className="grid gap-6 lg:grid-cols-[minmax(280px,20%)_1fr]">
          <div className="hidden lg:block">{historicoSidebar}</div>
          <section className="rounded-[2.5rem] border border-slate-200 bg-white/80 p-4 shadow-xl backdrop-blur md:p-6">
            <TriagemWizard />
          </section>
        </div>
      </div>

      {drawerAberto ? (
        <div className="fixed inset-0 z-50 bg-slate-950/50 lg:hidden">
          <div className="absolute right-0 top-0 h-full w-full max-w-md overflow-y-auto bg-white p-5 shadow-2xl">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="font-serif text-2xl text-slate-900">Historico</h2>
              <button
                type="button"
                onClick={() => setDrawerAberto(false)}
                className="rounded-full border border-slate-300 px-3 py-2 text-sm text-slate-700"
              >
                Fechar
              </button>
            </div>
            {historicoSidebar}
          </div>
        </div>
      ) : null}
    </main>
  );
}
