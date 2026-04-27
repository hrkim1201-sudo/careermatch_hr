import Card from "../common/Card.jsx";
import Tag from "../common/Tag.jsx";
import styles from "./ProgramCard.module.css";

const TYPE_INFO = {
  kdt:           { label: "내일배움카드", variant: "category" },
  apprenticeship:{ label: "일학습병행",   variant: "accent" },
  capability:    { label: "취업역량",     variant: "warn" },
  training:      { label: "훈련과정",     variant: "default" },
};

export default function ProgramCard({ program, compact = false }) {
  const typeInfo = TYPE_INFO[program.program_type] || { label: program.program_type, variant: "default" };

  return (
    <Card hoverable className={styles.card}>
      <div className={styles.top}>
        <Tag variant={typeInfo.variant}>{typeInfo.label}</Tag>
        {program.tuition && (
          <span className={styles.tuition}>{program.tuition}</span>
        )}
      </div>

      <h3 className={styles.title}>{program.title}</h3>

      <div className={styles.meta}>
        {program.provider && <span className={styles.metaItem}>🏫 {program.provider}</span>}
        {program.location && <span className={styles.metaItem}>📍 {program.location}</span>}
        {program.schedule && <span className={styles.metaItem}>🕐 {program.schedule}</span>}
      </div>

      {!compact && program.summary && (
        <p className={styles.summary}>{program.summary}</p>
      )}

      {program.skills && (
        <div className={styles.skills}>
          {program.skills.split(/\s+/).filter(Boolean).slice(0, 5).map((s) => (
            <span key={s} className={styles.skill}>{s}</span>
          ))}
        </div>
      )}

      <div className={styles.footer}>
        <div className={styles.tags}>
          {(program.tags || []).slice(0, 3).map((t) => <Tag key={t}>{t}</Tag>)}
          {program.ncs_name && <Tag variant="default">NCS {program.ncs_name}</Tag>}
        </div>
        {program.url && (
          <a
            href={program.url}
            target="_blank"
            rel="noreferrer"
            className={styles.link}
            onClick={(e) => e.stopPropagation()}
          >
            고용24에서 보기 ↗
          </a>
        )}
      </div>
    </Card>
  );
}
