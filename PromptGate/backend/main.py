from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from app.filter import evaluate_prompt
from app.logger import get_logger, log_to_elasticsearch
from app.api import router as api_router
from app.hybrid_security import get_hybrid_security_engine, close_hybrid_security_engine
from app.policy_engine import get_policy_engine, close_policy_engine
from app.secret_scanner import get_secret_scanner, close_secret_scanner
from app.pii_detector import get_pii_detector, close_pii_detector
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
    """애플리케이션 시작 시 하이브리드 보안 엔진 및 정책 엔진 초기화"""
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
        
        # toml 파일에서 패턴 로드 (우선순위 2)
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
        
        # toml 파일에서 패턴 로드 (우선순위 2)
        await pii_detector.load_patterns_from_toml()
        
        pii_status = pii_detector.get_scanner_status()
        logger.info(f"PII 탐지기 상태: {pii_status}")
    except Exception as e:
        logger.error(f"PII 탐지기 초기화 실패: {e}")
    
    try:
        # DB 필터링 엔진 초기화
        db_filter_engine = get_db_filter_engine()
        logger.info("DB 필터링 엔진 초기화 완료")
    except Exception as e:
        logger.error(f"DB 필터링 엔진 초기화 실패: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 리소스 정리"""
    logger.info("PromptGate 서비스 종료 - 리소스 정리")
    await close_hybrid_security_engine()
    await close_policy_engine()
    await close_secret_scanner()
    await close_pii_detector()

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
        # 하이브리드 보안 엔진 상태
        engine = await get_hybrid_security_engine()
        security_status = await engine.get_security_status()
        
        # 정책 엔진 상태
        policy_engine = await get_policy_engine()
        policy_status = await policy_engine.get_policy_status()
        
        # Secret Scanner 상태
        secret_scanner = await get_secret_scanner()
        scanner_status = secret_scanner.get_scanner_status()
        
        # PII 탐지기 상태
        pii_detector = await get_pii_detector()
        pii_status = pii_detector.get_scanner_status()
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "security_engine": security_status,
            "policy_engine": policy_status,
            "secret_scanner": scanner_status,
            "pii_detector": pii_status
        }
    except Exception as e:
        logger.error(f"보안 상태 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"상태 조회 실패: {str(e)}")

@app.post("/pii/scan")
async def scan_pii(request: Request):
    """PII 탐지 API"""
    try:
        data = await request.json()
        text = data.get("text", "")
        context = data.get("context", "")
        
        if not text:
            return {
                "status": "error",
                "message": "텍스트가 필요합니다",
                "timestamp": datetime.now().isoformat()
            }
        
        # PII 탐지기로 스캔
        pii_detector = await get_pii_detector()
        result = await pii_detector.scan_text(text, context)
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "result": {
                "has_pii": result.has_pii,
                "total_pii": result.total_pii,
                "high_confidence_pii": result.high_confidence_pii,
                "risk_score": result.risk_score,
                "processing_time": result.processing_time,
                "pii_matches": [
                    {
                        "pii_type": match.pii_type.value,
                        "confidence": match.confidence.value,
                        "matched_text": match.matched_text,
                        "start_pos": match.start_pos,
                        "end_pos": match.end_pos,
                        "metadata": match.metadata
                    }
                    for match in result.pii_matches
                ],
                "scanner_status": result.scanner_status,
                "error_messages": result.error_messages
            }
        }
    except Exception as e:
        logger.error(f"PII 스캔 실패: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/pii/anonymize")
async def anonymize_pii(request: Request):
    """PII 익명화 API"""
    try:
        data = await request.json()
        text = data.get("text", "")
        context = data.get("context", "")
        
        if not text:
            return {
                "status": "error",
                "message": "텍스트가 필요합니다",
                "timestamp": datetime.now().isoformat()
            }
        
        # PII 탐지기로 스캔
        pii_detector = await get_pii_detector()
        result = await pii_detector.scan_text(text, context)
        
        # 익명화
        anonymized_text = pii_detector.anonymize_text(text, result.pii_matches)
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "result": {
                "original_text": text,
                "anonymized_text": anonymized_text,
                "pii_detected": result.total_pii,
                "anonymization_applied": len(result.pii_matches),
                "processing_time": result.processing_time
            }
        }
    except Exception as e:
        logger.error(f"PII 익명화 실패: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {"status": "healthy", "service": "filter-service"}
