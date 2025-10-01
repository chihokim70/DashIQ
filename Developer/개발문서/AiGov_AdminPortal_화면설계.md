# 🛠 AiGov Admin Portal 주요 화면 구성 설계
> 대상: **Shadown AI 탐지 모듈**, **내부 LLM(향후 추가)** 모듈을 포함한 운영/보안 관점의 관리자 포털  
> 목표: 정책 중심(OPA), 필터 파이프라인(PEP), 섀도우 AI 가시화/차단, 내부 LLM 운영/평가를 **한 포털에서** 관리

---

## 0. 사용자 페르소나 & 권한(RBAC)
- **Org Admin**: 테넌트/사용자/역할 관리, 전역 설정
- **SecOps(보안운영)**: 정책/차단/승인흐름, 감사/알림
- **ML/Ops**: 내부 LLM 등록/배포/평가, 가드레일 설정
- **Auditor**: 읽기 전용(감사 로그/리포트 접근)
> 역할은 OPA 정책과 연동, 포털은 권한에 따른 메뉴/액션 가시화

---

## 1. 정보구조(IA) & 내비게이션
```
Dashboard
 ├─ Shadow AI
 │   ├─ 탐지 현황(리스크 지도)
 │   ├─ 에이전트/앱 식별 목록
 │   ├─ 차단/허용/승인 워크플로우
 │   └─ 소스(네트워크/프록시/SSO) 통합
 ├─ Policies
 │   ├─ Prompt Filters (Static/Secret/PII/Rebuff/ML/Embedding)
 │   ├─ OPA Bundles (버전/카나리/서명)
 │   ├─ Allowlist/Blocklist
 │   └─ Approval Rules
 ├─ LLM (Internal)
 │   ├─ Model Registry
 │   ├─ Safety & Guardrails
 │   ├─ Prompt Templates
 │   ├─ Eval & Monitoring
 │   └─ Traffic Routing (AB/Canary)
 ├─ Tenants & Access
 │   ├─ 테넌트/역할/사용자
 │   └─ API 토큰/SSO연동
 ├─ Audit & Logs
 │   ├─ Decisions(allow/deny/obligations)
 │   ├─ Incidents & Cases
 │   └─ Report/Export
 ├─ Alerts
 │   ├─ 임계치 기반 알림 규칙
 │   └─ 통합 알림 채널(Slack/Email/Webhook)
 └─ Settings
     ├─ Integrations(Proxy, SSO, SIEM, VectorDB)
     ├─ 시스템 파라미터(타임아웃/한도/보존)
     └─ 키 관리(KMS/Vault)
```

---

## 2. 대시보드(전역)
- **요약 KPI**: 총 요청, 차단율, 마스킹율, 평균 정책 지연, 상위 차단 사유 Top5
- **Shadow AI Top Sources**: 미인가 LLM/에이전트 탐지 상위 출처(앱/도메인/사용자)
- **내부 LLM 상태**: 가용 모델 수, 최신 배포 버전, 최근 품질지표(ASR/LlamaIndex 등 커스텀)
- **정책 변화 알림**: 최근 번들 배포, 카나리 결과, 롤백 이력
- **보안 이벤트**: 중대 사건(Secrets 유출 시도, 고위험 인젝션)

---

## 3. Shadow AI 모듈 화면
### 3.1 탐지 현황
- **리스크 트렌드**: 일/주간 Shadow AI 호출량, 차단/허용 추세
- **탐지 소스 매핑**: SSO/프록시/DNS 로그에서 추출한 **앱/도메인/클라이언트** 매핑
- **탐지 기준**: 미등록 LLM/에이전트, 외부 SaaS AI, 개인 액세스 토큰 사용

### 3.2 에이전트/앱 식별 리스트
- 컬럼: 이름/유형(웹/데스크톱/브라우저 확장)/출처/최초 탐지/최근 활동/리스크 점수/상태(차단/허용/승인필요)
- 행 액션: **차단**, **준수등록(Allow with constraints)**, **승인 요청 생성**

### 3.3 정책적용 & 시나리오
- **자동 차단 규칙**: 임계치 초과/특정 도메인/국가 차단
- **조건부 허용**: 마스킹 필수, 토큰 사용 제한, 데이터 카테고리 제한
- **승인 워크플로우**: 요청자 → 보안 검토 → 기간/범위 승인 → 만료 자동화

### 3.4 이벤트 상세(드릴다운)
- **요청 컨텍스트**(사용자/디바이스/네트워크/테넌트)
- **프롬프트 스냅샷**(민감정보 마스킹)
- **탐지 근거**(룰/모델 스코어, OPA 정책 버전, 결정 사유)
- **대응 버튼**: 차단/허용/승인/정책 생성으로 이동

---

## 4. Policies (필터/OPA) 화면
### 4.1 Prompt Filters
- 탭: Static(Regex/Vectorscan), Secret, PII, Rebuff, ML Classifier, Embedding
- 각 탭 공통:
  - **룰 편집기**(YAML/JSON 폼), **미리보기 테스트**(샘플 입력 → 탐지 결과)
  - **테넌트 스코프**, **임계치**, **예외 경로**
  - **드라이런 모드**(log-only)
- 저장 → **Draft** → **Submit** → **2인 승인** → **Publish**

### 4.2 OPA Bundles
- 버전/채널(`staging`, `canary`, `prod`), **서명 상태**, **최근 적용 노드 수**
- **Canary 슬라이더**(트래픽 %), **롤백** 버튼
- 번들 diff(정책 변경점 하이라이트), `opa test` 결과/커버리지

### 4.3 Allow/Block Lists
- 도메인/패턴/사용자/테넌트별 예외
- 만료일/사유/감사 라벨

### 4.4 Approval Rules
- 누가/무엇을/얼마나 기간 동안 승인할 수 있는지
- 조건: 리스크 점수, 데이터 카테고리, 시간대, 조직

---

## 5. LLM(Internal) 모듈 화면
### 5.1 Model Registry
- 모델 카드: 이름, 버전, 파라미터(크기/정밀도), 아티팩트 경로, 호환 하드웨어
- 상태: `staging/canary/prod`, 헬스체크, TPS/지연
- 액션: 배포/일시중지/롤백

### 5.2 Safety & Guardrails
- **정책 연결**: OPA 정책 버전 핀ning
- **가드레일**: 금칙 응답 카테고리, 컨텍스트 길이 제한, 토큰 상한
- **출력 필터**: PII/Secret 유출 방지 마스킹 규칙

### 5.3 Prompt Templates
- 시스템/도메인 템플릿 관리, 변수 스키마, 버전
- A/B 실험(템플릿 버전 간 비교), 사용 통계

### 5.4 Eval & Monitoring
- 평가 세트 등록(질문-정답/헛소리/안전성 항목)
- 자동 평가 파이프라인(정확성/금칙응답/독성/보안득점)
- 실사용 텔레메트리: 만족도, 래티시, 오류율

### 5.5 Traffic Routing
- AB/Canary 비율 조정, 테넌트별 라우팅, 폴백 체계
- 외부 LLM 대비 내부 LLM 우선순위

---

## 6. Tenants & Access
- 테넌트 생성/설정: 데이터 지역, 보존/암호화 정책
- 사용자/역할 매핑(RBAC), API 키/토큰 발급(권한 스코프)
- SSO(SAML/OIDC) 연동 상태

---

## 7. Audit & Logs
- **Policy Decisions**: allow/deny/obligations, 정책 버전, 근거
- **Incidents & Cases**: 사건 티켓화, 상태/담당/조치 결과
- **리포트**: 월간 요약, 규제준수(PII/시크릿 차단 통계), CSV/PDF Export

---

## 8. Alerts
- 규칙: 차단율 급증, 인젝션 탐지 급증, Secret 탐지 임계 초과
- 채널: Slack/Email/Webhook, 소음 억제(에스컬레이션, 스로틀링)
- 유지보수: 사일런스 기간/캘린더

---

## 9. Settings & Integrations
- Proxy/Ingress, SIEM(ELK), Metrics(Prometheus), VectorDB(Qdrant), KMS/Vault
- 시스템 파라미터: 입력 크기 상한, 타임아웃, Fail-Closed/Fail-Open 정책
- 키 회전 주기/권한, 정책 번들 서명 설정(Cosign)

---

## 10. 핵심 워크플로우(예시)
### 10.1 섀도우 AI 차단
1) 탐지 → 2) 이벤트 상세 확인 → 3) 차단/조건부 허용 → 4) 정책/예외 생성 → 5) 카나리 → 6) 배포

### 10.2 새 필터 규칙 도입
1) Draft 작성 → 2) 샘플 테스트 → 3) 2인 승인 → 4) OPA 번들 빌드/서명 → 5) Canary → 6) Prod

### 10.3 내부 LLM 새 버전 배포
1) 모델 업로드 → 2) Eval → 3) Canary 라우팅 → 4) KPI 임계 충족 시 Promote → 5) 롤백 옵션 유지

---

## 11. 데이터 모델(요약)
- `shadow_agent(id, name, type, source, risk, status, first_seen, last_seen)`
- `policy_bundle(id, version, channel, signed_digest, created_by, created_at)`
- `filter_rule(id, bundle_id, type, pattern, threshold, action, tenant_scope, enabled)`
- `allowlist(id, bundle_id, value, scope, expire_at)`
- `decision_log(id, ts, tenant, user, reason[], bundle_version, latency_ms)`
- `model_registry(id, name, version, params, status, tps, latency_ms)`
- `eval_result(id, model_id, suite, score, safety, timestamp)`

---

## 12. 화면 와이어프레임(간단 ASCII)
### Dashboard
```
+--------------------------------------------------------------+
| KPI: Total Req | Block % | Mask % | p95 Lat | OPA Ver | LLM | |
+----------------+---------+--------+---------+---------+-----+
| Shadow AI Top Sources       | Recent Policy Changes         |
| [list..]                    | [diff..]                      |
+-----------------------------+-------------------------------+
| Incidents (High)            | Internal LLM Health           |
| [cards..]                   | [gauges..]                    |
+--------------------------------------------------------------+
```

### Shadow AI List
```
Name      Type     Source     Risk  Status   Last Seen   Actions
---------------------------------------------------------------
ChatX     WebApp   proxy-1    87    Blocked  09-26 11:03 View | Allow | Approve
...
```

### Policies - Filters (Secret)
```
[Rules Editor YAML]        [Test Input]  [Run]
Pattern  Action  Tenant  Enabled
--------------------------------
AKIA..   block   *       ✔
JWT..    redact  finance ✔
```

### LLM - Registry
```
Model         Ver  Status   Lat  TPS  Channel  Actions
------------------------------------------------------
Aigov-7B      1.3  Canary   45   120  20%      Promote | Pause | Rollback
...
```

---

## 13. 기술 선택(권장)
- **프론트**: Next.js(+TypeScript), shadcn/ui, Recharts
- **백엔드(Portal API)**: FastAPI, SQLModel/SQLAlchemy
- **정책**: OPA(Bundle, Rego), Cosign 서명
- **로그/지표**: ELK, Prometheus/Grafana, Sentry
- **인증**: OIDC/Keycloak, RBAC는 OPA와 연합
- **배포**: Docker/K8s, ArgoCD, GitOps

---

## 14. 보안/운영 수칙
- 2인 승인, 번들 서명/검증, Deny-by-default, Fail-Closed 기본
- 민감정보 로그 마스킹, 데이터 보존정책, 테넌트 격리
- 카나리/롤백 표준 절차, 혼선 방지용 배너/배지(채널 표시)
