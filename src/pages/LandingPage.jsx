import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { usePortfolioStore } from "../store/portfolioStore.js";
import Button from "../components/common/Button.jsx";
import styles from "./LandingPage.module.css";

const EXAMPLES = [
  "서울에서 전기기사 자격증 따고 싶고 온라인도 괜찮아요",
  "IT 개발자로 취업하고 싶어요. Python이나 백엔드 쪽이요",
  "부산에서 용접 기술 배우고 싶어요",
  "온라인으로 데이터 분석 배우고 싶어요",
  "취업 공백이 길어서 면접 준비도 필요해요",
];

export default function LandingPage() {
  const navigate = useNavigate();
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const setStorePrompt = usePortfolioStore((s) => s.setPrompt);

  const handleStart = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
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
      <nav className={styles.nav}>
        <div className={styles.logo}>Career<span>Match</span></div>
        <div className={styles.navLinks}>
          <button className={styles.navBtn} onClick={() => navigate("/programs")}>훈련과정</button>
          <button className={styles.navBtn} onClick={() => navigate("/qualifications")}>국가자격</button>
        </div>
      </nav>

      <main className={styles.main}>
        <div className={styles.hero}>
          <p className={styles.eyebrow}>NCS 기반 취업 경로 추천</p>
          <h1 className={styles.title}>
            원하는 것을 말하면<br />
            <em>맞는 경로를 찾아드려요</em>
          </h1>
          <p className={styles.subtitle}>
            지역, 직무, 자격증, 온라인 여부를 자유롭게 입력하세요.<br />
            AI가 훈련과정과 국가자격을 함께 추천해 드립니다.
          </p>
        </div>

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
              <button
                key={ex}
                className={styles.exampleBtn}
                onClick={() => setPrompt(ex)}
              >
                {ex}
              </button>
            ))}
          </div>
          <div className={styles.actions}>
            <span className={styles.hint}>Shift+Enter로 줄바꿈, Enter로 검색</span>
            <Button
              variant="primary"
              onClick={handleStart}
              disabled={!prompt.trim() || loading}
            >
              {loading ? "분석 중..." : "추천 경로 찾기 →"}
            </Button>
          </div>
        </div>

        <div className={styles.features}>
          <div className={styles.feature}>
            <div className={styles.featureIcon}>🎯</div>
            <strong>자연어 이해</strong>
            <span>지역·직무·자격증을 자유롭게 말하면 AI가 파악합니다</span>
          </div>
          <div className={styles.feature}>
            <div className={styles.featureIcon}>📚</div>
            <strong>훈련과정 추천</strong>
            <span>국민내일배움카드 및 일학습병행 과정</span>
          </div>
          <div className={styles.feature}>
            <div className={styles.featureIcon}>🏆</div>
            <strong>국가자격 연계</strong>
            <span>Q-Net 국가기술자격 + 시험 일정 안내</span>
          </div>
          <div className={styles.feature}>
            <div className={styles.featureIcon}>🗺️</div>
            <strong>지역 맞춤</strong>
            <span>원하는 지역과 온라인 여부를 자동 반영</span>
          </div>
        </div>
      </main>
    </div>
  );
}
