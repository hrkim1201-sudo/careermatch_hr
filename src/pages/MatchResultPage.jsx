import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { usePortfolioStore } from "../store/portfolioStore.js";
import { api } from "../lib/apiClient.js";
import Nav from "../components/common/Nav.jsx";
import Card from "../components/common/Card.jsx";
import ProgramCard from "../components/program/ProgramCard.jsx";
import MatchScoreBadge from "../components/match/MatchScoreBadge.jsx";
import GuidePanel from "../components/match/GuidePanel.jsx";
import QualificationCard from "../components/qualification/QualificationCard.jsx";
import JobCard from "../components/job/JobCard.jsx";
import { methodLabel } from "../lib/format.js";
import styles from "./MatchResultPage.module.css";

export default function MatchResultPage() {
  const navigate = useNavigate();
  const { prompt, reset } = usePortfolioStore();
  const [results, setResults] = useState([]);
  const [usedMethod, setUsedMethod] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [guideById, setGuideById] = useState({});
  const [guideLoadingId, setGuideLoadingId] = useState(null);
  const [expandedQuals, setExpandedQuals] = useState({});
  const [expandedJobs, setExpandedJobs] = useState({});
  const ranRef = useRef(false);

  useEffect(() => {
    if (!prompt || ranRef.current) return;
    ranRef.current = true;
    setLoading(true);
    api.directMatch(prompt)
      .then((body) => { setResults(body.results || []); setUsedMethod(body.used_method); })
      .catch((e) => setError(e.message || "추천에 실패했습니다."))
      .finally(() => setLoading(false));
  }, [prompt]);

  const onShowGuide = async (program) => {
    setGuideLoadingId(program.id);
    try {
      const body = await api.generateGuide(program.id, { prompt });
      setGuideById((s) => ({ ...s, [program.id]: body }));
    } catch (e) {
      setGuideById((s) => ({ ...s, [program.id]: { guide: `가이드 오류: ${e.message}`, questions: [], used_method: "error" } }));
    } finally { setGuideLoadingId(null); }
  };

  const toggle = (setter, id) => setter((s) => ({ ...s, [id]: !s[id] }));

  return (
    <div className={styles.page}>
      <Nav />
      <main className={styles.container}>
        {prompt && (
          <div className={styles.queryBox}>
            <span className={styles.queryLabel}>검색</span>
            <span className={styles.queryText}>{prompt}</span>
          </div>
        )}

        <header className={styles.header}>
          <h1 className={styles.title}>추천 결과</h1>
          {!loading && results.length > 0 && (
            <span className={styles.meta}>{results.length}개 · {methodLabel(usedMethod)}</span>
          )}
          <button className={styles.retryBtn} onClick={() => { reset(); navigate("/"); }}>
            다시 검색
          </button>
        </header>

        {loading && (
          <div className={styles.loading}>
            <div className={styles.spinner} />
            <p>AI가 경로를 분석 중입니다...</p>
          </div>
        )}
        {error && <div className={styles.error}><p>{error}</p></div>}
        {!prompt && !loading && (
          <Card><p>검색어가 없습니다.</p>
            <button className={styles.retryBtn} onClick={() => navigate("/")}>처음으로</button>
          </Card>
        )}

        <div className={styles.list}>
          {results.map((item) => (
            <div key={item.id} className={styles.item}>
              <div className={styles.itemHead}>
                <MatchScoreBadge score={item.score} />
                {item.reason_keywords?.length > 0 && (
                  <span className={styles.reason}>{item.reason_keywords.join(", ")}</span>
                )}
              </div>

              <ProgramCard program={item.program} compact />

              {item.related_qualifications?.length > 0 && (
                <div className={styles.section}>
                  <button className={styles.toggler} onClick={() => toggle(setExpandedQuals, item.id)}>
                    🏆 관련 국가자격 {item.related_qualifications.length}개 {expandedQuals[item.id] ? "▲" : "▼"}
                  </button>
                  {expandedQuals[item.id] && (
                    <div className={styles.subGrid}>
                      {item.related_qualifications.map((rq) => (
                        <QualificationCard key={rq.qualification.qual_code} qualification={rq.qualification}
                          relevance={rq.relevance} nextExam={rq.next_exam} compact />
                      ))}
                    </div>
                  )}
                </div>
              )}

              {item.related_jobs?.length > 0 && (
                <div className={styles.section}>
                  <button className={`${styles.toggler} ${styles.jobToggler}`} onClick={() => toggle(setExpandedJobs, item.id)}>
                    💼 관련 채용공고 {item.related_jobs.length}개 {expandedJobs[item.id] ? "▲" : "▼"}
                  </button>
                  {expandedJobs[item.id] && (
                    <div className={styles.subGrid}>
                      {item.related_jobs.map((job) => (
                        <JobCard key={job.id} job={job} compact />
                      ))}
                    </div>
                  )}
                </div>
              )}

              <div className={styles.guideRow}>
                <button className={styles.guideBtn} onClick={() => onShowGuide(item.program)}>
                  학습 가이드 보기
                </button>
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
