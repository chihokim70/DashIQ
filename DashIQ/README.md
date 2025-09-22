# DashIQ - 대시보드 인텔리전스 & 로그관리

## 📋 개요
DashIQ는 AiGov 솔루션의 실시간 모니터링, 로그 분석, 리포팅을 담당하는 분석 모듈입니다.

## 🏗️ 구조
```
DashIQ/
├── frontend/                    # 실시간 대시보드, 리포트 UI
│   ├── public/                  # 정적 자산
│   ├── src/                     # 소스 코드
│   │   ├── components/          # React 컴포넌트
│   │   │   ├── common/          # 공통 컴포넌트
│   │   │   ├── dashboard/       # 대시보드 컴포넌트
│   │   │   ├── charts/          # 차트 컴포넌트
│   │   │   └── reports/         # 리포트 컴포넌트
│   │   ├── pages/               # 페이지 컴포넌트
│   │   │   ├── Dashboard/       # 메인 대시보드
│   │   │   ├── Analytics/       # 분석 페이지
│   │   │   ├── Reports/         # 리포트 페이지
│   │   │   └── Settings/        # 설정
│   │   ├── hooks/               # React 커스텀 훅
│   │   ├── services/            # API 호출 서비스
│   │   ├── utils/               # 유틸리티 함수
│   │   ├── store/               # 상태 관리
│   │   └── types/               # TypeScript 타입 정의
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── backend/                     # 로그 수집, 분석 엔진, 메트릭스
│   ├── src/
│   │   ├── controllers/         # API 컨트롤러
│   │   ├── services/            # 분석 엔진, 로그 처리
│   │   ├── middleware/          # 미들웨어
│   │   ├── models/              # 데이터 모델
│   │   ├── routes/              # API 라우트
│   │   ├── utils/               # 유틸리티
│   │   └── types/               # 타입 정의
│   ├── config/                  # 서버 설정
│   ├── package.json
│   └── tsconfig.json
├── database/                    # 로그 저장소, 메트릭 DB
│   ├── postgresql/              # PostgreSQL 관련
│   │   ├── migrations/          # DB 마이그레이션
│   │   ├── seeds/               # 초기 데이터
│   │   ├── schemas/             # 스키마 정의
│   │   ├── queries/             # SQL 쿼리
│   │   └── backup/              # 백업 스크립트
│   ├── redis/                   # Redis 설정
│   └── clickhouse/              # ClickHouse (로그 분석용)
│       ├── migrations/          # ClickHouse 마이그레이션
│       ├── schemas/             # 스키마 정의
│       └── queries/             # 분석 쿼리
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
- **실시간 대시보드**: AI 사용 현황, 보안 이벤트 모니터링
- **로그 분석**: 프롬프트 로그, 보안 이벤트 분석
- **리포팅**: 정기 리포트 생성, 커스텀 리포트
- **메트릭스**: 성능 지표, 사용량 통계
- **알림**: 이상 상황 감지 및 알림

## 🚀 시작하기
```bash
# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 테스트 실행
npm test
```
