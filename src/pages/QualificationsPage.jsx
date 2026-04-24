import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQualifications } from "../hooks/useQualifications.js";
import QualificationCard from "../components/qualification/QualificationCard.jsx";
import Button from "../components/common/Button.jsx";
import styles from "./QualificationsPage.module.css";

const QUAL_TYPES = ["전체", "기술사", "기능장", "기사", "산업기사", "기능사"];

export default function QualificationsPage() {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [qualType, setQualType] = useState("전체");
  const { qualifications, total, loading, error, load, refresh } = useQualifications();

  const handleSearch = () => {
    load({
      q: search || undefined,
      qual_type: qualType === "전체" ? undefined : qualType,
    });
  };

  const onKeyDown = (e) => {
    if (e.key === "Enter") handleSearch();
  };

  return (
    <div className={styles.page}>
      <nav className={styles.nav}>
        <div className={styles.logo} onClick={() => navigate("/")}>
          Career<span>Match</span>
        </div>
        <div className={styles.navActions}>
          <Button onClick={() => navigate("/programs")}>훈련과정</Button>
          <Button variant="primary" onClick={() => navigate("/portfolio")}>추천 받기</Button>
        </div>
      </nav>

      <main className={styles.container}>
        <header className={styles.header}>
          <div>
            <h1 className={styles.title}>국가기술자격 탐색</h1>
            <p className={styles.subtitle}>
              한국산업인력공단 Q-Net 기반 · 총 <strong>{total}</strong>개 자격종목
            </p>
          </div>
          <Button onClick={refresh} disabled={loading}>
            {loading ? "갱신 중..." : "Q-Net에서 다시 받기"}
          </Button>
        </header>

        <div className={styles.toolbar}>
          <input
            className={styles.search}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="자격명 또는 직무분야 검색"
          />
          <div className={styles.typeFilters}>
            {QUAL_TYPES.map((t) => (
              <button
                key={t}
                className={`${styles.typeBtn} ${qualType === t ? styles.active : ""}`}
                onClick={() => setQualType(t)}
              >
                {t}
              </button>
            ))}
          </div>
          <Button onClick={handleSearch}>검색</Button>
        </div>

        {error && <div className={styles.error}>{error}</div>}
        {loading && <div className={styles.loading}>자격 정보를 불러오는 중...</div>}
        {!loading && !error && qualifications.length === 0 && (
          <div className={styles.empty}>
            조건에 맞는 자격이 없습니다. Q-Net 데이터를 먼저 받아보세요.
          </div>
        )}

        <div className={styles.grid}>
          {qualifications.map((q) => (
            <QualificationCard key={q.qual_code} qualification={q} />
          ))}
        </div>
      </main>
    </div>
  );
}
