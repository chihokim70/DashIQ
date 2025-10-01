-- AiGov Admin Portal 초기 데이터 삽입
-- 기본 테넌트, 사용자, 역할, 정책 데이터

-- 1. 기본 테넌트 생성
INSERT INTO tenants (name, code, region, data_retention_days, encryption_profile, status) 
VALUES 
    ('KRA Internal', 'kra-internal', 'ap-northeast-2', 365, 'default', 'active')
ON CONFLICT (name) DO NOTHING;

-- 2. 기본 역할 생성
INSERT INTO roles (tenant_id, name, scope, description) VALUES
    (1, 'Org Admin', 'tenant', '조직 관리자 - 전체 시스템 관리 권한'),
    (1, 'SecOps', 'tenant', '보안 운영자 - 정책 및 보안 이벤트 관리'),
    (1, 'MLOps', 'tenant', 'ML 운영자 - 내부 LLM 모델 관리'),
    (1, 'Auditor', 'tenant', '감사자 - 읽기 전용 권한')
ON CONFLICT (tenant_id, name) DO NOTHING;

-- 3. 기본 사용자 생성
INSERT INTO users (tenant_id, email, display_name, status, auth_provider) VALUES
    (1, 'admin@kra.go.kr', 'KRA Admin', 'active', 'local'),
    (1, 'secops@kra.go.kr', 'Security Operator', 'active', 'local'),
    (1, 'mlops@kra.go.kr', 'ML Operator', 'active', 'local'),
    (1, 'auditor@kra.go.kr', 'Auditor', 'active', 'local')
ON CONFLICT (tenant_id, email) DO NOTHING;

-- 4. 사용자-역할 매핑
INSERT INTO user_roles (user_id, role_id, tenant_id, assigned_by) VALUES
    (1, 1, 1, 1), -- KRA Admin -> Org Admin
    (2, 2, 1, 1), -- Security Operator -> SecOps
    (3, 3, 1, 1), -- ML Operator -> MLOps
    (4, 4, 1, 1)  -- Auditor -> Auditor
ON CONFLICT (user_id, role_id, tenant_id) DO NOTHING;

-- 5. 기본 정책 번들 생성
INSERT INTO policy_bundles (tenant_id, name, version, channel, status, created_by) VALUES
    (1, 'promptgate-default', '1.0.0', 'prod', 'active', 1),
    (1, 'promptgate-staging', '1.1.0', 'staging', 'active', 1)
ON CONFLICT (tenant_id, name, version) DO NOTHING;

-- 6. 기본 필터 규칙 생성 (Static Patterns)
INSERT INTO filter_rules (bundle_id, tenant_id, type, pattern, action, enabled, created_by) VALUES
    -- 프롬프트 인젝션 패턴
    (1, 1, 'static', '(?i)ignore\\s+(all\\s+)?previous\\s+(instructions?|rules?)', 'block', true, 1),
    (1, 1, 'static', '(?i)forget\\s+everything\\s+before', 'block', true, 1),
    (1, 1, 'static', '(?i)disregard\\s+previous\\s+prompt', 'block', true, 1),
    (1, 1, 'static', '(?i)you\\s+are\\s+now\\s+different', 'block', true, 1),
    (1, 1, 'static', '(?i)pretend\\s+to\\s+be', 'block', true, 1),
    (1, 1, 'static', '(?i)act\\s+as\\s+if', 'block', true, 1),
    (1, 1, 'static', '(?i)ignore\\s+safety\\s+guidelines', 'block', true, 1),
    (1, 1, 'static', '(?i)bypass\\s+security', 'block', true, 1),
    
    -- 관리자 권한 관련
    (1, 1, 'static', '(?i)admin(istrator)?\\s+password', 'block', true, 1),
    (1, 1, 'static', '(?i)system\\s+prompt', 'block', true, 1),
    (1, 1, 'static', '(?i)jailbreak', 'block', true, 1)
ON CONFLICT DO NOTHING;

-- 7. 시크릿 패턴 규칙
INSERT INTO filter_rules (bundle_id, tenant_id, type, pattern, action, enabled, created_by) VALUES
    -- AWS 키
    (1, 1, 'secret', 'AKIA[0-9A-Z]{16}', 'block', true, 1),
    (1, 1, 'secret', '(?i)aws(.{0,20})?secret(.{0,20})?key(.{0,20})?[=:]?[a-zA-Z0-9/+]{40}', 'block', true, 1),
    
    -- OpenAI 키
    (1, 1, 'secret', 'sk-[a-zA-Z0-9]{48}', 'block', true, 1),
    (1, 1, 'secret', 'sk-proj-[a-zA-Z0-9]{48}', 'block', true, 1),
    
    -- Google API 키
    (1, 1, 'secret', 'AIza[0-9A-Za-z\\-_]{35}', 'block', true, 1),
    
    -- GitHub 토큰
    (1, 1, 'secret', 'ghp_[0-9a-zA-Z]{36}', 'block', true, 1),
    (1, 1, 'secret', 'gho_[0-9a-zA-Z]{36}', 'block', true, 1),
    
    -- Bearer 토큰
    (1, 1, 'secret', 'Bearer\\s+[a-zA-Z0-9\\-_\\.]{30,}', 'block', true, 1),
    
    -- JWT 토큰
    (1, 1, 'secret', 'ey[A-Za-z0-9-_=]+\\.[A-Za-z0-9-_=]+\\.[A-Za-z0-9-_.+/=]+', 'block', true, 1)
ON CONFLICT DO NOTHING;

-- 8. PII 패턴 규칙
INSERT INTO filter_rules (bundle_id, tenant_id, type, pattern, action, enabled, created_by) VALUES
    -- 한국 주민번호
    (1, 1, 'pii', '\\b\\d{6}-\\d{7}\\b', 'redact', true, 1),
    (1, 1, 'pii', '\\b\\d{6}\\d{7}\\b', 'redact', true, 1),
    
    -- 한국 휴대폰번호
    (1, 1, 'pii', '\\b01[016789]-\\d{3,4}-\\d{4}\\b', 'redact', true, 1),
    (1, 1, 'pii', '\\b01[016789]\\d{3,4}\\d{4}\\b', 'redact', true, 1),
    
    -- 카드번호
    (1, 1, 'pii', '\\b\\d{4}-\\d{4}-\\d{4}-\\d{4}\\b', 'redact', true, 1),
    (1, 1, 'pii', '\\b\\d{4}\\d{4}\\d{4}\\d{4}\\b', 'redact', true, 1),
    
    -- 계좌번호
    (1, 1, 'pii', '\\b\\d{2,4}(-\\d{2,4}){1,2}\\b', 'redact', true, 1),
    
    -- 이메일 주소
    (1, 1, 'pii', '\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b', 'redact', true, 1)
ON CONFLICT DO NOTHING;

-- 9. 기본 허용 목록
INSERT INTO allowlists (bundle_id, tenant_id, kind, value, scope, note) VALUES
    (1, 1, 'domain', 'openai.com', '*', 'OpenAI 공식 도메인 허용'),
    (1, 1, 'domain', 'api.openai.com', '*', 'OpenAI API 도메인 허용'),
    (1, 1, 'domain', 'anthropic.com', '*', 'Anthropic 공식 도메인 허용'),
    (1, 1, 'domain', 'api.anthropic.com', '*', 'Anthropic API 도메인 허용'),
    (1, 1, 'domain', 'google.com', '*', 'Google 공식 도메인 허용'),
    (1, 1, 'domain', 'generativelanguage.googleapis.com', '*', 'Google AI API 도메인 허용')
ON CONFLICT (bundle_id, kind, value, scope) DO NOTHING;

-- 10. 기본 차단 목록
INSERT INTO blocklists (bundle_id, tenant_id, kind, value, scope, note) VALUES
    (1, 1, 'domain', 'chatgpt.com', '*', 'ChatGPT 웹사이트 차단'),
    (1, 1, 'domain', 'claude.ai', '*', 'Claude 웹사이트 차단'),
    (1, 1, 'domain', 'bard.google.com', '*', 'Bard 웹사이트 차단'),
    (1, 1, 'pattern', '.*\\.ai$', '*', 'AI 관련 도메인 패턴 차단')
ON CONFLICT (bundle_id, kind, value, scope) DO NOTHING;

-- 완료 메시지
DO $$
BEGIN
    RAISE NOTICE '✅ AiGov Admin Portal 초기 데이터 삽입 완료!';
    RAISE NOTICE '📊 생성된 데이터:';
    RAISE NOTICE '  - 테넌트: % 개', (SELECT COUNT(*) FROM tenants);
    RAISE NOTICE '  - 사용자: % 개', (SELECT COUNT(*) FROM users);
    RAISE NOTICE '  - 역할: % 개', (SELECT COUNT(*) FROM roles);
    RAISE NOTICE '  - 정책 번들: % 개', (SELECT COUNT(*) FROM policy_bundles);
    RAISE NOTICE '  - 필터 규칙: % 개', (SELECT COUNT(*) FROM filter_rules);
    RAISE NOTICE '  - 허용 목록: % 개', (SELECT COUNT(*) FROM allowlists);
    RAISE NOTICE '  - 차단 목록: % 개', (SELECT COUNT(*) FROM blocklists);
END $$;