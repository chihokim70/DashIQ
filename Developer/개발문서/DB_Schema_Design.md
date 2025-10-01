# AiGov Admin Portal DB 스키마 설계

## 📋 개요
Admin Portal 설계를 기반으로 한 통합 데이터베이스 스키마 설계 문서입니다.
PromptGate, ShadowEye, DashIQ, TrustLLM, SolMan 모든 모듈의 데이터를 통합 관리합니다.

## 🎯 설계 원칙
- **정규화**: 3NF 이상의 정규화된 구조
- **확장성**: 새로운 모듈 추가 시 스키마 변경 최소화
- **성능**: 인덱스 최적화 및 파티셔닝 고려
- **보안**: 민감 정보 암호화 및 접근 제어
- **감사**: 모든 중요 데이터 변경 추적

## 🗄️ 핵심 엔티티 설계

### 1. 사용자 및 조직 관리

#### Users (사용자)
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone VARCHAR(20),
    department VARCHAR(100),
    position VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    updated_by INTEGER REFERENCES users(id)
);

-- 인덱스
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_department ON users(department);
CREATE INDEX idx_users_is_active ON users(is_active);
```

#### Organizations (조직/테넌트)
```sql
CREATE TABLE organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    description TEXT,
    domain VARCHAR(100),
    industry VARCHAR(50),
    size VARCHAR(20), -- 'small', 'medium', 'large', 'enterprise'
    country VARCHAR(50),
    timezone VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    updated_by INTEGER REFERENCES users(id)
);

-- 인덱스
CREATE INDEX idx_organizations_code ON organizations(code);
CREATE INDEX idx_organizations_domain ON organizations(domain);
CREATE INDEX idx_organizations_is_active ON organizations(is_active);
```

#### UserOrganizations (사용자-조직 관계)
```sql
CREATE TABLE user_organizations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL, -- 'admin', 'manager', 'user', 'viewer'
    is_primary BOOLEAN DEFAULT FALSE,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, organization_id)
);

-- 인덱스
CREATE INDEX idx_user_orgs_user_id ON user_organizations(user_id);
CREATE INDEX idx_user_orgs_org_id ON user_organizations(organization_id);
CREATE INDEX idx_user_orgs_role ON user_organizations(role);
```

### 2. 정책 관리 (PromptGate)

#### Policies (정책)
```sql
CREATE TABLE policies (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    policy_type VARCHAR(50) NOT NULL, -- 'prompt_filter', 'shadow_detection', 'trust_evaluation'
    version VARCHAR(20) DEFAULT '1.0',
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    updated_by INTEGER REFERENCES users(id),
    UNIQUE(organization_id, name)
);

-- 인덱스
CREATE INDEX idx_policies_org_id ON policies(organization_id);
CREATE INDEX idx_policies_type ON policies(policy_type);
CREATE INDEX idx_policies_is_active ON policies(is_active);
CREATE INDEX idx_policies_priority ON policies(priority);
```

#### PolicyRules (정책 규칙)
```sql
CREATE TABLE policy_rules (
    id SERIAL PRIMARY KEY,
    policy_id INTEGER NOT NULL REFERENCES policies(id) ON DELETE CASCADE,
    rule_name VARCHAR(100) NOT NULL,
    rule_type VARCHAR(50) NOT NULL, -- 'deny_pattern', 'pii_pattern', 'secret_pattern', 'length_limit', 'language_limit'
    rule_pattern TEXT, -- 정규식 패턴
    rule_value TEXT, -- 규칙 값 (예: 최대 길이, 허용 언어 등)
    severity VARCHAR(20) NOT NULL, -- 'low', 'medium', 'high', 'critical'
    action VARCHAR(20) NOT NULL, -- 'allow', 'deny', 'mask', 'sanitize', 'alert'
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    updated_by INTEGER REFERENCES users(id)
);

-- 인덱스
CREATE INDEX idx_policy_rules_policy_id ON policy_rules(policy_id);
CREATE INDEX idx_policy_rules_type ON policy_rules(rule_type);
CREATE INDEX idx_policy_rules_severity ON policy_rules(severity);
CREATE INDEX idx_policy_rules_action ON policy_rules(action);
CREATE INDEX idx_policy_rules_is_active ON policy_rules(is_active);
```

#### PolicyActions (정책 액션)
```sql
CREATE TABLE policy_actions (
    id SERIAL PRIMARY KEY,
    policy_id INTEGER NOT NULL REFERENCES policies(id) ON DELETE CASCADE,
    action_name VARCHAR(50) NOT NULL, -- 'suspicious', 'pii_found', 'secrets_found', 'injection_detected'
    action_type VARCHAR(20) NOT NULL, -- 'sanitize', 'mask', 'deny', 'allow', 'alert'
    action_config JSONB, -- 액션 설정 (JSON)
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    updated_by INTEGER REFERENCES users(id),
    UNIQUE(policy_id, action_name)
);

-- 인덱스
CREATE INDEX idx_policy_actions_policy_id ON policy_actions(policy_id);
CREATE INDEX idx_policy_actions_name ON policy_actions(action_name);
CREATE INDEX idx_policy_actions_type ON policy_actions(action_type);
```

### 3. ShadowEye 탐지 관리

#### DetectionRules (탐지 규칙)
```sql
CREATE TABLE detection_rules (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    rule_name VARCHAR(100) NOT NULL,
    rule_type VARCHAR(50) NOT NULL, -- 'ai_service_pattern', 'network_traffic', 'user_behavior'
    rule_pattern TEXT NOT NULL, -- 탐지 패턴
    ai_service VARCHAR(50), -- 'chatgpt', 'claude', 'gemini', 'custom'
    detection_method VARCHAR(50), -- 'regex', 'ml_model', 'signature', 'behavioral'
    severity VARCHAR(20) NOT NULL, -- 'low', 'medium', 'high', 'critical'
    action VARCHAR(20) NOT NULL, -- 'block', 'alert', 'log', 'quarantine'
    is_active BOOLEAN DEFAULT TRUE,
    confidence_threshold DECIMAL(3,2) DEFAULT 0.8,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    updated_by INTEGER REFERENCES users(id)
);

-- 인덱스
CREATE INDEX idx_detection_rules_org_id ON detection_rules(organization_id);
CREATE INDEX idx_detection_rules_type ON detection_rules(rule_type);
CREATE INDEX idx_detection_rules_ai_service ON detection_rules(ai_service);
CREATE INDEX idx_detection_rules_severity ON detection_rules(severity);
CREATE INDEX idx_detection_rules_is_active ON detection_rules(is_active);
```

#### DetectionEvents (탐지 이벤트)
```sql
CREATE TABLE detection_events (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    rule_id INTEGER NOT NULL REFERENCES detection_rules(id),
    event_type VARCHAR(50) NOT NULL, -- 'shadow_ai_detected', 'unauthorized_access', 'suspicious_behavior'
    ai_service VARCHAR(50),
    source_ip INET,
    user_agent TEXT,
    request_url TEXT,
    request_method VARCHAR(10),
    request_headers JSONB,
    request_body TEXT,
    response_status INTEGER,
    response_body TEXT,
    confidence_score DECIMAL(3,2),
    risk_score DECIMAL(3,2),
    action_taken VARCHAR(20), -- 'blocked', 'alerted', 'logged', 'quarantined'
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    resolved_by INTEGER REFERENCES users(id),
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 파티셔닝 (월별)
CREATE INDEX idx_detection_events_org_id ON detection_events(organization_id);
CREATE INDEX idx_detection_events_user_id ON detection_events(user_id);
CREATE INDEX idx_detection_events_rule_id ON detection_events(rule_id);
CREATE INDEX idx_detection_events_type ON detection_events(event_type);
CREATE INDEX idx_detection_events_ai_service ON detection_events(ai_service);
CREATE INDEX idx_detection_events_created_at ON detection_events(created_at);
CREATE INDEX idx_detection_events_is_resolved ON detection_events(is_resolved);
```

### 4. 프롬프트 로그 관리 (PromptGate)

#### PromptLogs (프롬프트 로그)
```sql
CREATE TABLE prompt_logs (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    session_id VARCHAR(100),
    original_prompt TEXT NOT NULL,
    masked_prompt TEXT,
    ai_service VARCHAR(50),
    is_blocked BOOLEAN DEFAULT FALSE,
    block_reason TEXT,
    detection_method VARCHAR(50), -- 'keyword', 'vector', 'rebuff', 'policy_engine'
    risk_score DECIMAL(3,2),
    processing_time DECIMAL(6,3), -- 처리 시간 (초)
    policy_violations JSONB, -- 위반된 정책 목록
    source_ip INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 파티셔닝 (일별)
CREATE INDEX idx_prompt_logs_org_id ON prompt_logs(organization_id);
CREATE INDEX idx_prompt_logs_user_id ON prompt_logs(user_id);
CREATE INDEX idx_prompt_logs_session_id ON prompt_logs(session_id);
CREATE INDEX idx_prompt_logs_ai_service ON prompt_logs(ai_service);
CREATE INDEX idx_prompt_logs_is_blocked ON prompt_logs(is_blocked);
CREATE INDEX idx_prompt_logs_created_at ON prompt_logs(created_at);
```

### 5. 신뢰성 평가 (TrustLLM)

#### AIModels (AI 모델)
```sql
CREATE TABLE ai_models (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    model_name VARCHAR(100) NOT NULL,
    model_provider VARCHAR(50) NOT NULL, -- 'openai', 'anthropic', 'google', 'custom'
    model_version VARCHAR(20),
    model_type VARCHAR(50), -- 'text_generation', 'image_generation', 'code_generation'
    description TEXT,
    capabilities JSONB, -- 모델 기능 목록
    limitations JSONB, -- 모델 제한사항
    is_approved BOOLEAN DEFAULT FALSE,
    approval_date TIMESTAMP,
    approved_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    updated_by INTEGER REFERENCES users(id),
    UNIQUE(organization_id, model_name, model_version)
);

-- 인덱스
CREATE INDEX idx_ai_models_org_id ON ai_models(organization_id);
CREATE INDEX idx_ai_models_provider ON ai_models(model_provider);
CREATE INDEX idx_ai_models_type ON ai_models(model_type);
CREATE INDEX idx_ai_models_is_approved ON ai_models(is_approved);
```

#### TrustEvaluations (신뢰성 평가)
```sql
CREATE TABLE trust_evaluations (
    id SERIAL PRIMARY KEY,
    model_id INTEGER NOT NULL REFERENCES ai_models(id) ON DELETE CASCADE,
    evaluation_type VARCHAR(50) NOT NULL, -- 'accuracy', 'bias', 'safety', 'robustness'
    evaluation_method VARCHAR(50) NOT NULL, -- 'automated', 'manual', 'hybrid'
    test_dataset VARCHAR(100),
    evaluation_metrics JSONB, -- 평가 지표 및 점수
    overall_score DECIMAL(3,2),
    confidence_level DECIMAL(3,2),
    evaluation_notes TEXT,
    evaluator_id INTEGER REFERENCES users(id),
    evaluation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_valid BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP
);

-- 인덱스
CREATE INDEX idx_trust_evaluations_model_id ON trust_evaluations(model_id);
CREATE INDEX idx_trust_evaluations_type ON trust_evaluations(evaluation_type);
CREATE INDEX idx_trust_evaluations_score ON trust_evaluations(overall_score);
CREATE INDEX idx_trust_evaluations_date ON trust_evaluations(evaluation_date);
CREATE INDEX idx_trust_evaluations_is_valid ON trust_evaluations(is_valid);
```

### 6. 솔루션 관리 (SolMan)

#### Solutions (솔루션)
```sql
CREATE TABLE solutions (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    solution_type VARCHAR(50) NOT NULL, -- 'ai_service', 'security_tool', 'monitoring_tool'
    vendor VARCHAR(100),
    version VARCHAR(20),
    license_type VARCHAR(50), -- 'commercial', 'open_source', 'free'
    license_key VARCHAR(255),
    license_expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    configuration JSONB, -- 솔루션 설정
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    updated_by INTEGER REFERENCES users(id),
    UNIQUE(organization_id, name, version)
);

-- 인덱스
CREATE INDEX idx_solutions_org_id ON solutions(organization_id);
CREATE INDEX idx_solutions_type ON solutions(solution_type);
CREATE INDEX idx_solutions_vendor ON solutions(vendor);
CREATE INDEX idx_solutions_is_active ON solutions(is_active);
CREATE INDEX idx_solutions_license_expires ON solutions(license_expires_at);
```

### 7. 시스템 설정 및 감사

#### SystemConfigs (시스템 설정)
```sql
CREATE TABLE system_configs (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    config_key VARCHAR(100) NOT NULL,
    config_value TEXT NOT NULL,
    config_type VARCHAR(50) NOT NULL, -- 'string', 'number', 'boolean', 'json'
    description TEXT,
    is_encrypted BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES users(id),
    UNIQUE(organization_id, config_key)
);

-- 인덱스
CREATE INDEX idx_system_configs_org_id ON system_configs(organization_id);
CREATE INDEX idx_system_configs_key ON system_configs(config_key);
CREATE INDEX idx_system_configs_type ON system_configs(config_type);
CREATE INDEX idx_system_configs_is_active ON system_configs(is_active);
```

#### AuditLogs (감사 로그)
```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    action_type VARCHAR(50) NOT NULL, -- 'create', 'update', 'delete', 'login', 'logout'
    resource_type VARCHAR(50) NOT NULL, -- 'user', 'policy', 'detection_rule', 'system_config'
    resource_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    action_details JSONB,
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 파티셔닝 (월별)
CREATE INDEX idx_audit_logs_org_id ON audit_logs(organization_id);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action_type ON audit_logs(action_type);
CREATE INDEX idx_audit_logs_resource_type ON audit_logs(resource_type);
CREATE INDEX idx_audit_logs_resource_id ON audit_logs(resource_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
```

## 🔧 데이터베이스 최적화

### 파티셔닝 전략
```sql
-- 월별 파티셔닝 (로그 테이블)
CREATE TABLE prompt_logs_y2024m01 PARTITION OF prompt_logs
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE detection_events_y2024m01 PARTITION OF detection_events
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE audit_logs_y2024m01 PARTITION OF audit_logs
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

### 인덱스 최적화
```sql
-- 복합 인덱스
CREATE INDEX idx_prompt_logs_org_user_date ON prompt_logs(organization_id, user_id, created_at);
CREATE INDEX idx_detection_events_org_type_date ON detection_events(organization_id, event_type, created_at);
CREATE INDEX idx_audit_logs_org_user_date ON audit_logs(organization_id, user_id, created_at);

-- 부분 인덱스
CREATE INDEX idx_active_policies ON policies(organization_id, name) WHERE is_active = TRUE;
CREATE INDEX idx_blocked_prompts ON prompt_logs(organization_id, created_at) WHERE is_blocked = TRUE;
CREATE INDEX idx_unresolved_events ON detection_events(organization_id, created_at) WHERE is_resolved = FALSE;
```

### 데이터 보안
```sql
-- 암호화된 컬럼
ALTER TABLE users ADD COLUMN encrypted_phone BYTEA;
ALTER TABLE system_configs ADD COLUMN encrypted_value BYTEA;

-- 행 수준 보안 (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE detection_events ENABLE ROW LEVEL SECURITY;

-- 정책 예시
CREATE POLICY user_organization_policy ON users
FOR ALL TO authenticated_users
USING (id IN (
    SELECT user_id FROM user_organizations 
    WHERE organization_id = current_setting('app.current_organization_id')::INTEGER
));
```

## 📊 데이터베이스 관계도

### 주요 관계
- **Organizations** ←→ **Users** (M:N via UserOrganizations)
- **Organizations** ←→ **Policies** (1:N)
- **Policies** ←→ **PolicyRules** (1:N)
- **Policies** ←→ **PolicyActions** (1:N)
- **Organizations** ←→ **DetectionRules** (1:N)
- **DetectionRules** ←→ **DetectionEvents** (1:N)
- **Organizations** ←→ **PromptLogs** (1:N)
- **Organizations** ←→ **AIModels** (1:N)
- **AIModels** ←→ **TrustEvaluations** (1:N)
- **Organizations** ←→ **Solutions** (1:N)
- **Organizations** ←→ **SystemConfigs** (1:N)
- **Organizations** ←→ **AuditLogs** (1:N)

## 🚀 구현 계획

### Phase 1: 기본 스키마 (1주)
- 사용자 및 조직 관리
- 정책 관리 기본 구조
- 감사 로그

### Phase 2: 모듈별 확장 (2주)
- ShadowEye 탐지 관리
- TrustLLM 신뢰성 평가
- SolMan 솔루션 관리

### Phase 3: 최적화 (1주)
- 파티셔닝 및 인덱스 최적화
- 보안 강화
- 성능 튜닝

## 📋 다음 단계
1. **마이그레이션 스크립트 작성**
2. **초기 데이터 시드 스크립트**
3. **백업 및 복구 전략**
4. **모니터링 및 알림 설정**

