import Card from "../common/Card.jsx";
import Tag from "../common/Tag.jsx";
import styles from "./JobCard.module.css";

export default function JobCard({ job, compact = false }) {
  return (
    <Card className={styles.card}>
      <div className={styles.head}>
        <div className={styles.title}>{job.title}</div>
        {job.employment_type && <Tag variant="category">{job.employment_type}</Tag>}
      </div>
      <div className={styles.meta}>
        <span>🏢 {job.company || "회사명 미공개"}</span>
        {job.location && <span>📍 {job.location}</span>}
        {job.salary && <span>💰 {job.salary}</span>}
        {job.deadline && <span>📅 ~{job.deadline}</span>}
      </div>
      {!compact && job.summary && (
        <p className={styles.summary}>{job.summary}</p>
      )}
      {job.skills && (
        <div className={styles.skills}>{job.skills}</div>
      )}
      <div className={styles.tags}>
        {(job.tags || []).map((t) => <Tag key={t}>{t}</Tag>)}
      </div>
      {job.url && (
        <a href={job.url} target="_blank" rel="noreferrer" className={styles.link}>
          채용공고 보기 ↗
        </a>
      )}
    </Card>
  );
}
