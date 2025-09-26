package promptgate.obligations

import data.promptgate.common

# 의무 사항들 (거부되지 않더라도 수행해야 할 것들)
obligations = [
    "mask_pii",
    "sanitize_prompt", 
    "log_request",
    "audit_trail",
    "rate_limit_check",
    "quota_check"
]

# PII 마스킹 의무
obligation_mask_pii {
    common.contains_korean_rrn(input.prompt.text)
}

obligation_mask_pii {
    common.contains_phone_number(input.prompt.text)
}

obligation_mask_pii {
    common.contains_card_number(input.prompt.text)
}

# 프롬프트 정화 의무
obligation_sanitize_prompt {
    common.contains_ignore_instructions(input.prompt.text)
}

obligation_sanitize_prompt {
    common.contains_admin_password(input.prompt.text)
}

obligation_sanitize_prompt {
    common.contains_system_prompt(input.prompt.text)
}

obligation_sanitize_prompt {
    common.contains_jailbreak(input.prompt.text)
}

# 요청 로깅 의무 (모든 요청)
obligation_log_request {
    true
}

# 감사 추적 의무 (모든 요청)
obligation_audit_trail {
    true
}

# 속도 제한 확인 의무
obligation_rate_limit_check {
    # 사용자별 속도 제한 확인
    user_id := input.user.id
    user_id != ""
}

# 할당량 확인 의무
obligation_quota_check {
    # 사용자별 할당량 확인
    user_id := input.user.id
    user_id != ""
}

# 활성 의무 수집
active_obligations = [
    "mask_pii" |
    obligation_mask_pii
]

active_obligations = [
    "sanitize_prompt" |
    obligation_sanitize_prompt
]

active_obligations = [
    "log_request" |
    obligation_log_request
]

active_obligations = [
    "audit_trail" |
    obligation_audit_trail
]

active_obligations = [
    "rate_limit_check" |
    obligation_rate_limit_check
]

active_obligations = [
    "quota_check" |
    obligation_quota_check
]

# 의무 우선순위
obligation_priority = {
    "mask_pii": 1,
    "sanitize_prompt": 2,
    "log_request": 3,
    "audit_trail": 4,
    "rate_limit_check": 5,
    "quota_check": 6
}

# 우선순위별 의무 정렬
sorted_obligations = sorted_obligations {
    obligations_with_priority := [
        {"obligation": obl, "priority": obligation_priority[obl]} |
        obl := active_obligations[_]
    ]
    
    sorted_obligations := [
        obl.obligation |
        obl := obligations_with_priority[_]
        sort(obligations_with_priority, obligations_with_priority[_].priority)
    ]
}
