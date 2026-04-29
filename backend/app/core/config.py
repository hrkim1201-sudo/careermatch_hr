from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── 데이터베이스 ───────────────────────────────────────────────────────────
    database_url: str = "sqlite:///./careermatch.db"

    # ── OpenAI ────────────────────────────────────────────────────────────────
    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-large"
    openai_chat_model: str = "gpt-4o-mini"

    # ── Work24 API 키 (고용24) ─────────────────────────────────────────────────
    work24_jobs_api_key: str = "bfa4cbc5-a49b-4ecc-84ea-3c65ddbb3301"        # 채용정보
    work24_kdt_api_key: str = "608d3aed-fa2e-4a8f-927f-04bcc67c18f7"         # 국민내일배움카드
    work24_bizowner_api_key: str = "15f629cc-d615-410f-8dba-a915e6e539f5"    # 사업주훈련
    work24_consortium_api_key: str = "e4d1b3dc-26b9-45d7-9292-ef147c2f3c6a" # 국가인적자원개발 컨소시엄
    work24_apprentice_api_key: str = "ff14ab69-6add-45cf-96f2-8711deeb3311"  # 일학습병행
    work24_capability_api_key: str = "99ae5f84-8422-4592-8953-331fd476bd12" # 구직자취업역량강화
    work24_sme_api_key: str = "8503c01c-5fa3-4dbf-b168-34e8cbc300b3"         # 강소기업
    work24_job_info_api_key: str = "be86512a-371f-4857-b6fa-bf5f48b3de57"   # 직업정보
    work24_common_api_key: str = "47abfcc6-0618-4730-988d-071d2997a9f3"     # 공통코드
    work24_duty_api_key: str = "39e9d50d-e930-4e5b-94a8-ee0b75f0f87f"       # 직무정보
    work24_major_api_key: str = "50ee9621-66d5-4237-8150-8bebf3a301fe"      # 학과정보

    # 하위 호환성
    work24_api_key: str = "bfa4cbc5-a49b-4ecc-84ea-3c65ddbb3301"

    # ── Q-Net API ─────────────────────────────────────────────────────────────
    qnet_api_key: str = ""
    qnet_api_key_decoded: str = ""
    qnet_qual_list_url: str = "https://www.q-net.or.kr/openapi/service/rest/GradListUtilApiService"
    qnet_exam_info_url: str = "https://www.q-net.or.kr/openapi/service/rest/ExamScheduleUtilApiService"

    # ── 서비스 설정 ───────────────────────────────────────────────────────────
    match_top_k: int = 10
    match_min_score: float = 0.0
    qual_top_k: int = 3
    work24_request_timeout: float = 15.0
    qnet_request_timeout: float = 15.0

    # ── 기타 ──────────────────────────────────────────────────────────────────
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins_str: str = '["http://localhost:5173","http://localhost:3000","https://careermatch-hr.vercel.app"]'

    @property
    def cors_origins(self) -> list[str]:
        import json
        try:
            return json.loads(self.cors_origins_str)
        except Exception:
            return ["http://localhost:5173"]

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
