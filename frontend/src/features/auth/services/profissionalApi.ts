import http from "../../../shared/utils/httpClient";
import type { Profissional } from "../../../shared/types";

export async function getMeuPerfil(accessToken?: string): Promise<Profissional> {
  const { data } = await http.get<Profissional>("/auth/me", {
    headers:
      accessToken === undefined
        ? undefined
        : {
            Authorization: `Bearer ${accessToken}`,
          },
  });
  return data;
}
