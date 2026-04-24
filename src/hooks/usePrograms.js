import { useCallback, useEffect, useState } from "react";
import { api } from "../lib/apiClient.js";

export function usePrograms() {
  const [data, setData] = useState({ programs: [], counts: {}, source: "empty" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const body = await api.listPrograms();
      setData(body);
    } catch (e) {
      setError(e.message || "프로그램을 불러오지 못했습니다.");
    } finally {
      setLoading(false);
    }
  }, []);

  const seed = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      await api.seedPrograms();
      const body = await api.listPrograms();
      setData(body);
    } catch (e) {
      setError(e.message || "시딩에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return { ...data, loading, error, seed, reload: load };
}
