"""Work24 채용정보 API 클라이언트.

샘플 데이터는 실제 기업명 대신 일반적인 업종명·가상 기업명을 사용합니다.
실데이터는 Work24 API에서 직접 가져옵니다.
"""
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

# 가상 기업명 사용 (실제 기업명 저작권·명예훼손 이슈 방지)
_REALISTIC_JOBS: list[dict] = [
    {
        "external_id": "w24-2026-IT-0001",
        "title": "Python 백엔드 개발자 (신입/경력)",
        "company": "IT 솔루션 기업",
        "location": "서울 강남구",
        "salary": "4,000 ~ 7,000만원 (협의)",
        "employment_type": "정규직",
        "deadline": "2026-06-30",
        "summary": "클라우드 기반 백엔드 서비스 개발. Python/FastAPI 기반 REST API 설계 및 구현, PostgreSQL·Redis 운용, Docker/K8s 환경에서의 서비스 개발.",
        "skills": "Python FastAPI PostgreSQL Redis Docker Kubernetes AWS",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=Python+백엔드+개발자",
        "ncs_code": "20", "ncs_name": "정보통신",
        "tags": ["백엔드", "Python", "클라우드", "정규직"],
    },
    {
        "external_id": "w24-2026-IT-0002",
        "title": "AI/ML 엔지니어",
        "company": "AI 전문 기업",
        "location": "경기 성남시 분당구",
        "salary": "5,000 ~ 9,000만원",
        "employment_type": "정규직",
        "deadline": "2026-06-15",
        "summary": "LLM 파인튜닝, RAG 파이프라인 구축, 대규모 데이터 처리 인프라 설계. AI 서비스 개발 및 성능 최적화.",
        "skills": "PyTorch LLM RAG Python MLOps GPU클러스터",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=AI+ML+엔지니어",
        "ncs_code": "20", "ncs_name": "정보통신",
        "tags": ["AI", "ML", "LLM", "정규직"],
    },
    {
        "external_id": "w24-2026-IT-0003",
        "title": "데이터 엔지니어",
        "company": "핀테크 기업",
        "location": "서울 강남구",
        "salary": "4,500 ~ 8,000만원",
        "employment_type": "정규직",
        "deadline": "2026-06-22",
        "summary": "금융 데이터 파이프라인 설계·구축·운영. Spark/Kafka 기반 실시간 데이터 처리, 데이터 레이크하우스 아키텍처 설계.",
        "skills": "Spark Kafka Airflow Python SQL Hadoop AWS",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=데이터+엔지니어",
        "ncs_code": "20", "ncs_name": "정보통신",
        "tags": ["데이터엔지니어링", "Spark", "핀테크", "정규직"],
    },
    {
        "external_id": "w24-2026-IT-0004",
        "title": "클라우드 인프라 엔지니어 (DevOps)",
        "company": "IT 서비스 기업",
        "location": "서울 강남구",
        "salary": "5,000 ~ 8,500만원",
        "employment_type": "정규직",
        "deadline": "2026-07-07",
        "summary": "글로벌 서비스를 지원하는 클라우드 인프라 구축·운영. Kubernetes 클러스터 관리, CI/CD 파이프라인 구축.",
        "skills": "Kubernetes AWS GCP Terraform Ansible Prometheus Grafana",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=클라우드+인프라+엔지니어",
        "ncs_code": "20", "ncs_name": "정보통신",
        "tags": ["DevOps", "클라우드", "인프라", "정규직"],
    },
    {
        "external_id": "w24-2026-IT-0005",
        "title": "정보보안 전문가 (보안 관제·분석)",
        "company": "보안 솔루션 기업",
        "location": "서울 중구",
        "salary": "3,500 ~ 6,000만원",
        "employment_type": "정규직",
        "deadline": "2026-06-30",
        "summary": "기업 고객 대상 보안 관제 및 침해사고 대응. 취약점 분석, 모의해킹, 보안 컨설팅. 정보보안기사 소지자 우대.",
        "skills": "보안관제 침투테스트 SIEM 포렌식 취약점분석 KaliLinux",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=정보보안+전문가",
        "ncs_code": "20", "ncs_name": "정보통신",
        "tags": ["보안", "정보보안기사", "관제", "정규직"],
    },
    {
        "external_id": "w24-2026-IT-0006",
        "title": "React 프론트엔드 개발자",
        "company": "이커머스 플랫폼 기업",
        "location": "서울 성동구",
        "salary": "4,000 ~ 7,000만원",
        "employment_type": "정규직",
        "deadline": "2026-06-25",
        "summary": "React 기반 웹·모바일 서비스 개발. TypeScript, Next.js 활용 서비스 구현, 성능 최적화, 사용자 경험 개선.",
        "skills": "React TypeScript Next.js GraphQL CSS-in-JS",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=React+프론트엔드",
        "ncs_code": "20", "ncs_name": "정보통신",
        "tags": ["프론트엔드", "React", "TypeScript", "정규직"],
    },
    {
        "external_id": "w24-2026-IT-0007",
        "title": "Java 백엔드 개발자 (Spring Boot)",
        "company": "금융 IT 기업",
        "location": "서울 중구",
        "salary": "4,500 ~ 7,500만원",
        "employment_type": "정규직",
        "deadline": "2026-07-01",
        "summary": "인터넷·모바일 뱅킹 백엔드 개발. Spring Boot, JPA, 마이크로서비스 아키텍처 설계 및 구현.",
        "skills": "Java SpringBoot JPA MSA Oracle RESTAPI",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=Java+백엔드+Spring",
        "ncs_code": "20", "ncs_name": "정보통신",
        "tags": ["Java", "SpringBoot", "금융IT", "정규직"],
    },
    {
        "external_id": "w24-2026-IT-0008",
        "title": "iOS 앱 개발자 (Swift/SwiftUI)",
        "company": "모바일 서비스 기업",
        "location": "경기 성남시 분당구",
        "salary": "5,000 ~ 8,000만원",
        "employment_type": "정규직",
        "deadline": "2026-06-30",
        "summary": "금융 서비스 iOS 앱 개발 및 유지보수. SwiftUI 기반 UI 구현, 결제·인증 모듈 개발.",
        "skills": "Swift SwiftUI Combine UIKit CoreData Firebase",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=iOS+앱+개발자",
        "ncs_code": "20", "ncs_name": "정보통신",
        "tags": ["iOS", "Swift", "모바일", "정규직"],
    },
    {
        "external_id": "w24-2026-IT-0009",
        "title": "게임 서버 개발자 (C++/Go)",
        "company": "게임 개발사",
        "location": "서울 강남구",
        "salary": "5,000 ~ 9,000만원",
        "employment_type": "정규직",
        "deadline": "2026-07-15",
        "summary": "글로벌 멀티플레이어 게임 서버 개발 및 운영. 고성능 서버 아키텍처 설계, 실시간 매칭 시스템 구현.",
        "skills": "C++ Go gRPC Redis Kubernetes 분산시스템",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=게임+서버+개발자",
        "ncs_code": "20", "ncs_name": "정보통신",
        "tags": ["게임서버", "C++", "Go", "정규직"],
    },
    {
        "external_id": "w24-2026-IT-0010",
        "title": "데이터 사이언티스트",
        "company": "소셜 미디어 기업",
        "location": "서울 강남구",
        "salary": "5,000 ~ 8,500만원",
        "employment_type": "정규직",
        "deadline": "2026-06-28",
        "summary": "실시간 추천·매칭 알고리즘 개발. 사용자 행동 분석, A/B 테스트 설계, 머신러닝 모델 프로덕션 배포.",
        "skills": "Python PyTorch 통계분석 A/B테스트 추천시스템 MLOps",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=데이터+사이언티스트",
        "ncs_code": "20", "ncs_name": "정보통신",
        "tags": ["데이터사이언스", "ML", "추천시스템", "정규직"],
    },
    {
        "external_id": "w24-2026-ELEC-0001",
        "title": "전기 설비 설계 엔지니어",
        "company": "전력 설비 전문 기업",
        "location": "전남 나주시",
        "salary": "4,000 ~ 5,500만원",
        "employment_type": "정규직",
        "deadline": "2026-06-20",
        "summary": "배전 설비 설계 및 시공 감리. 전기기사 이상 자격 필수. 변전소·배전선로 신설 및 개량 공사 설계.",
        "skills": "전기설비설계 배전계통 AutoCAD 전력공학 시공관리",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=전기+설비+설계",
        "ncs_code": "19", "ncs_name": "전기전자",
        "tags": ["전기기사", "설비설계", "정규직"],
    },
    {
        "external_id": "w24-2026-ELEC-0002",
        "title": "반도체 공정 엔지니어 (PE)",
        "company": "반도체 제조 기업",
        "location": "경기 화성시",
        "salary": "4,500 ~ 7,000만원",
        "employment_type": "정규직",
        "deadline": "2026-06-31",
        "summary": "반도체 메모리 공정 개발 및 수율 개선. 포토·식각·증착 공정 최적화, 불량 분석.",
        "skills": "반도체공정 포토리소그래피 CVD 식각 수율분석 SEM",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=반도체+공정+엔지니어",
        "ncs_code": "19", "ncs_name": "전기전자",
        "tags": ["반도체", "공정엔지니어", "정규직"],
    },
    {
        "external_id": "w24-2026-ELEC-0003",
        "title": "PLC 자동화 제어 엔지니어",
        "company": "스마트팩토리 솔루션 기업",
        "location": "울산 동구",
        "salary": "3,800 ~ 5,500만원",
        "employment_type": "정규직",
        "deadline": "2026-06-16",
        "summary": "스마트팩토리 PLC 프로그래밍 및 자동화 라인 구축. PLC 설계, HMI 개발, 현장 시운전 및 유지보수.",
        "skills": "PLC HMI 인버터 자동화 SCADA Siemens LS산전",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=PLC+자동화+엔지니어",
        "ncs_code": "19", "ncs_name": "전기전자",
        "tags": ["PLC", "자동화", "스마트팩토리", "정규직"],
    },
    {
        "external_id": "w24-2026-ELEC-0004",
        "title": "배터리 팩 설계 엔지니어",
        "company": "이차전지 제조 기업",
        "location": "경기 수원시",
        "salary": "4,500 ~ 7,000만원",
        "employment_type": "정규직",
        "deadline": "2026-07-10",
        "summary": "EV·ESS용 배터리 팩 구조 설계. BMS 연동, 냉각 시스템 설계, 안전 규격 인증, 양산 이관 지원.",
        "skills": "배터리팩설계 BMS 열관리 CAD 안전인증 CATIA",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=배터리+팩+설계",
        "ncs_code": "19", "ncs_name": "전기전자",
        "tags": ["배터리", "EV", "이차전지", "정규직"],
    },
    {
        "external_id": "w24-2026-MECH-0001",
        "title": "CNC 정밀 가공 기술자",
        "company": "자동차 부품 제조사",
        "location": "경남 창원시",
        "salary": "3,200 ~ 4,500만원",
        "employment_type": "정규직",
        "deadline": "2026-06-12",
        "summary": "자동차 부품 CNC 선반·밀링 가공. G-code 프로그래밍, 공구 선정, 치수 측정 및 품질 관리. 기계가공기능사 이상 우대.",
        "skills": "CNC선반 CNC밀링 G-code 정밀측정 도면해독 품질관리",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=CNC+정밀+가공",
        "ncs_code": "15", "ncs_name": "기계",
        "tags": ["CNC", "기계가공", "자동차부품", "정규직"],
    },
    {
        "external_id": "w24-2026-MECH-0002",
        "title": "산업용 로봇 시스템 엔지니어",
        "company": "로봇 자동화 기업",
        "location": "대구 달서구",
        "salary": "4,000 ~ 6,500만원",
        "employment_type": "정규직",
        "deadline": "2026-07-05",
        "summary": "산업용 로봇 시스템 설계 및 구축. 로봇 티칭, 그리퍼 설계, 비전 시스템 통합, 시운전 지원.",
        "skills": "산업용로봇 로봇티칭 비전시스템 PLC 기구설계 CAD",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=산업용+로봇+엔지니어",
        "ncs_code": "15", "ncs_name": "기계",
        "tags": ["로봇", "자동화", "기계설계", "정규직"],
    },
    {
        "external_id": "w24-2026-MECH-0003",
        "title": "특수 용접사 (TIG·MIG)",
        "company": "조선·해양 플랜트 기업",
        "location": "울산 동구",
        "salary": "3,500 ~ 5,000만원",
        "employment_type": "정규직",
        "deadline": "2026-06-08",
        "summary": "LNG 운반선·해양플랜트 구조물 특수 용접. TIG·MIG 용접, 스테인리스·알루미늄 재질 용접. 특수용접기능사 이상 필수.",
        "skills": "TIG용접 MIG용접 스테인리스 알루미늄 비파괴검사 도면해독",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=특수+용접사",
        "ncs_code": "15", "ncs_name": "기계",
        "tags": ["특수용접", "TIG", "조선", "정규직"],
    },
    {
        "external_id": "w24-2026-MECH-0004",
        "title": "전기차 배터리 개발 엔지니어",
        "company": "친환경차 부품 기업",
        "location": "충북 청주시",
        "salary": "4,500 ~ 7,000만원",
        "employment_type": "정규직",
        "deadline": "2026-06-28",
        "summary": "EV용 배터리 셀·모듈 개발 및 성능 최적화. 배터리 특성 평가, 수명 분석, BMS 연계 개발.",
        "skills": "배터리개발 BMS 전기화학 전기차 성능평가 재료분석",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=전기차+배터리+개발",
        "ncs_code": "19", "ncs_name": "전기전자",
        "tags": ["전기차", "배터리", "친환경차", "정규직"],
    },
    {
        "external_id": "w24-2026-CON-0001",
        "title": "건축 BIM 설계사",
        "company": "종합 건설사",
        "location": "서울 서초구",
        "salary": "4,000 ~ 6,500만원",
        "employment_type": "정규직",
        "deadline": "2026-06-29",
        "summary": "초고층·대형 건축물 BIM 기반 설계. Revit을 활용한 3D 모델링, 설계 도서 작성, 다분야 협업 조율.",
        "skills": "Revit BIM AutoCAD Navisworks 건축설계 도면작성",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=건축+BIM+설계",
        "ncs_code": "14", "ncs_name": "건설",
        "tags": ["BIM", "건축설계", "Revit", "정규직"],
    },
    {
        "external_id": "w24-2026-CON-0002",
        "title": "토목 현장 소장 (경력)",
        "company": "종합 건설사",
        "location": "인천 서구",
        "salary": "5,000 ~ 7,500만원",
        "employment_type": "정규직",
        "deadline": "2026-06-18",
        "summary": "도로·교량·터널 등 토목 현장 전반 관리. 공정·품질·안전 관리, 발주처 협의. 토목기사 필수.",
        "skills": "토목시공 공정관리 품질관리 안전관리 원가관리",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=토목+현장소장",
        "ncs_code": "14", "ncs_name": "건설",
        "tags": ["토목기사", "현장관리", "건설", "정규직"],
    },
    {
        "external_id": "w24-2026-CON-0003",
        "title": "소방 설비 설계 엔지니어",
        "company": "소방 설비 전문 기업",
        "location": "서울 구로구",
        "salary": "3,500 ~ 5,000만원",
        "employment_type": "정규직",
        "deadline": "2026-06-10",
        "summary": "소방 시스템 설계·시공 감리. 소화설비·경보설비·피난설비 설계, 소방법규 검토. 소방설비기사 필수.",
        "skills": "소방설비설계 소화설비 경보설비 도면작성 소방법규 AutoCAD",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=소방+설비+설계",
        "ncs_code": "14", "ncs_name": "건설",
        "tags": ["소방설비기사", "소방설계", "정규직"],
    },
    {
        "external_id": "w24-2026-BIZ-0001",
        "title": "회계·세무 담당자",
        "company": "대기업 계열사",
        "location": "서울 강동구",
        "salary": "3,500 ~ 5,000만원",
        "employment_type": "정규직",
        "deadline": "2026-06-23",
        "summary": "법인세·부가세 신고, 월별 결산, 재무제표 작성, 세무조사 대응. ERP(SAP) 활용. 전산세무 1급 또는 공인회계사 우대.",
        "skills": "SAP ERP 세무신고 결산 재무제표 부가세 법인세",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=회계+세무+담당자",
        "ncs_code": "02", "ncs_name": "경영회계사무",
        "tags": ["회계", "세무", "SAP", "정규직"],
    },
    {
        "external_id": "w24-2026-BIZ-0002",
        "title": "인사·노무 담당자 (경력 2년↑)",
        "company": "식품 대기업",
        "location": "서울 중구",
        "salary": "4,000 ~ 5,500만원",
        "employment_type": "정규직",
        "deadline": "2026-06-17",
        "summary": "채용·급여·4대보험·노무관리 전반. 취업규칙 운영, 노사관계 지원, HR 시스템 운영. 노무사 자격 우대.",
        "skills": "HR 급여계산 4대보험 채용 노무관리 SAP HCM",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=인사+노무+담당자",
        "ncs_code": "02", "ncs_name": "경영회계사무",
        "tags": ["인사", "노무", "HR", "정규직"],
    },
    {
        "external_id": "w24-2026-BIZ-0003",
        "title": "디지털 마케터 (퍼포먼스)",
        "company": "패션 플랫폼 기업",
        "location": "서울 성동구",
        "salary": "3,500 ~ 5,500만원",
        "employment_type": "정규직",
        "deadline": "2026-06-27",
        "summary": "SNS 광고 집행 및 성과 분석. 메타·구글·카카오 광고 운영, ROAS 최적화, CRM 마케팅.",
        "skills": "퍼포먼스마케팅 Meta광고 Google광고 GA4 SQL 데이터분석",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=디지털+마케터",
        "ncs_code": "02", "ncs_name": "경영회계사무",
        "tags": ["마케팅", "SNS광고", "퍼포먼스", "정규직"],
    },
    {
        "external_id": "w24-2026-BIZ-0004",
        "title": "물류 SCM 담당자",
        "company": "이커머스 물류 기업",
        "location": "경기 용인시",
        "salary": "3,800 ~ 5,500만원",
        "employment_type": "정규직",
        "deadline": "2026-06-19",
        "summary": "물류 센터 운영 및 공급망 최적화. 재고 관리, 배송 효율화, KPI 분석, 협력사 관리. 물류관리사 우대.",
        "skills": "SCM 재고관리 물류운영 데이터분석 ERP 협력사관리",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=물류+SCM+담당자",
        "ncs_code": "02", "ncs_name": "경영회계사무",
        "tags": ["물류관리사", "SCM", "이커머스", "정규직"],
    },
    {
        "external_id": "w24-2026-FOOD-0001",
        "title": "식품 품질관리 연구원 (QC)",
        "company": "식품 제조 기업",
        "location": "경기 수원시",
        "salary": "3,500 ~ 5,000만원",
        "employment_type": "정규직",
        "deadline": "2026-06-14",
        "summary": "식품 원료·완제품 품질 검사 및 규격 관리. 미생물 검사, 이화학 분석, HACCP 운영. 식품기사 우대.",
        "skills": "식품품질관리 미생물검사 HACCP GMP 이화학분석 식품법규",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=식품+품질관리+QC",
        "ncs_code": "21", "ncs_name": "식품가공",
        "tags": ["식품기사", "QC", "HACCP", "정규직"],
    },
    {
        "external_id": "w24-2026-FOOD-0002",
        "title": "바리스타 & 카페 매니저",
        "company": "프랜차이즈 카페",
        "location": "서울 전 지점",
        "salary": "2,800 ~ 3,500만원",
        "employment_type": "정규직",
        "deadline": "2026-06-30",
        "summary": "카페 파트너(바리스타) 정규직 채용. 음료 제조, 고객 서비스, 재고 관리, 신입 교육. 바리스타 자격증 우대.",
        "skills": "에스프레소 라떼아트 고객서비스 재고관리 팀워크",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=바리스타+카페+매니저",
        "ncs_code": "13", "ncs_name": "음식서비스",
        "tags": ["바리스타", "카페", "정규직"],
    },
    {
        "external_id": "w24-2026-FOOD-0003",
        "title": "호텔 조리사 (한식·양식)",
        "company": "특급 호텔",
        "location": "서울 중구",
        "salary": "3,000 ~ 4,500만원",
        "employment_type": "정규직",
        "deadline": "2026-06-22",
        "summary": "5성급 호텔 레스토랑 한식·양식 조리. 메뉴 개발 참여, 위생 관리, 식재료 원가 절감, 연회 조리 지원.",
        "skills": "한식조리 양식조리 위생관리 메뉴개발 식재료관리 연회",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=호텔+조리사",
        "ncs_code": "13", "ncs_name": "음식서비스",
        "tags": ["호텔조리사", "한식", "양식", "정규직"],
    },
    {
        "external_id": "w24-2026-HEALTH-0001",
        "title": "사회복지사 (지역아동센터)",
        "company": "사회복지법인",
        "location": "서울 노원구",
        "salary": "2,800 ~ 3,500만원",
        "employment_type": "정규직",
        "deadline": "2026-06-09",
        "summary": "지역아동센터 아동·청소년 사례관리 및 프로그램 운영. 방과후 교육 지원, 가족 상담. 사회복지사 2급 필수.",
        "skills": "사례관리 아동복지 상담 지역사회조직 프로그램기획",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=사회복지사+지역아동센터",
        "ncs_code": "07", "ncs_name": "사회복지종교",
        "tags": ["사회복지사", "아동복지", "사례관리", "정규직"],
    },
    {
        "external_id": "w24-2026-HEALTH-0002",
        "title": "의료기기 RA/QA 담당자",
        "company": "의료기기 전문 기업",
        "location": "서울 강서구",
        "salary": "3,500 ~ 5,500만원",
        "employment_type": "정규직",
        "deadline": "2026-06-26",
        "summary": "의료기기 국내외 인허가 등록·변경·갱신. FDA, CE, KFDA 인허가 문서 작성, 품질 시스템(ISO 13485) 운영.",
        "skills": "의료기기RA QA ISO13485 GMP 인허가 FDA CE",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=의료기기+RA+QA",
        "ncs_code": "06", "ncs_name": "보건의료",
        "tags": ["의료기기", "RA", "QA", "정규직"],
    },
    {
        "external_id": "w24-2026-ENV-0001",
        "title": "산업 안전관리자 (제조업)",
        "company": "철강 제조 기업",
        "location": "경북 포항시",
        "salary": "4,000 ~ 5,800만원",
        "employment_type": "정규직",
        "deadline": "2026-06-13",
        "summary": "제조 현장 안전 관리 계획 수립·이행. 위험성평가, 안전교육, 사고조사. 산업안전기사 필수.",
        "skills": "위험성평가 안전교육 재해예방 산업안전법 안전관리계획",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=산업+안전관리자",
        "ncs_code": "23", "ncs_name": "환경에너지안전",
        "tags": ["산업안전기사", "안전관리", "제조", "정규직"],
    },
    {
        "external_id": "w24-2026-ENV-0002",
        "title": "환경 컨설턴트 (환경영향평가)",
        "company": "환경 컨설팅 기업",
        "location": "서울 마포구",
        "salary": "3,800 ~ 5,500만원",
        "employment_type": "정규직",
        "deadline": "2026-06-21",
        "summary": "각종 개발사업 환경영향평가 용역 수행. 대기·수질·소음 영향 예측 및 저감 방안 수립. 환경기사 필수.",
        "skills": "환경영향평가 대기오염 수질오염 소음진동 환경법규 보고서작성",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=환경+컨설턴트",
        "ncs_code": "23", "ncs_name": "환경에너지안전",
        "tags": ["환경기사", "환경영향평가", "컨설팅", "정규직"],
    },
    {
        "external_id": "w24-2026-DESIGN-0001",
        "title": "브랜드 디자이너",
        "company": "IT 플랫폼 기업",
        "location": "서울 강남구",
        "salary": "4,500 ~ 7,500만원",
        "employment_type": "정규직",
        "deadline": "2026-07-08",
        "summary": "브랜드 아이덴티티 설계 및 마케팅 디자인. 캠페인 비주얼 디렉션, 모션 그래픽, 브랜드 가이드라인 관리.",
        "skills": "Figma Illustrator AfterEffects 브랜딩 타이포그래피 모션그래픽",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=브랜드+디자이너",
        "ncs_code": "08", "ncs_name": "문화예술디자인방송",
        "tags": ["브랜드디자인", "모션그래픽", "정규직"],
    },
    {
        "external_id": "w24-2026-DESIGN-0002",
        "title": "영상 PD (유튜브·숏폼)",
        "company": "미디어 콘텐츠 기업",
        "location": "서울 마포구",
        "salary": "3,500 ~ 5,500만원",
        "employment_type": "정규직",
        "deadline": "2026-06-29",
        "summary": "디지털 미디어 채널 영상 기획·제작·편집. 유튜브·틱톡·릴스 숏폼 콘텐츠 제작, 후반 작업 지휘.",
        "skills": "영상기획 PremiereP ro AfterEffects 콘텐츠전략 유튜브 숏폼",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=영상PD+유튜브",
        "ncs_code": "08", "ncs_name": "문화예술디자인방송",
        "tags": ["영상PD", "유튜브", "숏폼", "정규직"],
    },
    {
        "external_id": "w24-2026-AGRI-0001",
        "title": "스마트팜 운영 기사",
        "company": "스마트팜 전문 기업",
        "location": "경북 상주시",
        "salary": "3,200 ~ 4,500만원",
        "employment_type": "정규직",
        "deadline": "2026-06-20",
        "summary": "ICT 기반 스마트 온실 환경 제어·데이터 분석·작물 생산 관리. 자동화 시스템 모니터링, 생산성 향상 제안.",
        "skills": "스마트팜 온실제어 IoT 데이터분석 작물재배 환경제어",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=스마트팜+운영",
        "ncs_code": "24", "ncs_name": "농림어업",
        "tags": ["스마트팜", "IoT", "농업", "정규직"],
    },
]


def fetch_and_store(db: Session) -> tuple[int, str]:
    """Work24 채용정보를 가져와 DB에 저장. 실패하면 가상 기업 샘플 fallback."""
    settings = get_settings()
    api_key = settings.work24_api_key or settings.work24_kdt_api_key

    if not api_key:
        logger.warning("work24 jobs: no api key, using sample data")
        n = job_repo.upsert_many(db, _REALISTIC_JOBS)
        return n, "work24"

    jobs = _fetch_all_pages(api_key, settings.work24_request_timeout)
    if not jobs:
        logger.warning("work24 jobs: 0 results, using sample data")
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
