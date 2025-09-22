#!/bin/bash

echo "🚀 PromptGate Filter Service 설정을 시작합니다..."

# 1. Docker Compose로 서비스 시작
echo "📦 Docker 컨테이너를 시작합니다..."
docker-compose up -d

# 2. 서비스가 완전히 시작될 때까지 대기
echo "⏳ 서비스가 시작될 때까지 대기 중..."
sleep 30

# 3. 데이터베이스 초기화
echo "🗄️ 데이터베이스를 초기화합니다..."
docker-compose exec promptgate_filter-service python init_db.py

# 4. Qdrant 초기화
echo "🔍 Qdrant 벡터 DB를 초기화합니다..."
docker-compose exec promptgate_filter-service python init_qdrant.py

echo "✅ PromptGate Filter Service 설정이 완료되었습니다!"
echo ""
echo "📊 서비스 접속 정보:"
echo "  - Filter Service API: http://localhost:8001/docs"
echo "  - Kibana: http://localhost:5602"
echo "  - Qdrant: http://localhost:6334"
echo ""
echo "🧪 테스트 실행:"
echo "  docker-compose exec promptgate_filter-service python test_filter.py" 