import Card from "../common/Card.jsx";
import Tag from "../common/Tag.jsx";
import { formatExamDate, relevanceLabel } from "../../lib/format.js";
import styles from "./QualificationCard.module.css";

export default function QualificationCard({ qualification, relevance, nextExam, compact = false }) {
  return (
    <Card className={styles.card}>
      <div className={styles.head}>
        <div className={styles.name}>{qualification.qual_name}</div>
        <div className={styles.badges}>
          {qualification.qual_type && <Tag variant="category">{qualification.qual_type}</Tag>}
          {relevance && <Tag>{relevanceLabel(relevance)}</Tag>}
        </div>
      </div>

      {!compact && qualification.job_field_name && (
        <div className={styles.field}>
          직무분야: {qualification.job_field_name}
          {qualification.mid_job_field && ` > ${qualification.mid_job_field}`}
        </div>
      )}

      {!compact && qualification.related_jobs && (
        <p className={styles.jobs}>{qualification.related_jobs}</p>
      )}

      {nextExam && (
        <div className={styles.exam}>
          <span className={styles.examLabel}>다음 시험</span>
          <div className={styles.examDates}>
            {nextExam.year && <span>{nextExam.year}년 {nextExam.round_no}회</span>}
            {nextExam.written_exam_start && (
              <span>
                필기 {formatExamDate(nextExam.written_exam_start)}
                {nextExam.written_exam_end !== nextExam.written_exam_start
                  ? ` ~ ${formatExamDate(nextExam.written_exam_end)}`
                  : ""}
              </span>
            )}
            {nextExam.practical_exam_start && (
              <span>실기 {formatExamDate(nextExam.practical_exam_start)}</span>
            )}
          </div>
        </div>
      )}

      {qualification.detail_url && (
        <div className={styles.footer}>
          <a href={qualification.detail_url} target="_blank" rel="noreferrer" className={styles.link}>
            Q-Net 상세보기 ↗
          </a>
        </div>
      )}
    </Card>
  );
}
