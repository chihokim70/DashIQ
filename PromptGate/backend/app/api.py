from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import httpx
import json
import uuid
from datetime import datetime
from app.filter import evaluate_prompt_with_policy
from app.policy_engine import get_policy_engine
from app.secret_scanner import get_secret_scanner
from app.rebuff_sdk_client import get_rebuff_client
from app.ml_classifier import get_ml_classifier
from app.embedding_filter import get_embedding_filter

router = APIRouter()

class PromptRequest(BaseModel):
    prompt: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    tenant_id: Optional[str] = "kra-internal"
    user_roles: Optional[List[str]] = None
    user_permissions: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class PromptResponse(BaseModel):
    is_blocked: bool
    reason: str
    masked_prompt: str
    risk_score: float
    detection_method: str
    processing_time: float
    policy_processing_time: Optional[float] = None
    policy_violations: Optional[List[str]] = None
    requires_masking: Optional[bool] = None
    requires_alert: Optional[bool] = None
    filter_results: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    blocked_keywords: Optional[list] = None
    tactics: Optional[list] = None
    error: Optional[str] = None

class PolicyRequest(BaseModel):
    keyword: str
    category: str
    severity: str
    description: Optional[str] = None

class PolicyResponse(BaseModel):
    success: bool
    message: str
    policy_id: Optional[int] = None

class RebuffRequest(BaseModel):
    prompt: str
    run_heuristic: bool = True
    run_vector: bool = True
    run_llm: bool = True
    max_heuristic_score: float = 0.75
    max_vector_score: float = 0.9
    max_model_score: float = 0.9

class RebuffResponse(BaseModel):
    is_injection: bool
    confidence: float
    method: str
    reasons: List[str]
    tactics: List[str]
    processing_time: float
    error: Optional[str] = None

class MLClassificationRequest(BaseModel):
    prompt: str
    include_features: bool = False

class MLClassificationResponse(BaseModel):
    risk_category: str
    risk_score: float
    threat_types: List[str]
    confidence: float
    processing_time: float
    model_used: str
    features_extracted: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class EmbeddingSimilarityRequest(BaseModel):
    prompt: str
    threshold: Optional[float] = None
    max_results: Optional[int] = None

class EmbeddingSimilarityResponse(BaseModel):
    is_similar: bool
    similarity_score: float
    matched_prompts: List[Dict[str, Any]]
    method_used: str
    processing_time: float
    embedding_model: str
    threshold_used: float
    error: Optional[str] = None

@router.post("/evaluate", response_model=PromptResponse)
async def evaluate_prompt_endpoint(
    request: PromptRequest,
    http_request: Request
):
    """
    OPA 정책 엔진을 사용한 프롬프트 평가 및 필터링
    """
    try:
        # 클라이언트 정보 추출
        ip_address = http_request.client.host if http_request.client else None
        user_agent = http_request.headers.get("user-agent")
        
        # 세션 ID가 없으면 생성
        session_id = request.session_id or str(uuid.uuid4())
        
        # OPA 정책 엔진을 사용한 프롬프트 평가
        result = await evaluate_prompt_with_policy(
            prompt=request.prompt,
            tenant_id=request.tenant_id,
            user_id=request.user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            user_roles=request.user_roles,
            user_permissions=request.user_permissions
        )
        
        return PromptResponse(
            is_blocked=result.get("is_blocked", False),
            reason=result.get("reason", "Unknown"),
            masked_prompt=result.get("masked_prompt", request.prompt),
            risk_score=result.get("risk_score", 0.0),
            detection_method=result.get("detection_method", "unknown"),
            processing_time=result.get("processing_time", 0.0),
            policy_processing_time=result.get("policy_processing_time"),
            policy_violations=result.get("policy_violations"),
            requires_masking=result.get("requires_masking"),
            requires_alert=result.get("requires_alert"),
            filter_results=result.get("filter_results"),
            metadata=result.get("metadata"),
            blocked_keywords=result.get("blocked_keywords"),
            tactics=result.get("tactics"),
            error=result.get("error")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"프롬프트 평가 중 오류가 발생했습니다: {str(e)}")

@router.get("/policy/status")
async def get_policy_status():
    """
    정책 엔진 상태 조회
    """
    try:
        policy_engine = await get_policy_engine()
        status = await policy_engine.get_policy_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정책 상태 조회 실패: {str(e)}")

@router.get("/secret-scanner/status")
async def get_secret_scanner_status():
    """
    Secret Scanner 상태 조회
    """
    try:
        secret_scanner = await get_secret_scanner()
        status = secret_scanner.get_scanner_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Secret Scanner 상태 조회 실패: {str(e)}")

@router.post("/policy/blocked-keyword", response_model=PolicyResponse)
async def add_blocked_keyword(request: PolicyRequest):
    """
    차단 키워드를 추가합니다.
    """
    try:
        from app.schema import SessionLocal, BlockedKeyword
        
        db = SessionLocal()
        try:
            # 중복 확인
            existing = db.query(BlockedKeyword).filter(BlockedKeyword.keyword == request.keyword).first()
            if existing:
                return PolicyResponse(
                    success=False,
                    message=f"키워드 '{request.keyword}'는 이미 존재합니다."
                )
            
            # 새 키워드 추가
            new_keyword = BlockedKeyword(
                keyword=request.keyword,
                category=request.category,
                severity=request.severity,
                description=request.description
            )
            
            db.add(new_keyword)
            db.commit()
            db.refresh(new_keyword)
            
            return PolicyResponse(
                success=True,
                message=f"키워드 '{request.keyword}'가 성공적으로 추가되었습니다.",
                policy_id=new_keyword.id
            )
            
        finally:
            db.close()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"키워드 추가 중 오류가 발생했습니다: {str(e)}")

@router.get("/policy/blocked-keywords")
async def get_blocked_keywords():
    """
    모든 차단 키워드를 조회합니다.
    """
    try:
        from app.schema import SessionLocal, BlockedKeyword
        
        db = SessionLocal()
        try:
            keywords = db.query(BlockedKeyword).filter(BlockedKeyword.is_active == True).all()
            return {
                "success": True,
                "keywords": [
                    {
                        "id": kw.id,
                        "keyword": kw.keyword,
                        "category": kw.category,
                        "severity": kw.severity,
                        "description": kw.description
                    }
                    for kw in keywords
                ]
            }
        finally:
            db.close()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"키워드 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/stats")
async def get_filter_stats():
    """
    필터링 통계를 반환합니다.
    """
    try:
        from app.schema import SessionLocal, PromptLog
        from datetime import datetime, timedelta
        
        db = SessionLocal()
        try:
            # 최근 24시간 통계
            yesterday = datetime.utcnow() - timedelta(days=1)
            
            total_requests = db.query(PromptLog).filter(PromptLog.created_at >= yesterday).count()
            blocked_requests = db.query(PromptLog).filter(
                PromptLog.created_at >= yesterday,
                PromptLog.is_blocked == True
            ).count()
            
            # 탐지 방법별 통계
            detection_stats = db.query(PromptLog.detection_method).filter(
                PromptLog.created_at >= yesterday
            ).all()
            
            method_counts = {}
            for method in detection_stats:
                method_counts[method[0]] = method_counts.get(method[0], 0) + 1
            
            return {
                "success": True,
                "stats": {
                    "total_requests_24h": total_requests,
                    "blocked_requests_24h": blocked_requests,
                    "block_rate_24h": (blocked_requests / total_requests * 100) if total_requests > 0 else 0,
                    "detection_methods": method_counts
                }
            }
        finally:
            db.close()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 중 오류가 발생했습니다: {str(e)}")

@router.post("/rebuff/detect", response_model=RebuffResponse)
async def detect_prompt_injection(request: RebuffRequest):
    """Rebuff SDK를 사용한 프롬프트 인젝션 탐지"""
    try:
        rebuff_client = await get_rebuff_client()
        
        if not rebuff_client.is_initialized:
            raise HTTPException(
                status_code=503, 
                detail="Rebuff SDK가 초기화되지 않았습니다. 환경 변수를 확인해주세요."
            )
        
        result = await rebuff_client.detect_injection(
            prompt=request.prompt,
            run_heuristic=request.run_heuristic,
            run_vector=request.run_vector,
            run_llm=request.run_llm,
            max_heuristic_score=request.max_heuristic_score,
            max_vector_score=request.max_vector_score,
            max_model_score=request.max_model_score
        )
        
        return RebuffResponse(
            is_injection=result.is_injection,
            confidence=result.confidence,
            method=result.method.value,
            reasons=result.reasons,
            tactics=result.tactics,
            processing_time=result.processing_time
        )
        
    except Exception as e:
        logger.error(f"Rebuff 탐지 실패: {e}")
        return RebuffResponse(
            is_injection=False,
            confidence=0.0,
            method="error",
            reasons=[],
            tactics=[],
            processing_time=0.0,
            error=str(e)
        )

@router.get("/rebuff/status")
async def get_rebuff_status():
    """Rebuff SDK 상태 조회"""
    try:
        rebuff_client = await get_rebuff_client()
        status = rebuff_client.get_status()
        
        return {
            "success": True,
            "status": status,
            "initialized": rebuff_client.is_initialized,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Rebuff 상태 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"Rebuff 상태 조회 실패: {str(e)}")

@router.post("/ml/classify", response_model=MLClassificationResponse)
async def classify_prompt_with_ml(request: MLClassificationRequest):
    """ML Classifier를 사용한 프롬프트 위험도 분류"""
    try:
        ml_classifier = await get_ml_classifier()
        
        if not ml_classifier.is_initialized:
            raise HTTPException(
                status_code=503, 
                detail="ML Classifier가 초기화되지 않았습니다."
            )
        
        result = await ml_classifier.classify_prompt(request.prompt)
        
        return MLClassificationResponse(
            risk_category=result.risk_category.value,
            risk_score=result.risk_score,
            threat_types=[threat.value for threat in result.threat_types],
            confidence=result.confidence,
            processing_time=result.processing_time,
            model_used=result.model_used,
            features_extracted=result.features_extracted if request.include_features else None,
            error="; ".join(result.error_messages) if result.error_messages else None
        )
        
    except Exception as e:
        logger.error(f"ML 분류 실패: {e}")
        return MLClassificationResponse(
            risk_category="unknown",
            risk_score=0.0,
            threat_types=["unknown"],
            confidence=0.0,
            processing_time=0.0,
            model_used="error",
            error=str(e)
        )

@router.get("/ml/status")
async def get_ml_classifier_status():
    """ML Classifier 상태 조회"""
    try:
        ml_classifier = await get_ml_classifier()
        status = ml_classifier.get_status()
        
        return {
            "success": True,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"ML Classifier 상태 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"ML Classifier 상태 조회 실패: {str(e)}")

@router.post("/embedding/similarity", response_model=EmbeddingSimilarityResponse)
async def check_embedding_similarity(request: EmbeddingSimilarityRequest):
    """Embedding Filter를 사용한 프롬프트 유사도 검사"""
    try:
        embedding_filter = await get_embedding_filter()
        
        if not embedding_filter.is_initialized:
            raise HTTPException(
                status_code=503, 
                detail="Embedding Filter가 초기화되지 않았습니다."
            )
        
        result = await embedding_filter.check_similarity(
            prompt=request.prompt,
            threshold=request.threshold,
            max_results=request.max_results
        )
        
        return EmbeddingSimilarityResponse(
            is_similar=result.is_similar,
            similarity_score=result.similarity_score,
            matched_prompts=result.matched_prompts,
            method_used=result.method_used,
            processing_time=result.processing_time,
            embedding_model=result.embedding_model,
            threshold_used=result.threshold_used,
            error="; ".join(result.error_messages) if result.error_messages else None
        )
        
    except Exception as e:
        logger.error(f"Embedding 유사도 검사 실패: {e}")
        return EmbeddingSimilarityResponse(
            is_similar=False,
            similarity_score=0.0,
            matched_prompts=[],
            method_used="error",
            processing_time=0.0,
            embedding_model="error",
            threshold_used=request.threshold or 0.75,
            error=str(e)
        )

@router.post("/embedding/add-blocked")
async def add_blocked_prompt(
    prompt: str,
    category: str = "malicious",
    severity: str = "high",
    source: str = "manual"
):
    """차단 프롬프트 추가"""
    try:
        embedding_filter = await get_embedding_filter()
        
        if not embedding_filter.is_initialized:
            raise HTTPException(
                status_code=503, 
                detail="Embedding Filter가 초기화되지 않았습니다."
            )
        
        success = await embedding_filter.add_blocked_prompt(
            prompt=prompt,
            category=category,
            severity=severity,
            source=source
        )
        
        if success:
            return {
                "success": True,
                "message": "차단 프롬프트가 성공적으로 추가되었습니다.",
                "prompt": prompt[:50] + "..." if len(prompt) > 50 else prompt
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="차단 프롬프트 추가에 실패했습니다."
            )
        
    except Exception as e:
        logger.error(f"차단 프롬프트 추가 실패: {e}")
        raise HTTPException(status_code=500, detail=f"차단 프롬프트 추가 실패: {str(e)}")

@router.get("/embedding/stats")
async def get_embedding_stats():
    """Embedding Filter 통계 조회"""
    try:
        embedding_filter = await get_embedding_filter()
        
        if not embedding_filter.is_initialized:
            raise HTTPException(
                status_code=503, 
                detail="Embedding Filter가 초기화되지 않았습니다."
            )
        
        stats = await embedding_filter.get_collection_stats()
        
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Embedding 통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"Embedding 통계 조회 실패: {str(e)}")

@router.get("/embedding/status")
async def get_embedding_filter_status():
    """Embedding Filter 상태 조회"""
    try:
        embedding_filter = await get_embedding_filter()
        status = embedding_filter.get_status()
        
        return {
            "success": True,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Embedding Filter 상태 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"Embedding Filter 상태 조회 실패: {str(e)}")

@router.get("/health")
async def health_check():
    """서비스 상태 확인"""
    return {"status": "healthy", "service": "filter-service"} 