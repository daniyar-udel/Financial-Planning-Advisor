import type { AdvisorResponse, UserProfilePayload } from "./types";

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
