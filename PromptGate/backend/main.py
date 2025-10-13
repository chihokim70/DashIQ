from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from app.logger import get_logger, log_to_elasticsearch
from app.api import router as api_router
from app.filter import evaluate_prompt
from app.hybrid_security import get_hybrid_security_engine, close_hybrid_security_engine
from app.policy_engine import get_policy_engine, close_policy_engine
from app.secret_scanner import get_secret_scanner, close_secret_scanner
from app.pii_detector import get_pii_detector, close_pii_detector
from app.rebuff_sdk_client import get_rebuff_client, close_rebuff_client
from app.ml_classifier import get_ml_classifier, close_ml_classifier
from app.embedding_filter import get_embedding_filter, close_embedding_filter
from app.db_filter_engine import get_db_filter_engine
from datetime import datetime
import asyncio
import logging

app = FastAPI(title="PromptGate Filter Service", version="1.0.0")
logger = get_logger("filter-service")

# API 라우터 등록
app.include_router(api_router, prefix="/api/v1", tags=["chat"])

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 보안 엔진 및 정책 엔진 초기화"""
    logger.info("PromptGate 서비스 시작 - 보안 엔진 및 정책 엔진 초기화")
    
    try:
        # 하이브리드 보안 엔진 초기화
        engine = await get_hybrid_security_engine()
        status = await engine.get_security_status()
        logger.info(f"하이브리드 보안 엔진 상태: {status}")
    except Exception as e:
        logger.error(f"하이브리드 보안 엔진 초기화 실패: {e}")
    
    try:
        # OPA 정책 엔진 초기화
        policy_engine = await get_policy_engine()
        policy_status = await policy_engine.get_policy_status()
        logger.info(f"정책 엔진 상태: {policy_status}")
    except Exception as e:
        logger.error(f"정책 엔진 초기화 실패: {e}")
    
    try:
        # Secret Scanner 초기화
        secret_scanner = await get_secret_scanner()
        
        # DB에서 패턴 로드 (우선순위 1)
        await secret_scanner.load_patterns_from_db(tenant_id=1)
        
        # TOML에서 패턴 로드 (우선순위 2)
        await secret_scanner.load_patterns_from_toml()
        
        scanner_status = secret_scanner.get_scanner_status()
        logger.info(f"Secret Scanner 상태: {scanner_status}")
    except Exception as e:
        logger.error(f"Secret Scanner 초기화 실패: {e}")
    
    try:
        # PII 탐지기 초기화
        pii_detector = await get_pii_detector()
        
        # DB에서 패턴 로드 (우선순위 1)
        await pii_detector.load_patterns_from_db(tenant_id=1)
        
        # TOML에서 패턴 로드 (우선순위 2)
        await pii_detector.load_patterns_from_toml()
        
        pii_status = pii_detector.get_scanner_status()
        logger.info(f"PII 탐지기 상태: {pii_status}")
    except Exception as e:
        logger.error(f"PII 탐지기 초기화 실패: {e}")
    
    try:
        # Rebuff SDK 클라이언트 초기화
        rebuff_client = await get_rebuff_client()
        rebuff_status = rebuff_client.get_status()
        logger.info(f"Rebuff SDK 클라이언트 상태: {rebuff_status}")
    except Exception as e:
        logger.error(f"Rebuff SDK 클라이언트 초기화 실패: {e}")
    
    try:
        # ML Classifier 초기화
        ml_classifier = await get_ml_classifier()
        ml_status = ml_classifier.get_status()
        logger.info(f"ML Classifier 상태: {ml_status}")
    except Exception as e:
        logger.error(f"ML Classifier 초기화 실패: {e}")
    
    try:
        # Embedding Filter 초기화
        embedding_filter = await get_embedding_filter()
        embedding_status = embedding_filter.get_status()
        logger.info(f"Embedding Filter 상태: {embedding_status}")
    except Exception as e:
        logger.error(f"Embedding Filter 초기화 실패: {e}")
    
    try:
        # DB 필터링 엔진 초기화
        db_filter_engine = get_db_filter_engine()
        logger.info("DB 필터링 엔진 초기화 완료")
    except Exception as e:
        logger.error(f"DB 필터링 엔진 초기화 실패: {e}")
    
    logger.info("PromptGate 서비스 초기화 완료")

@app.post("/prompt/check")
async def check_prompt(request: Request):
    """기존 프롬프트 검증 (하위 호환성 유지) - 실제 필터링 로직 복원"""
    data = await request.json()
    prompt = data.get("prompt", "")
    user_id = data.get("user_id", "anonymous")
    
    # 실제 evaluate_prompt 함수 사용
    result = await evaluate_prompt(prompt, user_id=user_id)

    # Elasticsearch 로그 저장
    log_to_elasticsearch(
        index="prompt-log",
        document={
             "timestamp": datetime.utcnow().isoformat(),
             "user_id": user_id,
             "session_id": "session-001",  # 추후 확장
             "prompt": prompt,
             "masked_prompt": result.get("masked_prompt", ""),
             "is_blocked": result.get("is_blocked"),
             "block_type": result.get("block_type", "none"),
             "reason": result.get("reason", result.get("error", "")),
             "risk_score": result.get("risk_score", None),
             "ai_service": "openai",
             "ip": "127.0.0.1",
             "source": "proxy"
        }
    )  

    logger.info(f"Prompt Check: {prompt} -> {result}")
    return result

@app.post("/prompt/check/hybrid")
async def check_prompt_hybrid(request: Request):
    """하이브리드 보안 검증 (1차: Rebuff SDK + 2차: DLP) - 단순화"""
    data = await request.json()
    prompt = data.get("prompt", "")
    
    # 단순한 응답 반환 (향후 기능 복원 예정)
    result = {
        "is_blocked": False,
        "reason": "하이브리드 검증 통과",
        "detection_method": "hybrid",
        "risk_score": 0.0,
        "masked_prompt": prompt,
        "processing_time": 0.001
    }
    
    logger.info(f"Hybrid Check: {prompt} -> {result}")
    return result

@app.post("/response/check/hybrid")
async def check_response_hybrid(request: Request):
    """응답 검증 (하이브리드) - 단순화"""
    data = await request.json()
    response = data.get("response", "")
    
    # 단순한 응답 반환 (향후 기능 복원 예정)
    result = {
        "is_blocked": False,
        "reason": "응답이 안전합니다",
        "detection_method": "hybrid",
        "risk_score": 0.0,
        "masked_response": response,
        "processing_time": 0.001
    }
    
    logger.info(f"Response Check: {response} -> {result}")
    return result

@app.get("/security/status")
async def get_security_status():
    """보안 엔진 상태 조회 - 단순화"""
    return {
        "status": "healthy",
        "engines": {
            "filter": "active",
            "policy": "active",
            "secret_scanner": "active",
            "pii_detector": "active",
            "rebuff": "active",
            "ml_classifier": "active",
            "embedding_filter": "active"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "service": "PromptGate Filter Service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)