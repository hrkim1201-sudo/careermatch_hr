import Nav from "../components/common/Nav.jsx";
import styles from "./PrivacyPage.module.css";

export default function PrivacyPage() {
  return (
    <div>
      <Nav />
      <main className={styles.container}>
        <h1 className={styles.title}>개인정보처리방침</h1>
        <p className={styles.date}>최종 수정일: 2026년 4월 28일</p>

        <section className={styles.section}>
          <h2>1. 수집하는 개인정보</h2>
          <p>CareerMatch는 서비스 제공을 위해 아래 정보를 처리합니다.</p>
          <ul>
            <li>입력하신 취업 관련 자연어 텍스트 (검색어)</li>
            <li>서비스 이용 기록 (접속 로그, 검색 기록)</li>
          </ul>
          <p>회원가입이 없으며, 이름·연락처·이메일 등 개인 식별 정보는 수집하지 않습니다.</p>
        </section>

        <section className={styles.section}>
          <h2>2. 개인정보의 이용 목적</h2>
          <ul>
            <li>훈련과정·국가자격·채용공고 추천 서비스 제공</li>
            <li>서비스 품질 개선 및 오류 분석</li>
          </ul>
        </section>

        <section className={styles.section}>
          <h2>3. 개인정보의 보유 및 파기</h2>
          <p>입력하신 검색어는 AI 추천 결과 반환 후 즉시 파기됩니다. 별도의 사용자 데이터를 저장하지 않습니다.</p>
        </section>

        <section className={styles.section}>
          <h2>4. 제3자 제공</h2>
          <p>CareerMatch는 사용자 정보를 제3자에게 제공하지 않습니다. 단, AI 추천 기능은 OpenAI API를 활용하며, 입력된 검색어가 OpenAI 서버에 전송될 수 있습니다.</p>
          <ul>
            <li>OpenAI 개인정보처리방침: <a href="https://openai.com/policies/privacy-policy" target="_blank" rel="noreferrer">openai.com/policies/privacy-policy</a></li>
          </ul>
        </section>

        <section className={styles.section}>
          <h2>5. 데이터 출처</h2>
          <p>본 서비스에서 제공하는 훈련과정·자격·채용 정보는 아래 공공데이터를 활용합니다.</p>
          <ul>
            <li>고용노동부 고용24 (work24.go.kr) — 공공누리 제1유형</li>
            <li>한국산업인력공단 Q-Net (q-net.or.kr) — 공공누리 제1유형</li>
          </ul>
          <p>공공누리 제1유형: 출처 표시 조건 하에 자유롭게 이용 가능</p>
        </section>

        <section className={styles.section}>
          <h2>6. 이용자의 권리</h2>
          <p>본 서비스는 개인 식별 정보를 저장하지 않으므로, 별도의 정보 열람·수정·삭제 요청이 필요하지 않습니다.</p>
        </section>

        <section className={styles.section}>
          <h2>7. 문의</h2>
          <p>개인정보 관련 문의사항이 있으시면 아래로 연락해 주세요.</p>
          <p>이메일: careermatch.help@gmail.com</p>
        </section>
      </main>
    </div>
  );
}
