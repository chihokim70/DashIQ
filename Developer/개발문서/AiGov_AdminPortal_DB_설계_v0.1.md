# 📘 AiGov Admin Portal DB 상세 설계 (v0.1 Draft)
> 대상 모듈: **Shadow AI 탐지**, **Policies(OPA/Filters)**, **Internal LLM**, **Tenants & Access**, **Audit/Alerts/Settings**  
> 목표: 멀티테넌트, 감사가능성, 정책 버저닝/카나리, 고가용성/성능(파티셔닝·인덱스) 고려한 **초안 스키마** 제시

---

## 0) 공통 원칙
- **멀티테넌트**: 모든 주요 테이블에 `tenant_id` 포함(전역 테이블 제외)
- **감사 추적**: `created_by, created_at, updated_by, updated_at`, 중요 테이블은 `version`, `change_reason`
- **소프트 삭제**: `deleted_at` (필요 테이블만)
- **키 규칙**: PK는 `bigserial`(Postgres) 혹은 UUID, FK는 `ON DELETE RESTRICT` 기본
- **인덱스 규칙**: `tenant_id` + 자주 조회되는 열에 복합 인덱스
- **시간계열**: 대용량 로그는 **파티셔닝**(`yyyy_mm`), 압축/보존 주기 명시
- **레퍼런스 데이터**: enum은 **체크 제약** 또는 **lookup 테이블**

---

## 1) 테넌트/계정/권한 (Tenants & Access)

### 1.1 tenants
- 테넌트 기본 정보/정책(데이터 지역, 보존기간, 암호화 정책)
```
id (PK, bigserial)
name (text, unique)
code (text, unique, slug)
region (text) -- e.g., ap-northeast-2
data_retention_days (int, default 365)
encryption_profile (text)
status (enum: active|suspended)
created_at, created_by, updated_at, updated_by
```

### 1.2 users
```
id (PK)
tenant_id (FK -> tenants.id, index)
email (text, unique within tenant)
display_name (text)
status (enum: active|inactive|invited|blocked)
auth_provider (enum: local|sso)
created_at, updated_at, last_login_at
```

### 1.3 roles
```
id (PK)
tenant_id (FK, nullable for global roles)
name (text) -- Org Admin, SecOps, MLOps, Auditor ...
scope (enum: global|tenant)
unique(tenant_id, name)
```

### 1.4 user_roles (매핑)
```
user_id (FK -> users.id)
role_id (FK -> roles.id)
tenant_id (FK -> tenants.id)
assigned_by, assigned_at
PK (user_id, role_id, tenant_id)
```

### 1.5 api_tokens
```
id (PK)
tenant_id (FK)
user_id (FK)
name (text)
scopes (text[]) -- ['policies:write','logs:read']
hash (text) -- 토큰 해시 저장
expires_at (timestamptz)
created_at, revoked_at
index(tenant_id, user_id, expires_at)
```

### 1.6 sso_identities
```
id (PK)
tenant_id (FK)
user_id (FK)
provider (text) -- 'okta','azuread'
subject (text) -- 외부ID(SUB), unique per provider
linked_at, last_seen_at
unique(tenant_id, provider, subject)
```

---

## 2) 정책(OPA/Filters) & 번들

### 2.1 policy_bundles (버전/채널/서명)
```
id (PK)
tenant_id (FK, nullable for global bundle)
name (text) -- 'promptgate-default'
version (text) -- '1.4.2'
channel (enum: draft|staging|canary|prod)
signed_digest (text) -- cosign 서명값/다이제스트
status (enum: active|archived)
notes (text)
created_by, created_at, published_at, rolled_back_from (nullable)
unique(tenant_id, name, version)
index(tenant_id, channel, status)
```

### 2.2 filter_rules (정적/시크릿/PII/Rebuff/ML/Embedding)
```
id (PK)
bundle_id (FK -> policy_bundles.id, index)
tenant_id (FK -> tenants.id, index)
type (enum: static|secret|pii|rebuff|ml|embedding)
pattern (text) -- regex or descriptor
threshold (numeric, nullable) -- e.g., entropy/score
action (enum: block|redact|require_approval|log_only)
context (jsonb) -- 세부옵션: fields, languages, weight...
enabled (bool, default true)
created_by, created_at, updated_by, updated_at, change_reason
```

### 2.3 allowlists / blocklists
```
id (PK)
bundle_id (FK)
tenant_id (FK)
kind (enum: domain|pattern|user|path|keyprefix)
value (text)
scope (text) -- e.g., 'finance', '*' 
expire_at (timestamptz, nullable)
note (text)
unique(bundle_id, kind, value, scope)
index(tenant_id, kind, expire_at)
```

### 2.4 approval_rules (승인 기준)
```
id (PK)
bundle_id (FK)
tenant_id (FK)
criteria (jsonb) -- risk_score>=70 AND role!=admin ...
approver_group (text) -- 'sec-team'
valid_days (int) -- 승인 유효기간
enabled (bool)
created_at, created_by, updated_at
```

### 2.5 bundle_artifacts (Rego/데이터 파일)
```
id (PK)
bundle_id (FK)
path (text) -- 'promptgate/allow.rego'
sha256 (text)
size_bytes (bigint)
storage_url (text) -- OCI or HTTPS
created_at
unique(bundle_id, path)
```

### 2.6 policy_changes (감사용 diff)
```
id (PK)
bundle_id (FK)
diff (text) -- unified diff or JSONPatch
submitted_by, submitted_at
approved_by, approved_at
status (enum: draft|submitted|approved|rejected)
```

---

## 3) Shadow AI 탐지 모듈

### 3.1 shadow_agents (미인가 LLM/에이전트/앱 식별)
```
id (PK)
tenant_id (FK)
name (text)
type (enum: webapp|desktop|browser_ext|agent|api)
source (text) -- 'proxy-1','dns','sso'
risk (int) -- 0~100
status (enum: observed|allowed|blocked|pending_approval)
first_seen_at, last_seen_at
tags (text[])
unique(tenant_id, name, type, source)
index(tenant_id, status, risk desc)
```

### 3.2 shadow_events (탐지 이벤트)
- **파티셔닝(월별)**: `shadow_events_2025_09`
```
id (PK)
tenant_id (FK, index)
agent_id (FK -> shadow_agents.id, nullable)
user_id (FK -> users.id, nullable)
ts (timestamptz, index)
source (text) -- proxy/dns/sso/app
request (jsonb) -- headers, path, ip, device
indicators (jsonb) -- rules matched, scores
decision (enum: allow|deny|obligations)
decision_reason (text[])
bundle_version (text)
latency_ms (int)
```
인덱스 권장: `(tenant_id, ts desc)`, `(tenant_id, agent_id, ts desc)`, GIN on `indicators`

### 3.3 shadow_cases (사건/티켓)
```
id (PK)
tenant_id (FK)
title (text)
severity (enum: low|med|high|critical)
status (enum: open|in_progress|resolved|dismissed)
assignee (FK -> users.id, nullable)
opened_at, closed_at
summary (text)
links (jsonb) -- 외부 티켓/참조
```

### 3.4 case_events (사건-이벤트 매핑)
```
case_id (FK -> shadow_cases.id)
event_id (FK -> shadow_events.id)
added_at
PK (case_id, event_id)
```

---

## 4) 결정 로그 & 감사 (Decisions / Audit)

### 4.1 decision_logs (PEP←→PDP 결과)
- **파티셔닝(월별)**
```
id (PK)
tenant_id (FK)
user_id (FK, nullable)
ts (timestamptz, index)
route (text) -- '/llm/chat'
input_digest (text) -- 원문 해시 (민감정보 금지)
summary (jsonb) -- risk_score, pii_found, secrets_count...
decision (enum: allow|deny|obligations)
reasons (text[])
bundle_name (text), bundle_version (text)
policy_channel (text) -- 'canary','prod'
latency_ms (int) -- 정책 평가 지연
```
인덱스: `(tenant_id, ts desc)`, `(tenant_id, decision, ts desc)`

### 4.2 audit_logs (관리 행위 감사)
```
id (PK)
tenant_id (FK, nullable for global)
actor_user_id (FK -> users.id, nullable)
action (text) -- 'bundle.publish','rule.update','role.assign'
target (jsonb) -- {table:'filter_rules', id:123}
result (enum: success|fail)
detail (jsonb)
ts (timestamptz, index)
```

---

## 5) 알림 & 설정 (Alerts / Settings)

### 5.1 alert_rules
```
id (PK)
tenant_id (FK)
name (text)
query (jsonb) -- e.g., decision='deny' AND rate>5/min
threshold (jsonb) -- {value:5, window:'1m'}
channels (text[]) -- ['slack','email','webhook']
enabled (bool)
created_at, updated_at
```

### 5.2 alert_events
```
id (PK)
tenant_id (FK)
rule_id (FK -> alert_rules.id)
ts (timestamptz)
payload (jsonb)
status (enum: sent|silenced|error)
error_msg (text, nullable)
```

### 5.3 integrations (외부 연동 설정)
```
id (PK)
tenant_id (FK, nullable for global)
kind (enum: proxy|siem|metrics|vectordb|kms|vault|webhook|sso)
name (text)
config (jsonb) -- endpoint, token(ref to vault), options
enabled (bool)
created_at, updated_at
unique(tenant_id, kind, name)
```

---

## 6) 내부 LLM 모듈

### 6.1 model_registry
```
id (PK)
tenant_id (FK, nullable for shared)
name (text)
version (text)
params (jsonb) -- size, quant, context_len ...
status (enum: staging|canary|prod|paused)
artifacts_url (text)
hardware (text) -- 'A100x4'
tps (int), latency_p95_ms (int)
created_at, updated_at
unique(tenant_id, name, version)
```

### 6.2 model_guardrails
```
id (PK)
tenant_id (FK)
model_id (FK -> model_registry.id)
policy_bundle_id (FK -> policy_bundles.id)
output_filters (jsonb) -- PII/secret masking rules
token_limits (jsonb) -- max_input_tokens, max_output_tokens
enabled (bool)
created_at, updated_at
unique(model_id, policy_bundle_id)
```

### 6.3 prompt_templates
```
id (PK)
tenant_id (FK)
name (text)
version (text)
schema (jsonb) -- variables, defaults
content (text) -- 템플릿 본문
status (enum: draft|active|archived)
created_at, updated_at
unique(tenant_id, name, version)
```

### 6.4 eval_suites / eval_results
```
eval_suites:
  id (PK)
  tenant_id (FK)
  name (text)
  spec (jsonb) -- 평가 항목/가중치
  created_at

eval_results:
  id (PK)
  tenant_id (FK)
  model_id (FK -> model_registry.id)
  suite_id (FK -> eval_suites.id)
  score (numeric(5,2))
  safety (numeric(5,2))
  latency_p95_ms (int)
  ts (timestamptz)
  details (jsonb)
index(tenant_id, model_id, ts desc)
```

### 6.5 traffic_routes (AB/Canary)
```
id (PK)
tenant_id (FK)
name (text)
model_id_primary (FK)
model_id_secondary (FK, nullable)
ratio (int) -- 0~100 (secondary 비율)
scope (text) -- tenant/path/user-group
enabled (bool)
updated_at, updated_by
```

---

## 7) 성능/보존/보안 전략

### 7.1 파티셔닝 대상
- `decision_logs`, `shadow_events`: 월별 파티션 테이블 (자동 생성)
- 보존 정책: 테넌트별 `data_retention_days` 기준 아카이빙/삭제

### 7.2 인덱스 전략(예시)
- 공통: `tenant_id, ts desc` 복합
- JSON 필드(GIN): `indicators`, `summary`, `config`  
- 고유 조회: `(tenant_id, name, version)` 유니크

### 7.3 암호화/민감정보
- 시크릿 값 저장 금지(마스킹/해시)  
- 외부 키/토큰은 Vault/KMS에서 참조 키만 저장  
- PII/시크릿은 로그에 기록 금지(해시/마스킹)

### 7.4 트랜잭션/락
- 정책 배포: `policy_bundles.status` 전이 시 트랜잭션 처리, `FOR UPDATE`로 경쟁 제어
- 카나리 슬라이더: `traffic_routes` 원자적 업데이트

---

## 8) 관계 다이어그램(ASCII ERD 요약)
```
tenants ─┬─< users ─┬─< user_roles >─ roles
         ├─< api_tokens
         ├─< sso_identities
         ├─< policy_bundles ─┬─< filter_rules
         │                    ├─< allowlists
         │                    ├─< blocklists
         │                    └─< bundle_artifacts
         ├─< decision_logs
         ├─< audit_logs
         ├─< alert_rules ─┬─< alert_events
         ├─< shadow_agents ─┬─< shadow_events >─ shadow_cases >─ case_events
         ├─< model_registry ─┬─< model_guardrails
         │                    └─< eval_results
         ├─< prompt_templates
         └─< integrations
```

---

## 9) 샘플 DDL (PostgreSQL)

> 실제 배포 시에는 `schema.sql`과 마이그레이션 도구(Alembic)로 분리 권장

```sql
-- tenants
CREATE TABLE tenants (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  code TEXT NOT NULL UNIQUE,
  region TEXT,
  data_retention_days INT DEFAULT 365,
  encryption_profile TEXT,
  status TEXT CHECK (status IN ('active','suspended')) DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT now(),
  created_by BIGINT,
  updated_at TIMESTAMPTZ,
  updated_by BIGINT
);

-- policy_bundles
CREATE TABLE policy_bundles (
  id BIGSERIAL PRIMARY KEY,
  tenant_id BIGINT REFERENCES tenants(id),
  name TEXT NOT NULL,
  version TEXT NOT NULL,
  channel TEXT CHECK (channel IN ('draft','staging','canary','prod')) NOT NULL,
  signed_digest TEXT,
  status TEXT CHECK (status IN ('active','archived')) DEFAULT 'active',
  notes TEXT,
  created_by BIGINT,
  created_at TIMESTAMPTZ DEFAULT now(),
  published_at TIMESTAMPTZ,
  rolled_back_from TEXT,
  UNIQUE (tenant_id, name, version)
);
CREATE INDEX idx_policy_bundles_tenant_channel ON policy_bundles (tenant_id, channel, status);

-- filter_rules
CREATE TABLE filter_rules (
  id BIGSERIAL PRIMARY KEY,
  bundle_id BIGINT NOT NULL REFERENCES policy_bundles(id) ON DELETE CASCADE,
  tenant_id BIGINT REFERENCES tenants(id),
  type TEXT CHECK (type IN ('static','secret','pii','rebuff','ml','embedding')) NOT NULL,
  pattern TEXT,
  threshold NUMERIC,
  action TEXT CHECK (action IN ('block','redact','require_approval','log_only')) NOT NULL,
  context JSONB,
  enabled BOOLEAN DEFAULT TRUE,
  created_by BIGINT, created_at TIMESTAMPTZ DEFAULT now(),
  updated_by BIGINT, updated_at TIMESTAMPTZ, change_reason TEXT
);
CREATE INDEX idx_filter_rules_bundle ON filter_rules (bundle_id);
CREATE INDEX idx_filter_rules_tenant ON filter_rules (tenant_id, type, enabled);

-- decision_logs (파티셔닝은 파티션 테이블로 구현)
CREATE TABLE decision_logs (
  id BIGSERIAL PRIMARY KEY,
  tenant_id BIGINT NOT NULL REFERENCES tenants(id),
  user_id BIGINT,
  ts TIMESTAMPTZ NOT NULL,
  route TEXT,
  input_digest TEXT,
  summary JSONB,
  decision TEXT CHECK (decision IN ('allow','deny','obligations')),
  reasons TEXT[],
  bundle_name TEXT, bundle_version TEXT, policy_channel TEXT,
  latency_ms INT
);
CREATE INDEX idx_decision_logs_tenant_ts ON decision_logs (tenant_id, ts DESC);
CREATE INDEX idx_decision_logs_decision ON decision_logs (tenant_id, decision, ts DESC);
CREATE INDEX idx_decision_logs_summary_gin ON decision_logs USING GIN (summary);
```

---

## 10) 마이그레이션 & 운영
- **Alembic**: 스키마 버전 관리, 다운그레이드 포함
- **Seed 데이터**: 기본 역할/권한, 샘플 번들
- **데이터 보존 작업**: 월별 파티션 drop + 아카이브
- **백업/복구**: PITR, 주요 테이블 RPO/RTO 수립

---

## 11) 다음 단계(피드백 필요)
- 컬럼 enum/세부 타입 확정 (정수범위/정밀도)
- 파티셔닝 전략(월/주/일)과 보존기간 테넌트별 상이값 반영
- Shadow AI `indicators`/`request` 스키마 표준화 여부
- Internal LLM KPI 필드 추가(오류 코드/캐시 히트율 등)

---

### 부록) 명명 규칙
- 테이블: `snake_case` 복수형 (`policy_bundles`, `filter_rules`)
- PK: `id`, FK: `<table>_id`, 시간: `*_at`, 사용자: `*_by`

