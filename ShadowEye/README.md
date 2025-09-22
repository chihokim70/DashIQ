# ShadowEye - Shadow AI 탐지 & 차단

## 📋 개요
ShadowEye는 AiGov 솔루션의 비인가 AI 사용 탐지 및 차단을 담당하는 보안 모듈입니다.

## 🏗️ 구조
```
ShadowEye/
├── frontend/                    # 탐지 현황 모니터링 UI
│   ├── public/                  # 정적 자산
│   ├── src/                     # 소스 코드
│   │   ├── components/          # React 컴포넌트
│   │   │   ├── common/          # 공통 컴포넌트
│   │   │   ├── detection/       # 탐지 관련 컴포넌트
│   │   │   ├── monitoring/      # 모니터링 컴포넌트
│   │   │   └── alerts/          # 알림 컴포넌트
│   │   ├── pages/               # 페이지 컴포넌트
│   │   │   ├── Dashboard/       # 메인 대시보드
│   │   │   ├── Detection/       # 탐지 현황
│   │   │   ├── Monitoring/      # 실시간 모니터링
│   │   │   └── Settings/        # 설정
│   │   ├── hooks/               # React 커스텀 훅
│   │   ├── services/            # API 호출 서비스
│   │   ├── utils/               # 유틸리티 함수
│   │   ├── store/               # 상태 관리
│   │   └── types/               # TypeScript 타입 정의
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── backend/                     # 트래픽 분석, AI 탐지 엔진
│   ├── src/
│   │   ├── controllers/         # API 컨트롤러
│   │   ├── services/            # 탐지 엔진, 트래픽 분석
│   │   ├── middleware/          # 미들웨어
│   │   ├── models/              # 데이터 모델
│   │   ├── routes/              # API 라우트
│   │   ├── utils/               # 유틸리티
│   │   └── types/               # 타입 정의
│   ├── config/                  # 서버 설정
│   ├── package.json
│   └── tsconfig.json
├── database/                    # 탐지 로그, 패턴 분석 DB
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
- **네트워크 트래픽 분석**: AI 서비스 패턴 탐지
- **실시간 모니터링**: 비인가 AI 사용 실시간 감지
- **패턴 분석**: AI 사용 패턴 학습 및 분류
- **자동 차단**: 탐지된 비인가 AI 사용 자동 차단
- **알림 시스템**: 탐지 이벤트 실시간 알림

## 🚀 시작하기
```bash
# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 테스트 실행
npm test
```
