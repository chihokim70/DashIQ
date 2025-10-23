package promptgate

# 기본 허용 정책
default allow = false

# 허용 조건
allow {
    # 사용자 ID가 존재
    input.user.id != ""
    
    # 프롬프트 텍스트가 존재
    input.prompt.text != ""
    
    # 프롬프트 길이가 5000자 이하
    count(input.prompt.text) <= 5000
    
    # 시크릿 정보가 포함되지 않음
    not contains_secrets(input.prompt.text)
    
    # 프롬프트 인젝션이 포함되지 않음
    not contains_injection(input.prompt.text)
    
    # PII가 포함되지 않음
    not contains_pii(input.prompt.text)
}

# 시크릿 정보 포함 여부 확인
contains_secrets(text) {
    regex.match("AKIA[0-9A-Z]{16}", text)
}

contains_secrets(text) {
    regex.match("sk-[a-zA-Z0-9]{48}", text)
}

contains_secrets(text) {
    regex.match("Bearer\\s+[a-zA-Z0-9\\-_]+", text)
}

# 프롬프트 인젝션 패턴 확인
contains_injection(text) {
    regex.match("(?i)ignore\\s+(all\\s+)?previous\\s+(instructions?|rules?)", text)
}

contains_injection(text) {
    regex.match("(?i)admin(istrator)?\\s+password", text)
}

contains_injection(text) {
    regex.match("(?i)system\\s+prompt", text)
}

contains_injection(text) {
    regex.match("(?i)jailbreak", text)
}

# PII 패턴 확인
contains_pii(text) {
    regex.match("\\b\\d{6}-\\d{7}\\b", text)
}

contains_pii(text) {
    regex.match("\\b01[016789]-\\d{3,4}-\\d{4}\\b", text)
}

contains_pii(text) {
    regex.match("\\b\\d{4}-\\d{4}-\\d{4}-\\d{4}\\b", text)
}

# 거부 사유
violations = [
    "secret_detected" |
    contains_secrets(input.prompt.text)
]

violations = [
    "injection_detected" |
    contains_injection(input.prompt.text)
]

violations = [
    "pii_detected" |
    contains_pii(input.prompt.text)
]

violations = [
    "prompt_too_long" |
    count(input.prompt.text) > 5000
]

violations = [
    "user_unauthorized" |
    input.user.id == ""
]

# 위험도 점수 계산
risk_score = score {
    secret_count := count([v | v := violations[_]; v == "secret_detected"])
    injection_count := count([v | v := violations[_]; v == "injection_detected"])
    pii_count := count([v | v := violations[_]; v == "pii_detected"])
    
    score := (secret_count * 1.0) + (injection_count * 0.9) + (pii_count * 0.7)
}

risk_score = 0.0 {
    count(violations) == 0
}

# 정책 평가 결과 메타데이터
metadata = {
    "user_id": input.user.id,
    "prompt_length": count(input.prompt.text),
    "evaluation_time": time.now_ns(),
    "policy_version": "v1.0",
    "evaluation_method": "simple"
}


