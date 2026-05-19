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
  {
    name: "링크드인",
    color: "#0077b5",
    getUrl: (kw) => `https://www.linkedin.com/jobs/search/?keywords=${encodeURIComponent(kw)}&location=%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD`,
  },
];

export default function JobPortalLinks({ keyword }) {
  if (!keyword) return null;
  const kw = keyword.replace(/\s*\(.*?\)/g, "").trim();

  return (
    <div className={styles.wrap}>
      <p className={styles.label}>
        <span className={styles.dot} />
        <strong>"{kw}"</strong> 관련 채용공고를 각 포털에서 직접 검색하세요
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
