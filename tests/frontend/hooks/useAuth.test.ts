import { renderHook, act, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { server, errorHandler } from "../mocks/handlers";
import { useAuth } from "../../../frontend/src/features/auth/hooks/useAuth";
import { useAuthStore } from "../../../frontend/src/store/authSlice";

describe("useAuth", () => {
  it("test_login_sucesso_popula_store_com_profissional", async () => {
    const { result } = renderHook(() => useAuth());
    await act(async () => {
      await result.current.entrar("alice@triagem.local", "Senha@123");
    });
    expect(useAuthStore.getState().profissional?.email).toBe("alice@triagem.local");
  });

  it("test_login_sucesso_persiste_tokens_no_localstorage", async () => {
    const { result } = renderHook(() => useAuth());
    await act(async () => {
      await result.current.entrar("alice@triagem.local", "Senha@123");
    });
    expect(window.localStorage.getItem("access_token")).toBeTruthy();
  });

  it("test_login_credenciais_invalidas_seta_erro_legivel", async () => {
    server.use(errorHandler("/auth/login", 401, "Credenciais invalidas."));
    const { result } = renderHook(() => useAuth());
    await act(async () => {
      await expect(result.current.entrar("alice@triagem.local", "errada")).rejects.toBeDefined();
    });
    expect(result.current.erro).toBeTruthy();
  });

  it("test_logout_limpa_profissional_do_store", async () => {
    const { result } = renderHook(() => useAuth());
    await act(async () => {
      await result.current.entrar("alice@triagem.local", "Senha@123");
      result.current.sair();
    });
    expect(useAuthStore.getState().profissional).toBeNull();
  });

  it("test_logout_remove_tokens_do_localstorage", async () => {
    const { result } = renderHook(() => useAuth());
    await act(async () => {
      await result.current.entrar("alice@triagem.local", "Senha@123");
      result.current.sair();
    });
    expect(window.localStorage.getItem("access_token")).toBeNull();
  });

  it("test_is_authenticated_false_apos_logout", async () => {
    const { result } = renderHook(() => useAuth());
    await act(async () => {
      await result.current.entrar("alice@triagem.local", "Senha@123");
      result.current.sair();
    });
    expect(useAuthStore.getState().isAuthenticated).toBe(false);
  });

  it("test_registrar_sucesso_nao_loga_automaticamente", async () => {
    const { result } = renderHook(() => useAuth());
    await act(async () => {
      await result.current.registrar({
        nome: "Nova",
        email: "nova@triagem.local",
        senha: "Senha@123",
        cargo: "MEDICO",
      });
    });
    await waitFor(() => {
      expect(useAuthStore.getState().isAuthenticated).toBe(false);
    });
  });
});
