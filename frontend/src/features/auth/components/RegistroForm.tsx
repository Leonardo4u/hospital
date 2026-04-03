import { useMemo, useState, type FormEvent } from "react";

import type { Cargo } from "../../../shared/types";
import { validarCRM, validarEmail, validarSenha } from "../domain/authValidation";
import { useAuth } from "../hooks/useAuth";

interface RegistroFormProps {
  onSuccess: () => void;
}

export function RegistroForm({ onSuccess }: RegistroFormProps) {
  const { erro, isLoading, registrar } = useAuth();
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [crm, setCrm] = useState("");
  const [cargo, setCargo] = useState<Cargo>("ENFERMEIRO");

  const nomeErro = nome.trim().length === 0 ? "Informe o nome." : null;
  const emailErro = useMemo(() => validarEmail(email), [email]);
  const senhaErro = useMemo(() => validarSenha(senha), [senha]);
  const crmErro = useMemo(() => validarCRM(crm), [crm]);
  const isInvalido = [nomeErro, emailErro, senhaErro, crmErro].some((erroAtual) => erroAtual !== null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (isInvalido) {
      return;
    }

    try {
      await registrar({
        nome: nome.trim(),
        email: email.trim(),
        senha,
        crm: crm.trim().length > 0 ? crm.trim() : undefined,
        cargo,
      });
      onSuccess();
    } catch {
      return;
    }
  };

  return (
    <form
      className="w-full max-w-xl space-y-5 rounded-3xl border border-slate-200 bg-white p-8 shadow-xl"
      onSubmit={handleSubmit}
    >
      <div className="space-y-1">
        <h1 className="font-serif text-3xl text-slate-900">Novo Profissional</h1>
        <p className="text-sm text-slate-500">
          Cadastre o acesso inicial da equipe para o fluxo de triagem.
        </p>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium text-slate-700" htmlFor="nome">
          Nome completo
        </label>
        <input
          id="nome"
          type="text"
          value={nome}
          onChange={(event) => setNome(event.target.value)}
          aria-invalid={nomeErro !== null}
          className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
          placeholder="Dra. Maria da Silva"
        />
        {nomeErro !== null ? <p className="text-sm text-red-600">{nomeErro}</p> : null}
      </div>

      <div className="grid gap-5 md:grid-cols-2">
        <div className="space-y-2">
          <label className="text-sm font-medium text-slate-700" htmlFor="email">
            E-mail
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            aria-invalid={emailErro !== null}
            className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            placeholder="nome@hospital.com"
          />
          {emailErro !== null ? <p className="text-sm text-red-600">{emailErro}</p> : null}
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-slate-700" htmlFor="cargo">
            Cargo
          </label>
          <select
            id="cargo"
            value={cargo}
            onChange={(event) => setCargo(event.target.value as Cargo)}
            className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
          >
            <option value="MEDICO">Médico</option>
            <option value="ENFERMEIRO">Enfermeiro</option>
            <option value="TECNICO">Técnico</option>
          </select>
        </div>
      </div>

      <div className="grid gap-5 md:grid-cols-2">
        <div className="space-y-2">
          <label className="text-sm font-medium text-slate-700" htmlFor="senha">
            Senha
          </label>
          <input
            id="senha"
            type="password"
            value={senha}
            onChange={(event) => setSenha(event.target.value)}
            aria-invalid={senhaErro !== null}
            className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            placeholder="••••••••"
          />
          {senhaErro !== null ? <p className="text-sm text-red-600">{senhaErro}</p> : null}
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-slate-700" htmlFor="crm">
            CRM
          </label>
          <input
            id="crm"
            type="text"
            value={crm}
            onChange={(event) => setCrm(event.target.value.toUpperCase())}
            aria-invalid={crmErro !== null}
            className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            placeholder="CRM/SP 123456"
          />
          {crmErro !== null ? <p className="text-sm text-red-600">{crmErro}</p> : null}
        </div>
      </div>

      {erro !== null ? (
        <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {erro}
        </div>
      ) : null}

      <button
        type="submit"
        disabled={isLoading || isInvalido}
        className="w-full rounded-2xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-emerald-500 disabled:cursor-not-allowed disabled:bg-emerald-300"
      >
        {isLoading ? "Cadastrando..." : "Criar acesso"}
      </button>
    </form>
  );
}
