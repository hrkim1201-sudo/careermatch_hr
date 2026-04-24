import { useCallback, useState } from "react";
import { api, ApiError } from "../lib/apiClient.js";

export function useMatch() {
  const [results, setResults] = useState([]);
  const [usedMethod, setUsedMethod] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const run = useCallback(async (payload) => {
    setLoading(true);
    setError(null);
    try {
      const body = await api.match(payload);
      setResults(body.results || []);
      setUsedMethod(body.used_method);
      return body;
    } catch (e) {
      const msg =
        e instanceof ApiError ? `요청 실패 (${e.status})` : e.message || "추천 실패";
      setError(msg);
      throw e;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchGuide = useCallback(async (programId, payload) => {
    return api.generateGuide(programId, payload);
  }, []);

  return { results, usedMethod, loading, error, run, fetchGuide };
}
