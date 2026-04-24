# CareerMatch

고용24 실데이터 기반 AI 취업 프로그램 추천 웹서비스.
React + Vite 프론트엔드와 FastAPI 백엔드, PostgreSQL을 사용합니다.

## 아키텍처

```
[브라우저]
   │
   ▼ Vite dev (5173)
[React 18 + Zustand]
   │  fetch (apiClient.js)
   ▼
[FastAPI (8000)]
   ├─ routers   : /api/programs, /api/match, /api/portfolio
   ├─ services  : embedding (OpenAI ↔ TF-IDF), matcher, guide_generator
   ├─ work24_programs : 고용24 Open API 클라이언트 (sample fallback)
   └─ repository : SQL 격리
   │
   ▼
[PostgreSQL 16] ← Alembic 마이그레이션
```

## 빠른 시작 (Docker 권장)

```bash
git clone <repo-url>
cd careermatch

# 백엔드 환경변수 (선택값은 비워두면 fallback 동작)
cp backend/.env.example backend/.env

# DB + 백엔드 한 번에 기동
docker compose up --build

# 새 터미널에서 프론트엔드
cp .env.example .env
npm install
npm run dev
```

- API: <http://localhost:8000>
- API 문서(Swagger): <http://localhost:8000/docs>
- 프론트: <http://localhost:5173>

## 수동 설치 (Docker 없이)

PostgreSQL 16이 로컬에서 동작 중이어야 하며 `careermatch` DB가 있어야 합니다.

```bash
# 백엔드
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # DATABASE_URL 본인 환경에 맞춰 수정

alembic upgrade head
uvicorn main:app --reload

# 프론트엔드 (새 터미널)
cd ..
cp .env.example .env
npm install
npm run dev
```

## 환경변수

### Backend (`backend/.env`)

| 키 | 필수 | 기본값 | 설명 |
|----|------|--------|------|
| `DATABASE_URL` | Yes | `postgresql+psycopg2://...localhost...` | PostgreSQL 연결 문자열 |
| `OPENAI_API_KEY` | No | (없음) | 비우면 TF-IDF fallback 사용 |
| `OPENAI_EMBEDDING_MODEL` | No | `text-embedding-3-small` | 임베딩 모델명 |
| `OPENAI_CHAT_MODEL` | No | `gpt-4o-mini` | 가이드 생성 모델 |
| `WORK24_API_KEY` | No | (없음) | 비우면 샘플 데이터 사용 |
| `WORK24_BASE_URL` | No | `https://www.work24.go.kr/cm/openApi` | |
| `LOG_LEVEL` | No | `INFO` | |

### Frontend (`.env`)

| 키 | 기본값 | 설명 |
|----|--------|------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | 백엔드 주소 |

## 폴더 구조

```
careermatch/
├── .github/workflows/ci.yml
├── backend/
│   ├── alembic/              # DB 마이그레이션
│   ├── app/
│   │   ├── core/             # config, logging, exceptions
│   │   ├── routers/          # FastAPI 엔드포인트
│   │   ├── services/         # 비즈니스 로직 + 외부 API
│   │   ├── repositories/     # SQL 접근 격리
│   │   ├── database.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── tests/                # pytest
│   ├── Dockerfile
│   └── main.py
├── src/
│   ├── pages/                # 4개 화면
│   ├── components/           # common / program / match
│   ├── hooks/                # usePrograms, useMatch
│   ├── store/                # Zustand persist
│   ├── lib/                  # apiClient, format
│   └── styles/               # CSS 변수와 글로벌 스타일
├── docker-compose.yml
└── README.md
```

## 테스트

```bash
cd backend
pytest -v
```

테스트는 SQLite 인메모리 DB를 사용해서 PostgreSQL 없이도 실행됩니다.

```bash
# 프론트 린트
npm run lint
```

## 주요 API 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/programs` | 프로그램 목록과 카테고리별 카운트 |
| POST | `/api/programs/refresh` | 고용24에서 다시 받기 (키 없으면 샘플) |
| POST | `/api/match` | 추천 결과 (점수 내림차순) |
| POST | `/api/match/{program_id}/guide` | 학습 가이드 생성 |
| POST | `/api/portfolio` | 포트폴리오 저장 |
| GET | `/api/portfolio/{id}` | 포트폴리오 조회 |
| GET | `/health` | 헬스체크 |

## OpenAI 키 없이 동작하는가

네. 두 곳에서 자동으로 fallback 합니다.

- **임베딩**: OpenAI 호출 실패 또는 키 없음 → scikit-learn TF-IDF 사용. 응답 JSON의 `used_method` 필드로 어느 경로가 사용됐는지 알 수 있습니다.
- **학습 가이드**: OpenAI 실패 또는 키 없음 → 프로그램 메타데이터로 채우는 템플릿 사용.

이는 캡스톤 발표 시 네트워크/API 장애 상황에서도 데모가 깨지지 않도록 설계된 것입니다.

## 자주 생기는 문제

### 백엔드가 DB에 연결하지 못함
`backend/.env`의 `DATABASE_URL`이 본인 환경(또는 docker compose의 `db:5432`)과 일치하는지 확인하세요.

### `alembic upgrade head` 실행 시 모듈 오류
`backend/` 디렉토리 안에서 실행해야 하며, 가상환경이 활성화되어 있어야 합니다.

### 프론트가 백엔드와 통신하지 못함
- 백엔드가 8000 포트에서 동작 중인지 확인
- `.env`의 `VITE_API_BASE_URL`을 확인
- 브라우저 콘솔에서 CORS 에러가 보이면 `backend/app/core/config.py`의 `cors_origins`에 프론트 주소를 추가

### OpenAI 호출이 매번 실패함
키를 비우면 자동으로 TF-IDF fallback 됩니다. 특별히 OpenAI를 써야 하는 상황이 아니면 키 없이도 충분히 데모 가능합니다.

## 라이선스

MIT
