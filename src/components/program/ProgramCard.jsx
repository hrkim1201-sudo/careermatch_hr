import Card from "../common/Card.jsx";
import Tag from "../common/Tag.jsx";
import styles from "./ProgramCard.module.css";

const TYPE_INFO = {
  kdt:           { label: "내일배움카드", variant: "category" },
  apprenticeship:{ label: "일학습병행",   variant: "accent" },
  capability:    { label: "취업역량",     variant: "warn" },
  bizowner:      { label: "사업주훈련",   variant: "default" },
  consortium:    { label: "컨소시엄",     variant: "default" },
  training:      { label: "훈련과정",     variant: "default" },
};

function getWork24Url(program) {
  // 실제 Work24 데이터면 URL 그대로
  if (program.url && program.url.includes("work24.go.kr") && !program.external_id?.includes("sample")) {
    return program.url;
  }
  // 샘플은 제목으로 고용24 훈련과정 검색
  const keyword = encodeURIComponent((program.title || "").trim());
  const type = program.program_type;
  if (type === "capability") {
    return `https://www.work24.go.kr/wk/a/b/1400/retriveSrchJobAbilInfoList.do?schText=${keyword}`;
  }
  return `https://www.work24.go.kr/wk/a/b/1300/retriveSrchTraPbancInfoList.do?schText=${keyword}`;
}

export default function ProgramCard({ program, compact = false }) {
  const typeInfo = TYPE_INFO[program.program_type] || { label: program.program_type || "훈련과정", variant: "default" };
  const isSample = (program.external_id || "").includes("sample") || (program.source === "sample");
  const url = getWork24Url(program);

  return (
    <Card hoverable className={styles.card}>
      <div className={styles.top}>
        <div className={styles.badges}>
          <Tag variant={typeInfo.variant}>{typeInfo.label}</Tag>
          {isSample && <span className={styles.sampleBadge}>예시</span>}
        </div>
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
      </div>

      <a href={url} target="_blank" rel="noreferrer" className={styles.link}>
        고용24에서 훈련과정 확인하기 ↗
      </a>

      {isSample && (
        <p className={styles.notice}>
          ※ 예시 데이터입니다. 실제 훈련과정은 고용24에서 확인하세요.
        </p>
      )}
    </Card>
  );
}
