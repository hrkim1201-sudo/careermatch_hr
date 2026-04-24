import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { usePrograms } from "../hooks/usePrograms.js";
import ProgramCard from "../components/program/ProgramCard.jsx";
import ProgramFilters from "../components/program/ProgramFilters.jsx";
import Nav from "../components/common/Nav.jsx";
import styles from "./ProgramsPage.module.css";

export default function ProgramsPage() {
  const { programs, counts, loading, error, seed } = usePrograms();
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");

  const filtered = useMemo(() => {
    return programs
      .filter((p) => filter === "all" || p.category === filter)
      .filter((p) => {
        if (!search) return true;
        const q = search.toLowerCase();
        return (
          (p.title || "").toLowerCase().includes(q) ||
          (p.summary || "").toLowerCase().includes(q) ||
          (p.skills || "").toLowerCase().includes(q) ||
          (p.tags || []).some((t) => t.toLowerCase().includes(q))
        );
      });
  }, [programs, filter, search]);

  return (
    <div className={styles.page}>
      <Nav />
      <main className={styles.container}>
        <header className={styles.header}>
          <div>
            <h1 className={styles.title}>훈련과정 목록</h1>
            <p className={styles.subtitle}>국민내일배움카드 · 일학습병행 · 취업역량강화 과정</p>
          </div>
          <button className={styles.refreshBtn} onClick={seed} disabled={loading}>
            {loading ? "불러오는 중..." : "데이터 갱신"}
          </button>
        </header>

        <div className={styles.stats}>
          {[
            { label: "전체", value: counts.total || 0 },
            { label: "내일배움카드", value: counts["국민내일배움카드 훈련과정"] || 0 },
            { label: "일학습병행", value: counts["일학습병행훈련과정"] || 0 },
            { label: "취업역량", value: counts["구직자취업역량 강화프로그램"] || 0 },
          ].map((s) => (
            <div key={s.label} className={styles.stat}>
              <strong>{s.value}</strong>
              <span>{s.label}</span>
            </div>
          ))}
        </div>

        <div className={styles.toolbar}>
          <input
            className={styles.search}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="제목 / 요약 / 스킬 / 태그 검색"
          />
          <ProgramFilters value={filter} onChange={setFilter} />
        </div>

        {error && <div className={styles.error}>{error}</div>}
        {loading && <div className={styles.empty}>불러오는 중...</div>}
        {!loading && !error && filtered.length === 0 && (
          <div className={styles.empty}>조건에 맞는 훈련과정이 없습니다.</div>
        )}

        <div className={styles.grid}>
          {filtered.map((p) => (
            <ProgramCard key={`${p.source}-${p.id}`} program={p} />
          ))}
        </div>
      </main>
    </div>
  );
}
