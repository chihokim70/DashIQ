# Common - 공통 컴포넌트 & 라이브러리

## 📋 개요
Common은 AiGov 솔루션의 모든 도메인에서 공통으로 사용하는 컴포넌트와 라이브러리를 관리하는 모듈입니다.

## 🏗️ 구조
```
Common/
├── tools/                       # 개발 도구, 스크립트
│   ├── scripts/                 # 유틸리티 스크립트
│   ├── generators/              # 코드 생성기
│   └── validators/              # 검증 도구
├── modules/                     # 공통 모듈 (인증, 로깅 등)
│   ├── auth/                    # 인증 모듈
│   ├── logging/                 # 로깅 모듈
│   ├── encryption/              # 암호화 모듈
│   └── validation/              # 검증 모듈
├── utils/                       # 유틸리티 함수들
│   ├── date/                    # 날짜 처리
│   ├── string/                  # 문자열 처리
│   ├── data/                    # 데이터 변환
│   └── format/                  # 포맷팅
├── security/                    # 보안 관련 공통 기능
│   ├── jwt/                     # JWT 토큰 관리
│   ├── api-keys/                # API 키 관리
│   └── policies/                # 보안 정책
├── services/                    # 공통 서비스 (API 클라이언트 등)
│   ├── api-client/              # API 클라이언트
│   ├── email/                   # 이메일 서비스
│   └── notification/            # 알림 서비스
├── types/                       # TypeScript 타입 정의
│   ├── common/                  # 공통 타입
│   ├── api/                     # API 타입
│   └── domain/                  # 도메인 타입
├── constants/                   # 상수 및 설정값
│   ├── config/                  # 설정 상수
│   ├── enums/                   # 열거형
│   └── errors/                  # 에러 코드
├── tests/                       # 공통 테스트 유틸리티
│   ├── unit/                    # 단위 테스트
│   ├── integration/             # 통합 테스트
│   └── fixtures/                # 테스트 데이터
├── README.md
├── package.json
└── tsconfig.json
```

## 🎯 주요 기능
- **공통 모듈**: 인증, 로깅, 암호화 등 핵심 기능
- **유틸리티**: 날짜, 문자열, 데이터 처리 함수
- **보안**: JWT, API 키, 보안 정책 관리
- **서비스**: API 클라이언트, 이메일, 알림
- **타입**: TypeScript 타입 정의
- **상수**: 설정값, 에러 코드 등

## 🚀 시작하기
```bash
# 의존성 설치
npm install

# 빌드
npm run build

# 테스트 실행
npm test
```
