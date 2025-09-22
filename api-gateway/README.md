# API Gateway - 전체 시스템 API 게이트웨이

## 📋 개요
API Gateway는 AiGov 솔루션의 전체 시스템에 대한 통합 API 게이트웨이입니다.

## 🏗️ 구조
```
api-gateway/
├── config/                      # 게이트웨이 설정
├── middleware/                  # 공통 미들웨어
├── docker/                      # Docker 설정
└── README.md
```

## 🎯 주요 기능
- **라우팅**: 각 도메인별 API 라우팅
- **인증/인가**: 통합 인증 및 권한 관리
- **로드 밸런싱**: 트래픽 분산
- **Rate Limiting**: API 호출 제한
- **로깅**: API 호출 로깅
- **모니터링**: API 성능 모니터링

## 🚀 시작하기
```bash
# Docker 실행
docker-compose up -d

# 설정 확인
curl http://localhost:8080/health
```
