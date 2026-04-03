import "@testing-library/jest-dom/vitest";

import { afterAll, afterEach, beforeAll } from "vitest";

import { useAuthStore } from "../../frontend/src/store/authSlice";
import { server } from "./mocks/handlers";

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));

afterEach(() => {
  server.resetHandlers();
  window.localStorage.clear();
  useAuthStore.setState({
    profissional: null,
    accessToken: null,
    refreshToken: null,
    isAuthenticated: false,
  });
});

afterAll(() => server.close());
