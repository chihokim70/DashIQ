# SolMan - 솔루션 관리 & 정책 관리

## 📋 개요
SolMan은 AiGov 솔루션의 사용자 관리, 정책 관리, 시스템 운영 관리를 담당하는 핵심 모듈입니다.

## 🏗️ 구조
```
SolMan/
├── frontend/                    # 관리자 포탈 UI
│   ├── public/                  # 정적 자산
│   ├── src/                     # 소스 코드
│   │   ├── components/          # React 컴포넌트
│   │   │   ├── common/          # 공통 컴포넌트
│   │   │   ├── admin/           # 관리자 전용 컴포넌트
│   │   │   ├── policy/          # 정책 관리 컴포넌트
│   │   │   └── user/            # 사용자 관리 컴포넌트
│   │   ├── pages/               # 페이지 컴포넌트
│   │   │   ├── Dashboard/       # 대시보드
│   │   │   ├── Users/           # 사용자 관리
│   │   │   ├── Policies/        # 정책 관리
│   │   │   └── Settings/        # 설정
│   │   ├── hooks/               # React 커스텀 훅
│   │   ├── services/            # API 호출 서비스
│   │   ├── utils/               # 유틸리티 함수
│   │   ├── store/               # 상태 관리
│   │   └── types/               # TypeScript 타입 정의
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── backend/                     # 사용자 관리, 정책 엔진
│   ├── src/
│   │   ├── controllers/         # API 컨트롤러
│   │   ├── services/            # 비즈니스 로직
│   │   ├── middleware/          # 미들웨어
│   │   ├── models/              # 데이터 모델
│   │   ├── routes/              # API 라우트
│   │   ├── utils/               # 유틸리티
│   │   └── types/               # 타입 정의
│   ├── config/                  # 서버 설정
│   ├── package.json
│   └── tsconfig.json
├── database/                    # 사용자, 조직, 정책 DB
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
- **사용자 관리**: 사용자 인증, 권한 관리, 조직 관리
- **정책 관리**: AI 사용 정책 설정, 필터링 규칙 관리
- **시스템 운영**: 모니터링, 로그 관리, 알림 설정
- **컴플라이언스**: 규제 요구사항 자동 대응

## 🚀 시작하기
```bash
# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 테스트 실행
npm test
```
