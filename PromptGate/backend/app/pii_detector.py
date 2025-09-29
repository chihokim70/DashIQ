"""
PII (개인 식별 정보) 탐지기 구현
오픈소스 도구와 자체 개발을 결합한 하이브리드 접근법
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

# PII 탐지 라이브러리 import
try:
    import spacy
    from spacy import displacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_anonymizer import AnonymizerEngine
    from presidio_analyzer.entities import RecognizerResult
    PRESIDIO_AVAILABLE = True
except ImportError:
    PRESIDIO_AVAILABLE = False

try:
    import nltk
    from nltk import ne_chunk, pos_tag, word_tokenize
    from nltk.tree import Tree
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

logger = logging.getLogger(__name__)

class PIIType(Enum):
    """PII 타입 정의"""
    NAME = "name"
    EMAIL = "email"
    PHONE = "phone"
    ADDRESS = "address"
    SSN = "ssn"  # 주민등록번호
    CREDIT_CARD = "credit_card"
    BANK_ACCOUNT = "bank_account"
    PASSPORT = "passport"
    DRIVER_LICENSE = "driver_license"
    IP_ADDRESS = "ip_address"
    MAC_ADDRESS = "mac_address"
    DATE_OF_BIRTH = "date_of_birth"
    GENDER = "gender"
    NATIONALITY = "nationality"
    UNKNOWN = "unknown"

class PIIConfidence(Enum):
    """PII 탐지 신뢰도"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class PIIMatch:
    """PII 매치 결과"""
    pii_type: PIIType
    confidence: PIIConfidence
    pattern: str
    matched_text: str
    start_pos: int
    end_pos: int
    context: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PIIScanResult:
    """PII 스캔 결과"""
    has_pii: bool = False
    pii_matches: List[PIIMatch] = field(default_factory=list)
    total_pii: int = 0
    high_confidence_pii: int = 0
    risk_score: float = 0.0
    processing_time: float = 0.0
    scanner_status: Dict[str, bool] = field(default_factory=dict)
    error_messages: List[str] = field(default_factory=list)

class KoreanPIIPatterns:
    """한국어 PII 패턴 정의"""
    
    PATTERNS = {
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
        ]
    }

class AdvancedPIIDetector:
    """고급 PII 탐지기 - 하이브리드 접근법 + DB/toml 연동"""
    
    def __init__(self):
        self.patterns = KoreanPIIPatterns.PATTERNS  # 기본 패턴 (fallback)
        self.db_patterns = {}  # DB에서 로드된 패턴
        self.toml_patterns = {}  # toml 파일에서 로드된 패턴
        self.scanner_status = {
            "spacy": SPACY_AVAILABLE,
            "presidio": PRESIDIO_AVAILABLE,
            "nltk": NLTK_AVAILABLE,
            "regex": True,
            "db_patterns": False,
            "toml_patterns": False
        }
        
        # spaCy 모델 초기화
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                # 한국어 모델이 있으면 사용, 없으면 영어 모델 사용
                try:
                    self.nlp = spacy.load("ko_core_news_sm")
                except OSError:
                    try:
                        self.nlp = spacy.load("en_core_web_sm")
                    except OSError:
                        logger.warning("spaCy 모델을 찾을 수 없습니다. 패턴 매칭만 사용합니다.")
            except Exception as e:
                logger.error(f"spaCy 초기화 실패: {e}")
        
        # Presidio 초기화
        self.analyzer = None
        self.anonymizer = None
        if PRESIDIO_AVAILABLE:
            try:
                self.analyzer = AnalyzerEngine()
                self.anonymizer = AnonymizerEngine()
            except Exception as e:
                logger.error(f"Presidio 초기화 실패: {e}")
        
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
            from .db_filter_engine import get_db_filter_engine
            
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
                toml_path = os.path.join(current_dir, "..", "pii_patterns.toml")
            
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
                "NAME": [],
                "EMAIL": [],
                "PHONE": [],
                "SSN": [],
                "CREDIT_CARD": [],
                "BANK_ACCOUNT": [],
                "PASSPORT": [],
                "DRIVER_LICENSE": [],
                "IP_ADDRESS": [],
                "MAC_ADDRESS": [],
                "DATE_OF_BIRTH": [],
                "ADDRESS": []
            }
            
            for pii_type, type_patterns in config['pii_patterns'].items():
                if pii_type.upper() in pii_patterns:
                    for pattern_config in type_patterns:
                        pattern = pattern_config.get('regex', '')
                        severity_str = pattern_config.get('severity', 'medium').upper()
                        
                        # 심각도 매핑
                        severity_mapping = {
                            'LOW': 'LOW',
                            'MEDIUM': 'MEDIUM', 
                            'HIGH': 'HIGH',
                            'CRITICAL': 'CRITICAL'
                        }
                        severity = severity_mapping.get(severity_str, 'MEDIUM')
                        
                        pii_patterns[pii_type.upper()].append((pattern, severity))
            
            self.toml_patterns = pii_patterns
            self.scanner_status["toml_patterns"] = True
            logger.info(f"toml 파일에서 PII 패턴 로드 완료")
            return True
            
        except Exception as e:
            logger.error(f"toml 파일에서 패턴 로드 실패: {e}")
            return False
    
    async def scan_text(self, text: str, context: str = "") -> PIIScanResult:
        """텍스트에서 PII 스캔"""
        start_time = time.time()
        pii_matches = []
        error_messages = []
        
        try:
            # 1. 정규식 패턴 스캔
            regex_matches = await self._scan_with_regex(text, context)
            pii_matches.extend(regex_matches)
            
            # 2. spaCy NER 스캔
            if self.nlp:
                try:
                    spacy_matches = await self._scan_with_spacy(text, context)
                    pii_matches.extend(spacy_matches)
                except Exception as e:
                    error_messages.append(f"spaCy 스캔 실패: {e}")
            
            # 3. Presidio 스캔
            if self.analyzer:
                try:
                    presidio_matches = await self._scan_with_presidio(text, context)
                    pii_matches.extend(presidio_matches)
                except Exception as e:
                    error_messages.append(f"Presidio 스캔 실패: {e}")
            
            # 4. NLTK 스캔
            if NLTK_AVAILABLE:
                try:
                    nltk_matches = await self._scan_with_nltk(text, context)
                    pii_matches.extend(nltk_matches)
                except Exception as e:
                    error_messages.append(f"NLTK 스캔 실패: {e}")
            
            # 중복 제거 및 정렬
            pii_matches = self._deduplicate_matches(pii_matches)
            pii_matches.sort(key=lambda x: (x.confidence.value, x.start_pos))
            
            # 결과 집계
            high_confidence_count = sum(1 for m in pii_matches if m.confidence in [PIIConfidence.HIGH, PIIConfidence.VERY_HIGH])
            risk_score = self._calculate_risk_score(pii_matches)
            
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
                risk_score=0.0,
                processing_time=time.time() - start_time,
                scanner_status=self.scanner_status,
                error_messages=[f"스캔 실패: {e}"]
            )
    
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
                        confidence_enum = confidence
                    
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
    
    async def _scan_with_spacy(self, text: str, context: str) -> List[PIIMatch]:
        """spaCy NER을 사용한 PII 스캔"""
        matches = []
        
        if not self.nlp:
            return matches
        
        try:
            doc = self.nlp(text)
            
            for ent in doc.ents:
                # spaCy 엔티티를 PII 타입으로 매핑
                pii_type = self._map_spacy_entity_to_pii_type(ent.label_)
                if pii_type != PIIType.UNKNOWN:
                    confidence = self._calculate_spacy_confidence(ent)
                    
                    pii_match = PIIMatch(
                        pii_type=pii_type,
                        confidence=confidence,
                        pattern=f"spacy_{ent.label_}",
                        matched_text=ent.text,
                        start_pos=ent.start_char,
                        end_pos=ent.end_char,
                        context=context,
                        metadata={
                            "scanner": "spacy",
                            "spacy_label": ent.label_,
                            "spacy_confidence": ent._.prob if hasattr(ent._, 'prob') else 0.5
                        }
                    )
                    matches.append(pii_match)
            
        except Exception as e:
            logger.error(f"spaCy 스캔 실패: {e}")
        
        return matches
    
    async def _scan_with_presidio(self, text: str, context: str) -> List[PIIMatch]:
        """Presidio를 사용한 PII 스캔"""
        matches = []
        
        if not self.analyzer:
            return matches
        
        try:
            results = self.analyzer.analyze(text=text, language='en')
            
            for result in results:
                pii_type = self._map_presidio_entity_to_pii_type(result.entity_type)
                confidence = self._map_presidio_score_to_confidence(result.score)
                
                pii_match = PIIMatch(
                    pii_type=pii_type,
                    confidence=confidence,
                    pattern=f"presidio_{result.entity_type}",
                    matched_text=text[result.start:result.end],
                    start_pos=result.start,
                    end_pos=result.end,
                    context=context,
                    metadata={
                        "scanner": "presidio",
                        "presidio_entity": result.entity_type,
                        "presidio_score": result.score
                    }
                )
                matches.append(pii_match)
            
        except Exception as e:
            logger.error(f"Presidio 스캔 실패: {e}")
        
        return matches
    
    async def _scan_with_nltk(self, text: str, context: str) -> List[PIIMatch]:
        """NLTK를 사용한 PII 스캔"""
        matches = []
        
        if not NLTK_AVAILABLE:
            return matches
        
        try:
            tokens = word_tokenize(text)
            pos_tags = pos_tag(tokens)
            named_entities = ne_chunk(pos_tags)
            
            for chunk in named_entities:
                if isinstance(chunk, Tree):
                    entity_text = ' '.join([token for token, pos in chunk.leaves()])
                    entity_label = chunk.label()
                    
                    pii_type = self._map_nltk_entity_to_pii_type(entity_label)
                    if pii_type != PIIType.UNKNOWN:
                        # 텍스트에서 위치 찾기
                        start_pos = text.find(entity_text)
                        end_pos = start_pos + len(entity_text) if start_pos != -1 else 0
                        
                        pii_match = PIIMatch(
                            pii_type=pii_type,
                            confidence=PIIConfidence.MEDIUM,
                            pattern=f"nltk_{entity_label}",
                            matched_text=entity_text,
                            start_pos=start_pos,
                            end_pos=end_pos,
                            context=context,
                            metadata={
                                "scanner": "nltk",
                                "nltk_label": entity_label
                            }
                        )
                        matches.append(pii_match)
            
        except Exception as e:
            logger.error(f"NLTK 스캔 실패: {e}")
        
        return matches
    
    def _map_spacy_entity_to_pii_type(self, spacy_label: str) -> PIIType:
        """spaCy 엔티티를 PII 타입으로 매핑"""
        mapping = {
            'PERSON': PIIType.NAME,
            'PER': PIIType.NAME,
            'GPE': PIIType.ADDRESS,
            'LOC': PIIType.ADDRESS,
            'ORG': PIIType.UNKNOWN,
            'MONEY': PIIType.UNKNOWN,
            'DATE': PIIType.DATE_OF_BIRTH,
            'TIME': PIIType.UNKNOWN,
            'EMAIL': PIIType.EMAIL,
            'PHONE': PIIType.PHONE,
        }
        return mapping.get(spacy_label, PIIType.UNKNOWN)
    
    def _map_presidio_entity_to_pii_type(self, presidio_entity: str) -> PIIType:
        """Presidio 엔티티를 PII 타입으로 매핑"""
        mapping = {
            'PERSON': PIIType.NAME,
            'EMAIL_ADDRESS': PIIType.EMAIL,
            'PHONE_NUMBER': PIIType.PHONE,
            'CREDIT_CARD': PIIType.CREDIT_CARD,
            'IBAN_CODE': PIIType.BANK_ACCOUNT,
            'IP_ADDRESS': PIIType.IP_ADDRESS,
            'LOCATION': PIIType.ADDRESS,
            'DATE_TIME': PIIType.DATE_OF_BIRTH,
            'US_SSN': PIIType.SSN,
            'US_PASSPORT': PIIType.PASSPORT,
            'US_DRIVER_LICENSE': PIIType.DRIVER_LICENSE,
        }
        return mapping.get(presidio_entity, PIIType.UNKNOWN)
    
    def _map_nltk_entity_to_pii_type(self, nltk_label: str) -> PIIType:
        """NLTK 엔티티를 PII 타입으로 매핑"""
        mapping = {
            'PERSON': PIIType.NAME,
            'GPE': PIIType.ADDRESS,
            'LOCATION': PIIType.ADDRESS,
            'ORGANIZATION': PIIType.UNKNOWN,
            'MONEY': PIIType.UNKNOWN,
            'DATE': PIIType.DATE_OF_BIRTH,
            'TIME': PIIType.UNKNOWN,
        }
        return mapping.get(nltk_label, PIIType.UNKNOWN)
    
    def _calculate_spacy_confidence(self, ent) -> PIIConfidence:
        """spaCy 엔티티의 신뢰도 계산"""
        if hasattr(ent._, 'prob'):
            prob = ent._.prob
            if prob > 0.8:
                return PIIConfidence.VERY_HIGH
            elif prob > 0.6:
                return PIIConfidence.HIGH
            elif prob > 0.4:
                return PIIConfidence.MEDIUM
            else:
                return PIIConfidence.LOW
        return PIIConfidence.MEDIUM
    
    def _map_presidio_score_to_confidence(self, score: float) -> PIIConfidence:
        """Presidio 점수를 신뢰도로 매핑"""
        if score > 0.8:
            return PIIConfidence.VERY_HIGH
        elif score > 0.6:
            return PIIConfidence.HIGH
        elif score > 0.4:
            return PIIConfidence.MEDIUM
        else:
            return PIIConfidence.LOW
    
    def _deduplicate_matches(self, matches: List[PIIMatch]) -> List[PIIMatch]:
        """중복 매치 제거"""
        unique_matches = []
        seen_positions = set()
        
        for match in matches:
            position_key = (match.start_pos, match.end_pos, match.pii_type)
            if position_key not in seen_positions:
                seen_positions.add(position_key)
                unique_matches.append(match)
        
        return unique_matches
    
    def _calculate_risk_score(self, matches: List[PIIMatch]) -> float:
        """위험 점수 계산"""
        if not matches:
            return 0.0
        
        total_score = 0.0
        for match in matches:
            # PII 타입별 가중치
            type_weights = {
                PIIType.SSN: 1.0,
                PIIType.CREDIT_CARD: 0.9,
                PIIType.BANK_ACCOUNT: 0.8,
                PIIType.PASSPORT: 0.8,
                PIIType.DRIVER_LICENSE: 0.7,
                PIIType.EMAIL: 0.6,
                PIIType.PHONE: 0.5,
                PIIType.ADDRESS: 0.4,
                PIIType.NAME: 0.3,
                PIIType.IP_ADDRESS: 0.3,
                PIIType.MAC_ADDRESS: 0.2,
                PIIType.DATE_OF_BIRTH: 0.2,
                PIIType.GENDER: 0.1,
                PIIType.NATIONALITY: 0.1,
                PIIType.UNKNOWN: 0.1
            }
            
            # 신뢰도별 가중치
            confidence_weights = {
                PIIConfidence.VERY_HIGH: 1.0,
                PIIConfidence.HIGH: 0.8,
                PIIConfidence.MEDIUM: 0.6,
                PIIConfidence.LOW: 0.4
            }
            
            type_weight = type_weights.get(match.pii_type, 0.1)
            confidence_weight = confidence_weights.get(match.confidence, 0.4)
            
            total_score += type_weight * confidence_weight
        
        # 0-1 범위로 정규화
        max_possible_score = len(matches) * 1.0
        return min(total_score / max_possible_score, 1.0) if max_possible_score > 0 else 0.0
    
    def get_scanner_status(self) -> Dict[str, bool]:
        """스캐너 상태 반환"""
        return self.scanner_status.copy()
    
    def anonymize_text(self, text: str, matches: List[PIIMatch]) -> str:
        """텍스트 익명화"""
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
            PIIType.UNKNOWN: '*'
        }
        return mask_chars.get(pii_type, '*')

# 전역 인스턴스
_pii_detector_instance: Optional[AdvancedPIIDetector] = None

async def get_pii_detector() -> AdvancedPIIDetector:
    """PII 탐지기 인스턴스 반환"""
    global _pii_detector_instance
    
    if _pii_detector_instance is None:
        _pii_detector_instance = AdvancedPIIDetector()
    
    return _pii_detector_instance

async def close_pii_detector():
    """PII 탐지기 리소스 정리"""
    global _pii_detector_instance
    _pii_detector_instance = None
