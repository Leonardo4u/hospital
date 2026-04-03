import { lazy, Suspense, type ReactNode } from "react";
import { Navigate, createBrowserRouter, Link, useNavigate } from "react-router-dom";

import { LoginForm, RegistroForm } from "../../features/auth";
import { PrivateRoute } from "./PrivateRoute";

function Shell({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: ReactNode;
}) {
  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(37,99,235,0.12),_transparent_38%),linear-gradient(180deg,#F8FAFC_0%,#E2E8F0_100%)] px-6 py-12">
      <div className="mx-auto flex max-w-6xl flex-col items-center gap-8">
        <div className="w-full max-w-3xl text-center">
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500">
            Triagem Inteligente
          </p>
          <h1 className="mt-4 font-serif text-5xl text-slate-900">{title}</h1>
          <p className="mt-4 text-lg text-slate-600">{subtitle}</p>
        </div>
        {children}
      </div>
    </main>
  );
}

function LoginPage() {
  const navigate = useNavigate();

  return (
    <Shell
      title="Entrada Clinica Segura"
      subtitle="Autentique sua equipe para acessar o painel de triagem e confirmacao de risco."
    >
      <LoginForm onSuccess={() => navigate("/triagem")} />
      <p className="text-sm text-slate-600">
        Ainda sem acesso?{" "}
        <Link className="font-semibold text-blue-700 hover:text-blue-500" to="/registro">
          Registrar profissional
        </Link>
      </p>
    </Shell>
  );
}

const RegistroPage = lazy(async () => ({
  default: function RegistroPageComponent() {
    const navigate = useNavigate();

    return (
      <Shell
        title="Cadastro Inicial da Equipe"
        subtitle="Configure o primeiro acesso do time assistencial com seguranca e rastreabilidade."
      >
        <RegistroForm onSuccess={() => navigate("/login")} />
      </Shell>
    );
  },
}));

function PlaceholderPage({
  titulo,
  descricao,
}: {
  titulo: string;
  descricao: string;
}) {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-12 text-white">
      <div className="mx-auto max-w-5xl rounded-[2rem] border border-white/10 bg-white/5 p-10 backdrop-blur">
        <p className="text-sm uppercase tracking-[0.3em] text-cyan-300">Sessao seguinte</p>
        <h1 className="mt-4 font-serif text-5xl">{titulo}</h1>
        <p className="mt-5 max-w-2xl text-lg text-slate-300">{descricao}</p>
      </div>
    </main>
  );
}

const TriagemPage = lazy(async () => import("../../pages/TriagemPage"));

const PacientesPage = lazy(async () => ({
  default: function PacientesPageComponent() {
    return (
      <PlaceholderPage
        titulo="Gestao de Pacientes"
        descricao="A listagem, busca e edicao de pacientes entram na proxima etapa do frontend."
      />
    );
  },
}));

const HistoricoPage = lazy(async () => ({
  default: function HistoricoPageComponent() {
    return (
      <PlaceholderPage
        titulo="Historico Clinico"
        descricao="O historico de triagens confirmadas sera conectado nas proximas features."
      />
    );
  },
}));

function withSuspense(element: ReactNode) {
  return (
    <Suspense fallback={<div className="p-8 text-center text-slate-500">Carregando...</div>}>
      {element}
    </Suspense>
  );
}

export const router = createBrowserRouter([
  {
    path: "/login",
    element: <LoginPage />,
  },
  {
    path: "/registro",
    element: withSuspense(<RegistroPage />),
  },
  {
    element: <PrivateRoute />,
    children: [
      {
        path: "/",
        element: <Navigate to="/triagem" replace />,
      },
      {
        path: "/triagem",
        element: withSuspense(<TriagemPage />),
      },
      {
        path: "/pacientes",
        element: withSuspense(<PacientesPage />),
      },
      {
        path: "/historico",
        element: withSuspense(<HistoricoPage />),
      },
    ],
  },
]);
