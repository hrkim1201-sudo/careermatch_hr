import styles from "./Button.module.css";

export default function Button({
  children,
  variant = "default",
  onClick,
  type = "button",
  disabled = false,
}) {
  const cls = `${styles.btn} ${styles[variant] || ""}`.trim();
  return (
    <button type={type} className={cls} onClick={onClick} disabled={disabled}>
      {children}
    </button>
  );
}
