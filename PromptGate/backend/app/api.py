from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import httpx
import json
import uuid
from datetime import datetime
from app.filter import evaluate_prompt_with_policy
from app.policy_engine import get_policy_engine

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

@router.get("/health")
async def health_check():
    """서비스 상태 확인"""
    return {"status": "healthy", "service": "filter-service"} 