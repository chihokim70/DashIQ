
# Ubuntu 개발 환경 정리 문서 (KRASE 프로젝트)

## 1. 노트북 초기 세팅

- **노트북 환경**: x86 기반 및 ARM 기반 노트북 모두 가능
- **운영체제 설치**: Ubuntu 24.04.2 LTS Desktop 버전 설치 완료
- **설치 방식**: 공식 홈페이지에서 ISO 파일 다운로드 → 부팅 USB 제작 (Rufus 등 사용) → 설치

---

## 2. Docker 설치 및 개발 환경 준비

### 2-1. Docker 설치 명령어

```bash
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable docker
sudo systemctl start docker
```

### 2-2. Docker Compose 설치 (선택)

```bash
sudo apt install -y docker-compose
```

### 2-3. 일반 사용자 권한으로 Docker 사용 (Optional)

```bash
sudo usermod -aG docker $USER
# 이후 로그아웃 & 재로그인 필요
```

---

## 3. 개발 방식 선택: Docker 컨테이너 vs Ubuntu 가상환경

| 항목          | Docker 컨테이너 환경        | Ubuntu 가상환경 (로컬 개발) |
| ----------- | --------------------- | ------------------- |
| 격리성         | 강함 (OS 수준 격리)         | 약함 (동일 OS 내 구성 공유)  |
| 구성 속도       | 빠름 (이미지 기반)           | 느림 (직접 패키지 설치 필요)   |
| 재현성         | 우수 (Dockerfile로 자동화)  | 낮음 (개발자별 환경 차이 발생)  |
| 운영과 개발의 일관성 | 높음                    | 낮음                  |
| 리소스 사용량     | 낮음 (가상머신보다 가볍다)       | 중간                  |
| 디버깅/직접 접근   | 어려울 수 있음 (컨테이너 진입 필요) | 직접 접근 쉬움            |
| 권장 용도       | 배포, 협업 개발, CI/CD      | 초기 테스트, 교육, 직접 실습   |

**✅ 결론**  
- Docker 컨테이너 개발은 재현성과 확장성이 좋아 프로젝트 환경 통합 관리에 유리  
- Ubuntu 로컬 개발은 설정과 디버깅이 쉬워 학습 및 테스트에 적합

---

## 4. KRA-AIGov 전체 솔루션 구성

```
[KRA-AIGov]     : 메인 브랜드명
 ├─ PromptGate  : AI 프롬프트 필터링 프록시
 ├─ ShadowScan  : Shadow AI 탐지 시스템
 ├─ DashIQ      : AI 사용 로그 대시보드
 └─ TrustLLM    : 내부 사내 AI 제공 엔진
```

---

## 5. Docker 기반 AiGov-Proxy 개발 환경 구성

### 5-1. 디렉토리 구성 예시

```
/AiGov-Proxy
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
├── README.md
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   └── proxy.py
│   ├── core/
│   │   └── security.py
│   ├── config.py
│   ├── models/
│   │   └── schema.py
│   └── services/
│       └── logger.py
├── rebuff/
│   └── ...
└── .gitignore
```

> `.env` 파일 추가 → 환경별 설정 분리 및 보안 목적  
> `/core/security.py` → 인증/인가 및 보안 필터 모듈 (필요시 `filter.py`, `validator.py` 도입)

---

### 5-2. Dockerfile 예시 (FastAPI 기반 프록시 앱)

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app.main:app"]
```

---

### 5-3. requirements.txt 예시

```text
fastapi==0.115.12
uvicorn==0.34.2
gunicorn==21.2.0
python-dotenv==1.1.0
httpx==0.28.1
python-jose==3.5.0
passlib==1.7.4
python-multipart==0.0.20
loguru==0.7.2
pydantic==2.11.5
```

---

### 5-4. 컨테이너 실행

```bash
docker build -t aigov-proxy .
docker run -d -p 5000:5000 --name aigov-proxy aigov-proxy
```
