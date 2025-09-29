-- AiGov Admin Portal Database Schema
-- 기존 설계 문서 기반 PostgreSQL 스키마

-- 확장 기능 활성화
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. 테넌트/계정/권한 (Tenants & Access)

-- tenants 테이블
CREATE TABLE tenants (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    code TEXT NOT NULL UNIQUE,
    region TEXT DEFAULT 'ap-northeast-2',
    data_retention_days INT DEFAULT 365,
    encryption_profile TEXT DEFAULT 'default',
    status TEXT CHECK (status IN ('active', 'suspended')) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT now(),
    created_by BIGINT,
    updated_at TIMESTAMPTZ,
    updated_by BIGINT
);

-- users 테이블
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    display_name TEXT,
    password_hash TEXT,
    status TEXT CHECK (status IN ('active', 'inactive', 'invited', 'blocked')) DEFAULT 'active',
    auth_provider TEXT CHECK (auth_provider IN ('local', 'sso')) DEFAULT 'local',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ,
    last_login_at TIMESTAMPTZ,
    UNIQUE(tenant_id, email)
);

-- roles 테이블
CREATE TABLE roles (
    id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT REFERENCES tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    scope TEXT CHECK (scope IN ('global', 'tenant')) DEFAULT 'tenant',
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ,
    UNIQUE(tenant_id, name)
);

-- user_roles 매핑 테이블
CREATE TABLE user_roles (
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id BIGINT NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    tenant_id BIGINT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    assigned_by BIGINT REFERENCES users(id),
    assigned_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (user_id, role_id, tenant_id)
);

-- api_tokens 테이블
CREATE TABLE api_tokens (
    id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    scopes TEXT[] DEFAULT '{}',
    hash TEXT NOT NULL,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    revoked_at TIMESTAMPTZ
);

-- sso_identities 테이블
CREATE TABLE sso_identities (
    id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider TEXT NOT NULL,
    subject TEXT NOT NULL,
    linked_at TIMESTAMPTZ DEFAULT now(),
    last_seen_at TIMESTAMPTZ,
    UNIQUE(tenant_id, provider, subject)
);

-- 2. 정책(OPA/Filters) & 번들

-- policy_bundles 테이블
CREATE TABLE policy_bundles (
    id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT REFERENCES tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    channel TEXT CHECK (channel IN ('draft', 'staging', 'canary', 'prod')) NOT NULL,
    signed_digest TEXT,
    status TEXT CHECK (status IN ('active', 'archived')) DEFAULT 'active',
    notes TEXT,
    created_by BIGINT REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT now(),
    published_at TIMESTAMPTZ,
    rolled_back_from TEXT,
    UNIQUE(tenant_id, name, version)
);

-- filter_rules 테이블
CREATE TABLE filter_rules (
    id BIGSERIAL PRIMARY KEY,
    bundle_id BIGINT NOT NULL REFERENCES policy_bundles(id) ON DELETE CASCADE,
    tenant_id BIGINT REFERENCES tenants(id) ON DELETE CASCADE,
    type TEXT CHECK (type IN ('static', 'secret', 'pii', 'rebuff', 'ml', 'embedding')) NOT NULL,
    pattern TEXT,
    threshold NUMERIC,
    action TEXT CHECK (action IN ('block', 'redact', 'require_approval', 'log_only')) NOT NULL,
    context JSONB,
    enabled BOOLEAN DEFAULT TRUE,
    created_by BIGINT REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_by BIGINT REFERENCES users(id),
    updated_at TIMESTAMPTZ,
    change_reason TEXT
);

-- allowlists 테이블
CREATE TABLE allowlists (
    id BIGSERIAL PRIMARY KEY,
    bundle_id BIGINT NOT NULL REFERENCES policy_bundles(id) ON DELETE CASCADE,
    tenant_id BIGINT REFERENCES tenants(id) ON DELETE CASCADE,
    kind TEXT CHECK (kind IN ('domain', 'pattern', 'user', 'path', 'keyprefix')) NOT NULL,
    value TEXT NOT NULL,
    scope TEXT DEFAULT '*',
    expire_at TIMESTAMPTZ,
    note TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(bundle_id, kind, value, scope)
);

-- blocklists 테이블
CREATE TABLE blocklists (
    id BIGSERIAL PRIMARY KEY,
    bundle_id BIGINT NOT NULL REFERENCES policy_bundles(id) ON DELETE CASCADE,
    tenant_id BIGINT REFERENCES tenants(id) ON DELETE CASCADE,
    kind TEXT CHECK (kind IN ('domain', 'pattern', 'user', 'path', 'keyprefix')) NOT NULL,
    value TEXT NOT NULL,
    scope TEXT DEFAULT '*',
    expire_at TIMESTAMPTZ,
    note TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(bundle_id, kind, value, scope)
);

-- approval_rules 테이블
CREATE TABLE approval_rules (
    id BIGSERIAL PRIMARY KEY,
    bundle_id BIGINT NOT NULL REFERENCES policy_bundles(id) ON DELETE CASCADE,
    tenant_id BIGINT REFERENCES tenants(id) ON DELETE CASCADE,
    criteria JSONB NOT NULL,
    approver_group TEXT NOT NULL,
    valid_days INT DEFAULT 30,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT now(),
    created_by BIGINT REFERENCES users(id),
    updated_at TIMESTAMPTZ,
    updated_by BIGINT REFERENCES users(id)
);

-- bundle_artifacts 테이블
CREATE TABLE bundle_artifacts (
    id BIGSERIAL PRIMARY KEY,
    bundle_id BIGINT NOT NULL REFERENCES policy_bundles(id) ON DELETE CASCADE,
    path TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    size_bytes BIGINT NOT NULL,
    storage_url TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(bundle_id, path)
);

-- policy_changes 테이블
CREATE TABLE policy_changes (
    id BIGSERIAL PRIMARY KEY,
    bundle_id BIGINT NOT NULL REFERENCES policy_bundles(id) ON DELETE CASCADE,
    diff TEXT NOT NULL,
    submitted_by BIGINT REFERENCES users(id),
    submitted_at TIMESTAMPTZ DEFAULT now(),
    approved_by BIGINT REFERENCES users(id),
    approved_at TIMESTAMPTZ,
    status TEXT CHECK (status IN ('draft', 'submitted', 'approved', 'rejected')) DEFAULT 'draft'
);

-- 3. Shadow AI 탐지 모듈

-- shadow_agents 테이블
CREATE TABLE shadow_agents (
    id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    type TEXT CHECK (type IN ('webapp', 'desktop', 'browser_ext', 'agent', 'api')) NOT NULL,
    source TEXT NOT NULL,
    risk INT CHECK (risk >= 0 AND risk <= 100) DEFAULT 0,
    status TEXT CHECK (status IN ('observed', 'allowed', 'blocked', 'pending_approval')) DEFAULT 'observed',
    first_seen_at TIMESTAMPTZ DEFAULT now(),
    last_seen_at TIMESTAMPTZ DEFAULT now(),
    tags TEXT[] DEFAULT '{}',
    UNIQUE(tenant_id, name, type, source)
);

-- shadow_events 테이블 (파티셔닝 대상)
CREATE TABLE shadow_events (
    id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    agent_id BIGINT REFERENCES shadow_agents(id) ON DELETE SET NULL,
    user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    ts TIMESTAMPTZ NOT NULL DEFAULT now(),
    source TEXT NOT NULL,
    request JSONB,
    indicators JSONB,
    decision TEXT CHECK (decision IN ('allow', 'deny', 'obligations')) NOT NULL,
    decision_reason TEXT[],
    bundle_version TEXT,
    latency_ms INT
);

-- shadow_cases 테이블
CREATE TABLE shadow_cases (
    id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    severity TEXT CHECK (severity IN ('low', 'med', 'high', 'critical')) DEFAULT 'low',
    status TEXT CHECK (status IN ('open', 'in_progress', 'resolved', 'dismissed')) DEFAULT 'open',
    assignee BIGINT REFERENCES users(id),
    opened_at TIMESTAMPTZ DEFAULT now(),
    closed_at TIMESTAMPTZ,
    summary TEXT,
    links JSONB DEFAULT '{}'
);

-- case_events 매핑 테이블
CREATE TABLE case_events (
    case_id BIGINT NOT NULL REFERENCES shadow_cases(id) ON DELETE CASCADE,
    event_id BIGINT NOT NULL REFERENCES shadow_events(id) ON DELETE CASCADE,
    added_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (case_id, event_id)
);

-- 4. 결정 로그 & 감사 (Decisions / Audit)

-- decision_logs 테이블 (파티셔닝 대상)
CREATE TABLE decision_logs (
    id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    ts TIMESTAMPTZ NOT NULL DEFAULT now(),
    route TEXT,
    input_digest TEXT,
    summary JSONB,
    decision TEXT CHECK (decision IN ('allow', 'deny', 'obligations')) NOT NULL,
    reasons TEXT[],
    bundle_name TEXT,
    bundle_version TEXT,
    policy_channel TEXT,
    latency_ms INT
);

-- audit_logs 테이블
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT REFERENCES tenants(id) ON DELETE CASCADE,
    actor_user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    target JSONB,
    result TEXT CHECK (result IN ('success', 'fail')) DEFAULT 'success',
    detail JSONB,
    ts TIMESTAMPTZ DEFAULT now()
);

-- 5. 알림 & 설정 (Alerts / Settings)

-- alert_rules 테이블
CREATE TABLE alert_rules (
    id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    query JSONB NOT NULL,
    threshold JSONB NOT NULL,
    channels TEXT[] DEFAULT '{}',
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ,
    updated_by BIGINT REFERENCES users(id)
);

-- alert_events 테이블
CREATE TABLE alert_events (
    id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    rule_id BIGINT NOT NULL REFERENCES alert_rules(id) ON DELETE CASCADE,
    ts TIMESTAMPTZ DEFAULT now(),
    payload JSONB,
    status TEXT CHECK (status IN ('sent', 'silenced', 'error')) DEFAULT 'sent',
    error_msg TEXT
);

-- integrations 테이블
CREATE TABLE integrations (
    id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT REFERENCES tenants(id) ON DELETE CASCADE,
    kind TEXT CHECK (kind IN ('proxy', 'siem', 'metrics', 'vectordb', 'kms', 'vault', 'webhook', 'sso')) NOT NULL,
    name TEXT NOT NULL,
    config JSONB NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ,
    updated_by BIGINT REFERENCES users(id),
    UNIQUE(tenant_id, kind, name)
);

-- 6. 내부 LLM 모듈

-- model_registry 테이블
CREATE TABLE model_registry (
    id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT REFERENCES tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    params JSONB,
    status TEXT CHECK (status IN ('staging', 'canary', 'prod', 'paused')) DEFAULT 'staging',
    artifacts_url TEXT,
    hardware TEXT,
    tps INT,
    latency_p95_ms INT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ,
    updated_by BIGINT REFERENCES users(id),
    UNIQUE(tenant_id, name, version)
);

-- model_guardrails 테이블
CREATE TABLE model_guardrails (
    id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    model_id BIGINT NOT NULL REFERENCES model_registry(id) ON DELETE CASCADE,
    policy_bundle_id BIGINT NOT NULL REFERENCES policy_bundles(id) ON DELETE CASCADE,
    output_filters JSONB,
    token_limits JSONB,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ,
    updated_by BIGINT REFERENCES users(id),
    UNIQUE(model_id, policy_bundle_id)
);

-- prompt_templates 테이블
CREATE TABLE prompt_templates (
    id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    schema JSONB,
    content TEXT NOT NULL,
    status TEXT CHECK (status IN ('draft', 'active', 'archived')) DEFAULT 'draft',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ,
    updated_by BIGINT REFERENCES users(id),
    UNIQUE(tenant_id, name, version)
);

-- eval_suites 테이블
CREATE TABLE eval_suites (
    id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    spec JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    created_by BIGINT REFERENCES users(id)
);

-- eval_results 테이블
CREATE TABLE eval_results (
    id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    model_id BIGINT NOT NULL REFERENCES model_registry(id) ON DELETE CASCADE,
    suite_id BIGINT NOT NULL REFERENCES eval_suites(id) ON DELETE CASCADE,
    score NUMERIC(5,2),
    safety NUMERIC(5,2),
    latency_p95_ms INT,
    ts TIMESTAMPTZ DEFAULT now(),
    details JSONB
);

-- traffic_routes 테이블
CREATE TABLE traffic_routes (
    id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    model_id_primary BIGINT NOT NULL REFERENCES model_registry(id) ON DELETE CASCADE,
    model_id_secondary BIGINT REFERENCES model_registry(id) ON DELETE SET NULL,
    ratio INT CHECK (ratio >= 0 AND ratio <= 100) DEFAULT 0,
    scope TEXT DEFAULT '*',
    enabled BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMPTZ DEFAULT now(),
    updated_by BIGINT REFERENCES users(id)
);

-- 인덱스 생성
CREATE INDEX idx_users_tenant_email ON users (tenant_id, email);
CREATE INDEX idx_users_status ON users (status);
CREATE INDEX idx_user_roles_user_id ON user_roles (user_id);
CREATE INDEX idx_user_roles_role_id ON user_roles (role_id);
CREATE INDEX idx_api_tokens_tenant_user ON api_tokens (tenant_id, user_id, expires_at);
CREATE INDEX idx_api_tokens_hash ON api_tokens (hash);

CREATE INDEX idx_policy_bundles_tenant_channel ON policy_bundles (tenant_id, channel, status);
CREATE INDEX idx_filter_rules_bundle ON filter_rules (bundle_id);
CREATE INDEX idx_filter_rules_tenant ON filter_rules (tenant_id, type, enabled);
CREATE INDEX idx_allowlists_tenant_kind ON allowlists (tenant_id, kind, expire_at);
CREATE INDEX idx_blocklists_tenant_kind ON blocklists (tenant_id, kind, expire_at);

CREATE INDEX idx_shadow_agents_tenant_status ON shadow_agents (tenant_id, status, risk DESC);
CREATE INDEX idx_shadow_events_tenant_ts ON shadow_events (tenant_id, ts DESC);
CREATE INDEX idx_shadow_events_agent_ts ON shadow_events (tenant_id, agent_id, ts DESC);
CREATE INDEX idx_shadow_events_indicators_gin ON shadow_events USING GIN (indicators);

CREATE INDEX idx_decision_logs_tenant_ts ON decision_logs (tenant_id, ts DESC);
CREATE INDEX idx_decision_logs_decision ON decision_logs (tenant_id, decision, ts DESC);
CREATE INDEX idx_decision_logs_summary_gin ON decision_logs USING GIN (summary);

CREATE INDEX idx_audit_logs_tenant_ts ON audit_logs (tenant_id, ts DESC);
CREATE INDEX idx_audit_logs_actor ON audit_logs (actor_user_id, ts DESC);

CREATE INDEX idx_alert_rules_tenant ON alert_rules (tenant_id, enabled);
CREATE INDEX idx_alert_events_rule_ts ON alert_events (rule_id, ts DESC);

CREATE INDEX idx_model_registry_tenant ON model_registry (tenant_id, status);
CREATE INDEX idx_eval_results_model_ts ON eval_results (tenant_id, model_id, ts DESC);

-- 기본 데이터 삽입
INSERT INTO tenants (name, code, region, data_retention_days, encryption_profile, status) 
VALUES ('KRA Internal', 'kra-internal', 'ap-northeast-2', 365, 'default', 'active');

INSERT INTO roles (tenant_id, name, scope, description) VALUES
(1, 'Org Admin', 'tenant', '조직 관리자 - 전체 시스템 관리 권한'),
(1, 'SecOps', 'tenant', '보안 운영자 - 정책 및 보안 이벤트 관리'),
(1, 'MLOps', 'tenant', 'ML 운영자 - 내부 LLM 모델 관리'),
(1, 'Auditor', 'tenant', '감사자 - 읽기 전용 권한');

INSERT INTO users (tenant_id, email, display_name, status, auth_provider) VALUES
(1, 'admin@kra.go.kr', 'KRA Admin', 'active', 'local');

INSERT INTO user_roles (user_id, role_id, tenant_id, assigned_by) VALUES
(1, 1, 1, 1);

-- 기본 정책 번들 생성
INSERT INTO policy_bundles (tenant_id, name, version, channel, status, created_by) VALUES
(1, 'promptgate-default', '1.0.0', 'prod', 'active', 1);

-- 기본 필터 규칙 생성
INSERT INTO filter_rules (bundle_id, tenant_id, type, pattern, action, enabled, created_by) VALUES
(1, 1, 'static', '(?i)ignore\\s+(all\\s+)?previous\\s+(instructions?|rules?)', 'block', true, 1),
(1, 1, 'secret', 'AKIA[0-9A-Z]{16}', 'block', true, 1),
(1, 1, 'secret', 'sk-[a-zA-Z0-9]{48}', 'block', true, 1),
(1, 1, 'pii', '\\b\\d{6}-\\d{7}\\b', 'redact', true, 1),
(1, 1, 'pii', '\\b01[016789]-\\d{3,4}-\\d{4}\\b', 'redact', true, 1);

-- 기본 시스템 설정
INSERT INTO integrations (tenant_id, kind, name, config, enabled) VALUES
(1, 'proxy', 'default-proxy', '{"endpoint": "http://localhost:8080", "timeout": 30}', true),
(1, 'vectordb', 'qdrant', '{"host": "localhost", "port": 6333, "collection": "promptgate"}', true),
(1, 'metrics', 'prometheus', '{"endpoint": "http://localhost:9090"}', true);

COMMIT;
