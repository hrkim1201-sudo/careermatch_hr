import styles from "./GuidePanel.module.css";

export default function GuidePanel({ guide, questions, loading, method }) {
  if (loading) return <div className={styles.loading}>가이드 생성 중...</div>;
  if (!guide) return null;
  return (
    <div className={styles.panel}>
      <h4 className={styles.head}>
        학습 가이드
        {method && <span className={styles.method}>· {method}</span>}
      </h4>
      <p className={styles.body}>{guide}</p>
      {questions && questions.length > 0 && (
        <>
          <h4 className={styles.head}>자가 점검 질문</h4>
          <ul className={styles.list}>
            {questions.map((q, i) => (
              <li key={i}>{q}</li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
