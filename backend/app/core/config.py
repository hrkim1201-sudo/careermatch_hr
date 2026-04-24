"""Application configuration backed by environment variables."""
from functools import lru_cache
import json
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False
    )

    # --- Database ---
    database_url: str = (
        "postgresql+psycopg2://careermatch:careermatch@localhost:5432/careermatch"
    )

    # --- OpenAI ---
    openai_api_key: str | None = None
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o-mini"
    openai_request_timeout: float = 15.0

    # --- Work24 (4개 키) ---
    work24_api_key: str | None = None               # 범용 fallback
    work24_kdt_api_key: str | None = None           # 국민내일배움카드
    work24_apprentice_api_key: str | None = None    # 일학습병행
    work24_capability_api_key: str | None = None    # 구직자취업역량강화
    work24_request_timeout: float = 15.0

    # --- Q-Net ---
    qnet_api_key_encoded: str = (
        "DvJgIsnr0rv845jpTei3Lrlt75wIhFl86gYZ6dWEpJYKeDTsgXJAFxJ"
        "%2FZpd%2Fq4%2FbqSrHY8KDH4oSvH070lPHyQ%3D%3D"
    )
    qnet_api_key_decoded: str = (
        "DvJgIsnr0rv845jpTei3Lrlt75wIhFl86gYZ6dWEpJYKeDTsgXJAFxJ"
        "/Zpd/q4/bqSrHY8KDH4oSvH070lPHyQ=="
    )
    qnet_qual_list_url: str = (
        "https://openapi.q-net.or.kr/api/service/rest/InquiryListNationalQualifcationSVC"
    )
    qnet_exam_info_url: str = (
        "https://openapi.q-net.or.kr/api/service/rest/InquiryTestInformationNTQSVC"
    )
    qual_exam_schd_url: str = "https://apis.data.go.kr/B490007/qualExamSchd"
    qnet_request_timeout: float = 15.0

    # --- CORS ---
    cors_origins_str: str = '["http://localhost:5173","http://127.0.0.1:5173"]'

    @property
    def cors_origins(self) -> list[str]:
        try:
            return json.loads(self.cors_origins_str)
        except Exception:
            return [self.cors_origins_str]

    log_level: str = "INFO"
    environment: str = "development"

    # --- 추천 튜닝 ---
    match_top_k: int = 10
    match_min_score: float = 0.05
    qual_top_k: int = 5


@lru_cache
def get_settings() -> Settings:
    return Settings()
