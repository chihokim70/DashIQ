# 📁 AiGov Admin Portal 설계 확장안 (UI 시안 및 DB 스키마)

## ✅ 1. UI 시안 구성안 (기능 중심)

### 📊 대시보드 (/admin/dashboard)
- 오늘 필터링 건수
- 차단된 프롬프트 Top 5
- 차단율 추이 그래프

### 🔐 정책 관리 (/admin/policies)
- [탭1] 금지 키워드 관리
  - 키워드 리스트 (카테고리별 분류)
  - 추가 / 삭제 / 수정
- [탭2] 금지 프롬프트 (벡터 기반)
  - 등록된 프롬프트 리스트
  - 신규 등록 (자동 임베딩)
  - 유사도 기반 검색 테스트

### 🔍 로그 조회 (/admin/logs)
- 프롬프트 요청 로그 테이블
- 검색 필터: 날짜, 차단 여부, 키워드/벡터 사유
- Kibana 연동: [Kibana로 열기] 버튼 지원

### ⚙️ 설정 관리 (/admin/settings)
- 차단 모드: 경고 / 완전 차단
- score_threshold 설정 (ex. 0.75)
- Rebuff 사용 여부 On/Off

---

## ✅ 2. 관리자용 DB 스키마 초안 (PostgreSQL 기준)

### 🔹 blocked_keywords (정책 키워드 테이블)
```sql
CREATE TABLE blocked_keywords (
    id SERIAL PRIMARY KEY,
    keyword TEXT NOT NULL,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT now(),
    created_by VARCHAR(50)
);
```

### 🔹 vector_prompts (정책 벡터 프롬프트 테이블)
```sql
CREATE TABLE vector_prompts (
    id SERIAL PRIMARY KEY,
    prompt TEXT NOT NULL,
    embedding FLOAT8[],
    category VARCHAR(50),
    score_threshold FLOAT DEFAULT 0.75,
    created_at TIMESTAMP DEFAULT now(),
    created_by VARCHAR(50)
);
```

### 🔹 prompt_logs (필터링 로그 저장)
※ 실제 저장은 Elasticsearch, 백업용 또는 통계용으로 PostgreSQL에 일부 기록 가능
```sql
CREATE TABLE prompt_logs (
    id SERIAL PRIMARY KEY,
    prompt TEXT,
    is_blocked BOOLEAN,
    reason TEXT,
    source VARCHAR(20),
    created_at TIMESTAMP DEFAULT now()
);
```

---

## ✅ 향후 확장 고려 사항
- 사용자 테이블: `admin_users` (RBAC)
- 조직별 정책 구분을 위한 `organization_id` 필드 추가
- 정책 변경 이력 테이블 `policy_history`

---

필요 시 이 구조를 Figma/Whimsical 스타일 화면 흐름도나 OpenAPI 스펙으로 확장 가능합니다.
