package promptgate.allow

import data.promptgate.common

# 기본 허용 정책
default allow = false

# 허용 조건들
allow {
    # 테넌트가 존재하고 활성화되어 있음
    tenant_exists(input.tenant)
    
    # 사용자 권한 확인
    user_has_permission(input.user)
    
    # 프롬프트가 안전함
    prompt_is_safe(input.prompt)
    
    # 필터 결과가 허용 가능함
    filters_passed(input.filter_results)
}

# 테넌트 존재 확인
tenant_exists(tenant) {
    data.promptgate.policies[tenant]
}

# 사용자 권한 확인
user_has_permission(user) {
    # 기본 사용자는 허용
    user.id != ""
}

# 프롬프트 안전성 검사
prompt_is_safe(prompt) {
    not contains_secrets(prompt.text)
    not contains_injection(prompt.text)
    not contains_pii(prompt.text)
    prompt_length_valid(prompt.length)
    language_allowed(prompt.language)
}

# 시크릿 정보 포함 여부 확인
contains_secrets(text) {
    common.contains_aws_key(text)
}

contains_secrets(text) {
    common.contains_openai_key(text)
}

contains_secrets(text) {
    common.contains_bearer_token(text)
}

# 프롬프트 인젝션 패턴 확인
contains_injection(text) {
    common.contains_ignore_instructions(text)
}

contains_injection(text) {
    common.contains_admin_password(text)
}

contains_injection(text) {
    common.contains_system_prompt(text)
}

contains_injection(text) {
    common.contains_jailbreak(text)
}

# PII 패턴 확인
contains_pii(text) {
    common.contains_korean_rrn(text)
}

contains_pii(text) {
    common.contains_phone_number(text)
}

contains_pii(text) {
    common.contains_card_number(text)
}

# 프롬프트 길이 검증
prompt_length_valid(length) {
    tenant_policy := data.promptgate.policies[input.tenant]
    max_length := tenant_policy.rules.max_prompt_length
    common.is_valid_length(length, max_length)
}

# 언어 허용 여부 확인
language_allowed(language) {
    tenant_policy := data.promptgate.policies[input.tenant]
    allowed_languages := tenant_policy.rules.allowed_languages
    common.is_allowed_language(language, allowed_languages)
}

# 필터 결과 확인
filters_passed(filter_results) {
    common.all_filters_passed(filter_results)
}
