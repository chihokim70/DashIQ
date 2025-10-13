import re
import time
import asyncio
from typing import Dict, Any
from datetime import datetime
from app.logger import get_logger, log_to_elasticsearch
from app.vector_store import check_similarity
from app.policy_client import get_block_keywords, get_mask_keywords
from app.rebuff_integration import rebuff_integration
from app.policy_engine import get_policy_engine, RequestContext, PolicyAction
from app.secret_scanner import get_secret_scanner, SecretScanResult, SecretType, SecretSeverity

logger = get_logger("filter")


def mask_prompt(prompt: str) -> str:
    masked = prompt

    # ✅ 마스킹 대상 키워드 → 실제 숫자 패턴 마스킹 조건 키워드
    keyword_groups = {
        "주민번호": ["주민번호", "주민등록번호", "주번"],
        "계좌번호": ["계좌번호", "은행계좌", "계번"],
        "카드번호": ["카드번호", "신용카드"],
        "면허번호": ["운전면허증", "면허증"]
    }

    # ✅ 각 민감 정보 패턴
    patterns = {
        "주민번호": r"\b\d{6}-\d{7}\b",
        "계좌번호": r"\b\d{2,4}(-\d{2,4}){1,2}\b",
        "카드번호": r"\b\d{4}-\d{4}-\d{4}-\d{4}\b",
        "면허번호": r"\b\d{8,12}\b"
    }

    # ✅ 1단계: 원본 prompt 기준으로 키워드 존재 → 해당 category의 숫자 마스킹
    for category, keywords in keyword_groups.items():
        if any(kw in prompt for kw in keywords):  # ← prompt 원문 기준
            masked = re.sub(patterns[category], "***", masked)

    return masked


async def evaluate_prompt_with_policy(
    prompt: str, 
    tenant_id: str = "kra-internal",
    user_id: str = None, 
    session_id: str = None, 
    ip_address: str = None, 
    user_agent: str = None,
    user_roles: list = None,
    user_permissions: list = None
) -> Dict[str, Any]:
    """
    OPA 정책 엔진을 사용한 프롬프트 평가 및 필터링
    
    Args:
        prompt: 평가할 프롬프트
        tenant_id: 테넌트 ID
        user_id: 사용자 ID
        session_id: 세션 ID
        ip_address: IP 주소
        user_agent: User Agent
        user_roles: 사용자 역할 목록
        user_permissions: 사용자 권한 목록
    
    Returns:
        Dict: 평가 결과
    """
    start_time = time.time()
    
    try:
        # 1단계: 기본 필터링 (기존 로직)
        filter_results = []
        
        # 차단 키워드 검사
        blocked_keywords = [k for k in get_block_keywords() if k in prompt]
        if blocked_keywords:
            filter_results.append({
                "filter_type": "keyword",
                "action": "block",
                "reason": "Blocked keyword detected",
                "details": {"keywords": blocked_keywords}
            })
        
        # Rebuff SDK 기반 프롬프트 인젝션 탐지
        rebuff_result = await rebuff_integration.detect_prompt_injection(prompt)
        if rebuff_result["is_injection"]:
            filter_results.append({
                "filter_type": "rebuff",
                "action": "block",
                "reason": f"Prompt injection detected: {', '.join(rebuff_result['reasons'])}",
                "details": {
                    "method": rebuff_result["method"],
                    "score": rebuff_result["score"],
                    "tactics": rebuff_result["tactics"]
                }
            })
        
        # 벡터 기반 유사도 검사
        if check_similarity(prompt):
            filter_results.append({
                "filter_type": "vector",
                "action": "block",
                "reason": "Similar to known dangerous prompt",
                "details": {"similarity_score": 0.8}
            })
        
        # 고급 Secret Scanner 검사
        secret_scanner = await get_secret_scanner()
        secret_scan_result = await secret_scanner.scan_text(prompt, f"user:{user_id}, session:{session_id}")
        
        if secret_scan_result.has_secrets:
            # 고위험 시크릿이 발견된 경우
            high_risk_secrets = [s for s in secret_scan_result.secrets 
                               if s.severity in [SecretSeverity.HIGH, SecretSeverity.CRITICAL]]
            
            if high_risk_secrets:
                filter_results.append({
                    "filter_type": "secret_scanner",
                    "action": "block",
                    "reason": f"High-risk secrets detected: {len(high_risk_secrets)} secrets",
                    "details": {
                        "total_secrets": secret_scan_result.total_secrets,
                        "high_risk_secrets": secret_scan_result.high_risk_secrets,
                        "secret_types": [s.secret_type.value for s in high_risk_secrets],
                        "scanner_status": secret_scan_result.scanner_status,
                        "processing_time": secret_scan_result.processing_time
                    }
                })
            else:
                # 중위험 시크릿이 발견된 경우 (경고)
                filter_results.append({
                    "filter_type": "secret_scanner",
                    "action": "warn",
                    "reason": f"Secrets detected: {secret_scan_result.total_secrets} secrets",
                    "details": {
                        "total_secrets": secret_scan_result.total_secrets,
                        "high_risk_secrets": secret_scan_result.high_risk_secrets,
                        "secret_types": [s.secret_type.value for s in secret_scan_result.secrets],
                        "scanner_status": secret_scan_result.scanner_status,
                        "processing_time": secret_scan_result.processing_time
                    }
                })
        
        # 2단계: OPA 정책 엔진 평가
        policy_engine = await get_policy_engine()
        
        # 요청 컨텍스트 생성
        context = RequestContext(
            tenant_id=tenant_id,
            user_id=user_id or "anonymous",
            session_id=session_id or "unknown",
            request_id=f"req_{int(time.time())}",
            timestamp=datetime.now(),
            client_ip=ip_address or "unknown",
            user_agent=user_agent or "unknown",
            user_roles=user_roles or [],
            user_permissions=user_permissions or []
        )
        
        # 정책 평가 실행
        policy_result = await policy_engine.evaluate(context, prompt, filter_results)
        
        # 3단계: 최종 결과 결정
        if policy_result.action == PolicyAction.DENY:
            result = {
                "is_blocked": True,
                "reason": policy_result.reason,
                "detection_method": "policy_engine",
                "risk_score": 1.0,
                "policy_violations": policy_result.violations,
                "metadata": policy_result.metadata
            }
        elif policy_result.action == PolicyAction.MASK:
            result = {
                "is_blocked": False,
                "reason": policy_result.reason,
                "detection_method": "policy_engine",
                "risk_score": 0.5,
                "policy_violations": policy_result.violations,
                "metadata": policy_result.metadata,
                "requires_masking": True
            }
        elif policy_result.action == PolicyAction.ALERT:
            result = {
                "is_blocked": False,
                "reason": policy_result.reason,
                "detection_method": "policy_engine",
                "risk_score": 0.3,
                "policy_violations": policy_result.violations,
                "metadata": policy_result.metadata,
                "requires_alert": True
            }
        else:  # ALLOW
            result = {
                "is_blocked": False,
                "reason": policy_result.reason,
                "detection_method": "policy_engine",
                "risk_score": 0.0,
                "metadata": policy_result.metadata
            }
        
        # 마스킹된 프롬프트 생성
        masked_prompt = mask_prompt(prompt)
        result["masked_prompt"] = masked_prompt
        
        # 처리 시간 계산
        processing_time = time.time() - start_time
        result["processing_time"] = processing_time
        result["policy_processing_time"] = policy_result.processing_time
        
        # 필터 결과 추가
        result["filter_results"] = filter_results
        
        # Elasticsearch 로그 저장
        log_data = {
            "prompt": prompt,
            "masked_prompt": masked_prompt,
            "user_id": user_id,
            "session_id": session_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "tenant_id": tenant_id,
            "is_blocked": result["is_blocked"],
            "reason": result["reason"],
            "detection_method": result["detection_method"],
            "risk_score": result["risk_score"],
            "processing_time": processing_time,
            "policy_violations": policy_result.violations,
            "timestamp": datetime.now().isoformat()
        }
        
        await log_to_elasticsearch(log_data)
        
        return result
        
    except Exception as e:
        logger.error(f"프롬프트 평가 실패: {e}")
        return {
            "is_blocked": True,
            "reason": f"Evaluation failed: {str(e)}",
            "detection_method": "error",
            "risk_score": 1.0,
            "processing_time": time.time() - start_time,
            "masked_prompt": prompt
        }


async def evaluate_prompt(prompt: str, user_id: int = None, session_id: str = None, ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
    """
    기존 프롬프트 평가 및 필터링 (하위 호환성 유지) - 실제 필터링 로직 복원
    
    Args:
        prompt: 평가할 프롬프트
        user_id: 사용자 ID (선택사항)
        session_id: 세션 ID (선택사항)
        ip_address: IP 주소 (선택사항)
        user_agent: User Agent (선택사항)
    
    Returns:
        Dict: 평가 결과
    """
    start_time = time.time()
    
    try:
        # 1. 기본 키워드 필터링
        blocked_keywords = get_block_keywords()
        if any(keyword in prompt.lower() for keyword in blocked_keywords):
            return {
                "is_blocked": True,
                "reason": "차단된 키워드가 포함되어 있습니다",
                "detection_method": "keyword_filter",
                "risk_score": 1.0,
                "masked_prompt": mask_prompt(prompt),
                "processing_time": time.time() - start_time
            }
        
        # 2. Rebuff SDK를 통한 프롬프트 인젝션 탐지
        try:
            from app.rebuff_sdk_client import get_rebuff_client
            rebuff_client = await get_rebuff_client()
            rebuff_result = await rebuff_client.detect_injection(prompt)
            
            if rebuff_result.is_injection:
                return {
                    "is_blocked": True,
                    "reason": f"프롬프트 인젝션 탐지: {rebuff_result.reason}",
                    "detection_method": "rebuff_sdk",
                    "risk_score": rebuff_result.heuristic_score,
                    "masked_prompt": mask_prompt(prompt),
                    "processing_time": time.time() - start_time
                }
        except Exception as e:
            logger.warning(f"Rebuff SDK 탐지 실패: {e}")
        
        # 3. 벡터 유사도 검사
        try:
            from app.embedding_filter import get_embedding_filter
            embedding_filter = await get_embedding_filter()
            similarity_result = await embedding_filter.check_similarity(prompt)
            
            if similarity_result["is_similar"]:
                return {
                    "is_blocked": True,
                    "reason": f"유사한 차단된 프롬프트 탐지: {similarity_result['reason']}",
                    "detection_method": "embedding_filter",
                    "risk_score": similarity_result["similarity_score"],
                    "masked_prompt": mask_prompt(prompt),
                    "processing_time": time.time() - start_time
                }
        except Exception as e:
            logger.warning(f"벡터 유사도 검사 실패: {e}")
        
        # 4. ML 분류기 검사
        try:
            from app.ml_classifier import get_ml_classifier
            ml_classifier = await get_ml_classifier()
            classification_result = await ml_classifier.classify_prompt(prompt)
            
            if classification_result["is_malicious"]:
                return {
                    "is_blocked": True,
                    "reason": f"악성 프롬프트로 분류됨: {classification_result['reason']}",
                    "detection_method": "ml_classifier",
                    "risk_score": classification_result["confidence"],
                    "masked_prompt": mask_prompt(prompt),
                    "processing_time": time.time() - start_time
                }
        except Exception as e:
            logger.warning(f"ML 분류기 검사 실패: {e}")
        
        # 5. 모든 검사를 통과한 경우
        return {
            "is_blocked": False,
            "reason": "프롬프트가 안전합니다",
            "detection_method": "multi_layer",
            "risk_score": 0.0,
            "masked_prompt": prompt,
            "processing_time": time.time() - start_time
        }
        
    except Exception as e:
        logger.error(f"프롬프트 평가 중 오류 발생: {e}")
        return {
            "is_blocked": False,
            "reason": "평가 중 오류가 발생했습니다",
            "detection_method": "error",
            "risk_score": 0.0,
            "masked_prompt": prompt,
            "processing_time": time.time() - start_time,
            "error": str(e)
        }
