import { useEffect, useMemo, useState, type FormEvent } from "react";

import type { Paciente, Sexo } from "@/shared/types";

import { calcularIdade } from "../domain/validacaoClinica";
import { usePaciente } from "../hooks/usePaciente";

interface SeletorPacienteProps {
  onSelecionar: (paciente: Paciente) => void;
  pacienteSelecionado: Paciente | null;
}

interface NovoPacienteForm {
  nome_completo: string;
  data_nascimento: string;
  sexo: Sexo;
  cpf: string;
  contato_emergencia: string;
}

const FORM_INICIAL: NovoPacienteForm = {
  nome_completo: "",
  data_nascimento: "",
  sexo: "F",
  cpf: "",
  contato_emergencia: "",
};

export function SeletorPaciente({
  onSelecionar,
  pacienteSelecionado,
}: SeletorPacienteProps) {
  const { criarPaciente, pacientes } = usePaciente();
  const [busca, setBusca] = useState("");
  const [buscaDebounced, setBuscaDebounced] = useState("");
  const [modalAberto, setModalAberto] = useState(false);
  const [novoPaciente, setNovoPaciente] = useState<NovoPacienteForm>(FORM_INICIAL);

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      setBuscaDebounced(busca.trim().toLowerCase());
    }, 300);

    return () => {
      window.clearTimeout(timeout);
    };
  }, [busca]);

  const resultados = useMemo(() => {
    if (buscaDebounced.length === 0) {
      return pacientes.slice(0, 8);
    }

    return pacientes
      .filter((paciente) =>
        paciente.nome_completo.toLowerCase().includes(buscaDebounced),
      )
      .slice(0, 8);
  }, [buscaDebounced, pacientes]);

  const handleCriarPaciente = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const pacienteCriado = await criarPaciente({
      nome_completo: novoPaciente.nome_completo.trim(),
      data_nascimento: novoPaciente.data_nascimento,
      sexo: novoPaciente.sexo,
      cpf: novoPaciente.cpf.trim().length > 0 ? novoPaciente.cpf.trim() : null,
      contato_emergencia:
        novoPaciente.contato_emergencia.trim().length > 0
          ? novoPaciente.contato_emergencia.trim()
          : null,
    });

    onSelecionar(pacienteCriado);
    setNovoPaciente(FORM_INICIAL);
    setModalAberto(false);
    setBusca("");
  };

  return (
    <section className="space-y-5">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="font-serif text-2xl text-slate-900">Paciente</h2>
          <p className="text-sm text-slate-500">
            Busque um paciente existente ou crie um novo cadastro no fluxo.
          </p>
        </div>
        <button
          type="button"
          onClick={() => setModalAberto((estadoAtual) => !estadoAtual)}
          className="rounded-2xl border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-blue-400 hover:text-blue-700"
        >
          Novo paciente
        </button>
      </div>

      <div className="space-y-3">
        <label className="text-sm font-medium text-slate-700" htmlFor="busca-paciente">
          Buscar paciente
        </label>
        <input
          id="busca-paciente"
          type="text"
          value={busca}
          onChange={(event) => setBusca(event.target.value)}
          placeholder="Digite o nome do paciente"
          className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
        />

        <div
          role="listbox"
          aria-label="Resultados de pacientes"
          className="max-h-72 space-y-2 overflow-y-auto rounded-3xl border border-slate-200 bg-slate-50 p-3"
        >
          {resultados.length === 0 ? (
            <p className="px-2 py-3 text-sm text-slate-500">
              Nenhum paciente encontrado com esse nome.
            </p>
          ) : null}

          {resultados.map((paciente) => {
            const idade = calcularIdade(paciente.data_nascimento);
            const selecionado = pacienteSelecionado?.id === paciente.id;

            return (
              <button
                key={paciente.id}
                type="button"
                role="option"
                aria-selected={selecionado}
                onClick={() => onSelecionar(paciente)}
                className={`flex w-full items-center justify-between rounded-2xl border px-4 py-3 text-left transition ${
                  selecionado
                    ? "border-blue-500 bg-blue-50"
                    : "border-transparent bg-white hover:border-slate-200 hover:bg-slate-100"
                }`}
              >
                <div>
                  <p className="font-medium text-slate-900">{paciente.nome_completo}</p>
                  <p className="text-sm text-slate-500">
                    Nascimento: {paciente.data_nascimento}
                  </p>
                </div>
                <span className="rounded-full bg-slate-900 px-3 py-1 text-xs font-semibold text-white">
                  {idade} anos
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {pacienteSelecionado !== null ? (
        <div className="rounded-3xl border border-emerald-200 bg-emerald-50 px-5 py-4">
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-emerald-700">
            Paciente selecionado
          </p>
          <div className="mt-3 flex flex-wrap items-center gap-3">
            <p className="text-lg font-semibold text-slate-900">
              {pacienteSelecionado.nome_completo}
            </p>
            <span className="rounded-full bg-emerald-600 px-3 py-1 text-xs font-semibold text-white">
              {calcularIdade(pacienteSelecionado.data_nascimento)} anos
            </span>
          </div>
          <p className="mt-2 text-sm text-slate-600">
            Data de nascimento: {pacienteSelecionado.data_nascimento}
          </p>
        </div>
      ) : null}

      {modalAberto ? (
        <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-lg">
          <div className="mb-4">
            <h3 className="font-serif text-xl text-slate-900">Novo paciente</h3>
            <p className="text-sm text-slate-500">
              Crie o cadastro rapidamente sem sair da triagem.
            </p>
          </div>

          <form className="space-y-4" onSubmit={handleCriarPaciente}>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700" htmlFor="nome_completo">
                Nome completo
              </label>
              <input
                id="nome_completo"
                type="text"
                value={novoPaciente.nome_completo}
                onChange={(event) =>
                  setNovoPaciente((estadoAtual) => ({
                    ...estadoAtual,
                    nome_completo: event.target.value,
                  }))
                }
                className="w-full rounded-2xl border border-slate-300 px-4 py-3"
                required
              />
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700" htmlFor="data_nascimento">
                  Data de nascimento
                </label>
                <input
                  id="data_nascimento"
                  type="date"
                  value={novoPaciente.data_nascimento}
                  onChange={(event) =>
                    setNovoPaciente((estadoAtual) => ({
                      ...estadoAtual,
                      data_nascimento: event.target.value,
                    }))
                  }
                  className="w-full rounded-2xl border border-slate-300 px-4 py-3"
                  required
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700" htmlFor="sexo">
                  Sexo
                </label>
                <select
                  id="sexo"
                  value={novoPaciente.sexo}
                  onChange={(event) =>
                    setNovoPaciente((estadoAtual) => ({
                      ...estadoAtual,
                      sexo: event.target.value as Sexo,
                    }))
                  }
                  className="w-full rounded-2xl border border-slate-300 px-4 py-3"
                >
                  <option value="F">Feminino</option>
                  <option value="M">Masculino</option>
                  <option value="OUTRO">Outro</option>
                </select>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700" htmlFor="cpf">
                  CPF
                </label>
                <input
                  id="cpf"
                  type="text"
                  value={novoPaciente.cpf}
                  onChange={(event) =>
                    setNovoPaciente((estadoAtual) => ({
                      ...estadoAtual,
                      cpf: event.target.value,
                    }))
                  }
                  className="w-full rounded-2xl border border-slate-300 px-4 py-3"
                  placeholder="Opcional"
                />
              </div>

              <div className="space-y-2">
                <label
                  className="text-sm font-medium text-slate-700"
                  htmlFor="contato_emergencia"
                >
                  Contato de emergencia
                </label>
                <input
                  id="contato_emergencia"
                  type="text"
                  value={novoPaciente.contato_emergencia}
                  onChange={(event) =>
                    setNovoPaciente((estadoAtual) => ({
                      ...estadoAtual,
                      contato_emergencia: event.target.value,
                    }))
                  }
                  className="w-full rounded-2xl border border-slate-300 px-4 py-3"
                  placeholder="Opcional"
                />
              </div>
            </div>

            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setModalAberto(false)}
                className="rounded-2xl border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700"
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="rounded-2xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-500"
              >
                Salvar paciente
              </button>
            </div>
          </form>
        </div>
      ) : null}
    </section>
  );
}
