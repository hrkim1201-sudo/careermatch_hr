import Card from "../common/Card.jsx";
import styles from "./JobCard.module.css";

function buildJobUrl(job) {
  // external_id에서 실제 Work24 공고 번호 추출 시도
  const extId = job.external_id || "";
  const realId = extId.replace(/^work24-/, "");

  // 실제 Work24 공고 ID (숫자)인 경우 상세 페이지로 직접 이동
  if (/^\d{7,}$/.test(realId)) {
    return `https://www.work24.go.kr/wk/a/b/1200/retriveDtlEmpInfo.do?recrutPblntSn=${realId}`;
  }

  // 샘플/검색 URL이 이미 있으면 그대로 사용
  if (job.url && job.url !== "https://www.work24.go.kr" && job.url.includes("work24.go.kr")) {
    return job.url;
  }

  // 제목으로 Work24 검색
  const encoded = encodeURIComponent(job.title || "");
  return `https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=${encoded}`;
}

export default function JobCard({ job, compact }) {
  const jobUrl = buildJobUrl(job);

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
        href={jobUrl}
        target="_blank"
        rel="noreferrer"
        className={styles.link}
        onClick={(e) => e.stopPropagation()}
      >
        고용24에서 채용공고 확인하기 ↗
      </a>
    </Card>
  );
}
