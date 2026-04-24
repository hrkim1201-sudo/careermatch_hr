import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { usePrograms } from "../hooks/usePrograms.js";
import ProgramCard from "../components/program/ProgramCard.jsx";
import ProgramFilters from "../components/program/ProgramFilters.jsx";
import Button from "../components/common/Button.jsx";
import { sourceLabel } from "../lib/format.js";
import styles from "./ProgramsPage.module.css";

export default function ProgramsPage() {
  const navigate = useNavigate();
  const { programs, counts, source, loading, error, seed } = usePrograms();
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
      <nav className={styles.nav}>
        <div className={styles.logo} onClick={() => navigate("/")}>
          Career<span>Match</span>
        </div>
        <div className={styles.navActions}>
          <Button onClick={() => navigate("/qualifications")}>국가자격</Button>
          <Button variant="primary" onClick={() => navigate("/portfolio")}>
            추천 받기
          </Button>
        </div>
      </nav>

      <main className={styles.container}>
        <header className={styles.header}>
          <div>
            <h1 className={styles.title}>훈련과정 목록</h1>
            <p className={styles.subtitle}>
              현재 데이터: <strong>{sourceLabel(source)}</strong>
            </p>
          </div>
          <Button onClick={seed} disabled={loading}>
            {loading ? "로딩 중..." : "샘플 데이터 시딩"}
          </Button>
        </header>

        <section className={styles.stats}>
          <div className={styles.stat}>
            <strong>{counts.total || 0}</strong>
            <span>전체</span>
          </div>
          <div className={styles.stat}>
            <strong>{counts["국민내일배움카드 훈련과정"] || 0}</strong>
            <span>내일배움카드</span>
          </div>
          <div className={styles.stat}>
            <strong>{counts["일학습병행훈련과정"] || 0}</strong>
            <span>일학습병행</span>
          </div>
          <div className={styles.stat}>
            <strong>{counts["구직자취업역량 강화프로그램"] || 0}</strong>
            <span>취업역량</span>
          </div>
        </section>

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
        {loading && (
          <div className={styles.loading}>프로그램을 불러오는 중...</div>
        )}
        {!loading && !error && filtered.length === 0 && (
          <div className={styles.empty}>
            데이터가 없습니다. 상단의 &apos;샘플 데이터 시딩&apos; 버튼을 눌러주세요.
          </div>
        )}

        <div className={styles.list}>
          {filtered.map((p) => (
            <ProgramCard key={`${p.source}-${p.id}`} program={p} />
          ))}
        </div>
      </main>
    </div>
  );
}
