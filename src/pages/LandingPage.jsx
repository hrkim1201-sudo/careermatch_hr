import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { usePortfolioStore } from "../store/portfolioStore.js";
import Nav from "../components/common/Nav.jsx";
import DataSource from "../components/common/DataSource.jsx";
import styles from "./LandingPage.module.css";

const EXAMPLES = [
  "서울에서 전기기사 자격증 따고 싶어요",
  "Python 백엔드 개발자로 취업하고 싶어요",
  "온라인으로 데이터 분석을 배우고 싶어요",
  "부산에서 용접 기술 배우고 싶어요",
  "취업 공백이 길어서 면접 준비도 필요해요",
];

const AI_STEPS = [
  {
    step: "01",
    icon: "✦",
    title: "자연어 이해",
    desc: "입력한 문장을 AI가 분석해 지역·직무·자격증·온라인 여부를 자동으로 파악합니다",
    ai: "gpt-4o-mini",
  },
  {
    step: "02",
    icon: "◈",
    title: "의미 기반 매칭",
    desc: "text-embedding-3-large 모델이 입력 내용을 벡터로 변환, 116개 훈련과정과 유사도를 계산합니다",
    ai: "text-embedding-3-large",
  },
  {
    step: "03",
    icon: "◉",
    title: "국가자격 연계",
    desc: "NCS 코드 기반으로 관련 국가기술자격 215종목과 2026년 시험 일정을 자동 연결합니다",
    ai: "Q-Net 연계",
  },
  {
    step: "04",
    icon: "◆",
    title: "채용공고 연결",
    desc: "매칭된 훈련과정·자격증과 관련된 실제 채용공고를 고용24·잡코리아·사람인에서 검색합니다",
    ai: "고용24 연계",
  },
];

export default function LandingPage() {
  const navigate = useNavigate();
  const [prompt, setPrompt] = useState("");
  const [focused, setFocused] = useState(false);
  const setStorePrompt = usePortfolioStore((s) => s.setPrompt);

  const handleStart = () => {
    if (!prompt.trim()) return;
    setStorePrompt(prompt.trim());
    navigate("/match");
  };

  return (
    <div className={styles.page}>
      <Nav />
      <main>
        {/* ── 히어로 섹션 ───────────────────────────────────────── */}
        <section className={styles.hero}>
          <div className={styles.bgOrb1} aria-hidden />
          <div className={styles.bgOrb2} aria-hidden />
          <div className={styles.bgGrid} aria-hidden />

          <div className={styles.inner}>
            {/* 서비스 정체성 배지 */}
            <div className={styles.serviceBadge}>
              <span className={styles.badgeIcon}>🎯</span>
              <span>AI 취업 경로 추천 서비스</span>
              <span className={styles.badgeSep}>·</span>
              <span className={styles.badgeSub}>NCS 기반 · 고용24 · Q-Net 연계</span>
            </div>

            {/* 헤드라인 */}
            <h1 className={styles.h1}>
              원하는 것을 말하면<br />
              <ShaderText text="맞는 경로를 찾아드려요" />
            </h1>

            <p className={styles.sub}>
              직무·지역·자격증·온라인 여부를 자유롭게 입력하세요.<br className={styles.br} />
              AI가 훈련과정·국가자격·채용공고를 함께 추천합니다.
            </p>

            {/* 입력창 */}
            <div className={`${styles.inputWrap} ${focused ? styles.focused : ""}`}>
              <textarea
                className={styles.textarea}
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onFocus={() => setFocused(true)}
                onBlur={() => setFocused(false)}
                onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleStart(); } }}
                placeholder="예: 서울에서 프론트엔드 개발자로 취업하고 싶어요"
                rows={3}
                autoFocus
              />
              <div className={styles.inputBottom}>
                <div className={styles.examplesRow}>
                  {EXAMPLES.map((ex) => (
                    <button key={ex} className={styles.exBtn} onClick={() => setPrompt(ex)}>
                      {ex}
                    </button>
                  ))}
                </div>
                <button className={styles.startBtn} onClick={handleStart} disabled={!prompt.trim()}>
                  <span>추천 받기</span>
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </button>
              </div>
            </div>

            {/* 연계 서비스 뱃지 */}
            <div className={styles.partnerRow}>
              <span className={styles.partnerLabel}>연계 서비스</span>
              {["고용24", "Q-Net", "잡코리아", "사람인", "원티드"].map((p) => (
                <span key={p} className={styles.partnerChip}>{p}</span>
              ))}
            </div>
          </div>
        </section>

        {/* ── AI 작동 방식 ──────────────────────────────────────── */}
        <section className={styles.aiSection}>
          <div className={styles.aiInner}>
            <div className={styles.aiHeader}>
              <span className={styles.aiLabel}>HOW IT WORKS</span>
              <h2 className={styles.aiTitle}>AI가 이렇게 추천합니다</h2>
              <p className={styles.aiDesc}>
                단순 키워드 검색이 아닙니다. 입력 문장의 의미를 이해하고<br className={styles.br} />
                국가 공공 데이터와 연계해 최적의 경로를 찾아드립니다.
              </p>
            </div>

            <div className={styles.stepsGrid}>
              {AI_STEPS.map((s, i) => (
                <div key={s.step} className={styles.stepCard}>
                  <div className={styles.stepTop}>
                    <span className={styles.stepNum}>{s.step}</span>
                    {i < AI_STEPS.length - 1 && <span className={styles.stepArrow}>→</span>}
                  </div>
                  <div className={styles.stepIcon}>{s.icon}</div>
                  <h3 className={styles.stepTitle}>{s.title}</h3>
                  <p className={styles.stepDesc}>{s.desc}</p>
                  <div className={styles.stepAi}>
                    <span className={styles.aiChip}>{s.ai}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── 하단 ──────────────────────────────────────────────── */}
        <div className={styles.footer}>
          <DataSource />
          <button className={styles.privacyBtn} onClick={() => navigate("/privacy")}>
            개인정보처리방침
          </button>
        </div>
      </main>
    </div>
  );
}

function ShaderText({ text }) {
  return (
    <span className={styles.gradient}>{text}</span>
  );
}
