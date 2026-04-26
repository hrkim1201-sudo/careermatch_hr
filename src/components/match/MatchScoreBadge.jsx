import { useState } from "react";
import styles from "./MatchScoreBadge.module.css";

function getScoreInfo(score) {
  if (score >= 80) return { label: "ë§¤ìš° ?’ìŒ", color: "#00e5b0", bg: "rgba(0,229,176,0.12)", border: "rgba(0,229,176,0.3)" };
  if (score >= 60) return { label: "?’ìŒ",     color: "#4f7cff", bg: "rgba(79,124,255,0.12)", border: "rgba(79,124,255,0.3)" };
  if (score >= 40) return { label: "ë³´í†µ",     color: "#fbbf24", bg: "rgba(251,191,36,0.12)", border: "rgba(251,191,36,0.3)" };
  return               { label: "ì°¸ê³ ",      color: "#8b97b8", bg: "rgba(139,151,184,0.10)", border: "rgba(139,151,184,0.25)" };
}

const CRITERIA = [
  { range: "80 ~ 100", label: "ë§¤ìš° ?’ìŒ", desc: "ì§ë¬´Â·ì§€??·ìŠ¤???¤ìˆ˜ ë¶€?? ê±°ì˜ ë§ì¶¤?? },
  { range: "60 ~ 79",  label: "?’ìŒ",     desc: "ì§ë¬´ ë¶„ì•¼Â·ì£¼ìš” ê¸°ìˆ  ?¼ì¹˜" },
  { range: "40 ~ 59",  label: "ë³´í†µ",     desc: "ê´€??ë¶„ì•¼ ?ëŠ” ?¼ë? ?¤ì›Œ???°ê?" },
  { range: "0 ~ 39",   label: "ì°¸ê³ ",     desc: "ê°„ì ‘ ?°ê?, ?¤ë¥¸ ?µì…˜ê³?ë¹„êµ ì¶”ì²œ" },
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
        <span className={styles.unit}>??/span>
        <span className={styles.levelDot} style={{ background: info.color }} />
        <span className={styles.level}>{info.label}</span>
        <button
          className={styles.infoBtn}
          onClick={(e) => { e.stopPropagation(); setShowInfo(!showInfo); }}
          title="?ìˆ˜ ê¸°ì? ë³´ê¸°"
        >?</button>
      </div>

      {showInfo && (
        <div className={styles.tooltip} onClick={() => setShowInfo(false)}>
          <div className={styles.tooltipHeader}>
            <span>AI ì¶”ì²œ ?ìˆ˜ ê¸°ì?</span>
            <button className={styles.closeBtn} onClick={() => setShowInfo(false)}>??/button>
          </div>
          <p className={styles.tooltipDesc}>
            ?…ë ¥ ?´ìš©ê³??ˆë ¨ê³¼ì • ?•ë³´ë¥?AI(?„ë² ??ëª¨ë¸)ê°€ ?˜ë??ìœ¼ë¡?ë¹„êµ??? ì‚¬?„ë? 0~100?ìœ¼ë¡??˜ì‚°?©ë‹ˆ??
          </p>
          <div className={styles.criteria}>
            {CRITERIA.map((c) => (
              <div key={c.range} className={styles.criteriaRow}>
                <span className={styles.criteriaRange}>{c.range}??/span>
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
