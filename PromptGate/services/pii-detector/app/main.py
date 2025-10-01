"""
Presidio PII Detection Service
마이크로서비스로 분리된 PII 탐지 및 익명화 서비스
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import asyncio
from datetime import datetime

from app.pii_detector import PresidioPIIDetector
from app.models import PIIRequest, PIIResponse, AnonymizeRequest, AnonymizeResponse

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="Presidio PII Detection Service",
    description="Microsoft Presidio 기반 PII 탐지 및 익명화 마이크로서비스",
    version="1.0.0"
)

# 전역 PII 탐지기 인스턴스
pii_detector: Optional[PresidioPIIDetector] = None

@app.on_event("startup")
async def startup_event():
    """서비스 시작 시 PII 탐지기 초기화"""
    global pii_detector
    
    try:
        logger.info("Presidio PII Detection Service 시작 중...")
        pii_detector = PresidioPIIDetector()
        
        # DB 패턴 로드 시도
        await pii_detector.load_patterns_from_db()
        
        # toml 패턴 로드 시도
        await pii_detector.load_patterns_from_toml()
        
        # 초기화 상태 확인
        status = pii_detector.get_scanner_status()
        logger.info(f"PII 탐지기 초기화 완료: {status}")
        
    except Exception as e:
        logger.error(f"PII 탐지기 초기화 실패: {e}")
        raise HTTPException(status_code=500, detail=f"서비스 초기화 실패: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """서비스 종료 시 리소스 정리"""
    global pii_detector
    
    if pii_detector:
        logger.info("PII 탐지기 리소스 정리 완료")

@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    if pii_detector is None:
        raise HTTPException(status_code=503, detail="서비스 초기화 중")
    
    status = pii_detector.get_scanner_status()
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "pii_detector_status": status
    }

@app.get("/status")
async def get_status():
    """서비스 상태 조회"""
    if pii_detector is None:
        raise HTTPException(status_code=503, detail="서비스 초기화 중")
    
    return {
        "service": "Presidio PII Detection Service",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "pii_detector_status": pii_detector.get_scanner_status()
    }

@app.post("/detect", response_model=PIIResponse)
async def detect_pii(request: PIIRequest):
    """PII 탐지 API"""
    if pii_detector is None:
        raise HTTPException(status_code=503, detail="서비스 초기화 중")
    
    try:
        logger.info(f"PII 탐지 요청: {len(request.text)}자 텍스트")
        
        # PII 탐지 실행
        result = await pii_detector.scan_text(
            text=request.text,
            context=request.context or ""
        )
        
        logger.info(f"PII 탐지 완료: {result.total_pii}개 탐지")
        
        return PIIResponse(
            has_pii=result.has_pii,
            total_pii=result.total_pii,
            high_confidence_pii=result.high_confidence_pii,
            risk_score=result.risk_score,
            processing_time=result.processing_time,
            pii_matches=result.pii_matches,
            scanner_status=result.scanner_status,
            error_messages=result.error_messages
        )
        
    except Exception as e:
        logger.error(f"PII 탐지 실패: {e}")
        raise HTTPException(status_code=500, detail=f"PII 탐지 실패: {e}")

@app.post("/anonymize", response_model=AnonymizeResponse)
async def anonymize_pii(request: AnonymizeRequest):
    """PII 익명화 API"""
    if pii_detector is None:
        raise HTTPException(status_code=503, detail="서비스 초기화 중")
    
    try:
        logger.info(f"PII 익명화 요청: {len(request.text)}자 텍스트")
        
        # PII 익명화 실행
        anonymized_text = pii_detector.anonymize_text(
            text=request.text,
            matches=request.pii_matches
        )
        
        logger.info(f"PII 익명화 완료: {anonymized_text[:50]}...")
        
        return AnonymizeResponse(
            original_text=request.text,
            anonymized_text=anonymized_text,
            anonymization_method="mask",
            processing_time=0.0,
            anonymized_count=len(request.pii_matches)
        )
        
    except Exception as e:
        logger.error(f"PII 익명화 실패: {e}")
        raise HTTPException(status_code=500, detail=f"PII 익명화 실패: {e}")

@app.post("/detect-and-anonymize")
async def detect_and_anonymize(request: PIIRequest):
    """PII 탐지 및 익명화 통합 API"""
    if pii_detector is None:
        raise HTTPException(status_code=503, detail="서비스 초기화 중")
    
    try:
        logger.info(f"PII 탐지 및 익명화 요청: {len(request.text)}자 텍스트")
        
        # PII 탐지
        detection_result = await pii_detector.scan_text(
            text=request.text,
            context=request.context or ""
        )
        
        # PII 익명화
        anonymized_text = pii_detector.anonymize_text(
            text=request.text,
            matches=detection_result.pii_matches
        )
        
        logger.info(f"PII 탐지 및 익명화 완료: {detection_result.total_pii}개 탐지, 익명화 완료")
        
        return {
            "detection": {
                "has_pii": detection_result.has_pii,
                "total_pii": detection_result.total_pii,
                "high_confidence_pii": detection_result.high_confidence_pii,
                "risk_score": detection_result.risk_score,
                "pii_matches": detection_result.pii_matches
            },
            "anonymization": {
                "original_text": request.text,
                "anonymized_text": anonymized_text,
                "anonymization_method": "mask",
                "anonymized_count": len(detection_result.pii_matches)
            },
            "processing_time": detection_result.processing_time,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"PII 탐지 및 익명화 실패: {e}")
        raise HTTPException(status_code=500, detail=f"PII 탐지 및 익명화 실패: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)
