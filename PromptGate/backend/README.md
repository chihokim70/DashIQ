# PromptGate Filter Service

AI 서비스 보안을 위한 프롬프트 필터링 및 모니터링 서비스입니다.

## 🚀 주요 기능

### ✅ 완료된 기능
- **프롬프트 필터링**: 키워드 기반 차단 및 벡터 유사도 검사
- **민감 정보 마스킹**: 주민번호, 계좌번호, 카드번호 등 정규표현식 기반 마스킹
- **Elasticsearch 연동**: 로그 저장 및 모니터링
- **Qdrant 벡터 DB**: 유사 프롬프트 탐지
- **PostgreSQL 연동**: 정책 DB 구조 (SQLite 초기 적용)
- **Rebuff SDK 연동**: 프롬프트 인젝션 탐지

### 🔄 진행 중인 기능
- 정책 관리 UI 개발
- Kibana 대시보드 구성
- Presidio 연동 (민감 정보 탐지)

## 📋 시스템 요구사항

- Python 3.10+
- Docker & Docker Compose
- 4GB+ RAM (Elasticsearch 포함)

## 🛠️ 설치 및 실행

### 1. 환경 설정

```bash
# 프로젝트 디렉토리로 이동
cd services/filter-service

# 환경 변수 설정 (선택사항)
cp env.example .env
# .env 파일을 편집하여 필요한 설정을 추가
```

### 2. 데이터베이스 초기화

```bash
# 데이터베이스 테이블 생성 및 초기 데이터 삽입
python init_db.py
```

### 3. Docker 컨테이너 실행

```bash
# 모든 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f filter-service
```

### 4. 서비스 확인

- **API 문서**: http://localhost:8000/docs
- **Kibana**: http://localhost:5601
- **Qdrant 관리**: http://localhost:6333/dashboard

## 🔧 API 사용법

### 프롬프트 평가

```bash
curl -X POST "http://localhost:8000/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "안녕하세요, 오늘 날씨가 어떤가요?",
    "user_id": 1,
    "session_id": "session-123"
  }'
```

### 차단 키워드 추가

```bash
curl -X POST "http://localhost:8000/policy/blocked-keyword" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "비밀번호",
    "category": "security",
    "severity": "high",
    "description": "보안 관련 키워드"
  }'
```

### 통계 조회

```bash
curl -X GET "http://localhost:8000/stats"
```

## 🧪 테스트

```bash
# 자동 테스트 실행
python test_filter.py
```

## 📊 모니터링

### Elasticsearch 로그 확인

```bash
# 로그 인덱스 조회
curl -X GET "http://localhost:9200/promptgate_logs/_search?pretty"
```

### Kibana 대시보드

1. http://localhost:5601 접속
2. "Discover" 메뉴에서 `promptgate_logs` 인덱스 선택
3. 필터링 및 시각화 구성

## 🏗️ 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client App    │───▶│  Filter Service │───▶│   AI Service    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │   Qdrant        │    │  Elasticsearch  │
│   (Policy DB)   │    │   (Vector DB)   │    │   (Log DB)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔒 보안 기능

### 1. 키워드 기반 차단
- 정책 DB에서 차단 키워드 관리
- 카테고리별, 심각도별 분류

### 2. 벡터 유사도 검사
- Qdrant를 사용한 유사 프롬프트 탐지
- 임베딩 기반 유사도 계산

### 3. Rebuff SDK 연동
- 프롬프트 인젝션 탐지
- 휴리스틱, 벡터, 언어모델 기반 검사

### 4. 민감 정보 마스킹
- 정규표현식 기반 패턴 매칭
- 주민번호, 계좌번호, 카드번호 등 자동 마스킹

## 📈 성능 최적화

- **비동기 처리**: FastAPI 기반 비동기 API
- **벡터 캐싱**: Qdrant 클라이언트 연결 풀링
- **로그 배치**: Elasticsearch 배치 인덱싱
- **메모리 최적화**: 스트리밍 응답 처리

## 🚨 문제 해결

### 서비스 시작 실패
```bash
# 로그 확인
docker-compose logs filter-service

# 컨테이너 재시작
docker-compose restart filter-service
```

### 데이터베이스 연결 오류
```bash
# PostgreSQL 상태 확인
docker-compose ps postgres

# 데이터베이스 재초기화
python init_db.py
```

### Elasticsearch 메모리 부족
```bash
# docker-compose.yml에서 메모리 설정 조정
ES_JAVA_OPTS: "-Xms256m -Xmx256m"
```

## 🔄 개발 가이드

### 새로운 필터 규칙 추가

1. `app/filter.py`에서 패턴 추가
2. `app/schema.py`에서 DB 스키마 업데이트
3. `init_db.py`에서 초기 데이터 추가
4. 테스트 실행

### API 엔드포인트 추가

1. `app/api.py`에서 새 라우터 추가
2. Pydantic 모델 정의
3. 비즈니스 로직 구현
4. 테스트 케이스 작성

## 📝 라이센스

MIT License

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 