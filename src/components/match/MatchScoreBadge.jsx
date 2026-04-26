import { useState } from "react";
import styles from "./MatchScoreBadge.module.css";

function getScoreInfo(score) {
  if (score >= 80) return { label: "매우 높음", color: "#00e5b0", bg: "rgba(0,229,176,0.12)", border: "rgba(0,229,176,0.3)" };
  if (score >= 60) return { label: "높음",     color: "#4f7cff", bg: "rgba(79,124,255,0.12)", border: "rgba(79,124,255,0.3)" };
  if (score >= 40) return { label: "보통",     color: "#fbbf24", bg: "rgba(251,191,36,0.12)", border: "rgba(251,191,36,0.3)" };
  return               { label: "참고",      color: "#8b97b8", bg: "rgba(139,151,184,0.10)", border: "rgba(139,151,184,0.25)" };
}

const CRITERIA = [
  { range: "80 ~ 100", label: "매우 높음", desc: "직무·지역·스킬 다수 부합, 거의 맞춤형" },
  { range: "60 ~ 79",  label: "높음",     desc: "직무 분야·주요 기술 일치" },
  { range: "40 ~ 59",  label: "보통",     desc: "관련 분야 또는 일부 키워드 연관" },
  { range: "0 ~ 39",   label: "참고",     desc: "간접 연관, 다른 옵션과 비교 추천" },
];

export default function MatchScoreBadge({ score }) {
  const [showInfo, setShowInfo] = useState(false);
  const info = getScoreInfo(score);

  return (
    <div className={styles.wrapper}>
      <div
        className={styles.badge}
        style={{ color: info.color, background: info.bg, borderColor: info.border }}
      >
        <span className={styles.score}>{Math.round(score)}</span>
        <span className={styles.unit}>점</span>
        <span className={styles.levelDot} style={{ background: info.color }} />
        <span className={styles.level}>{info.label}</span>
        <button
          className={styles.infoBtn}
          onClick={(e) => { e.stopPropagation(); setShowInfo(!showInfo); }}
          title="점수 기준 보기"
        >?</button>
      </div>

      {showInfo && (
        <div className={styles.tooltip} onClick={() => setShowInfo(false)}>
          <div className={styles.tooltipHeader}>
            <span>AI 추천 점수 기준</span>
            <button className={styles.closeBtn} onClick={() => setShowInfo(false)}>✕</button>
          </div>
          <p className={styles.tooltipDesc}>
            입력 내용과 훈련과정 정보를 AI(임베딩 모델)가 의미적으로 비교해 유사도를 0~100점으로 환산합니다.
          </p>
          <div className={styles.criteria}>
            {CRITERIA.map((c) => (
              <div key={c.range} className={styles.criteriaRow}>
                <span className={styles.criteriaRange}>{c.range}점</span>
                <span className={styles.criteriaLabel}>{c.label}</span>
                <span className={styles.criteriaDesc}>{c.desc}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
