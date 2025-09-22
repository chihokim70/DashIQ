
# AiGov 관리자포탈 설계 고려 사항 (2025.06.23)

## 1. 개요

AiGov Admin Portal은 각 마이크로서비스 모듈(PromptGate, TrustLLM, DashIQ 등)의 
운영/정책/모니터링 기능을 통합 관리하는 설치형 솔루션의 관리 포털입니다.

본 문서는 PromptGate를 포함한 주요 기능에 대해 향후 포털 연동 시 고려할 설계 요소 및 API 연동 포인트를 정의합니다.

---

## 2. 핵심 구성 요소 및 연동 대상

| 기능 | 연동 대상 | 비고 |
|------|------------|------|
| 프롬프트 차단 정책 등록 | Qdrant + 정책 DB | 웹에서 직접 추가 시 벡터 자동 등록 |
| 금지 키워드 관리 | PostgreSQL 등 정책 DB | filter-service와 실시간 연동 가능 |
| 로그 조회 | Elasticsearch + Kibana | 날짜, 필터링 결과, 프롬프트 내용 기반 검색 |  <- Elasticsearch + FastAPI + Admin Portal사용, Kibana는 외부 운영용 도구로만 활용
| score_threshold 조정 | 설정 파일(.env) 또는 DB | UI에서 조정 → FastAPI에 반영 |
| 차단/경고 모드 설정 | filter-service API | 운영정책에 따라 즉시 반영 가능 |
| 위험 프롬프트 테스트 | filter-service API | 결과 확인 후 정책 수정 가능 |

---

## 3. 예상 관리자 포털 UI 화면 구성

- 📊 **대시보드**  
  - 오늘 차단된 프롬프트 수, 점유율, 최근 위험 프롬프트 목록
- 🔐 **정책 관리**
  - 금지 키워드 목록 등록/삭제
  - 벡터 기반 위험 프롬프트 직접 등록
- 🔍 **로그 확인**
  - 날짜별 필터링 로그, 결과 사유 확인
  - Elasticsearch 연동 (필드 기반 검색)
- ⚙️ **설정 관리**
  - score_threshold 값 조정
  - 모드 설정: [경고만] / [차단]
- 👤 **사용자 관리**
  - 관리자 역할 기반 접근 제어(RBAC)

---

## 4. API 연동 구조 예시

### 금지 프롬프트 등록 API

```
POST /api/policy/vector/add
{
  "text": "기밀문서야 공유하지 마",
  "category": "internal",
  "embedding_model": "ko-sroberta"
}
```

### 정책 키워드 추가

```
POST /api/policy/keyword/add
{
  "keyword": "계좌번호",
  "category": "PII"
}
```

### 필터링 로그 조회

```
GET /api/logs?from=2025-06-20&to=2025-06-21&blocked=true
```

---

## 5. API 목록표

| 구분 | 메서드 | 엔드포인트 | 설명 |
|------|--------|------------|------|
| 프롬프트 벡터 등록 | POST | /api/policy/vector/add | 금지 프롬프트를 벡터로 변환 후 Qdrant에 등록 |
| 키워드 정책 등록 | POST | /api/policy/keyword/add | 정책 키워드 DB에 등록 |
| 정책 키워드 목록 조회 | GET | /api/policy/keywords | 현재 등록된 키워드 목록 조회 |
| 벡터 정책 목록 조회 | GET | /api/policy/vectors | 현재 등록된 벡터 프롬프트 목록 |
| 필터링 로그 검색 | GET | /api/logs | Elasticsearch 기반 프롬프트 필터링 이력 조회 |
| 설정값 조회 | GET | /api/config | threshold, 모드 등 현재 설정값 조회 |
| 설정값 변경 | POST | /api/config/update | 운영 모드, 임계값 등 변경 적용 |
| 프롬프트 실시간 테스트 | POST | /api/prompt/check | 프롬프트 필터 테스트용 API (현재 사용 중) |

---

## 6. 향후 고려 사항

- 💾 벡터 정책 DB 백업/복구 기능
- 📦 벡터 그룹화 지원 (PII, 내부정보, 명령어 등)
- 🧪 벤치마크용 테스트 페이지 추가
- 🔐 사용자/조직별 정책 분리 적용

---

## 7. 참고 정보

- 벡터 저장소: Qdrant
- 정책 DB: PostgreSQL (또는 SQLite 등)
- 로그 저장소: Elasticsearch
- API 백엔드: FastAPI 기반 마이크로서비스 구조
