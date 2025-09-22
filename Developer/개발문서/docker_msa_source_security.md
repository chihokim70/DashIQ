# Docker 기반 MSA 상용 솔루션 포팅 시 소스코드 보안 전략
작성일: 2025-06-23

---

## ✅ 1. 기본 전략: 소스코드를 이미지에 포함하지 않기

- Dockerfile에서 `COPY . .` 대신, **Build 후 생성된 실행 파일/패키지**만 이미지에 포함
- 예시:
  - Python: `.py` → `.pyc`, `.so` 또는 zip 패키지
  - Node.js: Webpack 빌드 결과만 포함
  - Java: `.jar` 또는 `.war`

**예제 (Python multi-stage build):**
```Dockerfile
# 빌드 스테이지
FROM python:3.11-slim AS builder
COPY ./app /build/app
RUN cd /build/app && python -m compileall .

# 실행 스테이지
FROM python:3.11-slim
COPY --from=builder /build/app /app
CMD ["python", "/app/main.pyc"]
```

---

## 🔐 2. 코드 난독화 / 컴파일 처리

| 언어     | 보호 방식                          |
|----------|-----------------------------------|
| Python   | `pyarmor`, `cython`, `.pyc`, `.so` |
| Node.js  | `webpack`, `obfuscator`, `pkg`     |
| Java     | `proguard`, `jar` 난독화          |
| Go       | 빌드 시 바이너리 생성 (상대적으로 안전) |

---

## 📦 3. Docker 이미지 자체 보안

- `multi-stage build`로 중간 소스 제거
- `.env`나 비밀 키 포함 금지
- 최소 실행 이미지(base image) 사용
- 비공개 Docker Registry 사용 또는 on-premise registry 제공

---

## 🛠️ 4. 실행 보안 (고객사 무단 복제 방지)

### ✔️ 라이선스 체크 내장
- JWT 또는 고객 고유 정보 기반 인증

### ✔️ Docker 실행 조건 제약
- 특정 IP, HOSTNAME, 환경 변수 조건 필수
- H/W 정보 기반 라이선스 바인딩

### ✔️ 고급: Confidential Computing
- Intel SGX, AMD SEV 등 보안 하드웨어 활용
- 실행 중 메모리 보호

---

## 📃 5. 계약 및 추적 조치

- 계약서에 무단 복제 및 역공학 금지 조항 포함
- Docker 이미지에 고객 식별자 삽입
- 실행 로그에 고객 ID 남기기

---

## 💡 요약 테이블

| 단계        | 설명                              | 권장 기술                    |
|-------------|-----------------------------------|------------------------------|
| 빌드 분리   | 실행 파일만 이미지 포함           | Multi-stage build            |
| 코드 보호   | 난독화/바이너리화 처리            | PyArmor, ProGuard, Webpack   |
| 이미지 보호 | 이미지 내 정보 최소화             | Minimal base image 사용       |
| 실행 제한   | 고객사 전용 인증 및 제한          | IP/키/환경변수/토큰 제한     |
| 법적 보호   | 계약 조항 및 추적 마킹             | 고객 ID 삽입, 로그 기록      |

---

## 📎 보안 체크리스트

- [ ] 이미지에 소스코드 미포함 확인
- [ ] 라이선스 인증 시스템 포함
- [ ] 고객 고유 마커 삽입 여부 확인
- [ ] 민감 정보 포함 여부 검토
- [ ] Docker Registry 보안 적용
- [ ] 계약서에 기술적·법적 보호 조항 삽입
