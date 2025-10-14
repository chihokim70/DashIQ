-- Supabase Self-host 스키마 설정
-- 설계서에 따른 보안 아키텍처 구현

-- 1. 기본 스키마 생성
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS storage;
CREATE SCHEMA IF NOT EXISTS realtime;

-- 2. 기본 역할 생성 (RLS 보안)
CREATE ROLE IF NOT EXISTS anon NOLOGIN NOINHERIT;
CREATE ROLE IF NOT EXISTS authenticated NOLOGIN NOINHERIT;
CREATE ROLE IF NOT EXISTS service_role NOLOGIN NOINHERIT BYPASSRLS;

-- 3. 권한 설정
GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT USAGE ON SCHEMA auth TO anon, authenticated, service_role;
GRANT USAGE ON SCHEMA storage TO anon, authenticated, service_role;

-- 4. AiGov 핵심 테이블 생성 (설계서 기반)
CREATE TABLE IF NOT EXISTS public.organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE,
    full_name VARCHAR(255),
    organization_id UUID REFERENCES public.organizations(id),
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    organization_id UUID REFERENCES public.organizations(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.policy_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_id UUID REFERENCES public.policies(id) ON DELETE CASCADE,
    rule_name VARCHAR(255) NOT NULL,
    rule_type VARCHAR(100) NOT NULL,
    rule_config JSONB,
    priority INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.detection_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id),
    organization_id UUID REFERENCES public.organizations(id),
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB,
    risk_score DECIMAL(3,2) DEFAULT 0.00,
    is_blocked BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id),
    organization_id UUID REFERENCES public.organizations(id),
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(100),
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.system_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_key VARCHAR(255) UNIQUE NOT NULL,
    config_value JSONB,
    description TEXT,
    is_encrypted BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. RLS(Row Level Security) 활성화 (설계서 요구사항)
ALTER TABLE public.organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.policy_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.detection_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.system_configs ENABLE ROW LEVEL SECURITY;

-- 6. RLS 정책 생성 (조직별 데이터 격리)
CREATE POLICY "organizations_select_policy" ON public.organizations
    FOR SELECT USING (true);

CREATE POLICY "users_select_policy" ON public.users
    FOR SELECT USING (true);

CREATE POLICY "users_insert_policy" ON public.users
    FOR INSERT WITH CHECK (true);

CREATE POLICY "users_update_policy" ON public.users
    FOR UPDATE USING (true);

CREATE POLICY "policies_select_policy" ON public.policies
    FOR SELECT USING (true);

CREATE POLICY "policy_rules_select_policy" ON public.policy_rules
    FOR SELECT USING (true);

CREATE POLICY "detection_events_select_policy" ON public.detection_events
    FOR SELECT USING (true);

CREATE POLICY "detection_events_insert_policy" ON public.detection_events
    FOR INSERT WITH CHECK (true);

CREATE POLICY "audit_logs_select_policy" ON public.audit_logs
    FOR SELECT USING (true);

CREATE POLICY "audit_logs_insert_policy" ON public.audit_logs
    FOR INSERT WITH CHECK (true);

CREATE POLICY "system_configs_select_policy" ON public.system_configs
    FOR SELECT USING (true);

-- 7. 인덱스 생성 (성능 최적화)
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_organization_id ON public.users(organization_id);
CREATE INDEX IF NOT EXISTS idx_policies_organization_id ON public.policies(organization_id);
CREATE INDEX IF NOT EXISTS idx_policy_rules_policy_id ON public.policy_rules(policy_id);
CREATE INDEX IF NOT EXISTS idx_detection_events_user_id ON public.detection_events(user_id);
CREATE INDEX IF NOT EXISTS idx_detection_events_created_at ON public.detection_events(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON public.audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON public.audit_logs(created_at);

-- 8. 기본 데이터 삽입
INSERT INTO public.organizations (id, name, domain) VALUES 
    ('00000000-0000-0000-0000-000000000001', 'AiGov Default', 'aigov.local')
ON CONFLICT (domain) DO NOTHING;

INSERT INTO public.users (id, email, username, full_name, organization_id, role) VALUES 
    ('00000000-0000-0000-0000-000000000001', 'admin@aigov.local', 'admin', 'AiGov Administrator', '00000000-0000-0000-0000-000000000001', 'admin')
ON CONFLICT (email) DO NOTHING;

INSERT INTO public.system_configs (config_key, config_value, description) VALUES 
    ('supabase_version', '"1.0.0"', 'Supabase Self-host 버전'),
    ('aigov_version', '"2025.10"', 'AiGov 솔루션 버전'),
    ('security_level', '"high"', '보안 수준 설정')
ON CONFLICT (config_key) DO NOTHING;
