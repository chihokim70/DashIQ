"""
Rebuff SDK 클라이언트 구현
공식 Rebuff SDK를 사용한 프롬프트 인젝션 탐지
"""

import os
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class DetectionMethod(Enum):
    """탐지 방법"""
    HEURISTIC = "heuristic"
    VECTOR = "vector"
    LLM = "llm"
    HYBRID = "hybrid"

@dataclass
class RebuffResult:
    """Rebuff 탐지 결과"""
    is_injection: bool
    confidence: float
    method: DetectionMethod
    reasons: List[str]
    tactics: List[str]
    canary_word: Optional[str] = None
    processing_time: float = 0.0

class RebuffSDKClient:
    """Rebuff SDK 클라이언트"""
    
    def __init__(self, 
                 openai_api_key: str,
                 pinecone_api_key: Optional[str] = None,
                 pinecone_index: Optional[str] = None,
                 openai_model: str = "gpt-3.5-turbo"):
        """
        Rebuff SDK 클라이언트 초기화
        
        Args:
            openai_api_key: OpenAI API 키
            pinecone_api_key: Pinecone API 키 (선택사항)
            pinecone_index: Pinecone 인덱스명 (선택사항)
            openai_model: 사용할 OpenAI 모델
        """
        self.openai_api_key = openai_api_key
        self.pinecone_api_key = pinecone_api_key
        self.pinecone_index = pinecone_index
        self.openai_model = openai_model
        
        self.rebuff_client = None
        self.is_initialized = False
        
        # SDK 초기화 시도
        self._initialize_sdk()
    
    def _initialize_sdk(self):
        """Rebuff SDK 초기화"""
        try:
            from rebuff import RebuffSdk
            
            if self.pinecone_api_key and self.pinecone_index:
                # Pinecone을 사용한 완전한 SDK 초기화
                self.rebuff_client = RebuffSdk(
                    openai_apikey=self.openai_api_key,
                    pinecone_apikey=self.pinecone_api_key,
                    pinecone_index=self.pinecone_index,
                    openai_model=self.openai_model
                )
                logger.info("Rebuff SDK 초기화 성공 (Pinecone 포함)")
            else:
                # OpenAI만 사용한 기본 SDK 초기화
                self.rebuff_client = RebuffSdk(
                    openai_apikey=self.openai_api_key,
                    openai_model=self.openai_model
                )
                logger.info("Rebuff SDK 초기화 성공 (OpenAI만)")
            
            self.is_initialized = True
            
        except ImportError as e:
            logger.error(f"Rebuff SDK import 실패: {e}")
            self.is_initialized = False
        except Exception as e:
            logger.error(f"Rebuff SDK 초기화 실패: {e}")
            self.is_initialized = False
    
    async def detect_injection(self, 
                            prompt: str,
                            run_heuristic: bool = True,
                            run_vector: bool = True,
                            run_llm: bool = True,
                            max_heuristic_score: float = 0.75,
                            max_vector_score: float = 0.9,
                            max_model_score: float = 0.9) -> RebuffResult:
        """
        프롬프트 인젝션 탐지
        
        Args:
            prompt: 검사할 프롬프트
            run_heuristic: 휴리스틱 검사 실행 여부
            run_vector: 벡터 검사 실행 여부
            run_llm: LLM 검사 실행 여부
            max_heuristic_score: 휴리스틱 최대 점수
            max_vector_score: 벡터 최대 점수
            max_model_score: 모델 최대 점수
            
        Returns:
            RebuffResult: 탐지 결과
        """
        if not self.is_initialized or not self.rebuff_client:
            logger.warning("Rebuff SDK가 초기화되지 않음. Fallback 방식 사용")
            return self._fallback_detection(prompt)
        
        try:
            import time
            start_time = time.time()
            
            # Rebuff SDK를 사용한 탐지
            result = self.rebuff_client.detect_injection(prompt)
            
            processing_time = time.time() - start_time
            
            # 결과 파싱
            is_injection = result.injection_detected if hasattr(result, 'injection_detected') else False
            confidence = getattr(result, 'score', 0.0)
            
            # 탐지 방법 결정
            method = DetectionMethod.HYBRID
            if hasattr(result, 'method'):
                method = DetectionMethod(result.method)
            
            # 이유 및 전술 추출
            reasons = getattr(result, 'reasons', [])
            tactics = getattr(result, 'tactics', [])
            
            return RebuffResult(
                is_injection=is_injection,
                confidence=confidence,
                method=method,
                reasons=reasons if isinstance(reasons, list) else [str(reasons)],
                tactics=tactics if isinstance(tactics, list) else [str(tactics)],
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Rebuff SDK 탐지 실패: {e}")
            return self._fallback_detection(prompt)
    
    async def add_canary_word(self, prompt_template: str) -> tuple[str, str]:
        """
        프롬프트 템플릿에 카나리 워드 추가
        
        Args:
            prompt_template: 프롬프트 템플릿
            
        Returns:
            tuple: (카나리 워드가 추가된 프롬프트, 카나리 워드)
        """
        if not self.is_initialized or not self.rebuff_client:
            logger.warning("Rebuff SDK가 초기화되지 않음")
            return prompt_template, ""
        
        try:
            buffed_prompt, canary_word = self.rebuff_client.add_canary_word(prompt_template)
            return buffed_prompt, canary_word
            
        except Exception as e:
            logger.error(f"카나리 워드 추가 실패: {e}")
            return prompt_template, ""
    
    async def check_canary_leakage(self, 
                                 user_input: str,
                                 completion: str,
                                 canary_word: str) -> bool:
        """
        카나리 워드 유출 검사
        
        Args:
            user_input: 사용자 입력
            completion: AI 응답
            canary_word: 카나리 워드
            
        Returns:
            bool: 카나리 워드 유출 여부
        """
        if not self.is_initialized or not self.rebuff_client:
            logger.warning("Rebuff SDK가 초기화되지 않음")
            return False
        
        try:
            is_leaked = self.rebuff_client.is_canaryword_leaked(
                user_input, completion, canary_word
            )
            return is_leaked
            
        except Exception as e:
            logger.error(f"카나리 워드 유출 검사 실패: {e}")
            return False
    
    def _fallback_detection(self, prompt: str) -> RebuffResult:
        """
        Fallback 탐지 (SDK 실패 시)
        """
        import re
        import time
        
        start_time = time.time()
        
        # 기본적인 프롬프트 인젝션 패턴
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
            r"bypass.*security",
            r"jailbreak.*prompt",
            r"roleplay.*as",
            r"simulate.*scenario",
            r"override.*system",
            r"developer.*mode",
            r"admin.*access",
            r"root.*privileges",
            r"sudo.*command",
            r"execute.*code",
            r"run.*script"
        ]
        
        detected_patterns = []
        for pattern in injection_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                detected_patterns.append(pattern)
        
        is_injection = len(detected_patterns) > 0
        confidence = min(len(detected_patterns) * 0.3, 1.0)
        
        processing_time = time.time() - start_time
        
        return RebuffResult(
            is_injection=is_injection,
            confidence=confidence,
            method=DetectionMethod.HEURISTIC,
            reasons=detected_patterns,
            tactics=["heuristic"] if is_injection else [],
            processing_time=processing_time
        )
    
    def get_status(self) -> Dict[str, Any]:
        """SDK 상태 조회"""
        return {
            "is_initialized": self.is_initialized,
            "has_pinecone": bool(self.pinecone_api_key and self.pinecone_index),
            "openai_model": self.openai_model,
            "sdk_version": self._get_sdk_version()
        }
    
    def _get_sdk_version(self) -> str:
        """SDK 버전 조회"""
        try:
            import rebuff
            return getattr(rebuff, '__version__', 'unknown')
        except:
            return 'not_installed'

# 환경변수에서 설정 로드
def create_rebuff_client() -> RebuffSDKClient:
    """
    환경변수에서 설정을 로드하여 Rebuff 클라이언트 생성
    
    Returns:
        RebuffSDKClient: 생성된 클라이언트
    """
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    pinecone_api_key = os.getenv("PINECONE_API_KEY", "")
    pinecone_index = os.getenv("PINECONE_INDEX", "")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    if not openai_api_key:
        logger.warning("OPENAI_API_KEY가 설정되지 않음")
    
    return RebuffSDKClient(
        openai_api_key=openai_api_key,
        pinecone_api_key=pinecone_api_key,
        pinecone_index=pinecone_index,
        openai_model=openai_model
    )

# 전역 클라이언트 인스턴스
_rebuff_client: Optional[RebuffSDKClient] = None

def get_rebuff_client() -> RebuffSDKClient:
    """Rebuff 클라이언트 싱글톤 인스턴스 반환"""
    global _rebuff_client
    
    if _rebuff_client is None:
        _rebuff_client = create_rebuff_client()
    
    return _rebuff_client
