import Card from "../common/Card.jsx";
import Tag from "../common/Tag.jsx";
import styles from "./ProgramCard.module.css";

export default function ProgramCard({ program, compact = false }) {
  return (
    <Card className={`${styles.card} ${compact ? styles.compact : ""}`.trim()}>
      <div className={styles.head}>
        <div className={styles.title}>{program.title}</div>
        <span className={styles.source}>{program.source}</span>
      </div>
      <div className={styles.meta}>
        {program.provider || "운영기관 정보 없음"} · {program.location || "위치 정보 없음"}
        <br />
        {program.schedule || "일정 정보 없음"} · {program.tuition || "비용 정보 없음"}
      </div>
      {!compact && (
        <p className={styles.summary}>
          {program.summary || "요약 정보가 없습니다."}
        </p>
      )}
      <div className={styles.tags}>
        {program.category && <Tag variant="category">{program.category}</Tag>}
        {(program.tags || []).slice(0, 5).map((t) => (
          <Tag key={t}>{t}</Tag>
        ))}
      </div>
      {program.url && (
        <div className={styles.footer}>
          <a href={program.url} target="_blank" rel="noreferrer" className={styles.link}>
            외부 링크 ↗
          </a>
        </div>
      )}
    </Card>
  );
}
