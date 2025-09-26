package promptgate.common

# 언어 감지 헬퍼
detect_language(text) = "ko" {
    korean_chars := count([c | c := text[_]; c >= "\uac00"; c <= "\ud7af"])
    total_chars := count([c | c := text[_]; c >= "a"; c <= "z"] + [c | c := text[_]; c >= "A"; c <= "Z"] + [c | c := text[_]; c >= "\uac00"; c <= "\ud7af"])
    korean_chars / total_chars > 0.3
}

detect_language(text) = "en" {
    not detect_language(text) == "ko"
}

# 시크릿 패턴 검사
contains_aws_key(text) {
    regex.match("AKIA[0-9A-Z]{16}", text)
}

contains_openai_key(text) {
    regex.match("sk-[a-zA-Z0-9]{48}", text)
}

contains_bearer_token(text) {
    regex.match("Bearer\\s+[a-zA-Z0-9\\-_]+", text)
}

# 프롬프트 인젝션 패턴 검사
contains_ignore_instructions(text) {
    regex.match("(?i)ignore\\s+(all\\s+)?previous\\s+(instructions?|rules?)", text)
}

contains_admin_password(text) {
    regex.match("(?i)admin(istrator)?\\s+password", text)
}

contains_system_prompt(text) {
    regex.match("(?i)system\\s+prompt", text)
}

contains_jailbreak(text) {
    regex.match("(?i)jailbreak", text)
}

# PII 패턴 검사
contains_korean_rrn(text) {
    regex.match("\\b\\d{6}-\\d{7}\\b", text)
}

contains_phone_number(text) {
    regex.match("\\b01[016789]-\\d{3,4}-\\d{4}\\b", text)
}

contains_card_number(text) {
    regex.match("\\b\\d{4}-\\d{4}-\\d{4}-\\d{4}\\b", text)
}

# 프롬프트 길이 검증
is_valid_length(length, max_length) {
    length <= max_length
}

# 언어 허용 여부 확인
is_allowed_language(language, allowed_languages) {
    language in allowed_languages
}

# 필터 결과 검증
all_filters_passed(filter_results) {
    count(filter_results) == 0
}

all_filters_passed(filter_results) {
    all([result | result := filter_results[_]; result.action == "allow"])
}

# 위험도 계산
calculate_risk_score(violations) = risk_score {
    secret_violations := count([v | v := violations[_]; v == "secret_detected"])
    injection_violations := count([v | v := violations[_]; v == "injection_detected"])
    pii_violations := count([v | v := violations[_]; v == "pii_detected"])
    
    risk_score := (secret_violations * 1.0) + (injection_violations * 0.9) + (pii_violations * 0.7)
    risk_score <= 1.0
}

calculate_risk_score(violations) = 0.0 {
    count(violations) == 0
}
