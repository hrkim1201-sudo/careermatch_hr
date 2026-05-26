import { useState, useMemo } from "react";
import { useQualifications } from "../hooks/useQualifications.js";
import QualificationCard from "../components/qualification/QualificationCard.jsx";
import Nav from "../components/common/Nav.jsx";
import styles from "./QualificationsPage.module.css";

const TYPES = ["전체", "기술사", "기능장", "기사", "산업기사", "기능사"];

export default function QualificationsPage() {
  const [search, setSearch] = useState("");
  const [qualType, setQualType] = useState("전체");

  // 전체 데이터를 한 번에 불러오고, 필터는 프론트에서 처리
  const { qualifications, schedules, total, loading, error, refresh } = useQualifications();

  const filtered = useMemo(() => {
    return qualifications.filter((q) => {
      const matchType = qualType === "전체" || q.qual_type === qualType;
      const matchSearch = !search ||
        (q.qual_name || "").includes(search) ||
        (q.job_field_name || "").includes(search) ||
        (q.mid_job_field || "").includes(search);
      return matchType && matchSearch;
    });
  }, [qualifications, qualType, search]);

  return (
    <div className={styles.page}>
      <Nav />
      <main className={styles.container}>
        <header className={styles.header}>
          <div>
            <h1 className={styles.title}>국가기술자격 탐색</h1>
            <p className={styles.subtitle}>
              한국산업인력공단 Q-Net 기반 · 총 <strong>{filtered.length}</strong>개
              {qualType !== "전체" && <span className={styles.filterBadge}>{qualType}</span>}
            </p>
          </div>
          <button className={styles.refreshBtn} onClick={refresh} disabled={loading}>
            {loading ? "갱신 중..." : "Q-Net 갱신"}
          </button>
        </header>

        <div className={styles.toolbar}>
          <div className={styles.searchRow}>
            <input
              className={styles.search}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="자격명 또는 직무분야 검색"
            />
          </div>
          <div className={styles.typeRow}>
            {TYPES.map((t) => (
              <button
                key={t}
                className={`${styles.typeBtn} ${qualType === t ? styles.active : ""}`}
                onClick={() => setQualType(t)}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        {error && <div className={styles.msg + " " + styles.error}>{error}</div>}
        {loading && <div className={styles.msg}>자격 정보를 불러오는 중...</div>}
        {!loading && !error && filtered.length === 0 && (
          <div className={styles.msg}>
            {qualType !== "전체" ? `"${qualType}" 자격종목이 없습니다.` : "데이터가 없습니다."}
          </div>
        )}

        <div className={styles.grid}>
          {filtered.map((q) => (
            <QualificationCard
              key={q.qual_code}
              qualification={q}
              nextExam={schedules?.[q.qual_code] || null}
            />
          ))}
        </div>
      </main>
    </div>
  );
}
