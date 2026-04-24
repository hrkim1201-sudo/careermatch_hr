import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useThemeStore } from "../../store/themeStore.js";
import styles from "./Nav.module.css";

const LINKS = [
  { to: "/programs",       label: "훈련과정" },
  { to: "/qualifications", label: "국가자격" },
  { to: "/jobs",           label: "채용공고" },
];

export default function Nav() {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const { theme, toggleTheme } = useThemeStore();
  const [open, setOpen] = useState(false);

  return (
    <header className={styles.header}>
      <nav className={styles.nav}>
        {/* 로고 */}
        <div className={styles.logo} onClick={() => { navigate("/"); setOpen(false); }}>
          Career<span>Match</span>
        </div>

        {/* 데스크탑 링크 */}
        <div className={styles.links}>
          {LINKS.map((l) => (
            <button
              key={l.to}
              className={`${styles.link} ${pathname === l.to ? styles.active : ""}`}
              onClick={() => navigate(l.to)}
            >
              {l.label}
            </button>
          ))}
          <button
            className={styles.cta}
            onClick={() => navigate("/")}
          >
            추천 받기
          </button>
          <button className={styles.themeBtn} onClick={toggleTheme} title="테마 변경">
            {theme === "dark" ? "☀️" : "🌙"}
          </button>
        </div>

        {/* 모바일 우측 버튼들 */}
        <div className={styles.mobileRight}>
          <button className={styles.themeBtn} onClick={toggleTheme}>
            {theme === "dark" ? "☀️" : "🌙"}
          </button>
          <button className={styles.burger} onClick={() => setOpen(!open)}>
            <span className={`${styles.bar} ${open ? styles.open1 : ""}`} />
            <span className={`${styles.bar} ${open ? styles.open2 : ""}`} />
            <span className={`${styles.bar} ${open ? styles.open3 : ""}`} />
          </button>
        </div>
      </nav>

      {/* 모바일 드로어 */}
      {open && (
        <div className={styles.drawer}>
          {LINKS.map((l) => (
            <button
              key={l.to}
              className={`${styles.drawerLink} ${pathname === l.to ? styles.drawerActive : ""}`}
              onClick={() => { navigate(l.to); setOpen(false); }}
            >
              {l.label}
            </button>
          ))}
          <button
            className={styles.drawerCta}
            onClick={() => { navigate("/"); setOpen(false); }}
          >
            추천 받기
          </button>
        </div>
      )}
    </header>
  );
}
