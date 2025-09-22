#!/usr/bin/env python3
"""
PromptGate Filter Service 데이터베이스 초기화 스크립트
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.schema import init_db, insert_initial_data
from app.logger import get_logger

logger = get_logger("db-init")

def main():
    """데이터베이스 초기화 메인 함수"""
    try:
        print("🚀 PromptGate Filter Service 데이터베이스 초기화를 시작합니다...")
        
        # 1. 데이터베이스 테이블 생성
        print("📋 데이터베이스 테이블을 생성합니다...")
        init_db()
        print("✅ 테이블 생성 완료")
        
        # 2. 초기 데이터 삽입
        print("📝 초기 데이터를 삽입합니다...")
        insert_initial_data()
        print("✅ 초기 데이터 삽입 완료")
        
        print("🎉 데이터베이스 초기화가 완료되었습니다!")
        print("\n📊 생성된 테이블:")
        print("  - users: 사용자 정보")
        print("  - policies: 정책 정보")
        print("  - blocked_keywords: 차단 키워드")
        print("  - masked_keywords: 마스킹 키워드")
        print("  - prompt_logs: 프롬프트 로그")
        print("  - vector_embeddings: 벡터 임베딩")
        print("  - system_configs: 시스템 설정")
        
        print("\n🔧 다음 단계:")
        print("  1. docker-compose up -d")
        print("  2. http://localhost:8000/docs 에서 API 테스트")
        print("  3. http://localhost:5601 에서 Kibana 접속")
        
    except Exception as e:
        logger.error(f"데이터베이스 초기화 실패: {str(e)}")
        print(f"❌ 초기화 실패: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 