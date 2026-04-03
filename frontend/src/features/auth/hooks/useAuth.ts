import { useMemo, useState } from "react";

import type { ApiError, Profissional } from "../../../shared/types";
import { useAuthStore } from "../../../store/authSlice";
import * as authApi from "../services/authApi";
import { getMeuPerfil } from "../services/profissionalApi";

function extrairMensagemErro(error: unknown): string {
  if (typeof error === "object" && error !== null && "response" in error) {
    const response = (error as { response?: { data?: unknown } }).response;
    const data = response?.data;
    if (
      typeof data === "object" &&
      data !== null &&
      "detail" in data
    ) {
      const detail = (data as ApiError).detail;
      if (typeof detail === "string") {
        return detail;
      }
      if (Array.isArray(detail) && detail.length > 0) {
        return detail[0]?.msg ?? "Não foi possível concluir a operação.";
      }
    }
  }

  return "Não foi possível concluir a operação.";
}

type RegistroInput = authApi.RegistroInput;

interface UseAuthResult {
  profissional: Profissional | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  erro: string | null;
  entrar: (email: string, senha: string) => Promise<void>;
  sair: () => void;
  registrar: (dados: RegistroInput) => Promise<void>;
}

export function useAuth(): UseAuthResult {
  const profissional = useAuthStore((state) => state.profissional);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const storeLogin = useAuthStore((state) => state.login);
  const storeLogout = useAuthStore((state) => state.logout);
  const [isLoading, setIsLoading] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  return useMemo(
    () => ({
      profissional,
      isAuthenticated,
      isLoading,
      erro,
      entrar: async (email: string, senha: string) => {
        setIsLoading(true);
        setErro(null);
        try {
          const tokens = await authApi.login(email, senha);
          const perfil = await getMeuPerfil(tokens.access_token);
          storeLogin(perfil, tokens.access_token, tokens.refresh_token);
        } catch (error: unknown) {
          setErro(extrairMensagemErro(error));
          throw error;
        } finally {
          setIsLoading(false);
        }
      },
      sair: () => {
        setErro(null);
        storeLogout();
      },
      registrar: async (dados: RegistroInput) => {
        setIsLoading(true);
        setErro(null);
        try {
          await authApi.registro(dados);
        } catch (error: unknown) {
          setErro(extrairMensagemErro(error));
          throw error;
        } finally {
          setIsLoading(false);
        }
      },
    }),
    [erro, isAuthenticated, isLoading, profissional, storeLogin, storeLogout],
  );
}
