"""
Presidio PII Detection Service 핵심 로직
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

# Presidio imports
try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_anonymizer import AnonymizerEngine
    from presidio_analyzer.entities import RecognizerResult
    PRESIDIO_AVAILABLE = True
except ImportError:
    PRESIDIO_AVAILABLE = False

# spaCy imports
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

from .models import PIIMatch, PIIType, PIIConfidence

logger = logging.getLogger(__name__)

class PresidioPIIDetector:
    """Presidio 기반 PII 탐지기"""
    
    def __init__(self):
        self.analyzer = None
        self.anonymizer = None
        self.nlp = None
        self.status = {
            "presidio": False,
            "spacy": False,
            "initialized": False
        }
    
    async def initialize(self):
        """PII 탐지기 초기화"""
        try:
            logger.info("Presidio PII 탐지기 초기화 시작")
            
            # Presidio 초기화
            if PRESIDIO_AVAILABLE:
                try:
                    self.analyzer = AnalyzerEngine()
                    self.anonymizer = AnonymizerEngine()
                    self.status["presidio"] = True
                    logger.info("Presidio 초기화 성공")
                except Exception as e:
                    logger.warning(f"Presidio 초기화 실패: {e}")
                    self.status["presidio"] = False
            
            # spaCy 초기화
            if SPACY_AVAILABLE:
                try:
                    # 한국어 모델 시도
                    try:
                        self.nlp = spacy.load("ko_core_news_sm")
                    except OSError:
                        # 영어 모델 fallback
                        self.nlp = spacy.load("en_core_web_sm")
                    
                    self.status["spacy"] = True
                    logger.info("spaCy 초기화 성공")
                except Exception as e:
                    logger.warning(f"spaCy 초기화 실패: {e}")
                    self.status["spacy"] = False
            
            self.status["initialized"] = True
            logger.info(f"PII 탐지기 초기화 완료: {self.status}")
            
        except Exception as e:
            logger.error(f"PII 탐지기 초기화 실패: {e}")
            raise
    
    async def detect_pii(self, text: str, context: str = "", language: str = "ko") -> Dict[str, Any]:
        """PII 탐지 실행"""
        start_time = time.time()
        pii_matches = []
        error_messages = []
        
        try:
            # Presidio 탐지
            if self.analyzer:
                presidio_matches = await self._detect_with_presidio(text, context)
                pii_matches.extend(presidio_matches)
            
            # spaCy 탐지
            if self.nlp:
                spacy_matches = await self._detect_with_spacy(text, context)
                pii_matches.extend(spacy_matches)
            
            # 정규식 탐지 (fallback)
            regex_matches = await self._detect_with_regex(text, context)
            pii_matches.extend(regex_matches)
            
            # 중복 제거 및 정렬
            pii_matches = self._deduplicate_matches(pii_matches)
            pii_matches.sort(key=lambda x: (x.confidence.value, x.pii_type.value), reverse=True)
            
            # 결과 집계
            total_pii = len(pii_matches)
            high_confidence_pii = sum(1 for p in pii_matches if p.confidence in [PIIConfidence.HIGH, PIIConfidence.CRITICAL])
            risk_score = self._calculate_risk_score(pii_matches)
            
            processing_time = time.time() - start_time
            
            return {
                "has_pii": total_pii > 0,
                "total_pii": total_pii,
                "high_confidence_pii": high_confidence_pii,
                "risk_score": risk_score,
                "processing_time": processing_time,
                "pii_matches": pii_matches,
                "scanner_status": self.status.copy(),
                "error_messages": error_messages
            }
            
        except Exception as e:
            logger.error(f"PII 탐지 실패: {e}")
            error_messages.append(f"PII 탐지 실패: {e}")
            return {
                "has_pii": False,
                "total_pii": 0,
                "high_confidence_pii": 0,
                "risk_score": 0.0,
                "processing_time": time.time() - start_time,
                "pii_matches": [],
                "scanner_status": self.status.copy(),
                "error_messages": error_messages
            }
    
    async def anonymize_pii(self, text: str, pii_matches: List[PIIMatch], anonymization_method: str = "mask") -> Dict[str, Any]:
        """PII 익명화 실행"""
        start_time = time.time()
        
        try:
            if not pii_matches:
                return {
                    "original_text": text,
                    "anonymized_text": text,
                    "anonymization_method": anonymization_method,
                    "processing_time": time.time() - start_time,
                    "anonymized_count": 0
                }
            
            # Presidio 익명화 시도
            if self.anonymizer and anonymization_method == "presidio":
                anonymized_text = await self._anonymize_with_presidio(text, pii_matches)
            else:
                # 기본 마스킹
                anonymized_text = await self._anonymize_with_masking(text, pii_matches)
            
            processing_time = time.time() - start_time
            
            return {
                "original_text": text,
                "anonymized_text": anonymized_text,
                "anonymization_method": anonymization_method,
                "processing_time": processing_time,
                "anonymized_count": len(pii_matches)
            }
            
        except Exception as e:
            logger.error(f"PII 익명화 실패: {e}")
            return {
                "original_text": text,
                "anonymized_text": text,
                "anonymization_method": anonymization_method,
                "processing_time": time.time() - start_time,
                "anonymized_count": 0
            }
    
    async def _detect_with_presidio(self, text: str, context: str) -> List[PIIMatch]:
        """Presidio를 사용한 PII 탐지"""
        matches = []
        
        if not self.analyzer:
            return matches
        
        try:
            results = self.analyzer.analyze(text=text, language='ko')
            
            for result in results:
                pii_type = self._map_presidio_entity_to_pii_type(result.entity_type)
                confidence = self._map_presidio_score_to_confidence(result.score)
                
                match = PIIMatch(
                    pii_type=pii_type,
                    confidence=confidence,
                    pattern=f"presidio_{result.entity_type}",
                    matched_text=text[result.start:result.end],
                    start_pos=result.start,
                    end_pos=result.end,
                    context=context,
                    metadata={
                        "scanner": "presidio",
                        "entity_type": result.entity_type,
                        "score": result.score
                    }
                )
                matches.append(match)
            
            logger.debug(f"Presidio 탐지 완료: {len(matches)}개")
            
        except Exception as e:
            logger.warning(f"Presidio 탐지 실패: {e}")
        
        return matches
    
    async def _detect_with_spacy(self, text: str, context: str) -> List[PIIMatch]:
        """spaCy를 사용한 PII 탐지"""
        matches = []
        
        if not self.nlp:
            return matches
        
        try:
            doc = self.nlp(text)
            
            for ent in doc.ents:
                pii_type = self._map_spacy_entity_to_pii_type(ent.label_)
                confidence = PIIConfidence.MEDIUM
                
                match = PIIMatch(
                    pii_type=pii_type,
                    confidence=confidence,
                    pattern=f"spacy_{ent.label_}",
                    matched_text=ent.text,
                    start_pos=ent.start_char,
                    end_pos=ent.end_char,
                    context=context,
                    metadata={
                        "scanner": "spacy",
                        "entity_label": ent.label_,
                        "confidence": ent._.prob if hasattr(ent._, 'prob') else 0.8
                    }
                )
                matches.append(match)
            
            logger.debug(f"spaCy 탐지 완료: {len(matches)}개")
            
        except Exception as e:
            logger.warning(f"spaCy 탐지 실패: {e}")
        
        return matches
    
    async def _detect_with_regex(self, text: str, context: str) -> List[PIIMatch]:
        """정규식을 사용한 PII 탐지 (fallback)"""
        import re
        
        matches = []
        
        # 기본 한국어 PII 패턴
        patterns = {
            PIIType.SSN: [
                (r'\b\d{6}-[1-4]\d{6}\b', PIIConfidence.HIGH),
                (r'\b\d{6}[1-4]\d{6}\b', PIIConfidence.HIGH)
            ],
            PIIType.PHONE: [
                (r'\b01[016789]-?\d{3,4}-?\d{4}\b', PIIConfidence.HIGH),
                (r'\b0\d{1,2}-?\d{3,4}-?\d{4}\b', PIIConfidence.MEDIUM)
            ],
            PIIType.EMAIL: [
                (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', PIIConfidence.HIGH)
            ],
            PIIType.CREDIT_CARD: [
                (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', PIIConfidence.HIGH)
            ]
        }
        
        for pii_type, type_patterns in patterns.items():
            for pattern, confidence in type_patterns:
                try:
                    for match in re.finditer(pattern, text, re.IGNORECASE):
                        pii_match = PIIMatch(
                            pii_type=pii_type,
                            confidence=confidence,
                            pattern=pattern,
                            matched_text=match.group(),
                            start_pos=match.start(),
                            end_pos=match.end(),
                            context=context,
                            metadata={
                                "scanner": "regex",
                                "pattern": pattern
                            }
                        )
                        matches.append(pii_match)
                except Exception as e:
                    logger.warning(f"정규식 패턴 실패 ({pattern}): {e}")
        
        logger.debug(f"정규식 탐지 완료: {len(matches)}개")
        return matches
    
    async def _anonymize_with_presidio(self, text: str, pii_matches: List[PIIMatch]) -> str:
        """Presidio를 사용한 익명화"""
        if not self.anonymizer:
            return text
        
        try:
            # PIIMatch를 Presidio RecognizerResult로 변환
            presidio_results = []
            for match in pii_matches:
                if match.metadata.get("scanner") == "presidio":
                    result = RecognizerResult(
                        entity_type=match.metadata.get("entity_type", "UNKNOWN"),
                        start=match.start_pos,
                        end=match.end_pos,
                        score=match.metadata.get("score", 0.8)
                    )
                    presidio_results.append(result)
            
            if not presidio_results:
                return text
            
            # Presidio 익명화
            anonymized_result = self.anonymizer.anonymize(
                text=text,
                analyzer_results=presidio_results
            )
            
            return anonymized_result.text
            
        except Exception as e:
            logger.warning(f"Presidio 익명화 실패: {e}")
            return text
    
    async def _anonymize_with_masking(self, text: str, pii_matches: List[PIIMatch]) -> str:
        """기본 마스킹을 사용한 익명화"""
        anonymized_text = text
        
        # 위치 기준으로 역순 정렬 (뒤에서부터 마스킹)
        sorted_matches = sorted(pii_matches, key=lambda x: x.start_pos, reverse=True)
        
        for match in sorted_matches:
            mask_char = self._get_mask_character(match.pii_type)
            mask_length = len(match.matched_text)
            mask_text = mask_char * mask_length
            
            anonymized_text = (
                anonymized_text[:match.start_pos] + 
                mask_text + 
                anonymized_text[match.end_pos:]
            )
        
        return anonymized_text
    
    def _map_presidio_entity_to_pii_type(self, entity_type: str) -> PIIType:
        """Presidio 엔티티 타입을 PIIType으로 매핑"""
        mapping = {
            'PERSON': PIIType.NAME,
            'EMAIL_ADDRESS': PIIType.EMAIL,
            'PHONE_NUMBER': PIIType.PHONE,
            'LOCATION': PIIType.ADDRESS,
            'CREDIT_CARD': PIIType.CREDIT_CARD,
            'IP_ADDRESS': PIIType.IP_ADDRESS,
            'DATE_TIME': PIIType.DATE_OF_BIRTH,
            'SSN': PIIType.SSN
        }
        return mapping.get(entity_type, PIIType.UNKNOWN)
    
    def _map_spacy_entity_to_pii_type(self, entity_label: str) -> PIIType:
        """spaCy 엔티티 라벨을 PIIType으로 매핑"""
        mapping = {
            'PERSON': PIIType.NAME,
            'GPE': PIIType.ADDRESS,
            'LOC': PIIType.ADDRESS,
            'DATE': PIIType.DATE_OF_BIRTH
        }
        return mapping.get(entity_label, PIIType.UNKNOWN)
    
    def _map_presidio_score_to_confidence(self, score: float) -> PIIConfidence:
        """Presidio 점수를 PIIConfidence로 매핑"""
        if score >= 0.9:
            return PIIConfidence.CRITICAL
        elif score >= 0.8:
            return PIIConfidence.HIGH
        elif score >= 0.6:
            return PIIConfidence.MEDIUM
        else:
            return PIIConfidence.LOW
    
    def _get_mask_character(self, pii_type: PIIType) -> str:
        """PII 타입별 마스킹 문자 반환"""
        return '*'
    
    def _deduplicate_matches(self, matches: List[PIIMatch]) -> List[PIIMatch]:
        """중복 PII 매치 제거"""
        seen = set()
        unique_matches = []
        
        for match in matches:
            key = (match.start_pos, match.end_pos, match.pii_type)
            if key not in seen:
                seen.add(key)
                unique_matches.append(match)
        
        return unique_matches
    
    def _calculate_risk_score(self, matches: List[PIIMatch]) -> float:
        """위험 점수 계산"""
        if not matches:
            return 0.0
        
        total_score = 0.0
        for match in matches:
            if match.confidence == PIIConfidence.CRITICAL:
                total_score += 1.0
            elif match.confidence == PIIConfidence.HIGH:
                total_score += 0.8
            elif match.confidence == PIIConfidence.MEDIUM:
                total_score += 0.5
            else:
                total_score += 0.2
        
        return min(total_score / len(matches), 1.0)
    
    def get_status(self) -> Dict[str, Any]:
        """탐지기 상태 반환"""
        return self.status.copy()
    
    async def cleanup(self):
        """리소스 정리"""
        self.analyzer = None
        self.anonymizer = None
        self.nlp = None
        self.status["initialized"] = False
        logger.info("PII 탐지기 리소스 정리 완료")
