import Card from "../common/Card.jsx";
import Tag from "../common/Tag.jsx";
import { formatExamDate } from "../../lib/format.js";
import styles from "./QualificationCard.module.css";

const TYPE_VARIANT = {
  "기술사": "accent", "기능장": "accent",
  "기사": "category", "산업기사": "default", "기능사": "default",
};

export default function QualificationCard({ qualification: q, relevance, nextExam, compact }) {
  // 자격명 기반 Q-Net 검색 URL (가장 확실하게 해당 자격 페이지로 이동)
  const qnetUrl = `https://www.q-net.or.kr/crf005.do?id=crf00505&kw=${encodeURIComponent(q.qual_name)}`;

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
          {q.written_fee && q.written_fee !== "0" && (
            <span>필기 {Number(q.written_fee).toLocaleString()}원</span>
          )}
          {q.practical_fee && q.practical_fee !== "0" && (
            <span>실기 {Number(q.practical_fee).toLocaleString()}원</span>
          )}
        </div>
      )}

      {nextExam && (
        <div className={styles.exam}>
          <span className={styles.examDot} />
          {nextExam.year}년 {nextExam.round_no}회
          {nextExam.written_exam_start && ` · ${formatExamDate(nextExam.written_exam_start)}`}
        </div>
      )}

      <a
        href={qnetUrl}
        target="_blank"
        rel="noreferrer"
        className={styles.link}
        onClick={(e) => e.stopPropagation()}
      >
        Q-Net에서 {q.qual_name} 보기 ↗
      </a>
    </Card>
  );
}
