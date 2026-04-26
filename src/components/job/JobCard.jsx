import Card from "../common/Card.jsx";
import styles from "./JobCard.module.css";

export default function JobCard({ job, compact }) {
  return (
    <Card hoverable className={styles.card}>
      <div className={styles.head}>
        <div>
          <h3 className={styles.title}>{job.title}</h3>
          <span className={styles.company}>{job.company || "기업명 비공개"}</span>
        </div>
        {job.employment_type && (
          <span className={styles.typeBadge}>{job.employment_type}</span>
        )}
      </div>
      <div className={styles.meta}>
        {job.location && <span>📍 {job.location}</span>}
        {job.salary && <span>💰 {job.salary}</span>}
        {job.deadline && <span>📅 ~{job.deadline}</span>}
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
      <a
        href={job.url && job.url !== "https://www.work24.go.kr" ? job.url : "https://www.work24.go.kr/wk/a/b/1200/retriveDtlEmpSrchList.do"}
        target="_blank" rel="noreferrer" className={styles.link}
      >
        채용공고 확인하기 ↗
      </a>
    </Card>
  );
}
