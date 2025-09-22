# PromptGate UI 데모

이 폴더는 PromptGate의 UI 컴포넌트들을 Live Server로 확인할 수 있는 데모 페이지들을 포함합니다.

## 🚀 Live Server 실행 방법

### 1. Cursor에서 Live Server 확장 프로그램 설치

1. **확장 프로그램 열기**
   - `Ctrl + Shift + X` (Windows/Linux)
   - `Cmd + Shift + X` (Mac)

2. **Live Server 검색 및 설치**
   - 검색창에 "Live Server" 입력
   - **Live Server** (Ritwick Dey) 설치

### 2. 서버 실행

#### 방법 1: 우클릭 메뉴
- `index.html` 또는 `components.html` 파일 우클릭
- **"Open with Live Server"** 선택

#### 방법 2: 명령 팔레트
- `Ctrl + Shift + P` (Windows/Linux)
- `Cmd + Shift + P` (Mac)
- **"Live Server: Open with Live Server"** 입력 후 선택

#### 방법 3: 상태바
- Cursor 하단 상태바에서 **"Go Live"** 버튼 클릭

### 3. 브라우저에서 확인

- **채팅 UI**: `http://localhost:5500/index.html`
- **컴포넌트 갤러리**: `http://localhost:5500/components.html`

## 📱 데모 페이지 설명

### 1. index.html - ChatGPT 스타일 채팅 UI
- **기능**: 실시간 채팅 인터페이스
- **특징**: 
  - 한글 입력 지원
  - 타이핑 인디케이터
  - 자동 스크롤
  - 반응형 디자인
  - Filter Service 시뮬레이션

### 2. components.html - UI 컴포넌트 갤러리
- **기능**: 다양한 UI 컴포넌트 모음
- **포함 컴포넌트**:
  - 버튼 (기본, 보조, 위험, 비활성화)
  - 입력 필드 (텍스트, 비밀번호, 텍스트영역, 선택)
  - 카드 (보안 필터, 실시간 검사, 분석 대시보드)
  - 알림 (성공, 경고, 오류, 정보)
  - 로딩 (다양한 스타일)

## 🎨 디자인 시스템

### 색상 팔레트
- **Primary**: `#3B82F6` (파란색)
- **Secondary**: `#6B7280` (회색)
- **Success**: `#10B981` (초록색)
- **Warning**: `#F59E0B` (노란색)
- **Error**: `#EF4444` (빨간색)

### 타이포그래피
- **폰트**: Inter, -apple-system, BlinkMacSystemFont, sans-serif
- **크기**: 12px ~ 24px
- **행간**: 1.5

### 간격 시스템
- **XS**: 4px
- **SM**: 8px
- **MD**: 16px
- **LG**: 24px
- **XL**: 32px

## 🔧 개발 팁

### 1. 실시간 편집
- HTML 파일을 수정하면 브라우저가 자동으로 새로고침됩니다
- CSS 변경사항도 즉시 반영됩니다

### 2. 반응형 테스트
- 브라우저 개발자 도구에서 다양한 화면 크기로 테스트
- 모바일, 태블릿, 데스크톱 뷰 확인

### 3. 브라우저 호환성
- Chrome, Firefox, Safari, Edge에서 테스트
- 각 브라우저별 특성 확인

## 🐛 문제 해결

### Live Server가 실행되지 않는 경우
1. **포트 충돌**: 다른 프로세스가 5500 포트를 사용 중
   - `.vscode/settings.json`에서 포트 변경
2. **권한 문제**: 관리자 권한으로 Cursor 실행
3. **확장 프로그램 오류**: Live Server 재설치

### 한글 입력 문제
1. **브라우저 언어 설정**: 한국어로 설정
2. **IME 설정**: 한글 입력기 활성화
3. **폰트 문제**: 한글 폰트 설치 확인

## 📚 추가 리소스

- [Live Server 공식 문서](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer)
- [Tailwind CSS 문서](https://tailwindcss.com/docs)
- [Lucide 아이콘](https://lucide.dev/) 