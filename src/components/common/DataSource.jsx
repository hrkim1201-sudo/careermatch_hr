import styles from "./DataSource.module.css";

export default function DataSource() {
  return (
    <div className={styles.wrap}>
      <span className={styles.label}>데이터 출처</span>
      <a href="https://www.work24.go.kr" target="_blank" rel="noreferrer" className={styles.link}>
        고용노동부 고용24
      </a>
      <span className={styles.dot}>·</span>
      <a href="https://www.q-net.or.kr" target="_blank" rel="noreferrer" className={styles.link}>
        한국산업인력공단 Q-Net
      </a>
      <span className={styles.dot}>·</span>
      <span className={styles.license}>공공누리 제1유형</span>
    </div>
  );
}
