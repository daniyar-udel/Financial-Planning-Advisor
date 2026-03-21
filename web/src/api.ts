import type {
  AdvisorResponse,
  AuthResponse,
  LoginPayload,
  SignupPayload,
  User,
  UserProfilePayload,
} from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function generateStrategy(
  payload: UserProfilePayload,
): Promise<AdvisorResponse> {
  const response = await fetch(`${API_BASE_URL}/advisor/plan`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Unable to generate strategy recommendation.");
  }

  return response.json() as Promise<AdvisorResponse>;
}

export async function signup(payload: SignupPayload): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/signup`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    throw new Error(error?.detail ?? "Unable to create account.");
  }

  return response.json() as Promise<AuthResponse>;
}

export async function login(payload: LoginPayload): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    throw new Error(error?.detail ?? "Unable to log in.");
  }

  return response.json() as Promise<AuthResponse>;
}

export async function getCurrentUser(token: string): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error("Unable to load current user.");
  }

  return response.json() as Promise<User>;
}
