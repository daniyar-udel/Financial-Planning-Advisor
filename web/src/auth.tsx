import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { getCurrentUser, login, signup } from "./api";
import type { LoginPayload, SignupPayload, User } from "./types";

type AuthContextValue = {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  loginUser: (payload: LoginPayload) => Promise<void>;
  signupUser: (payload: SignupPayload) => Promise<void>;
  logoutUser: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);
const STORAGE_KEY = "aisa_auth_token";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(localStorage.getItem(STORAGE_KEY));
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function hydrateAuth() {
      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        const currentUser = await getCurrentUser(token);
        setUser(currentUser);
      } catch {
        localStorage.removeItem(STORAGE_KEY);
        setToken(null);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    }

    void hydrateAuth();
  }, [token]);

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      user,
      isAuthenticated: Boolean(token && user),
      isLoading,
      async loginUser(payload) {
        const result = await login(payload);
        localStorage.setItem(STORAGE_KEY, result.access_token);
        setToken(result.access_token);
        setUser(result.user);
      },
      async signupUser(payload) {
        const result = await signup(payload);
        localStorage.setItem(STORAGE_KEY, result.access_token);
        setToken(result.access_token);
        setUser(result.user);
      },
      logoutUser() {
        localStorage.removeItem(STORAGE_KEY);
        setToken(null);
        setUser(null);
      },
    }),
    [isLoading, token, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider.");
  }
  return context;
}
