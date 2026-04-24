import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { usePortfolioStore } from "../store/portfolioStore.js";
import Button from "../components/common/Button.jsx";
import styles from "./LandingPage.module.css";

const QUICK_PROMPTS = [
  "온라인 위주로 들을 수 있는 프로그램",
  "사무행정과 문서작성 역량을 키우고 싶어요",
  "IT 개발자로 취업하고 싶어요",
  "취업 공백이 길어서 면접 준비도 필요해요",
];

export default function LandingPage() {
  const navigate = useNavigate();
  const [text, setText] = useState("");
  const setPrompt = usePortfolioStore((s) => s.setPrompt);

  const start = () => {
    if (text.trim()) setPrompt(text.trim());
    navigate("/portfolio");
  };

  return (
    <div className={styles.page}>
      <nav className={styles.nav}>
        <div className={styles.logo} onClick={() => navigate("/")}>
          Career<span>Match</span>
        </div>
        <div className={styles.navActions}>
          <Button onClick={() => navigate("/programs")}>훈련과정</Button>
          <Button onClick={() => navigate("/qualifications")}>국가자격</Button>
          <Button variant="primary" onClick={start}>추천 받기</Button>
        </div>
      </nav>

      <main className={styles.container}>
        <section className={styles.hero}>
          <div className={styles.eyebrow}>CareerMatch · NCS 기반 취업 경로 추천</div>
          <h1 className={styles.title}>
            훈련과정부터 자격증까지<br />
            <em>취업 경로를 한눈에</em>
          </h1>
          <p className={styles.copy}>
            고용24 국민내일배움카드 훈련과정과 한국산업인력공단 국가기술자격을
            NCS 코드로 연결해 당신에게 맞는 취업 경로를 추천합니다.
          </p>
        </section>

        <section className={styles.promptCard}>
          <div className={styles.promptHead}>원하는 직무나 목표를 입력하세요</div>
          <textarea
            className={styles.promptBox}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="예: 전기기사 자격증을 따고 싶고, 관련 훈련도 같이 알고 싶어요."
            rows={4}
          />
          <div className={styles.quickRow}>
            {QUICK_PROMPTS.map((p) => (
              <button key={p} className={styles.quickBtn}
                onClick={() => setText((cur) => cur ? `${cur}\n${p}` : p)}>
                {p}
              </button>
            ))}
          </div>
          <div className={styles.cta}>
            <Button variant="primary" onClick={start}>추천 경로 찾기 →</Button>
          </div>
        </section>

        <section className={styles.points}>
          <div className={styles.point}>
            <strong>훈련과정</strong>
            <span>고용24 국민내일배움카드 기반 실데이터</span>
          </div>
          <div className={styles.point}>
            <strong>국가자격</strong>
            <span>Q-Net 국가기술자격 종목 + 시험일정</span>
          </div>
          <div className={styles.point}>
            <strong>NCS 연계</strong>
            <span>훈련 → 자격 경로를 코드로 연결</span>
          </div>
          <div className={styles.point}>
            <strong>AI 추천</strong>
            <span>입력한 목표에 맞게 자동 정렬</span>
          </div>
        </section>
      </main>
    </div>
  );
}
