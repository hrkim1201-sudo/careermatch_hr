import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useEffect } from "react";
import { api } from "../lib/apiClient.js";
import JobCard from "../components/job/JobCard.jsx";
import Button from "../components/common/Button.jsx";
import styles from "./JobsPage.module.css";

export default function JobsPage() {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");
  const [location, setLocation] = useState("");

  const load = async (q, loc) => {
    setLoading(true);
    setError(null);
    try {
      const params = {};
      if (q) params.q = q;
      if (loc) params.location = loc;
      const body = await api.listJobs(params);
      setJobs(body.jobs || []);
      setTotal(body.total || 0);
    } catch (e) {
      setError(e.message || "채용공고를 불러오지 못했습니다.");
    } finally {
      setLoading(false);
    }
  };

  const refresh = async () => {
    setLoading(true);
    try {
      await api.refreshJobs();
      await load(search, location);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load("", ""); }, []);

  const onSearch = () => load(search, location);

  return (
    <div className={styles.page}>
      <nav className={styles.nav}>
        <div className={styles.logo} onClick={() => navigate("/")}>Career<span>Match</span></div>
        <div className={styles.navActions}>
          <Button onClick={() => navigate("/programs")}>훈련과정</Button>
          <Button onClick={() => navigate("/qualifications")}>국가자격</Button>
          <Button variant="primary" onClick={() => navigate("/")}>추천 받기</Button>
        </div>
      </nav>

      <main className={styles.container}>
        <header className={styles.header}>
          <div>
            <h1 className={styles.title}>채용공고</h1>
            <p className={styles.subtitle}>Work24 고용24 기반 · 총 <strong>{total}</strong>개</p>
          </div>
          <Button onClick={refresh} disabled={loading}>
            {loading ? "갱신 중..." : "실데이터 가져오기"}
          </Button>
        </header>

        <div className={styles.toolbar}>
          <input className={styles.input} value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && onSearch()}
            placeholder="직무명, 회사명, 스킬 검색" />
          <input className={styles.input} value={location}
            onChange={(e) => setLocation(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && onSearch()}
            placeholder="지역 (서울, 경기...)" style={{maxWidth: 160}} />
          <Button onClick={onSearch}>검색</Button>
        </div>

        {error && <div className={styles.error}>{error}</div>}
        {loading && <div className={styles.loading}>불러오는 중...</div>}
        {!loading && !error && jobs.length === 0 && (
          <div className={styles.empty}>채용공고가 없습니다.</div>
        )}

        <div className={styles.grid}>
          {jobs.map((job) => <JobCard key={job.id} job={job} />)}
        </div>
      </main>
    </div>
  );
}
