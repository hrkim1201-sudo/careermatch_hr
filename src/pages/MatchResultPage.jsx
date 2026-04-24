import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { usePortfolioStore } from "../store/portfolioStore.js";
import { useMatch } from "../hooks/useMatch.js";
import Button from "../components/common/Button.jsx";
import Card from "../components/common/Card.jsx";
import ProgramCard from "../components/program/ProgramCard.jsx";
import MatchScoreBadge from "../components/match/MatchScoreBadge.jsx";
import GuidePanel from "../components/match/GuidePanel.jsx";
import QualificationCard from "../components/qualification/QualificationCard.jsx";
import { methodLabel } from "../lib/format.js";
import styles from "./MatchResultPage.module.css";

export default function MatchResultPage() {
  const navigate = useNavigate();
  const { prompt, skills, preferences } = usePortfolioStore();
  const { results, usedMethod, loading, error, run, fetchGuide } = useMatch();
  const [guideById, setGuideById] = useState({});
  const [guideLoadingId, setGuideLoadingId] = useState(null);
  const [expandedQuals, setExpandedQuals] = useState({});

  const hasInput = (prompt && prompt.trim().length > 0) || skills.length > 0;

  useEffect(() => {
    if (!hasInput) return;
    run({ prompt, skills, preferences }).catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const onShowGuide = async (program) => {
    setGuideLoadingId(program.id);
    try {
      const body = await fetchGuide(program.id, { prompt });
      setGuideById((s) => ({ ...s, [program.id]: body }));
    } catch (e) {
      setGuideById((s) => ({
        ...s,
        [program.id]: {
          guide: `가이드를 불러오지 못했습니다: ${e.message || e}`,
          questions: [],
          used_method: "error",
        },
      }));
    } finally {
      setGuideLoadingId(null);
    }
  };

  const toggleQuals = (id) =>
    setExpandedQuals((s) => ({ ...s, [id]: !s[id] }));

  return (
    <div className={styles.page}>
      <nav className={styles.nav}>
        <div className={styles.logo} onClick={() => navigate("/")}>Career<span>Match</span></div>
        <div className={styles.navActions}>
          <Button onClick={() => navigate("/programs")}>훈련과정</Button>
          <Button onClick={() => navigate("/qualifications")}>국가자격</Button>
          <Button onClick={() => navigate("/portfolio")}>다시 입력</Button>
        </div>
      </nav>

      <main className={styles.container}>
        <header className={styles.header}>
          <h1 className={styles.title}>추천 결과</h1>
          <div className={styles.meta}>
            {results.length}개 프로그램 · 추천 방식: <strong>{methodLabel(usedMethod) || "-"}</strong>
          </div>
        </header>

        {!hasInput && (
          <Card>
            <p>먼저 희망 직무나 목표를 입력해 주세요.</p>
            <Button variant="primary" onClick={() => navigate("/portfolio")}>입력 페이지로 이동</Button>
          </Card>
        )}

        {loading && <div className={styles.loading}>AI가 추천 경로를 분석 중입니다...</div>}
        {error && <div className={styles.error}>{error}</div>}

        <div className={styles.list}>
          {results.map((item) => (
            <div key={item.id} className={styles.item}>
              {/* 점수 + 키워드 */}
              <div className={styles.itemHead}>
                <MatchScoreBadge score={item.score} />
                {item.reason_keywords?.length > 0 && (
                  <span className={styles.reason}>관련 키워드: {item.reason_keywords.join(", ")}</span>
                )}
              </div>

              {/* 훈련과정 카드 */}
              <ProgramCard program={item.program} />

              {/* 연관 국가자격 */}
              {item.related_qualifications?.length > 0 && (
                <div className={styles.quals}>
                  <button
                    className={styles.qualsToggle}
                    onClick={() => toggleQuals(item.id)}
                  >
                    🎓 관련 국가자격 {item.related_qualifications.length}개
                    {expandedQuals[item.id] ? " ▲" : " ▼"}
                  </button>
                  {expandedQuals[item.id] && (
                    <div className={styles.qualsGrid}>
                      {item.related_qualifications.map((rq) => (
                        <QualificationCard
                          key={rq.qualification.qual_code}
                          qualification={rq.qualification}
                          relevance={rq.relevance}
                          nextExam={rq.next_exam}
                          compact
                        />
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* 학습 가이드 */}
              <div className={styles.actions}>
                <Button onClick={() => onShowGuide(item.program)}>
                  학습 가이드 보기
                </Button>
              </div>
              <GuidePanel
                guide={guideById[item.program.id]?.guide}
                questions={guideById[item.program.id]?.questions}
                method={methodLabel(guideById[item.program.id]?.used_method)}
                loading={guideLoadingId === item.program.id}
              />
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
