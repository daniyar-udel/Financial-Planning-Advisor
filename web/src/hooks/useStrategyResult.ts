import { useEffect, useState } from "react";

import { getStrategyResult } from "../api";
import { useAuth } from "../auth";
import type { StrategyResultResponse } from "../types";
import { getStoredStrategyResult } from "../utils";

export function useStrategyResult() {
  const { token } = useAuth();
  const [result, setResult] = useState<StrategyResultResponse | null>(getStoredStrategyResult);
  const [loading, setLoading] = useState(result === null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function hydrate() {
      if (result || !token) {
        setLoading(false);
        return;
      }

      try {
        const nextResult = await getStrategyResult(token);
        sessionStorage.setItem("strategy_result", JSON.stringify(nextResult));
        setResult(nextResult);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to load strategy result.");
      } finally {
        setLoading(false);
      }
    }

    void hydrate();
  }, [result, token]);

  return { result, loading, error };
}
