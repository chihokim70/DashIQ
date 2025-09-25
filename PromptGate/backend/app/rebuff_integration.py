"""
Rebuff SDK 완전 연동 모듈
Prompt Injection 탐지를 위한 Rebuff SDK 통합
"""

import os
import re
from typing import Dict, List, Optional
from app.logger import get_logger
from app.config import get_settings
from app.rebuff_sdk_client import get_rebuff_client, RebuffResult, DetectionMethod

logger = get_logger("rebuff-integration")

class RebuffIntegration:
    def __init__(self):
        self.settings = get_settings()
        self.rebuff_client = get_rebuff_client()
        logger.info(f"Rebuff Integration 초기화 완료. 상태: {self.rebuff_client.get_status()}")
    
    async def detect_prompt_injection(self, prompt: str) -> Dict:
        """
        Rebuff SDK를 사용한 프롬프트 인젝션 탐지
        
        Returns:
            Dict: {
                "is_injection": bool,
                "score": float,
                "reasons": List[str],
                "tactics": List[str],
                "method": str
            }
        """
        try:
            # 새로운 Rebuff SDK 클라이언트 사용
            result = await self.rebuff_client.detect_injection(prompt)
            
            return {
                "is_injection": result.is_injection,
                "score": result.confidence,
                "reasons": result.reasons,
                "tactics": result.tactics,
                "method": result.method.value,
                "processing_time": result.processing_time
            }
            
        except Exception as e:
            logger.error(f"Rebuff SDK 탐지 실패: {str(e)}")
            return self._fallback_detection(prompt)
    
    def _fallback_detection(self, prompt: str) -> Dict:
        """
        Rebuff SDK 실패 시 기본 탐지 로직
        """
        # 기본적인 프롬프트 인젝션 패턴 탐지
        injection_patterns = [
            r"ignore.*previous.*instructions",
            r"forget.*everything.*before",
            r"ignore.*above.*instructions",
            r"disregard.*previous.*prompt",
            r"ignore.*all.*instructions",
            r"you.*are.*now.*different",
            r"pretend.*to.*be",
            r"act.*as.*if",
            r"ignore.*safety.*guidelines",
            r"bypass.*security"
        ]
        
        detected_patterns = []
        for pattern in injection_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                detected_patterns.append(pattern)
        
        is_injection = len(detected_patterns) > 0
        score = min(len(detected_patterns) * 0.3, 1.0)
        
        return {
            "is_injection": is_injection,
            "score": score,
            "reasons": detected_patterns,
            "tactics": ["heuristic"] if is_injection else [],
            "method": "fallback"
        }
    
    def add_to_vector_db(self, prompt: str, is_injection: bool = True) -> bool:
        """
        위험한 프롬프트를 벡터 DB에 추가
        """
        if not self.rebuff_client:
            logger.warning("Rebuff SDK가 초기화되지 않아 벡터 DB 추가를 건너뜁니다.")
            return False
        
        try:
            # Rebuff SDK를 통한 벡터 DB 추가
            result = self.rebuff_client.add_prompt_injection(
                prompt=prompt,
                injection_type="prompt_injection" if is_injection else "safe_prompt"
            )
            
            logger.info(f"벡터 DB에 프롬프트 추가 완료: {result}")
            return True
            
        except Exception as e:
            logger.error(f"벡터 DB 추가 실패: {str(e)}")
            return False
    
    def get_similar_prompts(self, prompt: str, limit: int = 5) -> List[Dict]:
        """
        유사한 프롬프트 검색
        """
        if not self.rebuff_client:
            return []
        
        try:
            # Rebuff SDK를 통한 유사 프롬프트 검색
            similar_prompts = self.rebuff_client.search_similar_prompts(
                prompt=prompt,
                limit=limit
            )
            
            return similar_prompts
            
        except Exception as e:
            logger.error(f"유사 프롬프트 검색 실패: {str(e)}")
            return []

# 전역 인스턴스
rebuff_integration = RebuffIntegration() 