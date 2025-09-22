FROM python:3.10-slim

WORKDIR /app

# 백엔드 requirements.txt 복사 및 설치
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 백엔드 소스 코드 복사
COPY backend/main.py .
COPY backend/app/ app/
COPY backend/init_qdrant.py .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
