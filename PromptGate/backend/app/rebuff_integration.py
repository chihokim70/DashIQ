"""
Rebuff SDK 완전 연동 모듈
Prompt Injection 탐지를 위한 Rebuff SDK 통합
"""

import os
import re
from typing import Dict, List, Optional
from app.logger import get_logger
from app.config import get_settings

logger = get_logger("rebuff-integration")

# Rebuff SDK import (로컬 SDK 사용)
try:
    from rebuff_sdk.sdk import Rebuff
    REBUFF_AVAILABLE = True
except ImportError:
    logger.warning("Rebuff SDK를 찾을 수 없습니다. 로컬 SDK를 사용합니다.")
    REBUFF_AVAILABLE = False

class RebuffIntegration:
    def __init__(self):
        self.settings = get_settings()
        self.rebuff_client = None
        self._initialize_rebuff()
    
    def _initialize_rebuff(self):
        """Rebuff 클라이언트 초기화"""
        try:
            if REBUFF_AVAILABLE:
                # Rebuff SDK 초기화
                self.rebuff_client = Rebuff(
                    provider="openai",           # 'openai', 'anthropic' 등
                    api_key=self.settings.rebuff_api_key,  # 환경변수에서 가져오기
                    vector_db="qdrant",          # Qdrant 사용
                    qdrant_host=self.settings.qdrant_host,
                    qdrant_port=self.settings.qdrant_port
                )
                logger.info("Rebuff SDK 초기화 성공")
            else:
                logger.warning("Rebuff SDK를 사용할 수 없습니다. 기본 필터링만 사용합니다.")
                
        except Exception as e:
            logger.error(f"Rebuff SDK 초기화 실패: {str(e)}")
            self.rebuff_client = None
    
    def detect_prompt_injection(self, prompt: str) -> Dict:
        """
        Rebuff SDK를 사용한 프롬프트 인젝션 탐지
        
        Returns:
            Dict: {
                "is_injection": bool,
                "score": float,
                "reasons": List[str],
                "tactics": List[str]
            }
        """
        if not self.rebuff_client:
            return self._fallback_detection(prompt)
        
        try:
            # Rebuff SDK를 사용한 탐지
            result = self.rebuff_client.detect_prompt_injection(
                prompt=prompt,
                run_heuristic_check=True,
                run_vector_check=True,
                run_language_model_check=True,
                max_heuristic_score=0.75,
                max_vector_score=0.9,
                max_model_score=0.9
            )
            
            return {
                "is_injection": result.get("is_prompt_injection", False),
                "score": result.get("score", 0.0),
                "reasons": result.get("reasons", []),
                "tactics": result.get("tactics", []),
                "method": "rebuff_sdk"
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