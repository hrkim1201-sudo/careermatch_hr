import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { usePortfolioStore } from "../store/portfolioStore.js";
import Nav from "../components/common/Nav.jsx";
import styles from "./LandingPage.module.css";

const EXAMPLES = [
  "서울에서 전기기사 자격증 따고 싶어요",
  "Python 백엔드 개발자로 취업하고 싶어요",
  "온라인으로 데이터 분석 배우고 싶어요",
  "부산에서 용접 기술 배우고 싶어요",
  "취업 공백이 길어서 면접 준비도 필요해요",
];

export default function LandingPage() {
  const navigate = useNavigate();
  const [prompt, setPrompt] = useState("");
  const setStorePrompt = usePortfolioStore((s) => s.setPrompt);

  const handleStart = () => {
    if (!prompt.trim()) return;
    setStorePrompt(prompt.trim());
    navigate("/match");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleStart();
    }
  };

  return (
    <div className={styles.page}>
      <Nav />
      <main className={styles.main}>
        <section className={styles.hero}>
          <p className={styles.eyebrow}>NCS 기반 취업 경로 추천</p>
          <h1 className={styles.title}>
            원하는 것을 말하면<br />
            <em>맞는 경로를 찾아드려요</em>
          </h1>
          <p className={styles.subtitle}>
            지역·직무·자격증·온라인 여부를 자유롭게 입력하세요.
            <br className={styles.brDesktop} />
            AI가 훈련과정과 국가자격을 함께 추천해 드립니다.
          </p>
        </section>

        <div className={styles.inputCard}>
          <textarea
            className={styles.textarea}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="예: 서울에서 전기기사 자격증 따고 싶고 온라인도 괜찮아요"
            rows={4}
            autoFocus
          />
          <div className={styles.examples}>
            {EXAMPLES.map((ex) => (
              <button key={ex} className={styles.exBtn} onClick={() => setPrompt(ex)}>
                {ex}
              </button>
            ))}
          </div>
          <div className={styles.actions}>
            <span className={styles.hint}>Enter로 검색</span>
            <button
              className={styles.startBtn}
              onClick={handleStart}
              disabled={!prompt.trim()}
            >
              추천 경로 찾기 →
            </button>
          </div>
        </div>

        <div className={styles.features}>
          {[
            { icon: "🎯", title: "자연어 이해", desc: "지역·직무·자격증을 자유롭게 말하면 AI가 파악합니다" },
            { icon: "📚", title: "훈련과정 추천", desc: "국민내일배움카드 및 일학습병행 과정" },
            { icon: "🏆", title: "국가자격 연계", desc: "Q-Net 국가기술자격 + 시험 일정 안내" },
            { icon: "💼", title: "채용공고", desc: "관련 실제 채용공고까지 한눈에" },
          ].map((f) => (
            <div key={f.title} className={styles.feature}>
              <span className={styles.fIcon}>{f.icon}</span>
              <strong className={styles.fTitle}>{f.title}</strong>
              <span className={styles.fDesc}>{f.desc}</span>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
