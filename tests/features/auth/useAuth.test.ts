import { renderHook, act } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useAuthStore } from "../../../frontend/src/store/authSlice";
import { validarEmail, validarSenha } from "../../../frontend/src/features/auth/domain/authValidation";
import { useAuth } from "../../../frontend/src/features/auth/hooks/useAuth";

const loginMock = vi.fn();
const registroMock = vi.fn();
const getMeuPerfilMock = vi.fn();

vi.mock("../../../frontend/src/features/auth/services/authApi", () => ({
  login: (...args: unknown[]) => loginMock(...args),
  registro: (...args: unknown[]) => registroMock(...args),
}));

vi.mock("../../../frontend/src/features/auth/services/profissionalApi", () => ({
  getMeuPerfil: (...args: unknown[]) => getMeuPerfilMock(...args),
}));

describe("useAuth", () => {
  beforeEach(() => {
    loginMock.mockReset();
    registroMock.mockReset();
    getMeuPerfilMock.mockReset();
    useAuthStore.getState().logout();
    window.localStorage.clear();
  });

  it("test_login_sucesso_popula_store", async () => {
    loginMock.mockResolvedValue({
      access_token: "token-1",
      refresh_token: "refresh-1",
      token_type: "bearer",
    });
    getMeuPerfilMock.mockResolvedValue({
      id: "1",
      nome: "Dra. Alice",
      email: "alice@hospital.com",
      cargo: "MEDICO",
      ativo: true,
    });

    const { result } = renderHook(() => useAuth());

    await act(async () => {
      await result.current.entrar("alice@hospital.com", "segredo123");
    });

    const authState = useAuthStore.getState();
    expect(authState.isAuthenticated).toBe(true);
    expect(authState.profissional?.nome).toBe("Dra. Alice");
    expect(authState.accessToken).toBe("token-1");
  });

  it("test_login_falha_seta_erro_legivel", async () => {
    loginMock.mockRejectedValue({
      response: {
        data: {
          detail: "Credenciais inválidas.",
        },
      },
    });

    const { result } = renderHook(() => useAuth());

    await act(async () => {
      await expect(result.current.entrar("alice@hospital.com", "errada")).rejects.toBeDefined();
    });

    expect(result.current.erro).toBe("Credenciais inválidas.");
  });

  it("test_logout_limpa_store_e_localstorage", async () => {
    useAuthStore.getState().login(
      {
        id: "1",
        nome: "Dra. Alice",
        email: "alice@hospital.com",
        cargo: "MEDICO",
        ativo: true,
      },
      "token-1",
      "refresh-1",
    );

    const { result } = renderHook(() => useAuth());

    act(() => {
      result.current.sair();
    });

    const authState = useAuthStore.getState();
    expect(authState.isAuthenticated).toBe(false);
    expect(window.localStorage.getItem("access_token")).toBeNull();
    expect(window.localStorage.getItem("refresh_token")).toBeNull();
    expect(window.localStorage.getItem("profissional")).toBeNull();
  });

  it("test_validar_email_invalido_retorna_mensagem", () => {
    expect(validarEmail("email-invalido")).toBe("Informe um e-mail válido.");
  });

  it("test_validar_senha_curta_retorna_mensagem", () => {
    expect(validarSenha("123")).toBe("A senha deve ter no mínimo 8 caracteres.");
  });
});
