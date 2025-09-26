# 🛡 OPA(Open Policy Agent) 아키텍처

## 1) 전체 아키텍처 개요

```
[Client/Browser]
      │  HTTPS (JWT 포함)
      ▼
┌───────────────────────────────┐
│        FastAPI (PEP)          │  ← Policy Enforcement Point
│  - Auth/JWT 검증               │
│  - 프롬프트/메타데이터 수집    │
│  - OPA에 정책 질의 (PDP)       │
│  - allow/deny/obligation 적용  │
└───────────┬───────────┬───────┘
            │           │
            │ HTTP/gRPC │ Decision Logs
            ▼           ▼
┌────────────────┐   ┌──────────────────────┐
│   OPA (PDP)    │   │  Observability/Logs  │
│ - Rego 정책     │   │  - OpenSearch/ELK    │
│ - Data (테넌트) │   │  - Prometheus/Grafana │
│ - Partial Eval  │   │  - SIEM               │
└───────┬────────┘   └───────────┬──────────┘
        │  Bundle Pull/Sign       │
        ▼                         │
┌───────────────────────────────┐ │
│  Policy Registry (Bundle)     │ │
│  - Rego 정책 저장소(Git/OCI)  │ │
│  - Cosign 서명/검증           │ │
└───────────────────────────────┘ │
                                  │
               (옵션)             │
                ▼                 │
        ┌───────────────┐        │
        │ OPA WASM Lib  │  ← 핫패스는 Rego→WASM 컴파일 후
        │ (앱에 임베드) │     FastAPI 내부에서 로컬 평가
        └───────────────┘
```

---

## 2) 배포 패턴 (권장)

- **Sidecar PDP (권장)**: FastAPI Pod 옆에 OPA를 사이드카로 붙여 로컬 호출 (지연↓, 노출↓)
- **Central PDP**: 여러 서비스가 하나의 OPA 클러스터에 질의 (운영 단순·스케일 용이, 네트워크 레이턴시 고려)
- **WASM Embed**: 초저지연 필요 시 선택적으로 사용 (정책 일부만 내장, 나머지는 OPA)

---

## 3) 요청 흐름 (PromptGate 예)

1. FastAPI가 요청 수신 → JWT 검증, 테넌트/유저/네트워크/디바이스 정보 수집  
2. 프롬프트 입력을 필터 스택으로 검사 → risk_score, pii_found, secrets_count 등 산출  
3. PEP가 입력 JSON을 OPA에 질의  
4. OPA(Rego)가 allow/deny/obligation 결정 반환  
5. PEP가 결정에 따라 차단·마스킹·승인흐름 요청 등 실행  
6. 결정 로그/메트릭 기록

---

## 4) OPA 입력 스키마(예시)

```json
{
  "tenant": "kra-internal",
  "user": { "id": "u-123", "role": "analyst", "dept": "security" },
  "request": {
    "ip": "10.0.1.25",
    "path": "/llm/chat",
    "method": "POST",
    "time": "2025-09-26T03:05:00Z",
    "network": "corp"
  },
  "prompt": {
    "text": "고객 DB 비밀번호 알려줘",
    "risk_score": 82,
    "pii_found": true,
    "secrets_count": 1,
    "injection_flag": false
  },
  "context": {
    "work_mode": "production",
    "hour": 12,
    "locale": "ko-KR"
  }
}
```

---

## 5) Rego 정책 예시

**allow.rego**
```rego
package promptgate

default allow = false

allow {
  input.user.role == "admin"
}

allow {
  input.request.network == "corp"
  not high_risk
  not has_secrets
}

high_risk {
  input.prompt.risk_score >= 70
}

has_secrets {
  input.prompt.secrets_count > 0
}
```

**deny.rego**
```rego
package promptgate

deny[reason] {
  input.prompt.secrets_count > 0
  reason := "secrets_detected"
}

deny[reason] {
  input.prompt.pii_found
  reason := "pii_detected"
}

deny[reason] {
  input.prompt.risk_score >= 90
  reason := "risk_score_over_90"
}
```

**obligations.rego**
```rego
package promptgate

obligations[obj] {
  input.prompt.pii_found
  obj := {"action": "mask_pii"}
}

obligations[obj] {
  input.prompt.risk_score >= 70
  obj := {"action": "require_approval", "approver": "sec-team"}
}
```

---

## 6) FastAPI ↔ OPA 연동 예시

```python
import httpx
from fastapi import Request, HTTPException

OPA_URL = "http://localhost:8181/v1/data/promptgate"

async def ask_opa(decision_input: dict) -> dict:
    async with httpx.AsyncClient(timeout=1.0) as client:
        r = await client.post(OPA_URL, json={"input": decision_input})
        r.raise_for_status()
        return r.json().get("result", {})

async def enforce(request: Request, prompt_result: dict):
    decision_input = {
        "tenant": request.headers.get("X-Tenant"),
        "user": {"id": request.state.user_id, "role": request.state.user_role},
        "request": {
            "ip": request.client.host,
            "path": request.url.path,
            "method": request.method,
            "network": request.headers.get("X-Network", "corp"),
        },
        "prompt": prompt_result,
        "context": {"work_mode": "production"}
    }

    result = await ask_opa(decision_input)
    if not result.get("allow", False) or result.get("deny"):
        raise HTTPException(status_code=403, detail={"deny": result.get("deny", [])})

    for ob in result.get("obligations", []):
        if ob["action"] == "mask_pii":
            pass
        elif ob["action"] == "require_approval":
            pass

    return True
```

---

## 7) 정책 번들 & CI/CD 권장

1. PR 생성 시 `opa fmt`, `opa test` 자동 검사  
2. Cosign 서명 후 OCI 레지스트리에 push  
3. OPA가 주기적으로 pull + 서명 검증  
4. 스테이징 → 카나리 → 프로덕션 점진 배포

---

## 8) 성능/가용성 팁

- Partial Evaluation 활용 (사전 계산)  
- 입력 크기 제한 및 정규화  
- 타임아웃/서킷브레이커 설정  
- Sidecar 배치로 네트워크 지연 최소화  
- WASM으로 정책 일부를 앱에 임베드  

---

## 9) 감사/관측성

- Decision Logs: 테넌트, 정책버전, 결과, 사유 기록  
- 민감정보 마스킹  
- 메트릭: 결정 지연, allow/deny 비율 모니터링  

---

## 10) 실패 모드 전략

- Fail-Closed (권장): OPA 응답 없으면 차단  
- Fail-Open: 일부 가용성 우선 서비스만 예외  
- 드라이런 모드: 초기에는 allow 유지 + deny 사유만 기록
