import styles from "./JobPortalLinks.module.css";

// ── 지역 코드 매핑 ─────────────────────────────────────────────────────────
// 잡코리아 local 코드
const JOBKOREA_REGION = {
  "서울": "I010", "경기": "I020", "인천": "I030", "부산": "I040",
  "대구": "I050", "광주": "I060", "대전": "I070", "울산": "I080",
  "세종": "I090", "강원": "I100", "충북": "I110", "충남": "I120",
  "전북": "I130", "전남": "I140", "경북": "I150", "경남": "I160", "제주": "I170",
};

// 사람인 loc_mcd 코드
const SARAMIN_REGION = {
  "서울": "101", "경기": "102", "인천": "108", "부산": "106",
  "대구": "104", "광주": "103", "대전": "105", "울산": "107",
  "세종": "118", "강원": "109", "충북": "110", "충남": "111",
  "전북": "112", "전남": "113", "경북": "114", "경남": "115", "제주": "116",
};

// 고용24 sido 코드
const WORK24_REGION = {
  "서울": "I", "경기": "J", "인천": "B", "부산": "C",
  "대구": "D", "광주": "E", "대전": "F", "울산": "G",
  "강원": "H", "충북": "K", "충남": "L", "전북": "M",
  "전남": "N", "경북": "O", "경남": "P", "제주": "Q", "세종": "R",
};

// 지역명 정규화 (부분 문자열 매칭)
function normalizeRegion(region) {
  if (!region) return null;
  for (const key of Object.keys(JOBKOREA_REGION)) {
    if (region.includes(key)) return key;
  }
  return null;
}

// ── 포털 URL 빌더 ──────────────────────────────────────────────────────────
const PORTALS = [
  {
    name: "고용24",
    color: "#1a5fd4",
    getUrl: (kw, region) => {
      const base = `https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=${encodeURIComponent(kw)}`;
      const code = WORK24_REGION[region];
      return code ? `${base}&sido=${code}` : base;
    },
  },
  {
    name: "잡코리아",
    color: "#e8420e",
    getUrl: (kw, region) => {
      const base = `https://www.jobkorea.co.kr/Search/?stext=${encodeURIComponent(kw)}&tabType=recruit`;
      const code = JOBKOREA_REGION[region];
      return code ? `${base}&local=${code}` : base;
    },
  },
  {
    name: "사람인",
    color: "#0066cc",
    getUrl: (kw, region) => {
      const base = `https://www.saramin.co.kr/zf_user/search/recruit?searchword=${encodeURIComponent(kw)}`;
      const code = SARAMIN_REGION[region];
      return code ? `${base}&loc_mcd=${code}` : base;
    },
  },
  {
    name: "원티드",
    color: "#355eff",
    getUrl: (kw) =>
      `https://www.wanted.co.kr/search?query=${encodeURIComponent(kw)}&tab=position`,
  },
];

export default function JobPortalLinks({ keywords, region }) {
  if (!keywords || keywords.length === 0) return null;

  const kw = keywords.filter((k) => k && k.length >= 2).slice(0, 2).join(" ");
  if (!kw) return null;

  const normalizedRegion = normalizeRegion(region);
  const regionLabel = normalizedRegion ? ` · ${normalizedRegion}` : "";

  return (
    <div className={styles.wrap}>
      <p className={styles.label}>
        <span className={styles.dot} />
        <span>
          <strong>"{kw}"</strong>
          {normalizedRegion && <span className={styles.regionTag}>{normalizedRegion}</span>}
          {" "}관련 채용공고를 각 포털에서 직접 검색하세요
        </span>
      </p>
      <div className={styles.portals}>
        {PORTALS.map((p) => (
          <a
            key={p.name}
            href={p.getUrl(kw, normalizedRegion)}
            target="_blank"
            rel="noreferrer"
            className={styles.btn}
            style={{ "--c": p.color }}
          >
            {p.name}
            {normalizedRegion && p.name !== "원티드" && (
              <span className={styles.regionHint}> ({normalizedRegion})</span>
            )}
            {" "}↗
          </a>
        ))}
      </div>
    </div>
  );
}
