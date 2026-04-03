import { useEffect, type PropsWithChildren } from "react";

import { useAuthStore } from "../../store/authSlice";

export default function AuthProvider({ children }: PropsWithChildren) {
  useEffect(() => {
    useAuthStore.getState().hidratarDoStorage();
  }, []);

  return <>{children}</>;
}
