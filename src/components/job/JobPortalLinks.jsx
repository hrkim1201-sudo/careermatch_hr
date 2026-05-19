import styles from "./JobPortalLinks.module.css";

const PORTALS = [
  {
    name: "고용24",
    color: "#1a5fd4",
    getUrl: (kw) => `https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=${encodeURIComponent(kw)}`,
  },
  {
    name: "잡코리아",
    color: "#e8420e",
    getUrl: (kw) => `https://www.jobkorea.co.kr/Search/?stext=${encodeURIComponent(kw)}&tabType=recruit`,
  },
  {
    name: "사람인",
    color: "#0066cc",
    getUrl: (kw) => `https://www.saramin.co.kr/zf_user/search/recruit?searchword=${encodeURIComponent(kw)}`,
  },
  {
    name: "원티드",
    color: "#355eff",
    getUrl: (kw) => `https://www.wanted.co.kr/search?query=${encodeURIComponent(kw)}&tab=position`,
  },
];

export default function JobPortalLinks({ keywords }) {
  // keywords: 배열 ["전기기사", "전기설비"] 또는 빈 배열
  if (!keywords || keywords.length === 0) return null;

  // 핵심 키워드만 사용 (최대 2개, 짧게)
  const kw = keywords
    .filter((k) => k && k.length >= 2)
    .slice(0, 2)
    .join(" ");

  if (!kw) return null;

  return (
    <div className={styles.wrap}>
      <p className={styles.label}>
        <span className={styles.dot} />
        <span><strong>"{kw}"</strong> 관련 채용공고를 각 포털에서 직접 검색하세요</span>
      </p>
      <div className={styles.portals}>
        {PORTALS.map((p) => (
          <a
            key={p.name}
            href={p.getUrl(kw)}
            target="_blank"
            rel="noreferrer"
            className={styles.btn}
            style={{ "--c": p.color }}
          >
            {p.name} ↗
          </a>
        ))}
      </div>
    </div>
  );
}
