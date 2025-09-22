"""
정책 DB 스키마 정의
SQLite 초기 적용 후 PostgreSQL로 이전 예정
"""

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.config import get_settings

settings = get_settings()

# SQLite 데이터베이스 URL (초기 개발용)
SQLALCHEMY_DATABASE_URL = f"sqlite:///./policy.db"

# PostgreSQL 데이터베이스 URL (운영용)
# SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    """사용자 테이블"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Policy(Base):
    """정책 테이블"""
    __tablename__ = "policies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer)  # User ID
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BlockedKeyword(Base):
    """차단 키워드 테이블"""
    __tablename__ = "blocked_keywords"
    
    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, unique=True, index=True)
    description = Column(Text)
    category = Column(String)  # 'security', 'content', 'custom' 등
    severity = Column(String)  # 'low', 'medium', 'high', 'critical'
    is_active = Column(Boolean, default=True)
    policy_id = Column(Integer)  # Policy ID
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MaskedKeyword(Base):
    """마스킹 키워드 테이블"""
    __tablename__ = "masked_keywords"
    
    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, unique=True, index=True)
    mask_value = Column(String)  # 마스킹할 값
    pattern = Column(String)     # 정규표현식 패턴
    description = Column(Text)
    category = Column(String)    # 'pii', 'sensitive', 'custom' 등
    is_active = Column(Boolean, default=True)
    policy_id = Column(Integer)  # Policy ID
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PromptLog(Base):
    """프롬프트 로그 테이블"""
    __tablename__ = "prompt_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)  # User ID
    session_id = Column(String, index=True)
    original_prompt = Column(Text)
    masked_prompt = Column(Text)
    is_blocked = Column(Boolean, default=False)
    block_reason = Column(Text)
    risk_score = Column(Float)
    detection_method = Column(String)  # 'keyword', 'vector', 'rebuff', 'fallback'
    processing_time = Column(Float)  # 처리 시간 (초)
    ip_address = Column(String)
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class VectorEmbedding(Base):
    """벡터 임베딩 테이블"""
    __tablename__ = "vector_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    prompt_text = Column(Text)
    embedding_vector = Column(Text)  # JSON 형태로 저장
    is_dangerous = Column(Boolean, default=True)
    category = Column(String)  # 'prompt_injection', 'safe_prompt' 등
    similarity_threshold = Column(Float, default=0.75)
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemConfig(Base):
    """시스템 설정 테이블"""
    __tablename__ = "system_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(Text)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 데이터베이스 초기화
def init_db():
    """데이터베이스 테이블 생성"""
    Base.metadata.create_all(bind=engine)

# 기본 데이터 삽입
def insert_initial_data():
    """초기 데이터 삽입"""
    db = SessionLocal()
    
    try:
        # 기본 차단 키워드
        default_blocked_keywords = [
            {"keyword": "비밀번호", "description": "비밀번호 관련 키워드", "category": "security", "severity": "high"},
            {"keyword": "내부 문서", "description": "내부 문서 관련 키워드", "category": "content", "severity": "medium"},
            {"keyword": "개인정보", "description": "개인정보 관련 키워드", "category": "pii", "severity": "critical"},
            {"keyword": "기밀", "description": "기밀 정보 관련 키워드", "category": "security", "severity": "high"},
        ]
        
        for keyword_data in default_blocked_keywords:
            existing = db.query(BlockedKeyword).filter(BlockedKeyword.keyword == keyword_data["keyword"]).first()
            if not existing:
                blocked_keyword = BlockedKeyword(**keyword_data)
                db.add(blocked_keyword)
        
        # 기본 마스킹 키워드
        default_masked_keywords = [
            {"keyword": "주민번호", "mask_value": "***", "pattern": r"\\b\\d{6}-\\d{7}\\b", "category": "pii"},
            {"keyword": "계좌번호", "mask_value": "***", "pattern": r"\\b\\d{2,4}(-\\d{2,4}){1,2}\\b", "category": "pii"},
            {"keyword": "카드번호", "mask_value": "***", "pattern": r"\\b\\d{4}-\\d{4}-\\d{4}-\\d{4}\\b", "category": "pii"},
        ]
        
        for keyword_data in default_masked_keywords:
            existing = db.query(MaskedKeyword).filter(MaskedKeyword.keyword == keyword_data["keyword"]).first()
            if not existing:
                masked_keyword = MaskedKeyword(**keyword_data)
                db.add(masked_keyword)
        
        # 기본 시스템 설정
        default_configs = [
            {"key": "vector_similarity_threshold", "value": "0.75", "description": "벡터 유사도 임계값"},
            {"key": "max_prompt_length", "value": "10000", "description": "최대 프롬프트 길이"},
            {"key": "enable_rebuff_sdk", "value": "true", "description": "Rebuff SDK 활성화 여부"},
            {"key": "enable_elasticsearch_logging", "value": "true", "description": "Elasticsearch 로깅 활성화 여부"},
        ]
        
        for config_data in default_configs:
            existing = db.query(SystemConfig).filter(SystemConfig.key == config_data["key"]).first()
            if not existing:
                system_config = SystemConfig(**config_data)
                db.add(system_config)
        
        db.commit()
        print("✅ 초기 데이터 삽입 완료")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 초기 데이터 삽입 실패: {str(e)}")
    finally:
        db.close()

# 데이터베이스 세션 의존성
def get_db():
    """데이터베이스 세션 반환"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
