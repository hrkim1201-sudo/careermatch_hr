import { useCallback, useEffect, useState } from "react";
import { api } from "../lib/apiClient.js";

export function useQualifications(initialParams = {}) {
  const [data, setData] = useState({ qualifications: [], total: 0 });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const load = useCallback(async (params = {}) => {
    setLoading(true);
    setError(null);
    try {
      const body = await api.listQualifications(params);
      setData(body);
    } catch (e) {
      setError(e.message || "자격 정보를 불러오지 못했습니다. 백엔드 서버가 실행 중인지 확인하세요.");
    } finally {
      setLoading(false);
    }
  }, []);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      await api.refreshQualifications();
      const body = await api.listQualifications({});
      setData(body);
    } catch (e) {
      setError(e.message || "갱신에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  }, []);

  // 최초 마운트 시 자동 로드
  useEffect(() => {
    load(initialParams);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return { ...data, loading, error, load, refresh };
}
