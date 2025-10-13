# 🧩 AiGov용 Supabase 보안 아키텍처 설계서  
**Version:** 2025.10  
**작성자:** KRASE (김치호)  
**작성 목적:** Supabase를 AiGov 환경에 도입 시 발생 가능한 보안 리스크 분석 및 안전한 운영 아키텍처 정의

---

## 1️⃣ 개요

Supabase는 Firebase의 오픈소스 대체 플랫폼으로, 빠른 프로토타입 개발에 적합하다.  
그러나 AiGov와 같은 **기업용 AI 보안·정책 관리 솔루션**에서는  
데이터 보호, 접근 통제, 네트워크 경계, 규제 준수 등의 보안요소를 강화해야 한다.

이 문서는 Supabase를 AiGov 백엔드 일부로 통합할 때  
**Cloud형**과 **Self-host형**의 보안 아키텍처를 비교하고  
권장 설계 방향을 제시한다.

---

## 2️⃣ Supabase 기본 구성요소

| 구성요소 | 역할 | 설명 |
|-----------|------|------|
| **PostgreSQL** | 데이터 저장 | 완전한 RDBMS (SQL, View, Function, Extension 지원) |
| **Auth** | 사용자 인증 및 권한 관리 | 이메일, OAuth, JWT 기반 Role 제어 |
| **Storage** | 파일 저장소 | 이미지, 문서, 정책 파일 등 |
| **Realtime** | 실시간 데이터 동기화 | DB 변경 이벤트 WebSocket 전송 |
| **Edge Functions** | 서버리스 백엔드 로직 | JavaScript/TypeScript 기반 API 함수 |
| **API Gateway** | REST/GraphQL 인터페이스 | 클라이언트 직접 호출 또는 Proxy 중계 가능 |

---

## 3️⃣ 보안 리스크 요약

| 구분 | 리스크 내용 | 영향도 | 발생 원인 |
|------|--------------|----------|------------|
| ① | API Key 노출 (`anon`, `service_role`) | ★★★★★ | 클라이언트 코드 내 포함 |
| ② | RLS 미적용 | ★★★★★ | 데이터 접근통제 부재 |
| ③ | Storage 퍼블릭 설정 오류 | ★★★★☆ | URL 접근제어 미비 |
| ④ | Edge Function 무단 호출 | ★★★★☆ | 인증 로직 누락 |
| ⑤ | Cloud 리전 외부 저장 | ★★★★☆ | 데이터 주권 문제 |
| ⑥ | 감사로그 미비 | ★★★☆☆ | pgaudit 미설치 |
| ⑦ | 버전 업데이트 불안정 | ★★★☆☆ | 자동 패치 시 장애 가능 |

---

## 4️⃣ 보안 대응 전략

### 🔐 (1) RLS(Row Level Security) 활성화
모든 테이블에 RLS 적용 필수.  
`auth.uid()`와 `user_id`를 매핑하여 사용자 단위 접근통제.

```sql
ALTER TABLE public.prompts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "User can access own records"
ON public.prompts
FOR SELECT
USING (auth.uid() = user_id);
```

---

### 🧱 (2) Proxy Server 계층 추가
Supabase API를 직접 노출하지 않고,  
**AiGov Proxy Gateway(FastAPI 기반)** 를 중간 계층으로 구성.

```
[Frontend UI]
   ↓
[PromptGate / Admin Portal]
   ↓
[Proxy Server (Auth + OPA 정책)]
   ↓
[Supabase API (DB / Storage)]
```

**장점:**
- API Key 노출 차단  
- 중앙 정책(OPA, JWT 검증) 일원화  
- 요청 로깅 및 감사 추적 가능  

---

### 🧩 (3) Self-hosting (Docker 기반)
보안·규제 요건이 높은 경우 다음 구조로 내부망에 배포한다.

```
[Internal Network / Private VPC]
├── supabase-db (PostgreSQL)
├── supabase-auth
├── supabase-rest
├── supabase-realtime
├── supabase-storage
└── supabase-functions
```

**Docker Compose 예시:**
```bash
docker-compose up -d
```

**장점:**
- 데이터 주권 확보 (국내 리전)
- 보안정책 직접 통제 가능
- OPA, SIEM, WAF 등 연동 용이

---

### 🧮 (4) RBAC + OPA 통합 정책
- Supabase Auth → Role Claim(`auth.role`) 추출  
- OPA Policy Server → 접근허용 여부 결정  

예시 (Rego Policy):
```rego
package ai.policy

allow {
  input.auth.role == "admin"
  input.resource == "policy_config"
}
```

---

### 🧾 (5) Audit 및 로그 관리
- PostgreSQL 확장 모듈 `pgaudit` 활성화  
- Supabase Event Hooks를 통해 AiGov Audit DB로 전송  
- Prometheus + Grafana 기반 모니터링 대시보드 구성  

---

## 5️⃣ Cloud형 vs Self-host형 비교표

| 구분 | **Supabase Cloud형** | **Supabase Self-host형 (권장)** |
|------|----------------------|--------------------------------|
| **데이터 위치** | Supabase 리전(해외 서버) | 자체 서버 / 국내 리전 |
| **데이터 주권** | 외부 의존 | 완전 통제 가능 |
| **보안정책** | Supabase 내부정책 한정 | OPA/RLS 등 자유 설정 |
| **API Key 관리** | Cloud Dashboard | Vault 또는 Docker Secret |
| **접근 제어** | JWT + 정책 | Proxy + OPA + RLS |
| **운영비용** | 월 과금 | 초기 구축비 + 서버 유지비 |
| **유지보수** | Supabase 자동 업데이트 | 버전 고정 및 수동 관리 |
| **적합도** | MVP / PoC / 시범사업 | 본운영 / 공공 / 금융기관 |

---

## 6️⃣ AiGov 환경 권장 아키텍처 (Self-host형)

```text
+-----------------------------------------------------------+
|                   AiGov Secure Network                    |
|-----------------------------------------------------------|
| [Frontend: Admin Portal / Proxy UI]                       |
|        ↓                                                  |
| [AiGov Proxy Gateway (FastAPI + OPA + JWT 검증)]          |
|        ↓                                                  |
| [Supabase Backend (Self-host, Private VPC)]               |
|     ├── PostgreSQL (RLS 활성화)                           |
|     ├── Auth Service (Role Claim 관리)                    |
|     ├── Storage (Private bucket + Signed URL)             |
|     ├── Edge Functions (서버리스 로직)                    |
|     └── Realtime (내부 네트워크 한정)                     |
|-----------------------------------------------------------|
| [Audit/Monitoring Layer]                                  |
|     ├── pgaudit / syslog                                  |
|     ├── Prometheus / Grafana                              |
|     └── ElasticSearch (로그 인덱싱)                       |
+-----------------------------------------------------------+
```

---

## 7️⃣ 운영 시 체크리스트

| 구분 | 점검항목 | 주기 | 담당 |
|------|-----------|------|------|
| RLS 정책 검증 | 사용자별 Row 접근 테스트 | 월 1회 | 보안담당 |
| API Key 관리 | Vault Secret 변경 | 월 1회 | 운영팀 |
| Storage 접근 | Public URL 탐지 | 분기 1회 | 보안팀 |
| Edge Function 취약점 | 인증/검증 로직 점검 | 월 1회 | 개발팀 |
| Audit Log 검토 | 이상 행위 탐지 | 주 1회 | 보안팀 |

---

## 8️⃣ 결론

- **MVP 단계:** Supabase Cloud를 활용해 빠른 프로토타입 구축  
- **PoC 이후:** Proxy Server + RLS 정책으로 보안 강화  
- **운영 단계:** Self-hosting + Private VPC + OPA 통합  
- **장기 목표:** AiGov의 **PromptGate / Admin Portal / ShadowScan** 등과 통합하여  
  **정책 기반 통합 AI 거버넌스 아키텍처 완성**

---

## 📚 참고문헌
- [Supabase 공식문서](https://supabase.com/docs)
- [PostgreSQL RLS 가이드](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [Open Policy Agent (OPA)](https://www.openpolicyagent.org/)
- [pgaudit Extension](https://www.pgaudit.org/)
- KISA 「AI 서비스 보안 가이드라인」 (2024)

---

**© 2025 KRASE. All Rights Reserved.**
