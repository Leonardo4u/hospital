import { create } from "zustand";

import type { Profissional } from "../shared/types";

const ACCESS_TOKEN_KEY = "access_token";
const REFRESH_TOKEN_KEY = "refresh_token";
const PROFISSIONAL_KEY = "profissional";

interface AuthState {
  profissional: Profissional | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  login: (profissional: Profissional, accessToken: string, refreshToken: string) => void;
  logout: () => void;
  atualizarTokens: (accessToken: string, refreshToken: string) => void;
  hidratarDoStorage: () => void;
}

function salvarAuthNoStorage(
  profissional: Profissional | null,
  accessToken: string | null,
  refreshToken: string | null,
): void {
  if (typeof window === "undefined") {
    return;
  }

  if (accessToken === null || refreshToken === null || profissional === null) {
    window.localStorage.removeItem(ACCESS_TOKEN_KEY);
    window.localStorage.removeItem(REFRESH_TOKEN_KEY);
    window.localStorage.removeItem(PROFISSIONAL_KEY);
    return;
  }

  window.localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  window.localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  window.localStorage.setItem(PROFISSIONAL_KEY, JSON.stringify(profissional));
}

function lerProfissionalDoStorage(): Profissional | null {
  if (typeof window === "undefined") {
    return null;
  }

  const bruto = window.localStorage.getItem(PROFISSIONAL_KEY);
  if (bruto === null) {
    return null;
  }

  try {
    const parsed: unknown = JSON.parse(bruto);
    if (
      typeof parsed === "object" &&
      parsed !== null &&
      "id" in parsed &&
      "nome" in parsed &&
      "email" in parsed &&
      "cargo" in parsed &&
      "ativo" in parsed
    ) {
      return parsed as Profissional;
    }
  } catch {
    return null;
  }

  return null;
}

export const useAuthStore = create<AuthState>((set) => ({
  profissional: null,
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  login: (profissional, accessToken, refreshToken) => {
    salvarAuthNoStorage(profissional, accessToken, refreshToken);
    set({
      profissional,
      accessToken,
      refreshToken,
      isAuthenticated: accessToken !== null,
    });
  },
  logout: () => {
    salvarAuthNoStorage(null, null, null);
    set({
      profissional: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
    });
  },
  atualizarTokens: (accessToken, refreshToken) => {
    set((state) => {
      salvarAuthNoStorage(state.profissional, accessToken, refreshToken);
      return {
        accessToken,
        refreshToken,
        isAuthenticated: accessToken !== null,
      };
    });
  },
  hidratarDoStorage: () => {
    if (typeof window === "undefined") {
      return;
    }

    const accessToken = window.localStorage.getItem(ACCESS_TOKEN_KEY);
    const refreshToken = window.localStorage.getItem(REFRESH_TOKEN_KEY);
    const profissional = lerProfissionalDoStorage();

    set({
      profissional,
      accessToken,
      refreshToken,
      isAuthenticated: accessToken !== null,
    });
  },
}));
