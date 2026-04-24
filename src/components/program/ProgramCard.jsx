import Card from "../common/Card.jsx";
import Tag from "../common/Tag.jsx";
import styles from "./ProgramCard.module.css";

export default function ProgramCard({ program, compact = false }) {
  return (
    <Card className={styles.card}>
      <div className={styles.head}>
        <div className={styles.title}>{program.title}</div>
      </div>
      <div className={styles.meta}>
        {program.provider && <span>{program.provider}</span>}
        {program.location && <span>📍 {program.location}</span>}
        {program.schedule && <span>🕐 {program.schedule}</span>}
        {program.tuition && <span>💰 {program.tuition}</span>}
      </div>
      {!compact && program.summary && (
        <p className={styles.summary}>{program.summary}</p>
      )}
      <div className={styles.tags}>
        {program.category && <Tag variant="category">{program.category}</Tag>}
        {(program.tags || []).slice(0, 4).map((t) => <Tag key={t}>{t}</Tag>)}
      </div>
      {program.url && (
        <a href={program.url} target="_blank" rel="noreferrer" className={styles.link}>
          외부 링크 ↗
        </a>
      )}
    </Card>
  );
}
