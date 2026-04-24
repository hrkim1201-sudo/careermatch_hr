import { useState } from "react";
import { useQualifications } from "../hooks/useQualifications.js";
import QualificationCard from "../components/qualification/QualificationCard.jsx";
import Nav from "../components/common/Nav.jsx";
import styles from "./QualificationsPage.module.css";

const TYPES = ["전체", "기술사", "기능장", "기사", "산업기사", "기능사"];

export default function QualificationsPage() {
  const [search, setSearch] = useState("");
  const [qualType, setQualType] = useState("전체");
  const { qualifications, total, loading, error, load, refresh } = useQualifications();

  const handleSearch = () =>
    load({ q: search || undefined, qual_type: qualType === "전체" ? undefined : qualType });

  return (
    <div className={styles.page}>
      <Nav />
      <main className={styles.container}>
        <header className={styles.header}>
          <div>
            <h1 className={styles.title}>국가기술자격 탐색</h1>
            <p className={styles.subtitle}>한국산업인력공단 Q-Net 기반 · 총 <strong>{total}</strong>개 자격종목</p>
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
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              placeholder="자격명 또는 직무분야 검색"
            />
            <button className={styles.searchBtn} onClick={handleSearch}>검색</button>
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
        {!loading && !error && qualifications.length === 0 && (
          <div className={styles.msg}>데이터가 없습니다. Q-Net 갱신을 눌러주세요.</div>
        )}

        <div className={styles.grid}>
          {qualifications.map((q) => <QualificationCard key={q.qual_code} qualification={q} />)}
        </div>
      </main>
    </div>
  );
}
