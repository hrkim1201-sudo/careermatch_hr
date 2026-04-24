import styles from "./ProgramFilters.module.css";

const FILTERS = [
  { key: "all", label: "전체" },
  { key: "국민내일배움카드 훈련과정", label: "내일배움카드" },
  { key: "일학습병행훈련과정", label: "일학습병행" },
  { key: "구직자취업역량 강화프로그램", label: "취업역량" },
];

export default function ProgramFilters({ value, onChange }) {
  return (
    <div className={styles.row}>
      {FILTERS.map((f) => (
        <button
          key={f.key}
          className={`${styles.btn} ${value === f.key ? styles.active : ""}`.trim()}
          onClick={() => onChange(f.key)}
        >
          {f.label}
        </button>
      ))}
    </div>
  );
}
