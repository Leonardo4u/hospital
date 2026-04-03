import axios, {
  AxiosError,
  type AxiosHeaders,
  type AxiosInstance,
  type AxiosRequestConfig,
  type InternalAxiosRequestConfig,
} from "axios";

import type { TokenResponse } from "../types";
import { useAuthStore } from "../../store/authSlice";

interface RetryableAxiosRequestConfig extends AxiosRequestConfig {
  _retry?: boolean;
}

const baseURL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

const http: AxiosInstance = axios.create({
  baseURL,
});

const refreshClient: AxiosInstance = axios.create({
  baseURL,
});

http.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = useAuthStore.getState().accessToken;
  if (token === null) {
    return config;
  }

  const headers =
    config.headers instanceof axios.AxiosHeaders
      ? config.headers
      : new axios.AxiosHeaders(config.headers);
  headers.set("Authorization", `Bearer ${token}`);
  config.headers = headers as AxiosHeaders;
  return config;
});

http.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const status = error.response?.status;
    const originalRequest = error.config as RetryableAxiosRequestConfig | undefined;
    const authState = useAuthStore.getState();

    if (status !== 401) {
      return Promise.reject(error);
    }

    if (originalRequest?.url?.includes("/auth/refresh") === true) {
      authState.logout();
      return Promise.reject(error);
    }

    if (authState.refreshToken === null) {
      authState.logout();
      return Promise.reject(error);
    }

    if (originalRequest?._retry === true) {
      authState.logout();
      return Promise.reject(error);
    }

    try {
      const { data } = await refreshClient.post<TokenResponse>("/auth/refresh", {
        refresh_token: authState.refreshToken,
      });
      authState.atualizarTokens(data.access_token, data.refresh_token);

      if (originalRequest === undefined) {
        return Promise.reject(error);
      }

      originalRequest._retry = true;
      const retriedHeaders =
        originalRequest.headers instanceof axios.AxiosHeaders
          ? originalRequest.headers
          : new axios.AxiosHeaders(originalRequest.headers);
      retriedHeaders.set("Authorization", `Bearer ${data.access_token}`);
      originalRequest.headers = retriedHeaders;

      return http(originalRequest);
    } catch {
      authState.logout();
      return Promise.reject(error);
    }
  },
);

export { http };
export default http;
