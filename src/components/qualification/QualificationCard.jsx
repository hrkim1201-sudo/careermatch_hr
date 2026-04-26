import Card from "../common/Card.jsx";
import Tag from "../common/Tag.jsx";
import { formatExamDate } from "../../lib/format.js";
import styles from "./QualificationCard.module.css";

const TYPE_VARIANT = { "기술사": "accent", "기능장": "accent", "기사": "category", "산업기사": "default", "기능사": "default" };

export default function QualificationCard({ qualification: q, relevance, nextExam, compact }) {
  return (
    <Card hoverable className={styles.card}>
      <div className={styles.top}>
        {q.qual_type && <Tag variant={TYPE_VARIANT[q.qual_type] || "default"}>{q.qual_type}</Tag>}
        {q.job_field_name && <span className={styles.field}>{q.job_field_name}</span>}
      </div>
      <h3 className={styles.name}>{q.qual_name}</h3>
      {q.mid_job_field && <p className={styles.sub}>{q.mid_job_field}</p>}
      {q.related_jobs && !compact && (
        <p className={styles.jobs}>{q.related_jobs}</p>
      )}
      {(q.written_fee || q.practical_fee) && !compact && (
        <div className={styles.fees}>
          {q.written_fee && q.written_fee !== "0" && <span>필기 {parseInt(q.written_fee).toLocaleString()}원</span>}
          {q.practical_fee && q.practical_fee !== "0" && <span>실기 {parseInt(q.practical_fee).toLocaleString()}원</span>}
        </div>
      )}
      {nextExam && (
        <div className={styles.exam}>
          <span className={styles.examDot} />
          {nextExam.year}년 {nextExam.round_no}회 시험
          {nextExam.written_exam_start && ` · ${formatExamDate(nextExam.written_exam_start)}`}
        </div>
      )}
      {q.detail_url && (
        <a href={q.detail_url} target="_blank" rel="noreferrer" className={styles.link}>
          Q-Net 상세보기 ↗
        </a>
      )}
    </Card>
  );
}
