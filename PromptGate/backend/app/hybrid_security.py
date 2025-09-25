"""
하이브리드 보안 아키텍처 구현
1차: Rebuff SDK + 2차: DLP 검증
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import time

from .filter import evaluate_prompt
from .dlp_client import DLPClient, DLPResult, DLPAction, create_dlp_client, load_dlp_config

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """보안 수준"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityResult:
    """통합 보안 검증 결과"""
    # 기본 정보
    is_blocked: bool
    risk_score: float
    reason: str
    processing_time: float
    
    # 1차 검증 (Rebuff SDK)
    rebuff_result: Optional[Dict[str, Any]] = None
    rebuff_processing_time: Optional[float] = None
    
    # 2차 검증 (DLP)
    dlp_result: Optional[DLPResult] = None
    dlp_processing_time: Optional[float] = None
    
    # 통합 정보
    detection_methods: List[str] = None
    policy_violations: List[str] = None
    masked_prompt: Optional[str] = None
    audit_log_id: Optional[str] = None
    
    def __post_init__(self):
        if self.detection_methods is None:
            self.detection_methods = []
        if self.policy_violations is None:
            self.policy_violations = []

class HybridSecurityEngine:
    """하이브리드 보안 엔진"""
    
    def __init__(self, 
                 dlp_enabled: bool = True,
                 rebuff_enabled: bool = True,
                 security_level: SecurityLevel = SecurityLevel.MEDIUM):
        """
        하이브리드 보안 엔진 초기화
        
        Args:
            dlp_enabled: DLP 검증 활성화 여부
            rebuff_enabled: Rebuff SDK 활성화 여부
            security_level: 보안 수준
        """
        self.dlp_enabled = dlp_enabled
        self.rebuff_enabled = rebuff_enabled
        self.security_level = security_level
        
        # Rebuff SDK 초기화 (기존 evaluate_prompt 함수 사용)
        self.rebuff_enabled = rebuff_enabled
        if rebuff_enabled:
            logger.info("Rebuff SDK (기존 필터) 활성화")
        
        # DLP 클라이언트 초기화
        self.dlp_client = None
        if dlp_enabled:
            try:
                dlp_config = load_dlp_config()
                if dlp_config["api_key"]:
                    self.dlp_client = create_dlp_client(
                        api_url=dlp_config["api_url"],
                        api_key=dlp_config["api_key"]
                    )
                    logger.info("DLP 클라이언트 초기화 성공")
                else:
                    logger.warning("DLP API 키가 설정되지 않음")
                    self.dlp_enabled = False
            except Exception as e:
                logger.warning(f"DLP 클라이언트 초기화 실패: {e}")
                self.dlp_enabled = False
    
    async def validate_prompt(self,
                            prompt: str,
                            user_id: str = "anonymous",
                            session_id: str = "default",
                            context: Optional[Dict[str, Any]] = None) -> SecurityResult:
        """
        프롬프트 하이브리드 보안 검증
        
        Args:
            prompt: 검증할 프롬프트
            user_id: 사용자 ID
            session_id: 세션 ID
            context: 추가 컨텍스트
            
        Returns:
            SecurityResult: 통합 보안 검증 결과
        """
        start_time = time.time()
        
        # 1차 검증: Rebuff SDK
        rebuff_result = None
        rebuff_processing_time = None
        if self.rebuff_enabled:
            try:
                rebuff_start = time.time()
                rebuff_result = await self._validate_with_rebuff(prompt)
                rebuff_processing_time = time.time() - rebuff_start
                logger.info(f"Rebuff 검증 완료: {rebuff_processing_time:.3f}초")
            except Exception as e:
                logger.error(f"Rebuff 검증 실패: {e}")
                rebuff_result = {
                    "is_blocked": True,
                    "reason": f"Rebuff 검증 실패: {str(e)}",
                    "risk_score": 1.0,
                    "detection_method": "error"
                }
        
        # 2차 검증: DLP
        dlp_result = None
        dlp_processing_time = None
        if self.dlp_enabled and self.dlp_client:
            try:
                dlp_start = time.time()
                dlp_result = await self._validate_with_dlp(
                    prompt, user_id, session_id, context
                )
                dlp_processing_time = time.time() - dlp_start
                logger.info(f"DLP 검증 완료: {dlp_processing_time:.3f}초")
            except Exception as e:
                logger.error(f"DLP 검증 실패: {e}")
                dlp_result = DLPResult(
                    action=DLPAction.BLOCK,
                    confidence=1.0,
                    reason=f"DLP 검증 실패: {str(e)}",
                    policy_violations=["dlp_system_error"]
                )
        
        # 결과 통합
        final_result = self._integrate_results(
            prompt, rebuff_result, dlp_result, rebuff_processing_time, dlp_processing_time
        )
        
        total_time = time.time() - start_time
        final_result.processing_time = total_time
        
        # 감사 로그 기록
        if self.dlp_enabled and self.dlp_client:
            await self._log_security_event(
                "prompt_validation", user_id, session_id, {
                    "prompt_length": len(prompt),
                    "is_blocked": final_result.is_blocked,
                    "risk_score": final_result.risk_score,
                    "detection_methods": final_result.detection_methods,
                    "processing_time": total_time
                }
            )
        
        logger.info(f"하이브리드 보안 검증 완료: {total_time:.3f}초, 차단: {final_result.is_blocked}")
        return final_result
    
    async def validate_response(self,
                              response: str,
                              original_prompt: str,
                              user_id: str = "anonymous",
                              session_id: str = "default") -> SecurityResult:
        """
        AI 응답 하이브리드 보안 검증
        
        Args:
            response: 검증할 AI 응답
            original_prompt: 원본 프롬프트
            user_id: 사용자 ID
            session_id: 세션 ID
            
        Returns:
            SecurityResult: 통합 보안 검증 결과
        """
        start_time = time.time()
        
        # AI 응답은 주로 DLP로 검증 (데이터 유출 방지)
        dlp_result = None
        dlp_processing_time = None
        
        if self.dlp_enabled and self.dlp_client:
            try:
                dlp_start = time.time()
                dlp_result = await self.dlp_client.validate_response(
                    response, user_id, session_id, original_prompt
                )
                dlp_processing_time = time.time() - dlp_start
            except Exception as e:
                logger.error(f"AI 응답 DLP 검증 실패: {e}")
                dlp_result = DLPResult(
                    action=DLPAction.REVIEW,
                    confidence=0.0,
                    reason=f"DLP 검증 실패: {str(e)}",
                    policy_violations=["dlp_system_error"]
                )
        
        # 결과 생성
        is_blocked = dlp_result and dlp_result.action in [DLPAction.BLOCK, DLPAction.REVIEW]
        risk_score = dlp_result.confidence if dlp_result else 0.0
        reason = dlp_result.reason if dlp_result else "응답 검증 완료"
        
        result = SecurityResult(
            is_blocked=is_blocked,
            risk_score=risk_score,
            reason=reason,
            processing_time=time.time() - start_time,
            dlp_result=dlp_result,
            dlp_processing_time=dlp_processing_time,
            detection_methods=["dlp"] if dlp_result else [],
            policy_violations=dlp_result.policy_violations if dlp_result else [],
            masked_prompt=dlp_result.masked_content if dlp_result else response,
            audit_log_id=dlp_result.audit_log_id if dlp_result else None
        )
        
        return result
    
    async def _validate_with_rebuff(self, prompt: str) -> Dict[str, Any]:
        """Rebuff SDK를 사용한 프롬프트 검증"""
        if not self.rebuff_enabled:
            raise Exception("Rebuff 필터가 비활성화됨")
        
        # 기존 evaluate_prompt 함수 사용
        result = evaluate_prompt(prompt)
        
        return {
            "is_blocked": result.get("is_blocked", False),
            "reason": result.get("reason", ""),
            "risk_score": result.get("risk_score", 0.0),
            "detection_method": result.get("detection_method", "unknown"),
            "masked_prompt": result.get("masked_prompt", prompt)
        }
    
    async def _validate_with_dlp(self,
                               prompt: str,
                               user_id: str,
                               session_id: str,
                               context: Optional[Dict[str, Any]]) -> DLPResult:
        """DLP를 사용한 프롬프트 검증"""
        if not self.dlp_client:
            raise Exception("DLP 클라이언트가 초기화되지 않음")
        
        return await self.dlp_client.validate_prompt(
            prompt, user_id, session_id, context
        )
    
    def _integrate_results(self,
                         prompt: str,
                         rebuff_result: Optional[Dict[str, Any]],
                         dlp_result: Optional[DLPResult],
                         rebuff_time: Optional[float],
                         dlp_time: Optional[float]) -> SecurityResult:
        """Rebuff와 DLP 결과를 통합"""
        
        detection_methods = []
        policy_violations = []
        masked_prompt = prompt
        audit_log_id = None
        
        # Rebuff 결과 처리
        rebuff_blocked = False
        rebuff_risk = 0.0
        rebuff_reason = ""
        
        if rebuff_result:
            rebuff_blocked = rebuff_result.get("is_blocked", False)
            rebuff_risk = rebuff_result.get("risk_score", 0.0)
            rebuff_reason = rebuff_result.get("reason", "")
            detection_methods.append(rebuff_result.get("detection_method", "rebuff"))
            
            if rebuff_result.get("masked_prompt"):
                masked_prompt = rebuff_result["masked_prompt"]
        
        # DLP 결과 처리
        dlp_blocked = False
        dlp_risk = 0.0
        dlp_reason = ""
        
        if dlp_result:
            dlp_blocked = dlp_result.action in [DLPAction.BLOCK, DLPAction.REVIEW]
            dlp_risk = dlp_result.confidence
            dlp_reason = dlp_result.reason
            detection_methods.append("dlp")
            policy_violations.extend(dlp_result.policy_violations)
            
            if dlp_result.masked_content:
                masked_prompt = dlp_result.masked_content
            
            audit_log_id = dlp_result.audit_log_id
        
        # 최종 결정 로직
        is_blocked = rebuff_blocked or dlp_blocked
        risk_score = max(rebuff_risk, dlp_risk)
        
        # 이유 통합
        reasons = []
        if rebuff_reason:
            reasons.append(f"Rebuff: {rebuff_reason}")
        if dlp_reason:
            reasons.append(f"DLP: {dlp_reason}")
        
        final_reason = "; ".join(reasons) if reasons else "검증 완료"
        
        return SecurityResult(
            is_blocked=is_blocked,
            risk_score=risk_score,
            reason=final_reason,
            processing_time=0.0,  # 나중에 설정됨
            rebuff_result=rebuff_result,
            rebuff_processing_time=rebuff_time,
            dlp_result=dlp_result,
            dlp_processing_time=dlp_time,
            detection_methods=detection_methods,
            policy_violations=policy_violations,
            masked_prompt=masked_prompt,
            audit_log_id=audit_log_id
        )
    
    async def _log_security_event(self,
                                event_type: str,
                                user_id: str,
                                session_id: str,
                                details: Dict[str, Any]):
        """보안 이벤트 로그 기록"""
        if self.dlp_client:
            try:
                await self.dlp_client.log_audit_event(
                    event_type, user_id, session_id, details
                )
            except Exception as e:
                logger.error(f"보안 이벤트 로그 기록 실패: {e}")
    
    async def get_security_status(self) -> Dict[str, Any]:
        """보안 시스템 상태 조회"""
        status = {
            "rebuff_enabled": self.rebuff_enabled,
            "dlp_enabled": self.dlp_enabled,
            "security_level": self.security_level.value,
            "rebuff_status": "active" if self.rebuff_enabled else "inactive",
            "dlp_status": "active" if self.dlp_client else "inactive"
        }
        
        # DLP 정책 정보 추가
        if self.dlp_client:
            try:
                policies = await self.dlp_client.get_policies()
                status["dlp_policies_count"] = len(policies)
                status["dlp_policies"] = [
                    {
                        "id": p.policy_id,
                        "name": p.name,
                        "severity": p.severity,
                        "action": p.action.value
                    }
                    for p in policies
                ]
            except Exception as e:
                logger.error(f"DLP 정책 조회 실패: {e}")
                status["dlp_policies_error"] = str(e)
        
        return status
    
    async def close(self):
        """리소스 정리"""
        if self.dlp_client:
            await self.dlp_client.close()

# 전역 하이브리드 보안 엔진 인스턴스
_hybrid_engine: Optional[HybridSecurityEngine] = None

async def get_hybrid_security_engine() -> HybridSecurityEngine:
    """하이브리드 보안 엔진 싱글톤 인스턴스 반환"""
    global _hybrid_engine
    
    if _hybrid_engine is None:
        _hybrid_engine = HybridSecurityEngine()
    
    return _hybrid_engine

async def close_hybrid_security_engine():
    """하이브리드 보안 엔진 리소스 정리"""
    global _hybrid_engine
    
    if _hybrid_engine:
        await _hybrid_engine.close()
        _hybrid_engine = None
