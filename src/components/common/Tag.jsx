import styles from "./Tag.module.css";

export default function Tag({ children, variant = "default" }) {
  return (
    <span className={`${styles.tag} ${styles[variant] || ""}`.trim()}>
      {children}
    </span>
  );
}
