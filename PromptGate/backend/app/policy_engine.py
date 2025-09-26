"""
OPA (Open Policy Agent) 기반 정책 엔진 구현
Rego 정책 언어를 사용하여 테넌트별 정책 관리
"""

import json
import httpx
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class PolicyAction(Enum):
    ALLOW = "allow"
    DENY = "deny"
    SANITIZE = "sanitize"
    MASK = "mask"
    ALERT = "alert"

@dataclass
class PolicyResult:
    action: PolicyAction = PolicyAction.ALLOW
    reason: str = "Policy evaluation passed"
    confidence: float = 1.0
    violations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0

@dataclass
class RequestContext:
    tenant_id: str
    user_id: str
    session_id: str
    request_id: str
    timestamp: datetime
    client_ip: str
    user_agent: str
    user_roles: List[str] = field(default_factory=list)
    user_permissions: List[str] = field(default_factory=list)

class OPAClient:
    """OPA 서버와 통신하는 클라이언트"""
    
    def __init__(self, opa_url: str = "http://localhost:8181"):
        self.opa_url = opa_url
        self.timeout = 5.0
        logger.info(f"OPA 클라이언트 초기화: {opa_url}")
    
    async def query_policy(self, policy_path: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """OPA 정책 쿼리 실행"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.opa_url}/v1/data/{policy_path}",
                    json={"input": input_data}
                )
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            logger.error(f"OPA 쿼리 타임아웃: {policy_path}")
            return {"result": {"allow": False, "reason": "OPA timeout"}}
        except Exception as e:
            logger.error(f"OPA 쿼리 실패: {e}")
            return {"result": {"allow": False, "reason": f"OPA error: {str(e)}"}}
    
    async def health_check(self) -> bool:
        """OPA 서버 상태 확인"""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f"{self.opa_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"OPA 헬스체크 실패: {e}")
            return False

class PolicyEngine:
    """정책 엔진 메인 클래스"""
    
    def __init__(self, opa_url: str = None):
        self.opa_url = opa_url or os.getenv("OPA_URL", "http://localhost:8181")
        self.opa_client = OPAClient(self.opa_url)
        self.policies = {}
        self.is_initialized = False
        
        # 기본 정책 로드
        self._load_default_policies()
        logger.info("정책 엔진 초기화 완료")
    
    def _load_default_policies(self):
        """기본 정책 로드"""
        self.policies = {
            "kra-internal": {
                "rules": {
                    "deny_patterns": [
                        r"(?i)ignore\s+(all\s+)?previous\s+(instructions?|rules?)",
                        r"(?i)admin(istrator)?\s+password",
                        r"(?i)system\s+prompt",
                        r"(?i)jailbreak"
                    ],
                    "pii_patterns": [
                        r"\b\d{6}-\d{7}\b",  # 주민번호
                        r"\b01[016789]-\d{3,4}-\d{4}\b",  # 휴대폰번호
                        r"\b\d{4}-\d{4}-\d{4}-\d{4}\b"  # 카드번호
                    ],
                    "secret_patterns": [
                        r"AKIA[0-9A-Z]{16}",  # AWS Access Key
                        r"sk-[a-zA-Z0-9]{48}",  # OpenAI Secret Key
                        r"Bearer\s+[a-zA-Z0-9\-_]+",  # Bearer Token
                    ],
                    "max_prompt_length": 4000,
                    "allowed_languages": ["ko", "en"]
                },
                "actions": {
                    "suspicious": "sanitize",
                    "pii_found": "mask",
                    "secrets_found": "deny",
                    "injection_detected": "deny",
                    "default": "allow"
                }
            },
            "default": {
                "rules": {
                    "deny_patterns": [
                        r"(?i)ignore\s+previous\s+instructions"
                    ],
                    "max_prompt_length": 2000
                },
                "actions": {
                    "suspicious": "alert",
                    "default": "allow"
                }
            }
        }
    
    async def initialize(self) -> bool:
        """정책 엔진 초기화"""
        try:
            # OPA 서버 상태 확인
            if not await self.opa_client.health_check():
                logger.warning("OPA 서버가 사용 불가능합니다. 로컬 정책 엔진을 사용합니다.")
                self.is_initialized = True
                return True
            
            # 기본 정책을 OPA에 업로드
            await self._upload_policies_to_opa()
            self.is_initialized = True
            logger.info("정책 엔진 초기화 성공")
            return True
            
        except Exception as e:
            logger.error(f"정책 엔진 초기화 실패: {e}")
            self.is_initialized = False
            return False
    
    async def _upload_policies_to_opa(self):
        """정책을 OPA 서버에 업로드"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                for tenant_id, policy in self.policies.items():
                    policy_data = {
                        "tenant": tenant_id,
                        "rules": policy["rules"],
                        "actions": policy["actions"]
                    }
                    
                    response = await client.put(
                        f"{self.opa_url}/v1/data/promptgate/policies/{tenant_id}",
                        json=policy_data
                    )
                    response.raise_for_status()
                    logger.info(f"정책 업로드 완료: {tenant_id}")
                    
        except Exception as e:
            logger.error(f"정책 업로드 실패: {e}")
    
    async def evaluate(self, context: RequestContext, prompt: str, 
                      filter_results: List[Dict[str, Any]] = None) -> PolicyResult:
        """정책 평가 실행"""
        start_time = datetime.now()
        
        try:
            # 입력 데이터 준비
            input_data = {
                "tenant": context.tenant_id,
                "user": {
                    "id": context.user_id,
                    "roles": context.user_roles,
                    "permissions": context.user_permissions
                },
                "prompt": {
                    "text": prompt,
                    "length": len(prompt),
                    "language": self._detect_language(prompt)
                },
                "context": {
                    "session_id": context.session_id,
                    "request_id": context.request_id,
                    "client_ip": context.client_ip,
                    "user_agent": context.user_agent,
                    "timestamp": context.timestamp.isoformat()
                },
                "filter_results": filter_results or []
            }
            
            # OPA 정책 평가
            if await self.opa_client.health_check():
                result = await self._evaluate_with_opa(input_data)
            else:
                result = await self._evaluate_locally(input_data)
            
            # 처리 시간 계산
            processing_time = (datetime.now() - start_time).total_seconds()
            result["processing_time"] = processing_time
            
            return PolicyResult(**result)
            
        except Exception as e:
            logger.error(f"정책 평가 실패: {e}")
            return PolicyResult(
                action=PolicyAction.DENY,
                reason=f"Policy evaluation failed: {str(e)}",
                confidence=0.0,
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    async def _evaluate_with_opa(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """OPA 서버를 사용한 정책 평가"""
        result = await self.opa_client.query_policy("promptgate/allow", input_data)
        
        if "result" in result:
            opa_result = result["result"]
            return {
                "action": PolicyAction.ALLOW if opa_result.get("allow", False) else PolicyAction.DENY,
                "reason": opa_result.get("reason", "OPA policy evaluation"),
                "confidence": opa_result.get("confidence", 1.0),
                "violations": opa_result.get("violations", []),
                "metadata": opa_result.get("metadata", {})
            }
        else:
            return {
                "action": PolicyAction.DENY,
                "reason": "OPA evaluation failed",
                "confidence": 0.0,
                "violations": ["opa_error"],
                "metadata": {}
            }
    
    async def _evaluate_locally(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """로컬 정책 엔진을 사용한 평가"""
        tenant_id = input_data["tenant"]
        prompt = input_data["prompt"]["text"]
        
        # 테넌트 정책 가져오기
        policy = self.policies.get(tenant_id, self.policies["default"])
        rules = policy["rules"]
        actions = policy["actions"]
        
        violations = []
        
        # 패턴 매칭 검사
        import re
        for pattern in rules.get("deny_patterns", []):
            if re.search(pattern, prompt, re.IGNORECASE):
                violations.append(f"deny_pattern: {pattern}")
        
        # PII 패턴 검사
        for pattern in rules.get("pii_patterns", []):
            if re.search(pattern, prompt):
                violations.append(f"pii_pattern: {pattern}")
        
        # 시크릿 패턴 검사
        for pattern in rules.get("secret_patterns", []):
            if re.search(pattern, prompt):
                violations.append(f"secret_pattern: {pattern}")
        
        # 프롬프트 길이 검사
        max_length = rules.get("max_prompt_length", 2000)
        if len(prompt) > max_length:
            violations.append(f"prompt_too_long: {len(prompt)} > {max_length}")
        
        # 언어 검사
        allowed_languages = rules.get("allowed_languages", [])
        if allowed_languages:
            detected_lang = self._detect_language(prompt)
            if detected_lang not in allowed_languages:
                violations.append(f"language_not_allowed: {detected_lang}")
        
        # 액션 결정
        if violations:
            if any("secret_pattern" in v for v in violations):
                action = PolicyAction.DENY
                reason = "Secret information detected"
            elif any("pii_pattern" in v for v in violations):
                action = PolicyAction.MASK
                reason = "PII detected, masking required"
            elif any("deny_pattern" in v for v in violations):
                action = PolicyAction.DENY
                reason = "Suspicious pattern detected"
            else:
                action = PolicyAction.ALERT
                reason = "Policy violations detected"
        else:
            action = PolicyAction.ALLOW
            reason = "Policy evaluation passed"
        
        return {
            "action": action,
            "reason": reason,
            "confidence": 1.0 if not violations else 0.8,
            "violations": violations,
            "metadata": {
                "tenant": tenant_id,
                "policy_version": "local",
                "evaluation_method": "local"
            }
        }
    
    def _detect_language(self, text: str) -> str:
        """간단한 언어 감지 (한국어/영어)"""
        korean_chars = len([c for c in text if '\uac00' <= c <= '\ud7af'])
        total_chars = len([c for c in text if c.isalpha()])
        
        if total_chars == 0:
            return "unknown"
        
        korean_ratio = korean_chars / total_chars
        return "ko" if korean_ratio > 0.3 else "en"
    
    async def add_policy(self, tenant_id: str, policy: Dict[str, Any]) -> bool:
        """새 정책 추가"""
        try:
            self.policies[tenant_id] = policy
            
            if await self.opa_client.health_check():
                await self._upload_policies_to_opa()
            
            logger.info(f"정책 추가 완료: {tenant_id}")
            return True
            
        except Exception as e:
            logger.error(f"정책 추가 실패: {e}")
            return False
    
    async def update_policy(self, tenant_id: str, policy: Dict[str, Any]) -> bool:
        """정책 업데이트"""
        return await self.add_policy(tenant_id, policy)
    
    async def delete_policy(self, tenant_id: str) -> bool:
        """정책 삭제"""
        try:
            if tenant_id in self.policies:
                del self.policies[tenant_id]
            
            if await self.opa_client.health_check():
                async with httpx.AsyncClient(timeout=5.0) as client:
                    await client.delete(f"{self.opa_url}/v1/data/promptgate/policies/{tenant_id}")
            
            logger.info(f"정책 삭제 완료: {tenant_id}")
            return True
            
        except Exception as e:
            logger.error(f"정책 삭제 실패: {e}")
            return False
    
    async def get_policy_status(self) -> Dict[str, Any]:
        """정책 엔진 상태 반환"""
        opa_available = await self.opa_client.health_check()
        
        return {
            "is_initialized": self.is_initialized,
            "opa_available": opa_available,
            "opa_url": self.opa_url,
            "policies_count": len(self.policies),
            "available_tenants": list(self.policies.keys()),
            "evaluation_method": "opa" if opa_available else "local"
        }

# 전역 정책 엔진 인스턴스
_policy_engine: Optional[PolicyEngine] = None

async def get_policy_engine() -> PolicyEngine:
    """정책 엔진 인스턴스 반환 (싱글톤)"""
    global _policy_engine
    
    if _policy_engine is None:
        _policy_engine = PolicyEngine()
        await _policy_engine.initialize()
    
    return _policy_engine

async def close_policy_engine():
    """정책 엔진 정리"""
    global _policy_engine
    
    if _policy_engine:
        _policy_engine = None
        logger.info("정책 엔진 정리 완료")

