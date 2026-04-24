import styles from "./MatchScoreBadge.module.css";
import { formatScore } from "../../lib/format.js";

export default function MatchScoreBadge({ score }) {
  let bandClass = styles.low;
  if (score >= 70) bandClass = styles.high;
  else if (score >= 40) bandClass = styles.mid;

  return (
    <span className={`${styles.badge} ${bandClass}`}>{formatScore(score)}</span>
  );
}
