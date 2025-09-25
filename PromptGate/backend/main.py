from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from app.filter import evaluate_prompt
from app.logger import get_logger, log_to_elasticsearch
from app.api import router as api_router
from app.hybrid_security import get_hybrid_security_engine, close_hybrid_security_engine
from datetime import datetime
import asyncio
import logging

app = FastAPI(title="PromptGate Filter Service", version="1.0.0")
logger = get_logger("filter-service")

# API 라우터 등록
app.include_router(api_router, prefix="/api/v1", tags=["chat"])

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 하이브리드 보안 엔진 초기화"""
    logger.info("PromptGate 서비스 시작 - 하이브리드 보안 엔진 초기화")
    try:
        engine = await get_hybrid_security_engine()
        status = await engine.get_security_status()
        logger.info(f"하이브리드 보안 엔진 상태: {status}")
    except Exception as e:
        logger.error(f"하이브리드 보안 엔진 초기화 실패: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 리소스 정리"""
    logger.info("PromptGate 서비스 종료 - 리소스 정리")
    await close_hybrid_security_engine()

@app.post("/prompt/check")
async def check_prompt(request: Request):
    """기존 프롬프트 검증 (하위 호환성 유지)"""
    data = await request.json()
    prompt = data.get("prompt", "")
    result = evaluate_prompt(prompt)

    log_to_elasticsearch(
        index="prompt-log",
        document={
             "timestamp": datetime.utcnow().isoformat(),
             "user_id": "root",
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
    """하이브리드 보안 검증 (1차: Rebuff SDK + 2차: DLP)"""
    try:
        data = await request.json()
        prompt = data.get("prompt", "")
        user_id = data.get("user_id", "anonymous")
        session_id = data.get("session_id", "default")
        context = data.get("context", {})
        
        if not prompt:
            raise HTTPException(status_code=400, detail="프롬프트가 필요합니다")
        
        # 하이브리드 보안 엔진으로 검증
        engine = await get_hybrid_security_engine()
        security_result = await engine.validate_prompt(
            prompt=prompt,
            user_id=user_id,
            session_id=session_id,
            context=context
        )
        
        # 결과를 기존 형식으로 변환
        result = {
            "is_blocked": security_result.is_blocked,
            "reason": security_result.reason,
            "detection_method": "+".join(security_result.detection_methods),
            "risk_score": security_result.risk_score,
            "masked_prompt": security_result.masked_prompt,
            "processing_time": security_result.processing_time,
            "policy_violations": security_result.policy_violations,
            "audit_log_id": security_result.audit_log_id,
            "security_details": {
                "rebuff_result": security_result.rebuff_result,
                "dlp_result": {
                    "action": security_result.dlp_result.action.value if security_result.dlp_result else None,
                    "confidence": security_result.dlp_result.confidence if security_result.dlp_result else None,
                    "reason": security_result.dlp_result.reason if security_result.dlp_result else None
                } if security_result.dlp_result else None,
                "rebuff_processing_time": security_result.rebuff_processing_time,
                "dlp_processing_time": security_result.dlp_processing_time
            }
        }
        
        # Elasticsearch 로그 기록
        log_to_elasticsearch(
            index="prompt-log-hybrid",
            document={
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "session_id": session_id,
                "prompt": prompt,
                "masked_prompt": security_result.masked_prompt,
                "is_blocked": security_result.is_blocked,
                "reason": security_result.reason,
                "risk_score": security_result.risk_score,
                "detection_methods": security_result.detection_methods,
                "policy_violations": security_result.policy_violations,
                "processing_time": security_result.processing_time,
                "audit_log_id": security_result.audit_log_id,
                "ai_service": "hybrid_security",
                "ip": request.client.host if request.client else "127.0.0.1",
                "source": "hybrid_proxy"
            }
        )
        
        logger.info(f"하이브리드 보안 검증 완료: {prompt[:50]}... -> 차단: {security_result.is_blocked}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"하이브리드 보안 검증 실패: {e}")
        raise HTTPException(status_code=500, detail=f"보안 검증 실패: {str(e)}")

@app.post("/response/check/hybrid")
async def check_response_hybrid(request: Request):
    """AI 응답 하이브리드 보안 검증"""
    try:
        data = await request.json()
        response = data.get("response", "")
        original_prompt = data.get("original_prompt", "")
        user_id = data.get("user_id", "anonymous")
        session_id = data.get("session_id", "default")
        
        if not response:
            raise HTTPException(status_code=400, detail="AI 응답이 필요합니다")
        
        # 하이브리드 보안 엔진으로 응답 검증
        engine = await get_hybrid_security_engine()
        security_result = await engine.validate_response(
            response=response,
            original_prompt=original_prompt,
            user_id=user_id,
            session_id=session_id
        )
        
        result = {
            "is_blocked": security_result.is_blocked,
            "reason": security_result.reason,
            "risk_score": security_result.risk_score,
            "masked_response": security_result.masked_prompt,
            "processing_time": security_result.processing_time,
            "policy_violations": security_result.policy_violations,
            "audit_log_id": security_result.audit_log_id
        }
        
        logger.info(f"AI 응답 하이브리드 보안 검증 완료: 차단: {security_result.is_blocked}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI 응답 하이브리드 보안 검증 실패: {e}")
        raise HTTPException(status_code=500, detail=f"응답 검증 실패: {str(e)}")

@app.get("/security/status")
async def get_security_status():
    """하이브리드 보안 시스템 상태 조회"""
    try:
        engine = await get_hybrid_security_engine()
        status = await engine.get_security_status()
        return status
    except Exception as e:
        logger.error(f"보안 상태 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"상태 조회 실패: {str(e)}")

@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {"status": "healthy", "service": "filter-service"}
