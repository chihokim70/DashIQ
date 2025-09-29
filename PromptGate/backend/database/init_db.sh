#!/bin/bash
# AiGov Admin Portal Database 초기화 스크립트

set -e

# 환경 변수 설정
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-aigov_admin}
DB_USER=${DB_USER:-aigov_user}
DB_PASSWORD=${DB_PASSWORD:-aigov_password}

# 색상 출력
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 AiGov Admin Portal Database 초기화 시작${NC}"

# PostgreSQL 클라이언트 설치 확인
if ! command -v psql &> /dev/null; then
    echo -e "${RED}❌ PostgreSQL 클라이언트가 설치되지 않았습니다.${NC}"
    echo "Ubuntu/Debian: sudo apt-get install postgresql-client"
    echo "CentOS/RHEL: sudo yum install postgresql"
    exit 1
fi

# 데이터베이스 연결 테스트
echo -e "${YELLOW}📡 데이터베이스 연결 테스트...${NC}"
if ! PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "SELECT 1;" &> /dev/null; then
    echo -e "${RED}❌ 데이터베이스 연결 실패${NC}"
    echo "연결 정보를 확인하세요:"
    echo "  Host: $DB_HOST"
    echo "  Port: $DB_PORT"
    echo "  User: $DB_USER"
    echo "  Password: $DB_PASSWORD"
    exit 1
fi

echo -e "${GREEN}✅ 데이터베이스 연결 성공${NC}"

# 데이터베이스 생성 (존재하지 않는 경우)
echo -e "${YELLOW}🗄️ 데이터베이스 생성 중...${NC}"
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "
CREATE DATABASE $DB_NAME 
WITH 
    ENCODING = 'UTF8'
    LC_COLLATE = 'ko_KR.UTF-8'
    LC_CTYPE = 'ko_KR.UTF-8'
    TEMPLATE = template0;
" 2>/dev/null || echo -e "${YELLOW}⚠️ 데이터베이스가 이미 존재합니다.${NC}"

# 스키마 파일 실행
echo -e "${YELLOW}📋 스키마 생성 중...${NC}"
if [ -f "schema.sql" ]; then
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f schema.sql
    echo -e "${GREEN}✅ 스키마 생성 완료${NC}"
else
    echo -e "${RED}❌ schema.sql 파일을 찾을 수 없습니다.${NC}"
    exit 1
fi

# 테이블 생성 확인
echo -e "${YELLOW}🔍 테이블 생성 확인...${NC}"
TABLE_COUNT=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "
SELECT COUNT(*) 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE';
" | tr -d ' ')

echo -e "${GREEN}✅ 총 $TABLE_COUNT 개의 테이블이 생성되었습니다.${NC}"

# 기본 데이터 확인
echo -e "${YELLOW}📊 기본 데이터 확인...${NC}"
TENANT_COUNT=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM tenants;" | tr -d ' ')
USER_COUNT=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM users;" | tr -d ' ')
ROLE_COUNT=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM roles;" | tr -d ' ')
BUNDLE_COUNT=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM policy_bundles;" | tr -d ' ')
RULE_COUNT=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM filter_rules;" | tr -d ' ')

echo -e "${GREEN}📈 기본 데이터 생성 완료:${NC}"
echo "  - 테넌트: $TENANT_COUNT 개"
echo "  - 사용자: $USER_COUNT 개"
echo "  - 역할: $ROLE_COUNT 개"
echo "  - 정책 번들: $BUNDLE_COUNT 개"
echo "  - 필터 규칙: $RULE_COUNT 개"

# 연결 정보 출력
echo -e "${GREEN}🎉 데이터베이스 초기화 완료!${NC}"
echo -e "${YELLOW}📋 연결 정보:${NC}"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo "  Password: $DB_PASSWORD"

echo -e "${YELLOW}🔗 연결 명령어:${NC}"
echo "PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"

# 환경 변수 파일 생성
echo -e "${YELLOW}📝 환경 변수 파일 생성...${NC}"
cat > .env.database << EOF
# AiGov Admin Portal Database Configuration
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD

# Database URL for applications
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME
EOF

echo -e "${GREEN}✅ .env.database 파일이 생성되었습니다.${NC}"
echo -e "${YELLOW}💡 다음 단계:${NC}"
echo "  1. 애플리케이션에서 .env.database 파일을 로드"
echo "  2. 데이터베이스 연결 테스트"
echo "  3. 필터링 기능 개발 진행"
