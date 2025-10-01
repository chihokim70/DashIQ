"""
Presidio PII Detection Service 모델 정의
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime

class PIIType(str, Enum):
    """PII 타입 정의"""
    NAME = "name"
    EMAIL = "email"
    PHONE = "phone"
    ADDRESS = "address"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    BANK_ACCOUNT = "bank_account"
    PASSPORT = "passport"
    DRIVER_LICENSE = "driver_license"
    IP_ADDRESS = "ip_address"
    MAC_ADDRESS = "mac_address"
    DATE_OF_BIRTH = "date_of_birth"
    GENDER = "gender"
    NATIONALITY = "nationality"
    BUSINESS_NUMBER = "business_number"  # 사업자등록번호
    UNKNOWN = "unknown"

class PIIConfidence(str, Enum):
    """PII 신뢰도 정의"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PIIMatch(BaseModel):
    """PII 매치 정보"""
    pii_type: PIIType
    confidence: PIIConfidence
    pattern: str
    matched_text: str
    start_pos: int
    end_pos: int
    context: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PIIRequest(BaseModel):
    """PII 탐지 요청"""
    text: str = Field(..., description="탐지할 텍스트")
    context: Optional[str] = Field(None, description="텍스트 컨텍스트")
    language: Optional[str] = Field("ko", description="언어 코드")

class PIIResponse(BaseModel):
    """PII 탐지 응답"""
    has_pii: bool
    total_pii: int
    high_confidence_pii: int
    risk_score: float
    processing_time: float
    pii_matches: List[PIIMatch]
    scanner_status: Dict[str, bool]
    error_messages: List[str] = Field(default_factory=list)

class AnonymizeRequest(BaseModel):
    """PII 익명화 요청"""
    text: str = Field(..., description="익명화할 텍스트")
    pii_matches: List[PIIMatch] = Field(..., description="익명화할 PII 매치 목록")
    anonymization_method: Optional[str] = Field("mask", description="익명화 방법")

class AnonymizeResponse(BaseModel):
    """PII 익명화 응답"""
    original_text: str
    anonymized_text: str
    anonymization_method: str
    processing_time: float
    anonymized_count: int

class ServiceStatus(BaseModel):
    """서비스 상태"""
    service: str
    version: str
    status: str
    timestamp: datetime
    pii_detector_status: Dict[str, Any]
