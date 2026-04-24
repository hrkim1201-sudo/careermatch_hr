import Card from "../common/Card.jsx";
import Tag from "../common/Tag.jsx";
import styles from "./JobCard.module.css";

export default function JobCard({ job, compact = false }) {
  return (
    <Card className={styles.card}>
      <div className={styles.head}>
        <div className={styles.left}>
          <div className={styles.title}>{job.title}</div>
          <div className={styles.company}>{job.company || "기업명 비공개"}</div>
        </div>
        {job.employment_type && (
          <Tag variant="category">{job.employment_type}</Tag>
        )}
      </div>

      <div className={styles.meta}>
        {job.location && (
          <span className={styles.metaItem}>
            <span className={styles.icon}>📍</span>{job.location}
          </span>
        )}
        {job.salary && (
          <span className={styles.metaItem}>
            <span className={styles.icon}>💰</span>{job.salary}
          </span>
        )}
        {job.deadline && (
          <span className={styles.metaItem}>
            <span className={styles.icon}>📅</span>~{job.deadline}
          </span>
        )}
      </div>

      {!compact && job.summary && (
        <p className={styles.summary}>{job.summary}</p>
      )}

      {job.skills && (
        <div className={styles.skills}>
          {job.skills.split(/[\s,]+/).filter(Boolean).slice(0, 6).map((s) => (
            <span key={s} className={styles.skill}>{s}</span>
          ))}
        </div>
      )}

      {job.url && job.url !== "https://www.work24.go.kr" && (
        <a href={job.url} target="_blank" rel="noreferrer" className={styles.link}>
          공고 자세히 보기 ↗
        </a>
      )}
      {(!job.url || job.url === "https://www.work24.go.kr") && (
        <a href={`https://www.work24.go.kr/wk/a/b/1200/retriveDtlEmpSrchList.do`}
          target="_blank" rel="noreferrer" className={styles.link}>
          고용24에서 확인하기 ↗
        </a>
      )}
    </Card>
  );
}
