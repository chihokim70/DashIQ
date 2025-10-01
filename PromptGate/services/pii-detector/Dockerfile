# Presidio PII Detection Service Dockerfile
FROM python:3.12-slim

# 시스템 패키지 업데이트 및 필요한 도구 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 한국어 spaCy 모델 설치
RUN python -m spacy download ko_core_news_sm || echo "한국어 모델 설치 실패, 영어 모델 사용"

# 애플리케이션 코드 복사
COPY app/ ./app/
COPY config/ ./config/

# 포트 노출
EXPOSE 8082

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8082/health || exit 1

# 애플리케이션 실행
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8082"]
