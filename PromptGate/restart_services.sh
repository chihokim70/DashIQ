#!/bin/bash

# PromptGate 서비스 안정적인 재시작 스크립트
# 작성자: AI Assistant
# 날짜: 2025-10-13

set -e  # 오류 발생 시 스크립트 중단

echo "=== PromptGate 서비스 안정적인 재시작 시작 ==="

# 1. 현재 디렉토리 확인
cd /home/krase/AiGov/PromptGate

# 2. 기존 컨테이너 정리
echo "1. 기존 컨테이너 정리 중..."
docker rm -f promptgate_filter-service promptgate_pii-detector promptgate_opa 2>/dev/null || true

# 3. 불필요한 네트워크 정리
echo "2. 불필요한 네트워크 정리 중..."
docker network rm aigov-promptgate-v6_promptgate-network 2>/dev/null || true

# 4. Docker 시스템 정리 (캐시 정리)
echo "3. Docker 시스템 정리 중..."
docker system prune -f

# 5. 서비스 재시작 (고정된 프로젝트 이름 사용)
echo "4. 서비스 재시작 중..."
COMPOSE_PROJECT_NAME=aigov-promptgate-stable docker-compose up -d promptgate_filter-service pii-detector promptgate_opa

# 6. 서비스 시작 대기
echo "5. 서비스 시작 대기 중 (30초)..."
sleep 30

# 7. 서비스 상태 확인
echo "6. 서비스 상태 확인 중..."
echo "실행 중인 컨테이너:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep promptgate

echo ""
echo "네트워크 상태:"
docker network ls | grep promptgate

# 8. API 응답 테스트
echo ""
echo "7. API 응답 테스트 중..."
echo "Filter Service 헬스 체크:"
curl -s http://localhost:8001/health | jq . 2>/dev/null || curl -s http://localhost:8001/health

echo ""
echo "PII Detector 헬스 체크:"
curl -s http://localhost:8082/health | jq . 2>/dev/null || curl -s http://localhost:8082/health

echo ""
echo "OPA 헬스 체크:"
curl -s http://localhost:8181/health | jq . 2>/dev/null || curl -s http://localhost:8181/health

echo ""
echo "=== 재시작 완료 ==="
echo "서비스 상태를 확인하세요. 문제가 있다면 로그를 확인하세요:"
echo "docker-compose logs promptgate_filter-service"
echo "docker-compose logs promptgate_pii-detector"
echo "docker-compose logs promptgate_opa"
