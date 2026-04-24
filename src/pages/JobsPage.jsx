import { useEffect, useState } from "react";
import { api } from "../lib/apiClient.js";
import JobCard from "../components/job/JobCard.jsx";
import Nav from "../components/common/Nav.jsx";
import styles from "./JobsPage.module.css";

export default function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");
  const [location, setLocation] = useState("");

  const load = async (q, loc) => {
    setLoading(true); setError(null);
    try {
      const params = {};
      if (q) params.q = q;
      if (loc) params.location = loc;
      const body = await api.listJobs(params);
      setJobs(body.jobs || []); setTotal(body.total || 0);
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  const refresh = async () => {
    setLoading(true);
    try { await api.refreshJobs(); await load(search, location); }
    catch (e) { setError(e.message); setLoading(false); }
  };

  useEffect(() => { load("", ""); }, []);

  const onSearch = () => load(search, location);

  return (
    <div className={styles.page}>
      <Nav />
      <main className={styles.container}>
        <header className={styles.header}>
          <div>
            <h1 className={styles.title}>채용공고</h1>
            <p className={styles.subtitle}>총 <strong>{total}</strong>개 채용공고</p>
          </div>
          <button className={styles.refreshBtn} onClick={refresh} disabled={loading}>
            {loading ? "갱신 중..." : "실데이터 가져오기"}
          </button>
        </header>

        <div className={styles.toolbar}>
          <input className={styles.input} value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && onSearch()}
            placeholder="직무명, 회사명, 스킬 검색" />
          <div className={styles.row2}>
            <input className={styles.input} value={location}
              onChange={(e) => setLocation(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && onSearch()}
              placeholder="지역 (서울, 경기...)" style={{ flex: 1 }} />
            <button className={styles.searchBtn} onClick={onSearch}>검색</button>
          </div>
        </div>

        {error && <div className={styles.msg + " " + styles.error}>{error}</div>}
        {loading && <div className={styles.msg}>불러오는 중...</div>}
        {!loading && !error && jobs.length === 0 && <div className={styles.msg}>채용공고가 없습니다.</div>}

        <div className={styles.grid}>
          {jobs.map((job) => <JobCard key={job.id} job={job} />)}
        </div>
      </main>
    </div>
  );
}
