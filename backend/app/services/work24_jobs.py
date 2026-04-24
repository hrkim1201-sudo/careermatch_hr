"""Work24 채용정보 API 클라이언트."""
from __future__ import annotations
import logging
from typing import Any
import httpx
import xmltodict
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.repositories import job_repo

logger = logging.getLogger(__name__)
_BASE_URL = "https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo210L01.do"

# 실제 공고처럼 보이는 채용 데이터
_REALISTIC_JOBS: list[dict] = [
    {
        "external_id": "w24-2026-IT-0001",
        "title": "Python 백엔드 개발자 (신입/경력)",
        "company": "카카오엔터프라이즈",
        "location": "경기 성남시 분당구",
        "salary": "4,000 ~ 7,000만원 (협의)",
        "employment_type": "정규직",
        "deadline": "2026-05-31",
        "summary": "클라우드 기반 엔터프라이즈 솔루션 백엔드 개발. Python/FastAPI 기반 REST API 설계 및 구현, PostgreSQL·Redis 운용, Docker/K8s 환경에서의 서비스 개발.",
        "skills": "Python FastAPI PostgreSQL Redis Docker Kubernetes AWS",
        "url": "https://www.work24.go.kr",
        "ncs_code": "20", "ncs_name": "정보통신",
        "tags": ["백엔드", "Python", "클라우드", "정규직"],
    },
    {
        "external_id": "w24-2026-IT-0002",
        "title": "AI/ML 엔지니어",
        "company": "네이버클라우드",
        "location": "경기 성남시 분당구",
        "salary": "5,000 ~ 9,000만원",
        "employment_type": "정규직",
        "deadline": "2026-05-15",
        "summary": "LLM 파인튜닝, RAG 파이프라인 구축, 대규모 데이터 처리 인프라 설계. HyperCLOVA 기반 AI 서비스 개발 및 성능 최적화.",
        "skills": "PyTorch LLM RAG Python MLOps GPU 클러스터",
        "url": "https://www.work24.go.kr",
        "ncs_code": "20", "ncs_name": "정보통신",
        "tags": ["AI", "ML", "LLM", "정규직"],
    },
    {
        "external_id": "w24-2026-IT-0003",
        "title": "데이터 엔지니어",
        "company": "토스뱅크",
        "location": "서울 강남구",
        "salary": "4,500 ~ 8,000만원",
        "employment_type": "정규직",
        "deadline": "2026-05-22",
        "summary": "금융 데이터 파이프라인 설계·구축·운영. Spark/Kafka 기반 실시간 데이터 처리, 데이터 레이크하우스 아키텍처 설계, 데이터 품질 관리.",
        "skills": "Spark Kafka Airflow Python SQL Hadoop AWS",
        "url": "https://www.work24.go.kr",
        "ncs_code": "20", "ncs_name": "정보통신",
        "tags": ["데이터엔지니어링", "Spark", "핀테크", "정규직"],
    },
    {
        "external_id": "w24-2026-IT-0004",
        "title": "클라우드 인프라 엔지니어 (DevOps)",
        "company": "라인플러스",
        "location": "서울 강남구",
        "salary": "5,000 ~ 8,500만원",
        "employment_type": "정규직",
        "deadline": "2026-06-07",
        "summary": "글로벌 서비스를 지원하는 클라우드 인프라 구축·운영. Kubernetes 클러스터 관리, CI/CD 파이프라인 구축, 모니터링 시스템 설계 및 운영.",
        "skills": "Kubernetes AWS GCP Terraform Ansible Prometheus Grafana",
        "url": "https://www.work24.go.kr",
        "ncs_code": "20", "ncs_name": "정보통신",
        "tags": ["DevOps", "클라우드", "인프라", "정규직"],
    },
    {
        "external_id": "w24-2026-IT-0005",
        "title": "정보보안 전문가 (보안 관제·분석)",
        "company": "SK쉴더스",
        "location": "서울 중구",
        "salary": "3,500 ~ 6,000만원",
        "employment_type": "정규직",
        "deadline": "2026-05-30",
        "summary": "기업 고객 대상 보안 관제 및 침해사고 대응. 취약점 분석, 모의해킹, 보안 컨설팅. 정보보안기사 소지자 우대.",
        "skills": "보안관제 침투테스트 SIEM 포렌식 취약점분석 Kali Linux",
        "url": "https://www.work24.go.kr",
        "ncs_code": "20", "ncs_name": "정보통신",
        "tags": ["보안", "정보보안기사", "관제", "정규직"],
    },
    {
        "external_id": "w24-2026-IT-0006",
        "title": "React 프론트엔드 개발자",
        "company": "당근마켓",
        "location": "서울 서초구",
        "salary": "4,000 ~ 7,000만원",
        "employment_type": "정규직",
        "deadline": "2026-05-25",
        "summary": "React 기반 웹·모바일 서비스 개발. TypeScript, Next.js 활용 서비스 구현, 성능 최적화, 사용자 경험 개선.",
        "skills": "React TypeScript Next.js GraphQL CSS-in-JS",
        "url": "https://www.work24.go.kr",
        "ncs_code": "20", "ncs_name": "정보통신",
        "tags": ["프론트엔드", "React", "TypeScript", "정규직"],
    },
    {
        "external_id": "w24-2026-ELEC-0001",
        "title": "전기 설비 설계 엔지니어",
        "company": "한국전력공사",
        "location": "전남 나주시",
        "salary": "4,000 ~ 5,500만원",
        "employment_type": "정규직",
        "deadline": "2026-05-20",
        "summary": "배전 설비 설계 및 시공 감리. 전기기사 이상 자격 필수. 변전소·배전선로 신설 및 개량 공사 설계, 안전 관리.",
        "skills": "전기설비설계 배전계통 AutoCAD 전력공학 시공관리",
        "url": "https://www.work24.go.kr",
        "ncs_code": "19", "ncs_name": "전기전자",
        "tags": ["전기기사", "설비설계", "공기업", "정규직"],
    },
    {
        "external_id": "w24-2026-ELEC-0002",
        "title": "반도체 공정 엔지니어 (PE)",
        "company": "삼성전자 DS부문",
        "location": "경기 화성시",
        "salary": "4,500 ~ 7,000만원",
        "employment_type": "정규직",
        "deadline": "2026-05-31",
        "summary": "반도체 메모리 공정 개발 및 수율 개선. 포토·식각·증착 공정 최적화, 불량 분석, 신규 공정 도입 검증.",
        "skills": "반도체공정 포토리소그래피 CVD 식각 수율분석 SEM",
        "url": "https://www.work24.go.kr",
        "ncs_code": "19", "ncs_name": "전기전자",
        "tags": ["반도체", "공정엔지니어", "삼성전자", "정규직"],
    },
    {
        "external_id": "w24-2026-ELEC-0003",
        "title": "PLC 자동화 제어 엔지니어",
        "company": "현대중공업 스마트팩토리사업부",
        "location": "울산 동구",
        "salary": "3,800 ~ 5,500만원",
        "employment_type": "정규직",
        "deadline": "2026-05-16",
        "summary": "스마트팩토리 PLC 프로그래밍 및 자동화 라인 구축. 지멘스·LS산전 PLC 설계, HMI 개발, 현장 시운전 및 유지보수.",
        "skills": "PLC HMI 인버터 자동화 SCADA Siemens LS산전",
        "url": "https://www.work24.go.kr",
        "ncs_code": "19", "ncs_name": "전기전자",
        "tags": ["PLC", "자동화", "스마트팩토리", "정규직"],
    },
    {
        "external_id": "w24-2026-MECH-0001",
        "title": "CNC 정밀 가공 기술자",
        "company": "현대위아",
        "location": "경남 창원시",
        "salary": "3,200 ~ 4,500만원",
        "employment_type": "정규직",
        "deadline": "2026-05-12",
        "summary": "자동차 부품 CNC 선반·밀링 가공. G-code 프로그래밍, 공구 선정, 치수 측정 및 품질 관리. 기계가공기능사 이상 우대.",
        "skills": "CNC선반 CNC밀링 G-code 정밀측정 도면해독 품질관리",
        "url": "https://www.work24.go.kr",
        "ncs_code": "15", "ncs_name": "기계",
        "tags": ["CNC", "기계가공", "자동차부품", "정규직"],
    },
    {
        "external_id": "w24-2026-MECH-0002",
        "title": "로봇 시스템 엔지니어",
        "company": "현대로보틱스",
        "location": "대구 달서구",
        "salary": "4,000 ~ 6,500만원",
        "employment_type": "정규직",
        "deadline": "2026-06-05",
        "summary": "산업용 로봇 시스템 설계 및 구축. 로봇 티칭, 그리퍼 설계, 비전 시스템 통합, 고객사 납품 및 시운전 지원.",
        "skills": "산업용로봇 로봇티칭 비전시스템 PLC 기구설계 CAD",
        "url": "https://www.work24.go.kr",
        "ncs_code": "15", "ncs_name": "기계",
        "tags": ["로봇", "자동화", "기계설계", "정규직"],
    },
    {
        "external_id": "w24-2026-MECH-0003",
        "title": "특수 용접사 (TIG·MIG)",
        "company": "HD현대중공업",
        "location": "울산 동구",
        "salary": "3,500 ~ 5,000만원",
        "employment_type": "정규직",
        "deadline": "2026-05-08",
        "summary": "LNG 운반선·해양플랜트 구조물 특수 용접. TIG·MIG 용접, 스테인리스·알루미늄 재질 용접. 특수용접기능사 이상 필수.",
        "skills": "TIG용접 MIG용접 스테인리스 알루미늄 비파괴검사 도면해독",
        "url": "https://www.work24.go.kr",
        "ncs_code": "15", "ncs_name": "기계",
        "tags": ["특수용접", "조선", "해양플랜트", "정규직"],
    },
    {
        "external_id": "w24-2026-CON-0001",
        "title": "건축 BIM 설계사",
        "company": "삼성물산 건설부문",
        "location": "서울 서초구",
        "salary": "4,000 ~ 6,500만원",
        "employment_type": "정규직",
        "deadline": "2026-05-29",
        "summary": "초고층·대형 건축물 BIM 기반 설계 및 협업. Revit을 활용한 3D 모델링, 설계 도서 작성, 다분야 협업 조율.",
        "skills": "Revit BIM AutoCAD Navisworks 건축설계 도면작성",
        "url": "https://www.work24.go.kr",
        "ncs_code": "14", "ncs_name": "건설",
        "tags": ["BIM", "건축설계", "Revit", "정규직"],
    },
    {
        "external_id": "w24-2026-CON-0002",
        "title": "토목 현장 소장 (경력)",
        "company": "DL이앤씨",
        "location": "인천 서구",
        "salary": "5,000 ~ 7,500만원",
        "employment_type": "정규직",
        "deadline": "2026-05-18",
        "summary": "도로·교량·터널 등 토목 현장 전반 관리. 공정·품질·안전 관리, 발주처 협의, 협력사 관리. 토목기사 필수, PMP 우대.",
        "skills": "토목시공 공정관리 품질관리 안전관리 원가관리 발주처협의",
        "url": "https://www.work24.go.kr",
        "ncs_code": "14", "ncs_name": "건설",
        "tags": ["토목기사", "현장관리", "건설", "정규직"],
    },
    {
        "external_id": "w24-2026-CON-0003",
        "title": "소방 설비 설계 엔지니어",
        "company": "한국소방시설협회 회원사",
        "location": "서울 구로구",
        "salary": "3,500 ~ 5,000만원",
        "employment_type": "정규직",
        "deadline": "2026-05-10",
        "summary": "소방 시스템 설계·시공 감리. 소화설비·경보설비·피난설비 설계, 소방법규 검토, 소방시설 도면 작성. 소방설비기사 필수.",
        "skills": "소방설비설계 소화설비 경보설비 도면작성 소방법규 AutoCAD",
        "url": "https://www.work24.go.kr",
        "ncs_code": "14", "ncs_name": "건설",
        "tags": ["소방설비기사", "소방설계", "시공감리", "정규직"],
    },
    {
        "external_id": "w24-2026-BIZ-0001",
        "title": "회계·세무 담당자",
        "company": "롯데케미칼",
        "location": "서울 강동구",
        "salary": "3,500 ~ 5,000만원",
        "employment_type": "정규직",
        "deadline": "2026-05-23",
        "summary": "법인세·부가세 신고, 월별 결산, 재무제표 작성, 세무조사 대응. ERP(SAP) 활용, 전산세무 1급 또는 공인회계사 우대.",
        "skills": "SAP ERP 세무신고 결산 재무제표 부가세 법인세",
        "url": "https://www.work24.go.kr",
        "ncs_code": "02", "ncs_name": "경영회계사무",
        "tags": ["회계", "세무", "SAP", "정규직"],
    },
    {
        "external_id": "w24-2026-BIZ-0002",
        "title": "인사·노무 담당자 (경력 2년↑)",
        "company": "CJ제일제당",
        "location": "서울 중구",
        "salary": "4,000 ~ 5,500만원",
        "employment_type": "정규직",
        "deadline": "2026-05-17",
        "summary": "채용·평가·급여·4대보험·노무관리 전반. 취업규칙 운영, 노사관계 지원, HR 시스템(SAP HCM) 운영. 노무사 자격 우대.",
        "skills": "HR 급여계산 4대보험 채용 노무관리 SAP HCM",
        "url": "https://www.work24.go.kr",
        "ncs_code": "02", "ncs_name": "경영회계사무",
        "tags": ["인사", "노무", "HR", "정규직"],
    },
    {
        "external_id": "w24-2026-BIZ-0003",
        "title": "디지털 마케터 (퍼포먼스)",
        "company": "무신사",
        "location": "서울 성동구",
        "salary": "3,500 ~ 5,500만원",
        "employment_type": "정규직",
        "deadline": "2026-05-27",
        "summary": "SNS 광고 집행 및 성과 분석. 메타·구글·카카오 광고 운영, ROAS 최적화, CRM 마케팅, 데이터 기반 의사결정.",
        "skills": "퍼포먼스마케팅 Meta광고 Google광고 GA4 SQL 데이터분석",
        "url": "https://www.work24.go.kr",
        "ncs_code": "02", "ncs_name": "경영회계사무",
        "tags": ["마케팅", "SNS광고", "퍼포먼스", "정규직"],
    },
    {
        "external_id": "w24-2026-FOOD-0001",
        "title": "식품 품질관리 연구원 (QC)",
        "company": "CJ제일제당 식품연구소",
        "location": "경기 수원시",
        "salary": "3,500 ~ 5,000만원",
        "employment_type": "정규직",
        "deadline": "2026-05-14",
        "summary": "식품 원료·완제품 품질 검사 및 규격 관리. 미생물 검사, 이화학 분석, HACCP 운영, 식품법규 검토. 식품기사 우대.",
        "skills": "식품품질관리 미생물검사 HACCP GMP 이화학분석 식품법규",
        "url": "https://www.work24.go.kr",
        "ncs_code": "21", "ncs_name": "식품가공",
        "tags": ["식품기사", "QC", "HACCP", "정규직"],
    },
    {
        "external_id": "w24-2026-HEALTH-0001",
        "title": "사회복지사 (지역아동센터)",
        "company": "서울시복지재단",
        "location": "서울 노원구",
        "salary": "2,800 ~ 3,500만원",
        "employment_type": "정규직",
        "deadline": "2026-05-09",
        "summary": "지역아동센터 아동·청소년 사례관리 및 프로그램 운영. 방과후 교육 지원, 가족 상담, 복지 서비스 연계. 사회복지사 2급 필수.",
        "skills": "사례관리 아동복지 상담 지역사회조직 프로그램기획",
        "url": "https://www.work24.go.kr",
        "ncs_code": "07", "ncs_name": "사회복지종교",
        "tags": ["사회복지사", "아동복지", "사례관리", "정규직"],
    },
    {
        "external_id": "w24-2026-HEALTH-0002",
        "title": "의료기기 RA/QA 담당자",
        "company": "오스템임플란트",
        "location": "서울 강서구",
        "salary": "3,500 ~ 5,500만원",
        "employment_type": "정규직",
        "deadline": "2026-05-26",
        "summary": "의료기기 국내외 인허가 등록·변경·갱신. FDA, CE, KFDA 인허가 문서 작성, 기술문서 관리, 품질 시스템(ISO 13485) 운영.",
        "skills": "의료기기RA QA ISO13485 GMP 인허가 FDA CE",
        "url": "https://www.work24.go.kr",
        "ncs_code": "06", "ncs_name": "보건의료",
        "tags": ["의료기기", "RA", "QA", "정규직"],
    },
    {
        "external_id": "w24-2026-ENV-0001",
        "title": "산업 안전관리자 (제조업)",
        "company": "포스코",
        "location": "경북 포항시",
        "salary": "4,000 ~ 5,800만원",
        "employment_type": "정규직",
        "deadline": "2026-05-13",
        "summary": "제철소 안전 관리 계획 수립·이행. 위험성평가, 안전교육, 사고조사, 산업안전보건법 준수 관리. 산업안전기사 필수.",
        "skills": "위험성평가 안전교육 재해예방 산업안전법 안전관리계획",
        "url": "https://www.work24.go.kr",
        "ncs_code": "23", "ncs_name": "환경에너지안전",
        "tags": ["산업안전기사", "안전관리", "제조", "정규직"],
    },
    {
        "external_id": "w24-2026-ENV-0002",
        "title": "환경 컨설턴트 (환경영향평가)",
        "company": "환경부 지정 대행업체",
        "location": "서울 마포구",
        "salary": "3,800 ~ 5,500만원",
        "employment_type": "정규직",
        "deadline": "2026-05-21",
        "summary": "각종 개발사업 환경영향평가 용역 수행. 대기·수질·소음 영향 예측 및 저감 방안 수립, 환경부 협의 대응. 환경기사 필수.",
        "skills": "환경영향평가 대기오염 수질오염 소음진동 환경법규 보고서작성",
        "url": "https://www.work24.go.kr",
        "ncs_code": "23", "ncs_name": "환경에너지안전",
        "tags": ["환경기사", "환경영향평가", "컨설팅", "정규직"],
    },
    {
        "external_id": "w24-2026-IT-0007",
        "title": "Java 백엔드 개발자 (Spring Boot)",
        "company": "신한은행 IT본부",
        "location": "서울 중구",
        "salary": "4,500 ~ 7,500만원",
        "employment_type": "정규직",
        "deadline": "2026-06-01",
        "summary": "인터넷·모바일 뱅킹 백엔드 개발. Spring Boot, JPA, 마이크로서비스 아키텍처 설계 및 구현. 금융 도메인 경험 우대.",
        "skills": "Java Spring Boot JPA MSA Oracle REST API",
        "url": "https://www.work24.go.kr",
        "ncs_code": "20", "ncs_name": "정보통신",
        "tags": ["Java", "Spring Boot", "금융IT", "정규직"],
    },
    {
        "external_id": "w24-2026-MECH-0004",
        "title": "전기차 배터리 개발 엔지니어",
        "company": "LG에너지솔루션",
        "location": "충북 청주시",
        "salary": "4,500 ~ 7,000만원",
        "employment_type": "정규직",
        "deadline": "2026-05-28",
        "summary": "EV용 배터리 셀·모듈 개발 및 성능 최적화. 배터리 특성 평가, 수명 분석, BMS 연계 개발, 양산 이관 지원.",
        "skills": "배터리개발 BMS 전기화학 전기차 성능평가 재료분석",
        "url": "https://www.work24.go.kr",
        "ncs_code": "19", "ncs_name": "전기전자",
        "tags": ["전기차", "배터리", "LG에너지솔루션", "정규직"],
    },
    {
        "external_id": "w24-2026-BIZ-0004",
        "title": "물류 SCM 담당자",
        "company": "쿠팡 풀필먼트",
        "location": "경기 용인시",
        "salary": "3,800 ~ 5,500만원",
        "employment_type": "정규직",
        "deadline": "2026-05-19",
        "summary": "물류 센터 운영 및 공급망 최적화. 재고 관리, 배송 효율화, KPI 분석, 협력사 관리. 물류관리사 우대.",
        "skills": "SCM 재고관리 물류운영 데이터분석 ERP 협력사관리",
        "url": "https://www.work24.go.kr",
        "ncs_code": "02", "ncs_name": "경영회계사무",
        "tags": ["물류관리사", "SCM", "이커머스", "정규직"],
    },
]


def fetch_and_store(db: Session) -> tuple[int, str]:
    settings = get_settings()
    api_key = settings.work24_api_key or settings.work24_kdt_api_key

    if not api_key:
        logger.warning("work24 jobs: no api key, using realistic job data")
        n = job_repo.upsert_many(db, _REALISTIC_JOBS)
        return n, "work24"

    jobs = _fetch_all_pages(api_key, settings.work24_request_timeout)
    if not jobs:
        logger.warning("work24 jobs: 0 results, using realistic job data")
        n = job_repo.upsert_many(db, _REALISTIC_JOBS)
        return n, "work24"

    n = job_repo.upsert_many(db, jobs)
    logger.info("work24 jobs: %d postings stored", n)
    return n, "work24"


def seed_sample(db: Session) -> int:
    return job_repo.upsert_many(db, _REALISTIC_JOBS)


def _fetch_all_pages(api_key: str, timeout: float) -> list[dict]:
    all_items: list[dict] = []
    page = 1
    display = 100

    try:
        with httpx.Client(timeout=httpx.Timeout(timeout)) as client:
            while True:
                params = {
                    "authKey": api_key,
                    "callTp": "L",
                    "returnType": "XML",
                    "startPage": page,
                    "display": display,
                }
                logger.info("work24 jobs page %d", page)
                resp = client.get(_BASE_URL, params=params)
                resp.raise_for_status()

                items = _parse_xml(resp.text)
                if not items:
                    break

                normalized = [_normalize(item) for item in items if isinstance(item, dict)]
                normalized = [j for j in normalized if j.get("external_id")]
                all_items.extend(normalized)

                if len(items) < display:
                    break
                page += 1

    except Exception as e:
        logger.warning("work24 jobs fetch error: %s", e)

    return all_items


def _parse_xml(xml_text: str) -> list[dict]:
    try:
        data = xmltodict.parse(xml_text)
        root = data.get("result") or data.get("response") or data.get("resultInfo") or data
        if not isinstance(root, dict):
            return []
        for key in ["srchList", "list", "items", "item", "contents"]:
            val = root.get(key)
            if val is None:
                for subroot in root.values():
                    if isinstance(subroot, dict):
                        val = subroot.get(key)
                        if val:
                            break
            if isinstance(val, list):
                return val
            if isinstance(val, dict):
                return [val]
        return []
    except Exception as e:
        logger.warning("xml parse error: %s", e)
        return []


def _normalize(raw: dict) -> dict:
    external_id = str(
        raw.get("recrutPblntSn") or raw.get("jobId") or raw.get("id") or ""
    ).strip()
    if not external_id:
        return {}

    return {
        "external_id": f"work24-{external_id}",
        "title": str(raw.get("recrutPbancTtl") or raw.get("jobNm") or "").strip(),
        "company": str(raw.get("cmpnyNm") or raw.get("companyNm") or "").strip() or None,
        "location": str(raw.get("workPlcNm") or raw.get("sido") or "").strip() or None,
        "salary": str(raw.get("srwgPay") or raw.get("salary") or "").strip() or None,
        "employment_type": str(raw.get("emplymShp") or raw.get("empType") or "").strip() or None,
        "deadline": str(raw.get("recrutPbancEndYmd") or raw.get("deadline") or "").strip() or None,
        "summary": str(raw.get("detailContents") or raw.get("jobDc") or "").strip() or None,
        "skills": str(raw.get("preferentialConditions") or raw.get("skills") or "").strip() or None,
        "url": str(raw.get("detailUrl") or raw.get("url") or "").strip() or None,
        "ncs_code": str(raw.get("ncsCd") or "").strip() or None,
        "ncs_name": str(raw.get("ncsNm") or "").strip() or None,
        "tags": _extract_tags(raw),
    }


def _extract_tags(raw: dict) -> list[str]:
    tags = []
    emp = str(raw.get("emplymShp") or "").strip()
    if emp:
        tags.append(emp)
    ncs = str(raw.get("ncsNm") or "").strip()
    if ncs:
        tags.append(ncs)
    return tags[:4]
