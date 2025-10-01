"""
PII Detection Service 클라이언트
기존 PromptGate 서비스에서 Presidio PII Detection Service와 통신
"""

import httpx
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class PIIDetectionClient:
    """PII Detection Service 클라이언트"""
    
    def __init__(self, base_url: str = "http://pii-detector:8082"):
        self.base_url = base_url
        self.client = None
    
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        if self.client:
            await self.client.aclose()
    
    async def health_check(self) -> Dict[str, Any]:
        """PII Detection Service 헬스체크"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"PII Detection Service 헬스체크 실패: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    async def detect_pii(self, text: str, context: str = "", language: str = "ko") -> Dict[str, Any]:
        """PII 탐지 요청"""
        try:
            payload = {
                "text": text,
                "context": context,
                "language": language
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/detect",
                    json=payload
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.TimeoutException:
            logger.error("PII 탐지 요청 타임아웃")
            return {
                "has_pii": False,
                "total_pii": 0,
                "high_confidence_pii": 0,
                "risk_score": 0.0,
                "processing_time": 0.0,
                "pii_matches": [],
                "scanner_status": {"presidio": False, "spacy": False},
                "error_messages": ["PII 탐지 서비스 타임아웃"]
            }
        except Exception as e:
            logger.error(f"PII 탐지 요청 실패: {e}")
            return {
                "has_pii": False,
                "total_pii": 0,
                "high_confidence_pii": 0,
                "risk_score": 0.0,
                "processing_time": 0.0,
                "pii_matches": [],
                "scanner_status": {"presidio": False, "spacy": False},
                "error_messages": [f"PII 탐지 서비스 오류: {e}"]
            }
    
    async def anonymize_pii(self, text: str, pii_matches: List[Dict[str, Any]], anonymization_method: str = "mask") -> Dict[str, Any]:
        """PII 익명화 요청"""
        try:
            payload = {
                "text": text,
                "pii_matches": pii_matches,
                "anonymization_method": anonymization_method
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/anonymize",
                    json=payload
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.TimeoutException:
            logger.error("PII 익명화 요청 타임아웃")
            return {
                "original_text": text,
                "anonymized_text": text,
                "anonymization_method": anonymization_method,
                "processing_time": 0.0,
                "anonymized_count": 0
            }
        except Exception as e:
            logger.error(f"PII 익명화 요청 실패: {e}")
            return {
                "original_text": text,
                "anonymized_text": text,
                "anonymization_method": anonymization_method,
                "processing_time": 0.0,
                "anonymized_count": 0
            }
    
    async def detect_and_anonymize(self, text: str, context: str = "", language: str = "ko") -> Dict[str, Any]:
        """PII 탐지 및 익명화 통합 요청"""
        try:
            payload = {
                "text": text,
                "context": context,
                "language": language
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/detect-and-anonymize",
                    json=payload
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.TimeoutException:
            logger.error("PII 탐지 및 익명화 요청 타임아웃")
            return {
                "detection": {
                    "has_pii": False,
                    "total_pii": 0,
                    "high_confidence_pii": 0,
                    "risk_score": 0.0,
                    "pii_matches": []
                },
                "anonymization": {
                    "original_text": text,
                    "anonymized_text": text,
                    "anonymization_method": "mask",
                    "anonymized_count": 0
                },
                "processing_time": 0.0,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"PII 탐지 및 익명화 요청 실패: {e}")
            return {
                "detection": {
                    "has_pii": False,
                    "total_pii": 0,
                    "high_confidence_pii": 0,
                    "risk_score": 0.0,
                    "pii_matches": []
                },
                "anonymization": {
                    "original_text": text,
                    "anonymized_text": text,
                    "anonymization_method": "mask",
                    "anonymized_count": 0
                },
                "processing_time": 0.0,
                "timestamp": datetime.now().isoformat()
            }

# 전역 클라이언트 인스턴스
_pii_client: Optional[PIIDetectionClient] = None

async def get_pii_client() -> PIIDetectionClient:
    """PII Detection 클라이언트 인스턴스 반환"""
    global _pii_client
    
    if _pii_client is None:
        _pii_client = PIIDetectionClient()
    
    return _pii_client

async def close_pii_client():
    """PII Detection 클라이언트 리소스 정리"""
    global _pii_client
    
    if _pii_client and _pii_client.client:
        await _pii_client.client.aclose()
        _pii_client = None
