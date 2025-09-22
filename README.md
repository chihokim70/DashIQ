# PromptGate - AI 프롬프트 보안 시스템

PromptGate는 AI 프롬프트 인젝션 공격을 방지하고 보안을 강화하는 시스템입니다. ChatGPT와 같은 UI를 제공하며, Figma MCP를 통한 디자인 연동을 지원합니다.

## 🚀 주요 기능

- **프롬프트 필터링**: AI 프롬프트 인젝션 탐지 및 차단
- **ChatGPT 스타일 UI**: 직관적인 채팅 인터페이스
- **Figma 연동**: Figma API를 통한 디자인 시스템 연동
- **벡터 기반 유사도 검사**: Qdrant를 활용한 고급 필터링
- **실시간 로깅**: Elasticsearch를 통한 로그 관리

## 🏗️ 아키텍처

```
PromptGate/
├── app/                    # 메인 애플리케이션
├── services/
│   └── filter-service/     # 필터링 마이크로서비스
├── rebuff/                 # Rebuff SDK
├── ui-components/          # React UI 컴포넌트
├── figma-integration/      # Figma API 연동
└── tests/                  # 테스트 코드
```

## 🛠️ 설치 및 실행

### 1. 환경 설정

```bash
# 환경 변수 파일 복사
cp env.example .env

# 필요한 값들을 .env 파일에 설정
# - FIGMA_ACCESS_TOKEN
# - OPENAI_API_KEY
# - 데이터베이스 설정 등
```

### 2. Docker Compose로 실행

```bash
# 모든 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### 3. 개발 모드 실행

```bash
# Filter Service 실행
cd services/filter-service
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend 실행 (rebuff/server)
cd rebuff/server
npm install
npm run dev
```

## 📡 API 엔드포인트

### Filter Service

- `POST /api/v1/chat` - 채팅 메시지 처리
- `POST /prompt/check` - 프롬프트 검사
- `GET /api/v1/health` - 서비스 상태 확인

### 사용 예시

```bash
# 채팅 메시지 전송
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "안녕하세요!", "user_id": "user123"}'
```

## 🎨 Figma 연동

### 1. Figma API 토큰 설정

1. Figma에서 Personal Access Token 생성
2. `.env` 파일에 `FIGMA_ACCESS_TOKEN` 설정
3. Figma 파일 키를 `FIGMA_FILE_KEY`에 설정

### 2. 디자인 정보 가져오기

```javascript
const FigmaAPI = require('./figma-integration/figma-api');
const figma = new FigmaAPI();

// 파일 정보 가져오기
const fileInfo = await figma.getFile('your_file_key');

// 컴포넌트 정보 가져오기
const components = await figma.getComponents('your_file_key');
```

## 🎯 ChatGPT 스타일 UI

`ui-components/ChatInterface.tsx`를 사용하여 ChatGPT와 유사한 채팅 인터페이스를 구현할 수 있습니다.

### 주요 특징

- 실시간 메시지 전송
- 로딩 상태 표시
- 자동 스크롤
- 반응형 디자인
- 한글 입력 지원

## 🔧 개발 가이드

### 새로운 필터 규칙 추가

```python
# app/filter.py에서 새로운 필터링 로직 추가
def evaluate_prompt(prompt: str) -> dict:
    # 새로운 검사 로직 구현
    pass
```

### UI 컴포넌트 확장

```typescript
// 새로운 채팅 기능 추가
import ChatInterface from './ui-components/ChatInterface';

// 커스텀 메시지 핸들러
const handleMessage = async (message: string) => {
  // 메시지 처리 로직
  return response;
};
```

## 🧪 테스트

```bash
# Python 테스트 실행
cd tests
python -m pytest

# JavaScript 테스트 실행
cd rebuff/server
npm test
```

## 📊 모니터링

- **Elasticsearch**: 로그 및 메트릭 수집
- **Kibana**: 로그 시각화 (http://localhost:5601)
- **Qdrant**: 벡터 유사도 검색 모니터링

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🆘 지원

문제가 발생하거나 질문이 있으시면 이슈를 생성해주세요.
