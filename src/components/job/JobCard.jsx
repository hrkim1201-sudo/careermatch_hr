import Card from "../common/Card.jsx";
import styles from "./JobCard.module.css";

const WORK24_SEARCH = "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do";

function getWork24Url(job) {
  // 실제 Work24 ID가 있으면 상세 페이지
  const eid = job.external_id || "";
  const realId = eid.replace(/^work24-/, "");
  if (/^\d{7,}$/.test(realId)) {
    return `https://www.work24.go.kr/wk/a/b/1200/retriveDtlEmpInfo.do?wantedAuthNo=${realId}`;
  }
  // 샘플 데이터는 제목 기반 검색
  const keyword = encodeURIComponent((job.title || "").replace(/\s*\(.*?\)/g, "").trim());
  return `${WORK24_SEARCH}?schTxt=${keyword}`;
}

export default function JobCard({ job, compact }) {
  const isSample = (job.external_id || "").includes("sample");
  const url = getWork24Url(job);

  return (
    <Card hoverable className={styles.card}>
      <div className={styles.head}>
        <div>
          <div className={styles.titleRow}>
            <h3 className={styles.title}>{job.title}</h3>
            {isSample && <span className={styles.sampleBadge}>예시</span>}
          </div>
          <span className={styles.company}>{job.company || "기업명 미공개"}</span>
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

      <a href={url} target="_blank" rel="noreferrer" className={styles.link}>
        고용24에서 채용공고 확인하기 ↗
      </a>

      {isSample && (
        <p className={styles.notice}>
          ※ 예시 데이터입니다. 실제 채용공고는 고용24에서 확인하세요.
        </p>
      )}
    </Card>
  );
}
