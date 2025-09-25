"""
DLP (Data Loss Prevention) 연동 클라이언트
하이브리드 보안 아키텍처의 2차 검증을 담당
"""

import httpx
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class DLPAction(Enum):
    """DLP 검증 결과 액션"""
    ALLOW = "allow"
    BLOCK = "block"
    REVIEW = "review"
    MASK = "mask"

@dataclass
class DLPResult:
    """DLP 검증 결과"""
    action: DLPAction
    confidence: float
    reason: str
    policy_violations: List[str]
    masked_content: Optional[str] = None
    audit_log_id: Optional[str] = None

@dataclass
class DLPPolicy:
    """DLP 정책 설정"""
    policy_id: str
    name: str
    description: str
    severity: str  # low, medium, high, critical
    patterns: List[str]
    action: DLPAction

class DLPClient:
    """DLP 시스템 연동 클라이언트"""
    
    def __init__(self, 
                 api_url: str,
                 api_key: str,
                 timeout: int = 30,
                 retry_count: int = 3):
        """
        DLP 클라이언트 초기화
        
        Args:
            api_url: DLP API 서버 URL
            api_key: DLP API 인증 키
            timeout: 요청 타임아웃 (초)
            retry_count: 재시도 횟수
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.retry_count = retry_count
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "AiGov-PromptGate/1.0"
            }
        )
    
    async def validate_prompt(self, 
                            prompt: str,
                            user_id: str,
                            session_id: str,
                            context: Optional[Dict[str, Any]] = None) -> DLPResult:
        """
        프롬프트 DLP 검증
        
        Args:
            prompt: 검증할 프롬프트
            user_id: 사용자 ID
            session_id: 세션 ID
            context: 추가 컨텍스트 정보
            
        Returns:
            DLPResult: 검증 결과
        """
        try:
            payload = {
                "content": prompt,
                "content_type": "prompt",
                "user_id": user_id,
                "session_id": session_id,
                "context": context or {},
                "scan_options": {
                    "scan_pii": True,
                    "scan_sensitive_data": True,
                    "scan_compliance": True,
                    "scan_custom_patterns": True
                }
            }
            
            response = await self._make_request(
                "POST", 
                "/api/v1/scan",
                json=payload
            )
            
            return self._parse_response(response)
            
        except Exception as e:
            logger.error(f"DLP 검증 실패: {e}")
            # DLP 실패 시 안전하게 차단
            return DLPResult(
                action=DLPAction.BLOCK,
                confidence=1.0,
                reason=f"DLP 검증 실패: {str(e)}",
                policy_violations=["dlp_system_error"]
            )
    
    async def validate_response(self,
                              response: str,
                              user_id: str,
                              session_id: str,
                              original_prompt: str) -> DLPResult:
        """
        AI 응답 DLP 검증
        
        Args:
            response: 검증할 AI 응답
            user_id: 사용자 ID
            session_id: 세션 ID
            original_prompt: 원본 프롬프트
            
        Returns:
            DLPResult: 검증 결과
        """
        try:
            payload = {
                "content": response,
                "content_type": "ai_response",
                "user_id": user_id,
                "session_id": session_id,
                "original_prompt": original_prompt,
                "scan_options": {
                    "scan_pii": True,
                    "scan_sensitive_data": True,
                    "scan_compliance": True,
                    "scan_data_leakage": True
                }
            }
            
            response_data = await self._make_request(
                "POST",
                "/api/v1/scan",
                json=payload
            )
            
            return self._parse_response(response_data)
            
        except Exception as e:
            logger.error(f"AI 응답 DLP 검증 실패: {e}")
            return DLPResult(
                action=DLPAction.REVIEW,
                confidence=0.0,
                reason=f"DLP 검증 실패: {str(e)}",
                policy_violations=["dlp_system_error"]
            )
    
    async def get_policies(self) -> List[DLPPolicy]:
        """
        활성 DLP 정책 목록 조회
        
        Returns:
            List[DLPPolicy]: 활성 정책 목록
        """
        try:
            response = await self._make_request("GET", "/api/v1/policies")
            
            policies = []
            for policy_data in response.get("policies", []):
                policy = DLPPolicy(
                    policy_id=policy_data["id"],
                    name=policy_data["name"],
                    description=policy_data["description"],
                    severity=policy_data["severity"],
                    patterns=policy_data["patterns"],
                    action=DLPAction(policy_data["action"])
                )
                policies.append(policy)
            
            return policies
            
        except Exception as e:
            logger.error(f"DLP 정책 조회 실패: {e}")
            return []
    
    async def log_audit_event(self,
                            event_type: str,
                            user_id: str,
                            session_id: str,
                            details: Dict[str, Any]) -> Optional[str]:
        """
        감사 이벤트 로그 기록
        
        Args:
            event_type: 이벤트 타입
            user_id: 사용자 ID
            session_id: 세션 ID
            details: 이벤트 상세 정보
            
        Returns:
            Optional[str]: 감사 로그 ID
        """
        try:
            payload = {
                "event_type": event_type,
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": asyncio.get_event_loop().time(),
                "details": details
            }
            
            response = await self._make_request(
                "POST",
                "/api/v1/audit/log",
                json=payload
            )
            
            return response.get("audit_log_id")
            
        except Exception as e:
            logger.error(f"감사 로그 기록 실패: {e}")
            return None
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        DLP API 요청 실행 (재시도 로직 포함)
        
        Args:
            method: HTTP 메서드
            endpoint: API 엔드포인트
            **kwargs: 요청 파라미터
            
        Returns:
            Dict[str, Any]: 응답 데이터
        """
        url = f"{self.api_url}{endpoint}"
        
        for attempt in range(self.retry_count):
            try:
                response = await self.client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500 and attempt < self.retry_count - 1:
                    # 서버 오류 시 재시도
                    await asyncio.sleep(2 ** attempt)  # 지수 백오프
                    continue
                else:
                    raise
            except Exception as e:
                if attempt < self.retry_count - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                else:
                    raise
    
    def _parse_response(self, response_data: Dict[str, Any]) -> DLPResult:
        """
        DLP API 응답 파싱
        
        Args:
            response_data: API 응답 데이터
            
        Returns:
            DLPResult: 파싱된 결과
        """
        action = DLPAction(response_data.get("action", "allow"))
        confidence = response_data.get("confidence", 0.0)
        reason = response_data.get("reason", "")
        violations = response_data.get("policy_violations", [])
        masked_content = response_data.get("masked_content")
        audit_log_id = response_data.get("audit_log_id")
        
        return DLPResult(
            action=action,
            confidence=confidence,
            reason=reason,
            policy_violations=violations,
            masked_content=masked_content,
            audit_log_id=audit_log_id
        )
    
    async def close(self):
        """클라이언트 연결 종료"""
        await self.client.aclose()

# DLP 클라이언트 팩토리 함수
def create_dlp_client(api_url: str, api_key: str) -> DLPClient:
    """
    DLP 클라이언트 생성
    
    Args:
        api_url: DLP API 서버 URL
        api_key: DLP API 인증 키
        
    Returns:
        DLPClient: 생성된 DLP 클라이언트
    """
    return DLPClient(api_url=api_url, api_key=api_key)

# 환경변수에서 DLP 설정 로드
def load_dlp_config() -> Dict[str, str]:
    """
    환경변수에서 DLP 설정 로드
    
    Returns:
        Dict[str, str]: DLP 설정
    """
    import os
    
    return {
        "api_url": os.getenv("DLP_API_URL", "https://dlp.company.com/api"),
        "api_key": os.getenv("DLP_API_KEY", ""),
        "timeout": os.getenv("DLP_TIMEOUT", "30"),
        "retry_count": os.getenv("DLP_RETRY_COUNT", "3")
    }
