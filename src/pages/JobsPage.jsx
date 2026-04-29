import { useEffect, useState, useCallback } from "react";
import { api } from "../lib/apiClient.js";
import JobCard from "../components/job/JobCard.jsx";
import Nav from "../components/common/Nav.jsx";
import DataSource from "../components/common/DataSource.jsx";
import styles from "./JobsPage.module.css";

const NCS_OPTIONS = [
  { code: "", label: "전체 분야" },
  { code: "20", label: "정보통신" },
  { code: "19", label: "전기·전자" },
  { code: "15", label: "기계" },
  { code: "14", label: "건설" },
  { code: "02", label: "경영·회계" },
  { code: "06", label: "보건·의료" },
  { code: "07", label: "사회복지" },
  { code: "08", label: "디자인·방송" },
  { code: "13", label: "음식서비스" },
  { code: "23", label: "환경·안전" },
  { code: "21", label: "식품가공" },
  { code: "17", label: "화학·바이오" },
  { code: "09", label: "운전·운송" },
  { code: "12", label: "관광·스포츠" },
  { code: "24", label: "농림어업" },
  { code: "16", label: "재료" },
  { code: "03", label: "금융·보험" },
  { code: "10", label: "영업·판매" },
  { code: "18", label: "섬유·의복" },
];

const EMP_OPTIONS = [
  { value: "", label: "고용형태 전체" },
  { value: "정규직", label: "정규직" },
  { value: "계약직", label: "계약직" },
  { value: "인턴", label: "인턴" },
];

const PAGE_SIZE = 20;

export default function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");
  const [location, setLocation] = useState("");
  const [ncsCode, setNcsCode] = useState("");
  const [empType, setEmpType] = useState("");
  const [page, setPage] = useState(0);
  const [inputSearch, setInputSearch] = useState("");
  const [inputLocation, setInputLocation] = useState("");

  const load = useCallback(async (q, loc, ncs, emp, pg) => {
    setLoading(true); setError(null);
    try {
      const params = { limit: PAGE_SIZE, offset: pg * PAGE_SIZE };
      if (q) params.q = q;
      if (loc) params.location = loc;
      if (ncs) params.ncs_code = ncs;
      if (emp) params.emp_type = emp;
      const body = await api.listJobs(params);
      setJobs(body.jobs || []);
      setTotal(body.total || 0);
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { load(search, location, ncsCode, empType, page); },
    [load, search, location, ncsCode, empType, page]);

  const onSearch = () => {
    setSearch(inputSearch); setLocation(inputLocation); setPage(0);
  };
  const onNcsChange = (v) => { setNcsCode(v); setPage(0); };
  const onEmpChange = (v) => { setEmpType(v); setPage(0); };

  const totalPages = Math.ceil(total / PAGE_SIZE);
  const isDark = true; // 테마는 CSS 변수로 처리

  return (
    <div className={styles.page}>
      <Nav />
      <main className={styles.container}>
        <header className={styles.header}>
          <div>
            <h1 className={styles.title}>채용공고</h1>
            <p className={styles.subtitle}>
              총 <strong>{total.toLocaleString()}</strong>개 채용공고 · 고용24 연계
            </p>
          </div>
          <a
            href="https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do"
            target="_blank" rel="noreferrer"
            className={styles.work24Btn}
          >
            고용24에서 더 보기 ↗
          </a>
        </header>

        {/* 검색 필터 */}
        <div className={styles.filterBox}>
          <div className={styles.searchRow}>
            <input className={styles.input} value={inputSearch}
              onChange={(e) => setInputSearch(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && onSearch()}
              placeholder="직무명, 회사명, 스킬 검색" />
            <input className={styles.input} value={inputLocation}
              onChange={(e) => setInputLocation(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && onSearch()}
              placeholder="지역 (서울, 경기...)"
              style={{ maxWidth: 150 }} />
            <button className={styles.searchBtn} onClick={onSearch}>검색</button>
          </div>
          <div className={styles.filterRow}>
            <select className={styles.select} value={ncsCode} onChange={(e) => onNcsChange(e.target.value)}>
              {NCS_OPTIONS.map((o) => <option key={o.code} value={o.code}>{o.label}</option>)}
            </select>
            <select className={styles.select} value={empType} onChange={(e) => onEmpChange(e.target.value)}>
              {EMP_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
            {(search || location || ncsCode || empType) && (
              <button className={styles.resetBtn} onClick={() => {
                setSearch(""); setLocation(""); setNcsCode(""); setEmpType("");
                setInputSearch(""); setInputLocation(""); setPage(0);
              }}>초기화</button>
            )}
          </div>
        </div>

        {error && <div className={styles.msg + " " + styles.error}>{error}</div>}
        {loading && <div className={styles.msg}>불러오는 중...</div>}
        {!loading && !error && jobs.length === 0 && (
          <div className={styles.msg}>
            조건에 맞는 채용공고가 없습니다.
            <br />
            <a href="https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do"
              target="_blank" rel="noreferrer" style={{ color: "var(--color-primary)" }}>
              고용24에서 직접 검색하기 ↗
            </a>
          </div>
        )}

        <div className={styles.grid}>
          {jobs.map((job) => <JobCard key={job.id} job={job} />)}
        </div>

        {/* 페이지네이션 */}
        {totalPages > 1 && (
          <div className={styles.pagination}>
            <button className={styles.pageBtn} onClick={() => setPage(0)} disabled={page === 0}>처음</button>
            <button className={styles.pageBtn} onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0}>이전</button>
            <span className={styles.pageInfo}>{page + 1} / {totalPages}</span>
            <button className={styles.pageBtn} onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))} disabled={page >= totalPages - 1}>다음</button>
            <button className={styles.pageBtn} onClick={() => setPage(totalPages - 1)} disabled={page >= totalPages - 1}>끝</button>
          </div>
        )}

        <DataSource />
      </main>
    </div>
  );
}
