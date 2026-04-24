import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { usePortfolioStore } from "../store/portfolioStore.js";
import Button from "../components/common/Button.jsx";
import Card from "../components/common/Card.jsx";
import Tag from "../components/common/Tag.jsx";
import styles from "./PortfolioPage.module.css";

export default function PortfolioPage() {
  const navigate = useNavigate();
  const { prompt, skills, preferences, setPrompt, setSkills, setPreferences } =
    usePortfolioStore();
  const [skillInput, setSkillInput] = useState("");

  const addSkill = () => {
    const s = skillInput.trim();
    if (!s || skills.includes(s)) return;
    setSkills([...skills, s]);
    setSkillInput("");
  };

  const removeSkill = (s) => setSkills(skills.filter((x) => x !== s));

  const submit = () => navigate("/match");

  const canSubmit = (prompt && prompt.trim().length > 0) || skills.length > 0;

  return (
    <div className={styles.page}>
      <nav className={styles.nav}>
        <div className={styles.logo} onClick={() => navigate("/")}>
          Career<span>Match</span>
        </div>
        <Button onClick={() => navigate("/programs")}>프로그램 목록</Button>
      </nav>

      <main className={styles.container}>
        <h1 className={styles.title}>준비 상태를 입력하세요</h1>
        <p className={styles.subtitle}>
          입력 내용은 브라우저에 저장되며 추천 결과를 정렬하는 기준으로 사용됩니다.
        </p>

        <Card>
          <div className={styles.label}>희망 사항 / 자유 문장</div>
          <textarea
            className={styles.textarea}
            value={prompt || ""}
            onChange={(e) => setPrompt(e.target.value)}
            rows={5}
            placeholder="예: 온라인으로 들을 수 있는 백엔드 개발 과정을 찾고 있어요."
          />
        </Card>

        <Card>
          <div className={styles.label}>보유 스킬 / 관심 키워드</div>
          <div className={styles.skillRow}>
            <input
              className={styles.input}
              value={skillInput}
              onChange={(e) => setSkillInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  addSkill();
                }
              }}
              placeholder="예: Python (엔터로 추가)"
            />
            <Button onClick={addSkill}>추가</Button>
          </div>
          <div className={styles.skillTags}>
            {skills.length === 0 && (
              <span className={styles.empty}>아직 추가된 스킬이 없습니다.</span>
            )}
            {skills.map((s) => (
              <span key={s} className={styles.skillTag}>
                <Tag>{s}</Tag>
                <button
                  type="button"
                  className={styles.removeBtn}
                  onClick={() => removeSkill(s)}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </Card>

        <Card>
          <div className={styles.label}>선호 조건</div>
          <div className={styles.prefRow}>
            <label className={styles.checkLabel}>
              <input
                type="checkbox"
                checked={preferences.online || false}
                onChange={(e) =>
                  setPreferences({ ...preferences, online: e.target.checked })
                }
              />
              <span>온라인 우선</span>
            </label>
            <input
              className={styles.input}
              value={preferences.location || ""}
              onChange={(e) =>
                setPreferences({ ...preferences, location: e.target.value })
              }
              placeholder="희망 지역 (선택)"
            />
          </div>
        </Card>

        <div className={styles.actions}>
          <Button onClick={() => navigate("/")}>← 처음으로</Button>
          <Button variant="primary" onClick={submit} disabled={!canSubmit}>
            추천 결과 보기 →
          </Button>
        </div>
      </main>
    </div>
  );
}
