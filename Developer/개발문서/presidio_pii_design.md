# Presidio 기반 PII 탐지 기능 기술 설계 & DB 설계 (PromptGate / AiGov)
_v1.0 · 2025-09-29 · 작성자: ChatGPT (설계 초안)_

> 목적: AiGov의 **PromptGate → Prompt Filter Service** 내에 **Microsoft Presidio**를 활용한 PII(개인식별정보) 탐지/마스킹/차단 기능을 설계하고, **PostgreSQL/Elasticsearch** 기반의 정책·로그 스키마를 정의한다.  
> 범위: 탐지 파이프라인, 정책 제어, 관리자 포털 연계(API), DB/Index 설계, 운영/보안/성능/테스트, 배포 및 관찰성.

---

## 1. 전체 아키텍처 개요

```
[Client/Employee]
    ↓  (Prompt/Completion)
[PromptGateway API]
    ↓
[Prompt Filter Service (FastAPI, Async)]
  ├─ ① 룰 기반 필터(금칙어/주제)
  ├─ ② PII 탐지기 (Presidio: Analyzer + Anonymizer)
  │      ├─ Regex Recognizers (주민등록번호, 전화, 이메일, 카드, 계좌 등)
  │      └─ NER Model (spaCy/HF, ko 지원 커스텀 가능)
  ├─ ③ 컨텍스트 방어(Rebuff/Guardrails)
  ├─ ④ 정책 결정(마스킹/차단/허용) + OPA(선택)
  ├─ ⑤ 감사 로깅(Postgres + Elasticsearch)
    ↓
[Allowed Prompt → LLM Provider(s)]
```

- **핵심 포인트**
  - Presidio **Analyzer**로 PII 엔티티 탐지 → 정책에 따라 **Anonymizer**로 마스킹/치환 → **차단(DENY)** 시 상위 레이어에 에러 반환.
  - **정책(Policy)**, **패턴(Regex)**, **예외(Allow‑List)**를 Admin Portal에서 실시간 관리.
  - **PostgreSQL**: 정책/패턴/설정 저장 (**정합성/트랜잭션** 필요 영역).  
  - **Elasticsearch**: 탐지 이벤트/감사 로그/통계 질의(**대량 검색/시각화**)에 사용.

---

## 2. Presidio 구성 설계

### 2.1 Analyzer/Anonymizer 구성
- **AnalyzerEngine**: 텍스트에서 PII 엔티티 추출.
- **AnonymizerEngine**: 탐지 결과에 따라 마스킹·치환 수행.
- **Recognizer**: Regex/Heuristic/ML 기반 엔티티 인식기.
- **Supported Language**: `ko` (한국어). Regex/커스텀 Recognizer로 한글 패턴 보강.

### 2.2 기본 엔티티(초안)
| 엔티티 | 예시 | 탐지 방식 | 기본 조치 |
|---|---|---|---|
| PERSON_NAME | “홍길동” | ML(ko NER) + 사전 | 마스킹(`홍*동`) |
| KOR_RRN (주민등록번호) | `800101-1234567` | Regex + Checksum(선택) | 전면 마스킹 |
| PHONE_NUMBER | `010-1234-5678` | Regex | 중간 4자리 마스킹 |
| EMAIL_ADDRESS | `user@example.com` | Regex | 로컬파트 부분 마스킹 |
| CREDIT_CARD | `4111-1111-1111-1111` | Regex + Luhn | 중간 마스킹 |
| BANK_ACCOUNT | `123-456-7890123` | Regex | 전면/중간 마스킹 |
| ADDRESS | “서울시 강남구 ...” | ML(ko NER) | 토큰 단위 마스킹 |
| IP_ADDRESS | `192.168.0.1` | Regex | 전면 마스킹 |

> 필요 시 **사업자등록번호**, **여권번호**, **운전면허번호** 등 추가.

### 2.3 샘플 코드 (FastAPI 서비스 레벨)

```python
# app/pii/presidio.py
from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer, RecognizerResult
from presidio_anonymizer import AnonymizerEngine
from typing import List, Dict

analyzer = AnalyzerEngine()  # can inject custom registry
anonymizer = AnonymizerEngine()

# 예: 한국 휴대전화 간단 Regex (고도화는 정책 DB에서 로드)
from presidio_analyzer import PatternRecognizer
import re

phone_pattern = Pattern(name="ko_phone", regex=r"(?:\+82[-\s]?)?0?1[0-9][-]?\d{3,4}[-]?\d{4}", score=0.6)
phone_recognizer = PatternRecognizer(supported_entity="PHONE_NUMBER", patterns=[phone_pattern])

# Analyzer에 등록 (런타임에 동적 로딩도 가능)
analyzer.registry.add_recognizer(phone_recognizer)

def detect_pii(text: str, language: str = "ko"):
    return analyzer.analyze(text=text, entities=[], language=language)

def anonymize_text(text: str, results: List[RecognizerResult], policy_map: Dict[str, Dict]):
    # policy_map 예: {"PHONE_NUMBER": {"action": "mask", "masking_char": "*", "chars_to_mask": 4}}
    operators = {}
    for ent, conf in policy_map.items():
        action = conf.get("action", "mask")
        if action == "mask":
            operators[ent] = {"type": "mask", "masking_char": conf.get("masking_char", "*"), "chars_to_mask": conf.get("chars_to_mask", 8)}
        elif action == "replace":
            operators[ent] = {"type": "replace", "new_value": conf.get("new_value", "[REDACTED]")}
        elif action == "hash":
            operators[ent] = {"type": "hash", "hash_type": "sha256"}
        else:
            operators[ent] = {"type": "redact"}  # 전면 삭제

    return anonymizer.anonymize(text=text, analyzer_results=results, operators=operators).text
```

### 2.4 정책 적용 순서
1. **Allow‑List/Context 예외** 우선 적용 (예: 내부 테스트 데이터).
2. 엔티티 탐지(Analyzer) → 결과 스코어 기반 **신뢰도 임계치** 필터링.
3. 엔티티별 정책(Action=mask/replace/hash/deny/allow) 적용.
4. **deny** 포함 시 즉시 차단 응답 + 감사 로깅.
5. 마스킹·치환 결과를 LLM에 전달.

---

## 3. 정책/운영 모델

### 3.1 정책 계층
- **Global Policy**: 조직 공통 기본값 (예: RRN 무조건 차단).
- **Tenant/Project Policy**: 부서/서비스 별 예외(허용/완화).
- **Route/Model Policy**: 특정 LLM/벤더로 가는 트래픽에 별도 정책.

### 3.2 결정 매트릭스 (요약)

| 우선순위 | 조건 | 결과 |
|---|---|---|
| 1 | `entity.action == "deny"` | 요청 차단(HTTP 422 + 상세 코드) |
| 2 | `entity.action == "mask/replace/hash"` | 변환 후 전달 |
| 3 | `entity.action == "allow"` | 원문 전달 |
| 4 | 미정의 | Global 기본값 적용(보수적) |

### 3.3 OPA(Rego) 연계 (선택)
- 요청 컨텍스트(역할/부서/모델/시간대/위험점수)를 **OPA**에 전달 → `allow/deny/mutate` 결정.
- Presidio 결과를 OPA input에 포함해 **상황별 차등 정책** 가능.

```rego
package pii.policy

default decision = {"action": "mask"}

deny_entities := {"KOR_RRN", "CREDIT_CARD"}

decision = {"action": "deny"} {
  some r
  input.entities[r].type == deny_entities[_]
}

decision = {"action": "mask"} {
  input.user.role != "pii_admin"
}
```

---

## 4. Admin Portal 연계 (API 초안)

### 4.1 REST 엔드포인트 예시
- `GET /pii/policies` : 정책 조회 (스코프별 병합 결과 포함)
- `PUT /pii/policies/{scope}` : 정책 저장 (`global` / `tenant:{id}` / `route:{id}`)
- `GET /pii/patterns` : Regex/Recognizer 목록 조회
- `POST /pii/patterns` : 신규 패턴 등록 (정규식/스코어/엔티티/검증식)
- `PUT /pii/patterns/{id}` : 수정
- `DELETE /pii/patterns/{id}` : 삭제
- `POST /pii/patterns/import` : TOML/JSON Import
- `GET /pii/patterns/export` : TOML/JSON Export
- `GET /pii/events` : 탐지 이벤트 검색(ES)
- `GET /pii/stats` : 유형·모델·사용자 별 통계

### 4.2 TOML 예시 (패턴/정책 Export)

```toml
# pii_patterns.toml
[[patterns]]
id = "phone_kr_v1"
entity = "PHONE_NUMBER"
regex = "(?:\\+82[-\\s]?)?0?1[0-9][-]?\\d{3,4}[-]?\\d{4}"
score = 0.6
description = "KR mobile phone"

[[patterns]]
id = "rrn_kr_v1"
entity = "KOR_RRN"
regex = "\\b\\d{6}-\\d{7}\\b"
score = 0.8
description = "KR Resident Registration Number"

# policies
[policies.global]
"KOR_RRN" = { action = "deny" }
"PHONE_NUMBER" = { action = "mask", masking_char = "*", chars_to_mask = 6 }
"EMAIL_ADDRESS" = { action = "mask", masking_char = "*", chars_to_mask = 6 }

[policies."tenant:fin_div"]
"CREDIT_CARD" = { action = "deny" }
```

---

## 5. 데이터 모델 설계

### 5.1 PostgreSQL (정책/패턴/설정)

#### 5.1.1 ER 개요
```
pii_pattern (패턴 정의) 1─* pii_pattern_scope (*스코프 연결*)
pii_policy  (행동정책)  1─* pii_policy_entity (*엔티티별 액션*)
allowlist   (예외)      → scope 연계
```

#### 5.1.2 테이블 스키마 (초안)

```sql
-- 스코프: global, tenant:{id}, route:{id}
CREATE TABLE pii_scope (
  id SERIAL PRIMARY KEY,
  scope_key VARCHAR(128) UNIQUE NOT NULL,   -- e.g., 'global', 'tenant:123', 'route:pg_llama3'
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- 정규식/커스텀 패턴 (Presidio Recognizer에 주입)
CREATE TABLE pii_pattern (
  id SERIAL PRIMARY KEY,
  pattern_key VARCHAR(128) UNIQUE NOT NULL, -- 'phone_kr_v1'
  entity VARCHAR(64) NOT NULL,              -- 'PHONE_NUMBER', 'KOR_RRN'
  regex TEXT NOT NULL,
  score NUMERIC(3,2) DEFAULT 0.5,
  description TEXT,
  is_enabled BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- 패턴과 스코프 연결 (스코프별 enable/disable 가능)
CREATE TABLE pii_pattern_scope (
  id SERIAL PRIMARY KEY,
  pattern_id INT NOT NULL REFERENCES pii_pattern(id) ON DELETE CASCADE,
  scope_id INT NOT NULL REFERENCES pii_scope(id) ON DELETE CASCADE,
  is_enabled BOOLEAN DEFAULT TRUE,
  UNIQUE (pattern_id, scope_id)
);

-- 정책(스코프 단위)
CREATE TABLE pii_policy (
  id SERIAL PRIMARY KEY,
  scope_id INT NOT NULL REFERENCES pii_scope(id) ON DELETE CASCADE,
  name VARCHAR(128) NOT NULL,               -- 'default_policy'
  description TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  created_by VARCHAR(128),
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (scope_id, name)
);

-- 엔티티별 액션 설정
CREATE TABLE pii_policy_entity (
  id SERIAL PRIMARY KEY,
  policy_id INT NOT NULL REFERENCES pii_policy(id) ON DELETE CASCADE,
  entity VARCHAR(64) NOT NULL,
  action VARCHAR(16) NOT NULL,              -- 'deny' | 'mask' | 'replace' | 'hash' | 'allow'
  config JSONB DEFAULT '{}'::jsonb,         -- {masking_char, chars_to_mask, new_value, ...}
  UNIQUE (policy_id, entity)
);

-- 허용 예외(Allow-list)
CREATE TABLE pii_allowlist (
  id SERIAL PRIMARY KEY,
  scope_id INT NOT NULL REFERENCES pii_scope(id) ON DELETE CASCADE,
  pattern TEXT NOT NULL,                    -- 정규식/키워드
  description TEXT,
  is_enabled BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (scope_id, pattern)
);

-- Presidio 런타임 설정 (임계치 등)
CREATE TABLE pii_runtime_config (
  id SERIAL PRIMARY KEY,
  scope_id INT NOT NULL REFERENCES pii_scope(id) ON DELETE CASCADE,
  confidence_threshold NUMERIC(3,2) DEFAULT 0.5,
  language VARCHAR(8) DEFAULT 'ko',
  extra JSONB DEFAULT '{}'::jsonb,
  UNIQUE (scope_id)
);
```

**인덱스 권장**  
```sql
CREATE INDEX idx_pii_pattern_entity ON pii_pattern(entity);
CREATE INDEX idx_pii_policy_entity_entity ON pii_policy_entity(entity);
CREATE INDEX idx_pii_allowlist_scope ON pii_allowlist(scope_id);
```

### 5.2 Elasticsearch (이벤트/감사 로그)

#### 5.2.1 Index 설계
- 인덱스 이름: `pii-events-YYYY.MM` (월별 롤오버)
- 수명주기(ILM): 90~180일 보관(조직 정책에 맞춤)

#### 5.2.2 매핑(초안)
```json
{
  "mappings": {
    "properties": {
      "timestamp": { "type": "date" },
      "request_id": { "type": "keyword" },
      "user_id": { "type": "keyword" },
      "tenant_id": { "type": "keyword" },
      "route": { "type": "keyword" },
      "model": { "type": "keyword" },
      "source_ip": { "type": "ip" },
      "action": { "type": "keyword" },              
      "entities": {
        "type": "nested",
        "properties": {
          "type": { "type": "keyword" },
          "start": { "type": "integer" },
          "end": { "type": "integer" },
          "score": { "type": "float" }
        }
      },
      "original_prompt_hash": { "type": "keyword" },
      "masked_prompt": { "type": "text", "index": false },
      "decision": { "type": "keyword" },           
      "policy_scope": { "type": "keyword" },
      "policy_name": { "type": "keyword" },
      "latency_ms": { "type": "integer" }
    }
  }
}
```

> **개인정보 원문은 저장하지 않음**이 원칙. 필요 시 **해시(SHA‑256 + salt)** 로 원문 추적 가능성을 제공.

---

## 6. 처리 플로우 (시퀀스)

```
Client → PromptGateway → FilterSvc
  1) scope 식별(tenant/model/route)
  2) allowlist 매칭 → 예외 시 bypass
  3) Analyzer.analyze (ko)
  4) confidence >= threshold 만 유지
  5) 정책 조회(scope → merged policy)
  6) deny 엔티티 발견 시 즉시 차단 + ES 로그
  7) anonymizer 로 마스킹/치환/해시
  8) ES 이벤트 기록 + Postgres 카운터 업데이트(선택)
  9) LLM 요청 전송
```

---

## 7. 보안/개인정보 보호

- **원문 최소보관**: ES에는 원문 미저장. 필요 시 **부분 마스킹된 프롬프트**만 저장.
- **키 관리**: 해시 salt/비밀키는 Vault(KMS) 관리.
- **권한 분리**: 정책 편집자(pii_admin)와 운영자(viewer) RBAC 분리.
- **감사 추적**: 모든 정책 변경은 Postgres에 **감사 테이블**로 이력화.

```sql
CREATE TABLE audit_policy_change (
  id SERIAL PRIMARY KEY,
  actor VARCHAR(128) NOT NULL,
  scope_key VARCHAR(128) NOT NULL,
  change JSONB NOT NULL,         -- diff
  created_at TIMESTAMPTZ DEFAULT now()
);
```

---

## 8. 성능/가용성

- **비동기 I/O** (uvicorn + FastAPI) + **ThreadPool/ProcessPool** 로 Analyzer 호출 병렬화.
- 고빈도 Regex는 **Hyperscan**(선택) 또는 pre‑compiled 패턴 캐시.
- 배포: **K8s HPA**, **Pod anti‑affinity**, **read‑only root fs**.
- **콜드 스타트** 최소화를 위해 Recognizer 프리로드.
- **샘플 목표**: P50 < 20ms(PII 없음), P95 < 60ms(엔티티 3개 이내).

---

## 9. 테스트 전략

- **유닛 테스트**: 엔티티별 Regex/Anonymizer 동작 검증.
- **시나리오 테스트**: 차단/마스킹/허용 분기 검증.
- **회귀 테스트**: 패턴 업데이트 시 드리프트 점검.
- **오탐/미탐 측정**: 표본 세트(내부 생성 + 공개 샘플) 기반 Precision/Recall 추적.
- **부하 테스트**: 95퍼센타일 지연, QPS 한계, 스케일링 검증.

```python
def test_phone_masking():
    text = "연락처 010-1234-5678 로 주세요"
    results = detect_pii(text)
    policy = {"PHONE_NUMBER": {"action": "mask", "masking_char": "*", "chars_to_mask": 6}}
    out = anonymize_text(text, results, policy)
    assert "5678" in out and out.count("*") >= 6
```

---

## 10. 배포 & 운영

- **컨테이너화(Docker)**: `presidio-analyzer`, `presidio-anonymizer` 런타임 의존성 포함 베이스 이미지.
- **구성 주입**: 정책/패턴은 **DB → 런타임 캐시**로 주기적 동기화(예: 30초 폴링 or 이벤트 기반).
- **옵저버빌리티**: Prometheus 메트릭(처리량, 지연, 엔티티 분포, 차단율), Grafana 대시보드.
- **ES Kibana**: 유형별/테넌트별 PII 탐지 추이 모니터링.
- **릴리즈 관리**: 패턴 변경은 **Blue/Green** 또는 **canary** 롤아웃.

---

## 11. 예시: 주민등록번호/전화/이메일 마스킹 규칙

- **RRN(KOR_RRN)**: `\b\d{6}-\d{7}\b` → `***************` (전면 마스킹)
- **PHONE_NUMBER**: 중간 3~4자리 마스킹 → `010-****-****`
- **EMAIL_ADDRESS**: 로컬파트 중간 마스킹 → `u***@example.com`

> 실제 운영 Regex는 **더 엄격한 경계/검증**(룬/체크섬 등)을 권장.

---

## 12. 마이그레이션 가이드 (초기 데이터)

```sql
INSERT INTO pii_scope (scope_key, description) VALUES
('global', 'Global default'),
('tenant:fin_div', 'Finance division'),
('route:pg_llama3', 'PromptGateway route to Llama3');

INSERT INTO pii_policy (scope_id, name, description) VALUES
((SELECT id FROM pii_scope WHERE scope_key='global'), 'default', 'Global default PII policy');

INSERT INTO pii_policy_entity (policy_id, entity, action, config) VALUES
((SELECT id FROM pii_policy p JOIN pii_scope s ON p.scope_id=s.id WHERE s.scope_key='global' AND p.name='default'), 'KOR_RRN', 'deny', '{}'),
((SELECT id FROM pii_policy p JOIN pii_scope s ON p.scope_id=s.id WHERE s.scope_key='global' AND p.name='default'), 'PHONE_NUMBER', 'mask', '{"masking_char":"*","chars_to_mask":6}'),
((SELECT id FROM pii_policy p JOIN pii_scope s ON p.scope_id=s.id WHERE s.scope_key='global' AND p.name='default'), 'EMAIL_ADDRESS', 'mask', '{"masking_char":"*","chars_to_mask":6}');
```

---

## 13. 운영 체크리스트

- [ ] ES에 **원문 저장 금지** 확인 (mask된 필드만 저장).
- [ ] 정책 변경 시 **감사 로그** 생성 및 알림.
- [ ] 임계치/스코어 튜닝 절차 수립(월 1회 리뷰).
- [ ] 정규식 업데이트 시 회귀 테스트 패스.
- [ ] DR 백업: Postgres(정책), ES(이벤트) 스냅샷.
- [ ] 장애 시 Bypass/Safe‑fail 모드 정의(기본: **fail‑closed** 권장).

---

## 14. 향후 확장

- **문서·이미지 OCR PII** (pdf/png → 텍스트 추출 후 동일 파이프라인).
- **멀티모달**: 음성 전사(ASR) 후 PII 탐지.
- **학습 데이터 파이프라인**: 미탐 사례 수집 → ko NER 파인튜닝.

---

## 부록 A. FastAPI 엔드포인트 스켈레톤

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from .presidio import detect_pii, anonymize_text
from .policy import get_merged_policy_for_scope  # DB에서 스코프 병합 정책 로드

router = APIRouter(prefix="/filter")

class FilterRequest(BaseModel):
    text: str
    scope_key: str = "global"

@router.post("/pii")
async def filter_pii(req: FilterRequest):
    policy_map, deny_set, threshold = await get_merged_policy_for_scope(req.scope_key)
    results = detect_pii(req.text, language="ko")
    results = [r for r in results if r.score >= threshold]

    # deny 우선 평가
    if any(r.entity_type in deny_set for r in results):
        # ES 로그 전송 (생략)
        raise HTTPException(status_code=422, detail={"code": "PII_DENY", "msg": "PII policy deny"})

    masked = anonymize_text(req.text, results, policy_map)
    # ES 로그 전송 (생략)

    return {"masked_text": masked, "entities": [r.entity_type for r in results]}
```

---

## 부록 B. 운영 정책 샘플(요약)

- Global: RRN/CREDIT_CARD = **deny**, EMAIL/PHONE/BANK = **mask**, NAME/ADDRESS = **mask**  
- 금융 테넌트: BANK_ACCOUNT = **deny**, IP_ADDRESS = **mask**  
- 외부 테스트 라우트: 대부분 **allow**, 단 RRN은 **deny** 고정.

---

_끝. 피드백 주시면 DB 상세(인덱스/파티셔닝/권한), Admin Portal 화면 스펙, CI/CD 파이프라인 정의까지 이어서 확장하겠습니다._
