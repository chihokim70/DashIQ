# TrustLLM - 내부 LLM & 응답 처리

## 📋 개요
TrustLLM은 AiGov 솔루션의 내부 LLM 운영, 응답 포매팅/마스킹을 담당하는 AI 모듈입니다.

## 🏗️ 구조
```
TrustLLM/
├── backend/                     # LLM 엔진, 응답 포매팅/마스킹
│   ├── src/
│   │   ├── controllers/         # API 컨트롤러
│   │   ├── services/            # LLM 서비스, 응답 처리
│   │   ├── middleware/          # 미들웨어
│   │   ├── models/              # 데이터 모델
│   │   ├── routes/              # API 라우트
│   │   ├── utils/               # 유틸리티
│   │   └── types/               # 타입 정의
│   ├── config/                  # 서버 설정
│   ├── package.json
│   └── tsconfig.json
├── models/                      # AI 모델 파일 및 가중치
│   ├── checkpoints/             # 모델 체크포인트
│   ├── configs/                 # 모델 설정 파일
│   └── weights/                 # 모델 가중치
├── database/                    # 모델 메타데이터, 학습 데이터
│   ├── postgresql/              # PostgreSQL 관련
│   │   ├── migrations/          # DB 마이그레이션
│   │   ├── seeds/               # 초기 데이터
│   │   ├── schemas/             # 스키마 정의
│   │   ├── queries/             # SQL 쿼리
│   │   └── backup/              # 백업 스크립트
│   └── redis/                   # Redis 설정
├── docker/                      # Docker 설정
├── tests/                       # 테스트 파일
│   ├── unit/                    # 단위 테스트
│   ├── integration/             # 통합 테스트
│   ├── e2e/                     # E2E 테스트
│   └── fixtures/                # 테스트 데이터
├── README.md
├── .env.example
├── .gitignore
└── Makefile
```

## 🎯 주요 기능
- **내부 LLM 운영**: 자체 LLM 모델 서빙
- **응답 포매팅**: AI 응답을 사용자 친화적으로 변환
- **응답 마스킹**: 민감 정보 자동 마스킹
- **모델 관리**: 모델 버전 관리, 성능 모니터링
- **학습 데이터 관리**: 모델 학습용 데이터 관리

## 🚀 시작하기
```bash
# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 테스트 실행
npm test
```
