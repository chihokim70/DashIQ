package promptgate.deny

import data.promptgate.common

# 거부 사유들
deny_reasons = [
    "secret_detected",
    "injection_detected", 
    "pii_detected",
    "prompt_too_long",
    "language_not_allowed",
    "tenant_not_found",
    "user_unauthorized",
    "filters_failed"
]

# 시크릿 정보 탐지로 인한 거부
deny_secret_detected {
    common.contains_aws_key(input.prompt.text)
}

deny_secret_detected {
    common.contains_openai_key(input.prompt.text)
}

deny_secret_detected {
    common.contains_bearer_token(input.prompt.text)
}

# 프롬프트 인젝션 탐지로 인한 거부
deny_injection_detected {
    common.contains_ignore_instructions(input.prompt.text)
}

deny_injection_detected {
    common.contains_admin_password(input.prompt.text)
}

deny_injection_detected {
    common.contains_system_prompt(input.prompt.text)
}

deny_injection_detected {
    common.contains_jailbreak(input.prompt.text)
}

# PII 탐지로 인한 거부
deny_pii_detected {
    common.contains_korean_rrn(input.prompt.text)
}

deny_pii_detected {
    common.contains_phone_number(input.prompt.text)
}

deny_pii_detected {
    common.contains_card_number(input.prompt.text)
}

# 프롬프트 길이 초과로 인한 거부
deny_prompt_too_long {
    tenant_policy := data.promptgate.policies[input.tenant]
    max_length := tenant_policy.rules.max_prompt_length
    not common.is_valid_length(input.prompt.length, max_length)
}

# 언어 미허용으로 인한 거부
deny_language_not_allowed {
    tenant_policy := data.promptgate.policies[input.tenant]
    allowed_languages := tenant_policy.rules.allowed_languages
    not common.is_allowed_language(input.prompt.language, allowed_languages)
}

# 테넌트 미존재로 인한 거부
deny_tenant_not_found {
    not data.promptgate.policies[input.tenant]
}

# 사용자 미인증으로 인한 거부
deny_user_unauthorized {
    input.user.id == ""
}

# 필터 실패로 인한 거부
deny_filters_failed {
    not common.all_filters_passed(input.filter_results)
}

# 거부 사유 수집
violations = [
    "secret_detected" |
    deny_secret_detected
]

violations = [
    "injection_detected" |
    deny_injection_detected
]

violations = [
    "pii_detected" |
    deny_pii_detected
]

violations = [
    "prompt_too_long" |
    deny_prompt_too_long
]

violations = [
    "language_not_allowed" |
    deny_language_not_allowed
]

violations = [
    "tenant_not_found" |
    deny_tenant_not_found
]

violations = [
    "user_unauthorized" |
    deny_user_unauthorized
]

violations = [
    "filters_failed" |
    deny_filters_failed
]

# 위험도 점수 계산
risk_score = score {
    score := common.calculate_risk_score(violations)
}
