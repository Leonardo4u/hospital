import { useMemo, useState, type FormEvent } from "react";

import { validarEmail, validarSenha } from "../domain/authValidation";
import { useAuth } from "../hooks/useAuth";

interface LoginFormProps {
  onSuccess: () => void;
}

export function LoginForm({ onSuccess }: LoginFormProps) {
  const { entrar, erro, isLoading } = useAuth();
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");

  const emailErro = useMemo(() => validarEmail(email), [email]);
  const senhaErro = useMemo(() => validarSenha(senha), [senha]);
  const isInvalido = emailErro !== null || senhaErro !== null;

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (isInvalido) {
      return;
    }

    try {
      await entrar(email, senha);
      onSuccess();
    } catch {
      return;
    }
  };

  return (
    <form
      className="w-full max-w-md space-y-5 rounded-3xl border border-slate-200 bg-white p-8 shadow-xl"
      onSubmit={handleSubmit}
    >
      <div className="space-y-1">
        <h1 className="font-serif text-3xl text-slate-900">Acesso Profissional</h1>
        <p className="text-sm text-slate-500">
          Entre para registrar triagens e acompanhar a fila clínica.
        </p>
      </div>

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

      {erro !== null ? (
        <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {erro}
        </div>
      ) : null}

      <button
        type="submit"
        disabled={isLoading || isInvalido}
        className="w-full rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
      >
        {isLoading ? "Entrando..." : "Entrar"}
      </button>
    </form>
  );
}
