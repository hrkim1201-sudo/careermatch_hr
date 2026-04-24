import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { usePortfolioStore } from "../store/portfolioStore.js";
import { api } from "../lib/apiClient.js";
import Button from "../components/common/Button.jsx";
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
      .then((body) => {
        setResults(body.results || []);
        setUsedMethod(body.used_method);
      })
      .catch((e) => setError(e.message || "추천에 실패했습니다."))
      .finally(() => setLoading(false));
  }, [prompt]);

  const onShowGuide = async (program) => {
    setGuideLoadingId(program.id);
    try {
      const body = await api.generateGuide(program.id, { prompt });
      setGuideById((s) => ({ ...s, [program.id]: body }));
    } catch (e) {
      setGuideById((s) => ({
        ...s,
        [program.id]: { guide: `가이드를 불러오지 못했습니다: ${e.message}`, questions: [], used_method: "error" },
      }));
    } finally {
      setGuideLoadingId(null);
    }
  };

  const toggleQuals = (id) => setExpandedQuals((s) => ({ ...s, [id]: !s[id] }));
  const toggleJobs = (id) => setExpandedJobs((s) => ({ ...s, [id]: !s[id] }));

  const handleRetry = () => { reset(); navigate("/"); };

  return (
    <div className={styles.page}>
      <nav className={styles.nav}>
        <div className={styles.logo} onClick={() => navigate("/")}>Career<span>Match</span></div>
        <div className={styles.navActions}>
          <Button onClick={() => navigate("/programs")}>훈련과정</Button>
          <Button onClick={() => navigate("/qualifications")}>국가자격</Button>
          <Button onClick={() => navigate("/jobs")}>채용공고</Button>
          <Button variant="primary" onClick={handleRetry}>다시 검색</Button>
        </div>
      </nav>

      <main className={styles.container}>
        {prompt && (
          <div className={styles.queryBox}>
            <span className={styles.queryLabel}>검색 내용</span>
            <span className={styles.queryText}>{prompt}</span>
          </div>
        )}

        <header className={styles.header}>
          <h1 className={styles.title}>추천 결과</h1>
          {!loading && results.length > 0 && (
            <div className={styles.meta}>
              {results.length}개 프로그램 · 추천 방식: <strong>{methodLabel(usedMethod)}</strong>
            </div>
          )}
        </header>

        {loading && (
          <div className={styles.loading}>
            <div className={styles.spinner} />
            <p>AI가 경로를 분석하고 있습니다...</p>
          </div>
        )}

        {error && (
          <div className={styles.error}>
            <p>{error}</p>
            <Button onClick={handleRetry}>다시 시도</Button>
          </div>
        )}

        {!prompt && !loading && (
          <Card>
            <p>검색어가 없습니다.</p>
            <Button variant="primary" onClick={() => navigate("/")}>처음으로</Button>
          </Card>
        )}

        <div className={styles.list}>
          {results.map((item) => (
            <div key={item.id} className={styles.item}>
              <div className={styles.itemHead}>
                <MatchScoreBadge score={item.score} />
                {item.reason_keywords?.length > 0 && (
                  <span className={styles.reason}>관련: {item.reason_keywords.join(", ")}</span>
                )}
              </div>

              <ProgramCard program={item.program} />

              {/* 연관 국가자격 */}
              {item.related_qualifications?.length > 0 && (
                <div className={styles.section}>
                  <button className={styles.sectionToggle} onClick={() => toggleQuals(item.id)}>
                    🏆 관련 국가자격 {item.related_qualifications.length}개
                    {expandedQuals[item.id] ? " ▲" : " ▼"}
                  </button>
                  {expandedQuals[item.id] && (
                    <div className={styles.grid}>
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

              {/* 관련 채용공고 */}
              {item.related_jobs?.length > 0 && (
                <div className={styles.section}>
                  <button className={styles.sectionToggle + " " + styles.jobToggle} onClick={() => toggleJobs(item.id)}>
                    💼 관련 채용공고 {item.related_jobs.length}개
                    {expandedJobs[item.id] ? " ▲" : " ▼"}
                  </button>
                  {expandedJobs[item.id] && (
                    <div className={styles.grid}>
                      {item.related_jobs.map((job) => (
                        <JobCard key={job.id} job={job} compact />
                      ))}
                    </div>
                  )}
                </div>
              )}

              <div className={styles.actions}>
                <Button onClick={() => onShowGuide(item.program)}>학습 가이드 보기</Button>
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
