"""
PII (개인 식별 정보) 탐지기 구현 - 3단계 완성
spaCy 없이 정규식 + 검증기 + 컨텍스트 분석 + 한국어 처리로 한국형 PII 탐지
"""

import re
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time
import hashlib
from datetime import datetime
import os
import toml

# PII 탐지 라이브러리 import (Presidio 제거)
# try:
#     from presidio_analyzer import AnalyzerEngine
#     from presidio_anonymizer import AnonymizerEngine
#     from presidio_analyzer.entities import RecognizerResult
#     PRESIDIO_AVAILABLE = True
# except ImportError:
#     PRESIDIO_AVAILABLE = False

PRESIDIO_AVAILABLE = False  # 호환성 문제로 비활성화

try:
    import nltk
    from nltk import ne_chunk, pos_tag, word_tokenize
    from nltk.tree import Tree
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
except Exception as e:
    print(f"NLTK import 실패: {e}")
    NLTK_AVAILABLE = False

# 한국어 검증기, 컨텍스트 분석기, 한국어 처리기 import
from .korean_validator import KoreanPIIValidator
from .context_analyzer import ContextAnalyzer
from .korean_processor import LightweightKoreanProcessor
from .models import PIIMatch, PIIType, PIIConfidence

logger = logging.getLogger(__name__)

@dataclass
class PIIScanResult:
    """PII 스캔 결과"""
    has_pii: bool
    pii_matches: List[PIIMatch]
    total_pii: int
    high_confidence_pii: int
    risk_score: float
    processing_time: float
    scanner_status: Dict[str, bool]
    error_messages: List[str] = field(default_factory=list)

class KoreanPIIPatterns:
    """한국어 PII 정규식 패턴 모음 (기본 패턴)"""
    PATTERNS: Dict[PIIType, List[Tuple[str, PIIConfidence]]] = {
        PIIType.SSN: [
            # 주민등록번호 (13자리)
            (r"\b\d{6}-[1-4]\d{6}\b", PIIConfidence.HIGH),
            (r"\b\d{6}[1-4]\d{6}\b", PIIConfidence.HIGH),
            # 외국인등록번호
            (r"\b\d{6}-[5-8]\d{6}\b", PIIConfidence.HIGH),
            (r"\b\d{6}[5-8]\d{6}\b", PIIConfidence.HIGH),
        ],
        PIIType.PHONE: [
            # 한국 휴대폰 번호
            (r"\b01[016789]-?\d{3,4}-?\d{4}\b", PIIConfidence.HIGH),
            (r"\b01[016789]\d{7,8}\b", PIIConfidence.HIGH),
            # 한국 일반 전화번호
            (r"\b0\d{1,2}-?\d{3,4}-?\d{4}\b", PIIConfidence.MEDIUM),
            (r"\b0\d{9,10}\b", PIIConfidence.MEDIUM),
            # 국제 전화번호
            (r"\+\d{1,3}-?\d{1,4}-?\d{3,4}-?\d{4}\b", PIIConfidence.MEDIUM),
        ],
        PIIType.EMAIL: [
            # 이메일 주소
            (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", PIIConfidence.HIGH),
            # 한국 도메인 이메일
            (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(co\.kr|go\.kr|ac\.kr|or\.kr)\b", PIIConfidence.HIGH),
        ],
        PIIType.CREDIT_CARD: [
            # 신용카드 번호 (16자리)
            (r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", PIIConfidence.HIGH),
            # 체크카드 번호 (16자리)
            (r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", PIIConfidence.HIGH),
        ],
        PIIType.BANK_ACCOUNT: [
            # 한국 은행 계좌번호
            (r"\b\d{3}-\d{2}-\d{6}\b", PIIConfidence.HIGH),
            (r"\b\d{3}-\d{2}-\d{7}\b", PIIConfidence.HIGH),
            (r"\b\d{3}-\d{2}-\d{8}\b", PIIConfidence.HIGH),
            (r"\b\d{3}-\d{2}-\d{9}\b", PIIConfidence.HIGH),
            (r"\b\d{3}-\d{2}-\d{10}\b", PIIConfidence.HIGH),
            (r"\b\d{3}-\d{2}-\d{11}\b", PIIConfidence.HIGH),
            (r"\b\d{3}-\d{2}-\d{12}\b", PIIConfidence.HIGH),
            (r"\b\d{3}-\d{2}-\d{13}\b", PIIConfidence.HIGH),
            (r"\b\d{3}-\d{2}-\d{14}\b", PIIConfidence.HIGH),
            (r"\b\d{3}-\d{2}-\d{15}\b", PIIConfidence.HIGH),
        ],
        PIIType.IP_ADDRESS: [
            # IPv4 주소
            (r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", PIIConfidence.MEDIUM),
            # IPv6 주소
            (r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b", PIIConfidence.MEDIUM),
        ],
        PIIType.MAC_ADDRESS: [
            # MAC 주소
            (r"\b(?:[0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}\b", PIIConfidence.MEDIUM),
        ],
        PIIType.DATE_OF_BIRTH: [
            # 생년월일 (YYYY-MM-DD)
            (r"\b(19|20)\d{2}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])\b", PIIConfidence.MEDIUM),
            # 생년월일 (YYYY.MM.DD)
            (r"\b(19|20)\d{2}\.(0[1-9]|1[0-2])\.(0[1-9]|[12]\d|3[01])\b", PIIConfidence.MEDIUM),
            # 생년월일 (YYYY/MM/DD)
            (r"\b(19|20)\d{2}/(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])\b", PIIConfidence.MEDIUM),
        ],
        PIIType.ADDRESS: [
            # 한국 주소 패턴
            (r"\b(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)\s+[가-힣\s\d-]+", PIIConfidence.MEDIUM),
            # 우편번호
            (r"\b\d{5}\b", PIIConfidence.LOW),
        ],
        PIIType.NAME: [
            # 한국 이름 패턴 (2-4글자)
            (r"\b[가-힣]{2,4}\b", PIIConfidence.LOW),
        ],
        PIIType.BUSINESS_NUMBER: [
            # 사업자등록번호
            (r"\b\d{3}-\d{2}-\d{5}\b", PIIConfidence.HIGH),
        ]
    }

class PresidioKoreanRecognizer:
    """Presidio 한국어 커스텀 Recognizer"""
    
    def __init__(self):
        self.patterns = KoreanPIIPatterns.PATTERNS
        self.recognizers = {}
        self._initialize_recognizers()
    
    def _initialize_recognizers(self):
        """한국어 패턴 기반 Recognizer 초기화"""
        for pii_type, patterns in self.patterns.items():
            recognizer = {
                'patterns': patterns,
                'entity_type': pii_type.upper(),
                'confidence': 0.8
            }
            self.recognizers[pii_type] = recognizer
    
    def get_recognizers(self) -> Dict[str, Any]:
        """Presidio용 Recognizer 반환"""
        return self.recognizers

class PresidioPIIDetector:
    """고급 PII 탐지기 - spaCy 없이 정규식 + 검증기 + 컨텍스트 분석 + 한국어 처리 기반"""
    
    def __init__(self):
        self.patterns = KoreanPIIPatterns.PATTERNS  # 기본 패턴 (fallback)
        self.db_patterns = {}  # DB에서 로드된 패턴
        self.toml_patterns = {}  # toml 파일에서 로드된 패턴
        self.korean_validator = KoreanPIIValidator()  # 한국어 검증기
        self.context_analyzer = ContextAnalyzer()  # 컨텍스트 분석기
        self.korean_processor = LightweightKoreanProcessor()  # 한국어 처리기
        
        self.scanner_status = {
            "presidio": PRESIDIO_AVAILABLE,
            "nltk": NLTK_AVAILABLE,
            "regex": True,
            "korean_validator": True,  # 한국어 검증기 활성화
            "context_analyzer": True,
            "korean_processor": True,  # 한국어 처리기 활성화
            "db_patterns": False,
            "toml_patterns": False
        }
        
        # Presidio 초기화 (비활성화)
        self.analyzer = None
        self.anonymizer = None
        self.korean_recognizer = None
        
        logger.info("Presidio 비활성화됨. 한국어 검증기 기반 탐지 사용")
                
        # NLTK 초기화
        if NLTK_AVAILABLE:
            try:
                nltk.download('punkt', quiet=True)
                nltk.download('averaged_perceptron_tagger', quiet=True)
                nltk.download('maxent_ne_chunker', quiet=True)
                nltk.download('words', quiet=True)
            except Exception as e:
                logger.error(f"NLTK 초기화 실패: {e}")
        
        logger.info(f"PII 탐지기 초기화 완료. 상태: {self.scanner_status}")
    
    async def load_patterns_from_db(self, tenant_id: int = 1) -> bool:
        """DB에서 PII 패턴 로드"""
        try:
            # NOTE: 이 서비스는 독립적으로 실행되므로, DB 접근 방식 변경 필요
            # 현재는 임시로 db_filter_engine을 직접 import하지만,
            # 실제 마이크로서비스 환경에서는 별도의 DB 접근 계층 또는 API 호출을 통해 패턴을 가져와야 함.
            from ...backend.app.db_filter_engine import get_db_filter_engine
            
            db_engine = get_db_filter_engine()
            patterns = await db_engine.get_pii_patterns(tenant_id)
            
            if patterns:
                self.db_patterns = patterns
                self.scanner_status["db_patterns"] = True
                logger.info(f"DB에서 {len(patterns)}개의 PII 패턴 로드 완료")
                return True
            else:
                logger.warning("DB에서 PII 패턴을 찾을 수 없습니다. 기본 패턴을 사용합니다.")
                return False
                
        except Exception as e:
            logger.error(f"DB에서 패턴 로드 실패: {e}")
            return False
    
    async def load_patterns_from_toml(self, toml_path: str = None) -> bool:
        """toml 파일에서 PII 패턴 로드"""
        try:
            if toml_path is None:
                # 기본 경로 설정
                current_dir = os.path.dirname(os.path.abspath(__file__))
                toml_path = os.path.join(current_dir, "..", "..", "..", "backend", "pii_patterns.toml")
            
            if not os.path.exists(toml_path):
                logger.warning(f"toml 파일을 찾을 수 없습니다: {toml_path}")
                return False
            
            with open(toml_path, 'r', encoding='utf-8') as f:
                config = toml.load(f)
            
            if 'pii_patterns' not in config:
                logger.warning("toml 파일에 pii_patterns 섹션이 없습니다.")
                return False
            
            # 패턴을 PIIType별로 분류
            pii_patterns = {
                "NAME": [], "EMAIL": [], "PHONE": [], "SSN": [], "CREDIT_CARD": [],
                "BANK_ACCOUNT": [], "PASSPORT": [], "DRIVER_LICENSE": [], "IP_ADDRESS": [],
                "MAC_ADDRESS": [], "DATE_OF_BIRTH": [], "ADDRESS": []
            }
            
            for pii_type, type_patterns in config['pii_patterns'].items():
                if pii_type.upper() in pii_patterns:
                    for pattern_config in type_patterns:
                        pattern = pattern_config.get('regex', '')
                        severity_str = pattern_config.get('severity', 'medium').upper()
                        
                        # 심각도 매핑
                        severity_mapping = {
                            'LOW': 'LOW', 'MEDIUM': 'MEDIUM', 'HIGH': 'HIGH', 'CRITICAL': 'CRITICAL'
                        }
                        severity = severity_mapping.get(severity_str, 'MEDIUM')
                        
                        pii_patterns[pii_type.upper()].append((pattern, PIIConfidence[severity]))
            
            self.toml_patterns = pii_patterns
            self.scanner_status["toml_patterns"] = True
            logger.info(f"toml 파일에서 PII 패턴 로드 완료")
            return True
            
        except Exception as e:
            logger.error(f"toml 파일에서 패턴 로드 실패: {e}")
            return False
    
    async def scan_text(self, text: str, context: str = "") -> PIIScanResult:
        """텍스트에서 PII 스캔 - 다단계 하이브리드 접근법"""
        start_time = time.time()
        pii_matches = []
        error_messages = []
        
        try:
            # 1단계: 한국어 검증기로 스캔 (재활성화 테스트)
            korean_matches = await self._scan_with_korean_validator(text, context)
            pii_matches.extend(korean_matches)
            logger.info(f"한국어 검증기 스캔 완료: {len(korean_matches)}개 탐지")
            
            # 2단계: 한국어 처리기로 엔티티 추출 (재활성화 테스트)
            korean_entities = await self._scan_with_korean_processor(text, context)
            pii_matches.extend(korean_entities)
            logger.info(f"한국어 처리기 스캔 완료: {len(korean_entities)}개 탐지")
            
            # 3단계: 정규식 패턴 스캔 (재활성화 테스트)
            regex_matches = await self._scan_with_regex(text, context)
            pii_matches.extend(regex_matches)
            logger.info(f"정규식 패턴 스캔 완료: {len(regex_matches)}개 탐지")
            
            # 4단계: NLTK 스캔 (임시 비활성화)
            # if NLTK_AVAILABLE:
            #     try:
            #         nltk_matches = await self._scan_with_nltk(text, context)
            #         pii_matches.extend(nltk_matches)
            #     except Exception as e:
            #         error_messages.append(f"NLTK 스캔 실패: {e}")
            logger.info("NLTK 스캔 임시 비활성화됨")
            
            # 5단계: 컨텍스트 분석으로 신뢰도 조정 및 중복 제거 (재활성화 테스트)
            pii_matches = self.context_analyzer.analyze_context(text, pii_matches)
            pii_matches = self._deduplicate_matches(pii_matches)
            pii_matches.sort(key=lambda x: (x.confidence, x.start_pos))
            logger.info(f"컨텍스트 분석 및 정렬 완료: {len(pii_matches)}개 매치")
            
            # 결과 집계 (임시 간소화)
            high_confidence_count = 0
            risk_score = 0.0
            
            # 컨텍스트 정보 추가 (임시 비활성화)
            # for pii_match in pii_matches:
            #     if not pii_match.context:
            #         pii_match.context = self._get_pii_context(text, pii_match.start_pos, pii_match.end_pos)
            
            processing_time = time.time() - start_time
            
            return PIIScanResult(
                has_pii=len(pii_matches) > 0,
                pii_matches=pii_matches,
                total_pii=len(pii_matches),
                high_confidence_pii=high_confidence_count,
                risk_score=risk_score,
                processing_time=processing_time,
                scanner_status=self.scanner_status,
                error_messages=error_messages
            )
            
        except Exception as e:
            logger.error(f"PII 스캔 실패: {e}")
            return PIIScanResult(
                has_pii=False,
                pii_matches=[],
                total_pii=0,
                high_confidence_pii=0,
                risk_score=0.0,
                processing_time=time.time() - start_time,
                scanner_status=self.scanner_status,
                error_messages=[f"스캔 실패: {e}"]
            )
    
    async def _scan_with_korean_validator(self, text: str, context: str) -> List[PIIMatch]:
        """한국어 검증기로 PII 스캔"""
        matches = []
        
        try:
            # 한국어 검증기로 모든 PII 타입 검증
            validation_results = self.korean_validator.validate_all(text)
            
            # 결과를 PIIMatch 객체로 변환
            for pii_type_str, validation_matches in validation_results.items():
                pii_type = self._map_korean_type_to_pii_type(pii_type_str)
                
                for matched_text, start_pos, end_pos, confidence in validation_matches:
                    pii_match = PIIMatch(
                        pii_type=pii_type,
                        confidence=self._map_confidence_value(confidence),
                        pattern=f"korean_validator_{str(pii_type_str)}",
                        matched_text=matched_text,
                        start_pos=start_pos,
                        end_pos=end_pos,
                        context=context,
                        metadata={
                            "scanner": "korean_validator",
                            "pattern_type": "korean_validator",
                            "pattern_source": "korean_validator"
                        }
                    )
                    matches.append(pii_match)
            
            logger.debug(f"한국어 검증기 스캔 완료: {len(matches)}개 PII 탐지")
            
        except Exception as e:
            logger.error(f"한국어 검증기 스캔 실패: {e}")
        
        return matches
    
    async def _scan_with_korean_processor(self, text: str, context: str) -> List[PIIMatch]:
        """한국어 처리기로 엔티티 추출"""
        matches = []
        
        try:
            # 한국어 엔티티 추출
            entities = self.korean_processor.extract_korean_entities(text)
            
            # 엔티티를 PIIMatch로 변환
            for entity in entities:
                pii_type = self._map_korean_entity_to_pii_type(entity.entity_type)
                
                if pii_type != PIIType.UNKNOWN:
                    pii_match = PIIMatch(
                        pii_type=pii_type,
                        confidence=self._map_confidence_value(entity.confidence),
                        pattern=f"korean_processor_{entity.entity_type.value}",
                        matched_text=entity.text,
                        start_pos=entity.start_pos,
                        end_pos=entity.end_pos,
                        context=context,
                        metadata={
                            "scanner": "korean_processor",
                            "entity_type": entity.entity_type.value,
                            "extraction_method": entity.metadata.get("extraction_method", "unknown"),
                            "pattern_source": "korean_processor"
                        }
                    )
                    matches.append(pii_match)
            
            logger.debug(f"한국어 처리기 스캔 완료: {len(matches)}개 PII 탐지")
            
        except Exception as e:
            logger.error(f"한국어 처리기 스캔 실패: {e}")
        
        return matches
    
    def _map_korean_entity_to_pii_type(self, entity_type) -> PIIType:
        """한국어 엔티티 타입을 PIIType으로 매핑"""
        mapping = {
            "person": PIIType.NAME,
            "organization": PIIType.UNKNOWN,  # 기관명은 일반적으로 PII가 아님
            "location": PIIType.ADDRESS,
            "date": PIIType.DATE_OF_BIRTH,
            "time": PIIType.UNKNOWN,
            "money": PIIType.UNKNOWN,
            "percent": PIIType.UNKNOWN,
            "unknown": PIIType.UNKNOWN
        }
        return mapping.get(entity_type.value, PIIType.UNKNOWN)
    
    def _map_korean_type_to_pii_type(self, korean_type: str) -> PIIType:
        """한국어 검증기 타입을 PIIType으로 매핑"""
        mapping = {
            "names": PIIType.NAME,
            "phones": PIIType.PHONE,
            "ssns": PIIType.SSN,
            "emails": PIIType.EMAIL,
            "credit_cards": PIIType.CREDIT_CARD,
            "addresses": PIIType.ADDRESS,
        }
        return mapping.get(korean_type, PIIType.UNKNOWN)
    
    def _map_confidence_value(self, confidence: float) -> PIIConfidence:
        """신뢰도 값을 PIIConfidence로 매핑"""
        if confidence >= 0.9:
            return PIIConfidence.CRITICAL
        elif confidence >= 0.8:
            return PIIConfidence.HIGH
        elif confidence >= 0.6:
            return PIIConfidence.MEDIUM
        else:
            return PIIConfidence.LOW
    
    async def _scan_with_regex(self, text: str, context: str) -> List[PIIMatch]:
        """정규식을 사용한 PII 스캔 - DB/toml 패턴 우선 사용"""
        matches = []
        
        # 패턴 우선순위: DB > toml > 기본 패턴
        if self.db_patterns:
            patterns_to_use = self.db_patterns
        elif self.toml_patterns:
            patterns_to_use = self.toml_patterns
        else:
            patterns_to_use = self.patterns
        
        for pii_type, patterns in patterns_to_use.items():
            for pattern, confidence in patterns:
                try:
                    # PIIType enum으로 변환
                    if isinstance(pii_type, str):
                        pii_type_enum = PIIType(pii_type.lower())
                    else:
                        pii_type_enum = pii_type
                    
                    # PIIConfidence enum으로 변환
                    if isinstance(confidence, str):
                        confidence_enum = PIIConfidence(confidence.lower())
                    else:
                        confidence_enum = self._map_confidence_value(confidence)
                    
                    regex_matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
                    for match in regex_matches:
                        pii_match = PIIMatch(
                            pii_type=pii_type_enum,
                            confidence=confidence_enum,
                            pattern=pattern,
                            matched_text=match.group(),
                            start_pos=match.start(),
                            end_pos=match.end(),
                            context=context,
                            metadata={
                                "scanner": "regex",
                                "pattern_type": "regex",
                                "pattern_source": "db" if self.db_patterns else ("toml" if self.toml_patterns else "default")
                            }
                        )
                        matches.append(pii_match)
                except Exception as e:
                    logger.warning(f"정규식 패턴 스캔 실패 ({pattern}): {e}")
        
        return matches
    
    async def _scan_with_presidio(self, text: str, context: str) -> List[PIIMatch]:
        """Presidio 스캔 (비활성화됨)"""
        logger.debug("Presidio 스캔 비활성화됨")
        return []
    
    async def _scan_with_nltk(self, text: str, context: str) -> List[PIIMatch]:
        """NLTK를 사용한 PII 스캔"""
        matches = []
        if not NLTK_AVAILABLE:
            return matches
        
        try:
            tokens = word_tokenize(text)
            tagged = pos_tag(tokens)
            named_entities = ne_chunk(tagged)
            
            for tree in named_entities:
                if isinstance(tree, Tree):
                    entity_type = tree.label()
                    entity_text = " ".join([word for word, tag in tree.leaves()])
                    
                    pii_type = self._map_nltk_entity_to_pii_type(entity_type)
                    if pii_type != PIIType.UNKNOWN:
                        # NLTK는 정확한 위치 정보를 제공하지 않으므로, 텍스트 검색으로 위치 추정
                        start_pos = text.find(entity_text)
                        end_pos = start_pos + len(entity_text) if start_pos != -1 else -1
                        
                        if start_pos != -1:
                            pii_match = PIIMatch(
                                pii_type=pii_type,
                                confidence=PIIConfidence.MEDIUM,
                                pattern=entity_type,
                                matched_text=entity_text,
                                start_pos=start_pos,
                                end_pos=end_pos,
                                context=context,
                                metadata={"scanner": "nltk", "entity_label": entity_type}
                            )
                            matches.append(pii_match)
        except Exception as e:
            logger.error(f"NLTK 스캔 실패: {e}")
        
        return matches
    
    def _deduplicate_matches(self, matches: List[PIIMatch]) -> List[PIIMatch]:
        """중복 PII 매치 제거 (동일 타입, 동일 위치)"""
        unique_matches = []
        seen = set()
        for match in matches:
            key = (match.pii_type, match.start_pos, match.end_pos)
            if key not in seen:
                unique_matches.append(match)
                seen.add(key)
        return unique_matches
    
    def _calculate_risk_score(self, matches: List[PIIMatch]) -> float:
        """탐지된 PII 매치를 기반으로 위험 점수 계산"""
        if not matches:
            return 0.0
        
        # 신뢰도 문자열을 숫자로 변환하는 매핑
        confidence_values = {
            PIIConfidence.LOW: 0.3,
            PIIConfidence.MEDIUM: 0.6,
            PIIConfidence.HIGH: 0.8,
            PIIConfidence.CRITICAL: 1.0
        }
        
        total_score = 0.0
        for match in matches:
            # 신뢰도와 PII 타입에 따른 가중치 부여
            weight = 1.0
            if match.pii_type in [PIIType.SSN, PIIType.CREDIT_CARD, PIIType.BANK_ACCOUNT, PIIType.PASSPORT, PIIType.DRIVER_LICENSE]:
                weight = 2.0 # 민감도가 높은 PII
            
            confidence_value = confidence_values.get(match.confidence, 0.3)
            total_score += confidence_value * weight
        
        # 정규화 (최대 점수 대비)
        max_possible_score = len(matches) * 1.0 * 2.0 # 모든 PII가 가장 민감하고 최고 신뢰도일 경우
        return min(total_score / max_possible_score, 1.0) if max_possible_score > 0 else 0.0
    
    def _get_pii_context(self, text: str, start_pos: int, end_pos: int, window_size: int = 50) -> str:
        """PII 주변 텍스트 컨텍스트 추출"""
        start = max(0, start_pos - window_size)
        end = min(len(text), end_pos + window_size)
        return text[start:end]
    
    def _map_presidio_entity_to_pii_type(self, entity_label: str) -> PIIType:
        """Presidio 엔티티 라벨을 PII 타입으로 매핑"""
        mapping = {
            "PERSON": PIIType.NAME,
            "EMAIL_ADDRESS": PIIType.EMAIL,
            "PHONE_NUMBER": PIIType.PHONE,
            "CREDIT_CARD": PIIType.CREDIT_CARD,
            "IBAN_CODE": PIIType.BANK_ACCOUNT,
            "US_SSN": PIIType.SSN,
            "IP_ADDRESS": PIIType.IP_ADDRESS,
            "LOCATION": PIIType.ADDRESS,
            "DATE": PIIType.DATE_OF_BIRTH,
            "NRP": PIIType.NATIONALITY,
            "MEDICAL_LICENSE": PIIType.UNKNOWN,
            "URL": PIIType.UNKNOWN,
            "ORGANIZATION": PIIType.UNKNOWN,
            "CRYPTO": PIIType.UNKNOWN,
        }
        return mapping.get(entity_label, PIIType.UNKNOWN)
    
    def _map_presidio_score_to_confidence(self, score: float) -> PIIConfidence:
        """Presidio 점수를 PII 신뢰도로 매핑"""
        if score >= 0.9:
            return PIIConfidence.CRITICAL
        elif score >= 0.8:
            return PIIConfidence.HIGH
        elif score >= 0.6:
            return PIIConfidence.MEDIUM
        else:
            return PIIConfidence.LOW
    
    def _map_nltk_entity_to_pii_type(self, entity_label: str) -> PIIType:
        """NLTK 엔티티 라벨을 PII 타입으로 매핑"""
        mapping = {
            "PERSON": PIIType.NAME,
            "ORGANIZATION": PIIType.UNKNOWN,
            "GPE": PIIType.ADDRESS,
            "LOCATION": PIIType.ADDRESS,
            "DATE": PIIType.DATE_OF_BIRTH,
            "TIME": PIIType.UNKNOWN,
            "MONEY": PIIType.UNKNOWN,
            "PERCENT": PIIType.UNKNOWN,
            "FACILITY": PIIType.ADDRESS,
        }
        return mapping.get(entity_label, PIIType.UNKNOWN)
    
    def get_scanner_status(self) -> Dict[str, bool]:
        """스캐너 상태 반환"""
        return self.scanner_status.copy()
    
    def anonymize_text(self, text: str, matches: List[PIIMatch]) -> str:
        """텍스트 익명화 - 기본 마스킹 방식 사용"""
        if not matches:
            return text
        
        # 기본 마스킹 방식 사용
        anonymized_text = text
        
        # 위치 기준으로 역순 정렬 (뒤에서부터 마스킹)
        sorted_matches = sorted(matches, key=lambda x: x.start_pos, reverse=True)
        
        for match in sorted_matches:
            # 마스킹 문자 생성
            mask_char = self._get_mask_character(match.pii_type)
            mask_length = len(match.matched_text)
            mask_text = mask_char * mask_length
            
            # 텍스트 마스킹
            anonymized_text = (
                anonymized_text[:match.start_pos] + 
                mask_text + 
                anonymized_text[match.end_pos:]
            )
        
        return anonymized_text
    
    
    def _get_mask_character(self, pii_type: PIIType) -> str:
        """PII 타입별 마스킹 문자 반환"""
        mask_chars = {
            PIIType.NAME: '*',
            PIIType.EMAIL: '*',
            PIIType.PHONE: '*',
            PIIType.ADDRESS: '*',
            PIIType.SSN: '*',
            PIIType.CREDIT_CARD: '*',
            PIIType.BANK_ACCOUNT: '*',
            PIIType.PASSPORT: '*',
            PIIType.DRIVER_LICENSE: '*',
            PIIType.IP_ADDRESS: '*',
            PIIType.MAC_ADDRESS: '*',
            PIIType.DATE_OF_BIRTH: '*',
            PIIType.GENDER: '*',
            PIIType.NATIONALITY: '*',
            PIIType.BUSINESS_NUMBER: '*',
            PIIType.UNKNOWN: '*'
        }
        return mask_chars.get(pii_type, '*')