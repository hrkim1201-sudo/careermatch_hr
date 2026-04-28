import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { usePortfolioStore } from "../store/portfolioStore.js";
import Nav from "../components/common/Nav.jsx";
import DataSource from "../components/common/DataSource.jsx";
import { useNavigate } from "react-router-dom";
import styles from "./LandingPage.module.css";

const EXAMPLES = [
  "서울에서 전기기사 자격증 따고 싶어요",
  "Python 백엔드 개발자로 취업하고 싶어요",
  "온라인으로 데이터 분석을 배우고 싶어요",
  "부산에서 용접 기술 배우고 싶어요",
  "취업 공백이 길어서 면접 준비도 필요해요",
];

const FEATURES = [
  { icon: "✦", label: "자연어 이해", desc: "지역·직무·자격을 자유롭게 입력" },
  { icon: "◈", label: "훈련과정 매칭", desc: "고용24 내일배움카드 과정 116개" },
  { icon: "◉", label: "국가자격 연계", desc: "Q-Net 215개 자격 + 시험일정" },
  { icon: "◆", label: "채용공고 연결", desc: "관련 실제 채용공고 추천" },
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
      <main className={styles.hero}>
        {/* 배경 장식 */}
        <div className={styles.bgOrb1} aria-hidden="true" />
        <div className={styles.bgOrb2} aria-hidden="true" />
        <div className={styles.bgGrid} aria-hidden="true" />

        <div className={styles.inner}>
          {/* 뱃지 */}
          <div className={styles.badge}>
            <span className={styles.badgeDot} />
            NCS 기반 취업 경로 추천
          </div>

          {/* 헤드라인 */}
          <h1 className={styles.h1}>
            원하는 것을 말하면<br />
            <span className={styles.highlight}>맞는 경로</span>를 찾아드려요
          </h1>

          <p className={styles.sub}>
            직무·지역·자격증·온라인 여부를 자유롭게 입력하세요.<br className={styles.br} />
            AI가 훈련과정·국가자격·채용공고를 함께 추천합니다.
          </p>

          {/* 입력 영역 */}
          <div className={`${styles.inputWrap} ${focused ? styles.focused : ""}`}>
            <textarea
              className={styles.textarea}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onFocus={() => setFocused(true)}
              onBlur={() => setFocused(false)}
              onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleStart(); } }}
              placeholder="예: IT 개발자로 취업하고 싶어요. Python이나 백엔드 쪽이요"
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

          {/* 피처 뱃지 */}
          <div className={styles.features}>
            {FEATURES.map((f) => (
              <div key={f.label} className={styles.feature}>
                <span className={styles.featureIcon}>{f.icon}</span>
                <div>
                  <div className={styles.featureLabel}>{f.label}</div>
                  <div className={styles.featureDesc}>{f.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

          {/* 데이터 출처 표기 (공공누리 의무) */}
          <DataSource />
          <div className={styles.privacyLink}>
            <button className={styles.privacyBtn} onClick={() => navigate('/privacy')}>
              개인정보처리방침
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
