import re
import time
from typing import Dict, Any
from app.logger import get_logger, log_to_elasticsearch
from app.vector_store import check_similarity
from app.policy_client import get_block_keywords, get_mask_keywords
from app.rebuff_integration import rebuff_integration

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


def evaluate_prompt(prompt: str, user_id: int = None, session_id: str = None, ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
    """
    프롬프트 평가 및 필터링
    
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
        # ✅ 1단계: 차단 키워드 검사
        blocked_keywords = [k for k in get_block_keywords() if k in prompt]
        if blocked_keywords:
            result = {
                "is_blocked": True,
                "reason": "해당 컨텐츠는 사내 규정에 의해 차단 및 모니터링 되고 있습니다.",
                "blocked_keywords": blocked_keywords,
                "detection_method": "keyword",
                "risk_score": 1.0
            }
        else:
            # ✅ 2단계: Rebuff SDK 기반 프롬프트 인젝션 탐지
            import asyncio
            rebuff_result = asyncio.run(rebuff_integration.detect_prompt_injection(prompt))
            
            if rebuff_result["is_injection"]:
                result = {
                    "is_blocked": True,
                    "reason": f"프롬프트 인젝션 탐지: {', '.join(rebuff_result['reasons'])}",
                    "detection_method": rebuff_result["method"],
                    "risk_score": rebuff_result["score"],
                    "tactics": rebuff_result["tactics"]
                }
            else:
                # ✅ 3단계: 벡터 기반 유사도 검사
                if check_similarity(prompt):
                    result = {
                        "is_blocked": True,
                        "reason": "Similar to known dangerous prompt",
                        "detection_method": "vector",
                        "risk_score": 0.8
                    }
                else:
                    # ✅ 4단계: 허용된 경우
                    result = {
                        "is_blocked": False,
                        "reason": "Allowed",
                        "detection_method": "passed",
                        "risk_score": 0.0
                    }
        
        # ✅ 마스킹된 프롬프트 생성
        masked_prompt = mask_prompt(prompt)
        result["masked_prompt"] = masked_prompt
        
        # ✅ 처리 시간 계산
        processing_time = time.time() - start_time
        result["processing_time"] = processing_time
        
        # ✅ Elasticsearch 로그 저장
        log_data = {
            "user_id": user_id,
            "session_id": session_id,
            "original_prompt": prompt,
            "masked_prompt": masked_prompt,
            "is_blocked": result["is_blocked"],
            "block_reason": result.get("reason", ""),
            "risk_score": result.get("risk_score", 0.0),
            "detection_method": result.get("detection_method", ""),
            "processing_time": processing_time,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "timestamp": time.time()
        }
        
        log_to_elasticsearch("promptgate_logs", log_data)
        
        # ✅ 차단된 경우 벡터 DB에 추가
        if result["is_blocked"]:
            rebuff_integration.add_to_vector_db(prompt, is_injection=True)
        
        return result

    except Exception as e:
        logger.error(f"[PromptFilter] 검사 실패: {str(e)}")
        return {
            "is_blocked": False,
            "error": str(e),
            "processing_time": time.time() - start_time
        }
