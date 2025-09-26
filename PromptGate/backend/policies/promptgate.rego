package promptgate

import data.promptgate.allow
import data.promptgate.deny
import data.promptgate.obligations
import data.promptgate.common

# 메인 허용 정책
allow = allow.allow

# 거부 사유
violations = deny.violations

# 위험도 점수
risk_score = deny.risk_score

# 활성 의무
active_obligations = obligations.active_obligations

# 정책 평가 결과 메타데이터
metadata = {
    "tenant": input.tenant,
    "user_id": input.user.id,
    "prompt_length": input.prompt.length,
    "language": input.prompt.language,
    "evaluation_time": time.now_ns(),
    "policy_version": "v2.0",
    "evaluation_method": "modular"
}
