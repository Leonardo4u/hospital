import { create } from "zustand";

type ToastTipo = "sucesso" | "erro" | "aviso";

interface ToastState {
  mensagem: string;
  tipo: ToastTipo;
}

interface UIState {
  isLoading: boolean;
  toast: ToastState | null;
  setLoading: (valor: boolean) => void;
  showToast: (mensagem: string, tipo: ToastTipo) => void;
  clearToast: () => void;
}

export const useUIStore = create<UIState>((set) => ({
  isLoading: false,
  toast: null,
  setLoading: (valor) => set({ isLoading: valor }),
  showToast: (mensagem, tipo) => set({ toast: { mensagem, tipo } }),
  clearToast: () => set({ toast: null }),
}));
