import type { StrategyResultResponse } from "./types";

export function getStoredStrategyResult(): StrategyResultResponse | null {
  const stored = sessionStorage.getItem("strategy_result");
  if (!stored) {
    return null;
  }

  try {
    return JSON.parse(stored) as StrategyResultResponse;
  } catch {
    return null;
  }
}

export function capitalizeWords(value: string) {
  return value.replace(/\b\w/g, (char) => char.toUpperCase());
}
