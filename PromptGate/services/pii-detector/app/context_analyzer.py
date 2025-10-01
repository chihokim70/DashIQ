"""
컨텍스트 기반 PII 검증 모듈
PII 탐지 후 컨텍스트를 분석하여 신뢰도 조정
"""

import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ContextType(Enum):
    """컨텍스트 타입"""
    FORM_FIELD = "form_field"      # 폼 필드
    DOCUMENT = "document"           # 문서
    CONVERSATION = "conversation"   # 대화
    DATABASE = "database"          # 데이터베이스
    LOG = "log"                    # 로그
    EMAIL = "email"                # 이메일
    CHAT = "chat"                  # 채팅
    UNKNOWN = "unknown"            # 알 수 없음

@dataclass
class ContextInfo:
    """컨텍스트 정보"""
    context_type: ContextType
    keywords: List[str]
    confidence_boost: float
    description: str

class ContextAnalyzer:
    """컨텍스트 분석기"""
    
    def __init__(self):
        self.context_patterns = self._init_context_patterns()
        self.korean_context_keywords = self._init_korean_keywords()
    
    def _init_context_patterns(self) -> Dict[ContextType, List[str]]:
        """컨텍스트 패턴 초기화"""
        return {
            ContextType.FORM_FIELD: [
                r"(이름|성명|성함|name)\s*[:：]",
                r"(전화번호|연락처|핸드폰|휴대폰|phone)\s*[:：]",
                r"(이메일|메일|email)\s*[:：]",
                r"(주소|거주지|address)\s*[:：]",
                r"(생년월일|생일|birth)\s*[:：]",
                r"(주민번호|주민등록번호|ssn)\s*[:：]",
                r"(계좌번호|통장|account)\s*[:：]",
            ],
            ContextType.DOCUMENT: [
                r"(신분증|여권|passport|id card)",
                r"(계약서|contract|agreement)",
                r"(신청서|application|form)",
                r"(증명서|certificate|proof)",
                r"(보고서|report|document)",
            ],
            ContextType.CONVERSATION: [
                r"(안녕하세요|안녕|hello|hi)",
                r"(감사합니다|고맙습니다|thank you)",
                r"(죄송합니다|미안합니다|sorry)",
                r"(질문|question|문의)",
                r"(답변|answer|reply)",
            ],
            ContextType.DATABASE: [
                r"(select|insert|update|delete)",
                r"(table|column|row|record)",
                r"(primary key|foreign key)",
                r"(database|db|데이터베이스)",
            ],
            ContextType.LOG: [
                r"(log|로그|logging)",
                r"(error|오류|exception)",
                r"(debug|info|warn|warning)",
                r"(timestamp|시간|time)",
            ],
            ContextType.EMAIL: [
                r"(from|to|cc|bcc|subject)",
                r"(발신자|수신자|제목)",
                r"(mail|메일|이메일)",
                r"(smtp|pop|imap)",
            ],
            ContextType.CHAT: [
                r"(채팅|chat|message|메시지)",
                r"(방|room|channel|채널)",
                r"(사용자|user|member|멤버)",
                r"(실시간|realtime|live)",
            ]
        }
    
    def _init_korean_keywords(self) -> Dict[str, List[str]]:
        """한국어 컨텍스트 키워드 초기화"""
        return {
            "name_context": [
                "이름", "성명", "성함", "고객명", "회원명", "사용자명",
                "씨", "님", "선생님", "교수님", "부장님", "과장님", "대리님",
                "고객", "회원", "사용자", "담당자", "책임자"
            ],
            "phone_context": [
                "전화번호", "연락처", "핸드폰", "휴대폰", "폰번호",
                "연락", "통화", "전화", "문의", "상담"
            ],
            "email_context": [
                "이메일", "메일", "이메일주소", "메일주소",
                "발송", "수신", "전송", "문의", "답변"
            ],
            "address_context": [
                "주소", "거주지", "살고", "거주", "배송지", "주소지",
                "배송", "택배", "우편", "우편번호", "주소록"
            ],
            "ssn_context": [
                "주민번호", "주민등록번호", "주민등록", "신분증",
                "신분", "등록", "번호", "식별"
            ],
            "card_context": [
                "카드", "신용카드", "체크카드", "결제", "결제수단",
                "카드번호", "카드정보", "결제정보", "결제카드"
            ],
            "account_context": [
                "계좌", "계좌번호", "통장", "은행", "입금", "출금",
                "계좌정보", "은행계좌", "통장번호", "계좌이체"
            ]
        }
    
    def analyze_context(self, text: str, pii_matches: List[Any]) -> List[Any]:
        """컨텍스트 분석으로 PII 신뢰도 조정"""
        enhanced_matches = []
        
        for match in pii_matches:
            # 컨텍스트 윈도우 추출
            context_window = self._get_context_window(text, match.start_pos, match.end_pos, 100)
            
            # 컨텍스트 타입 분석
            context_type = self._detect_context_type(context_window)
            
            # 신뢰도 조정
            adjusted_confidence = self._adjust_confidence_by_context(
                match, context_window, context_type
            )
            
            # 컨텍스트 정보 추가
            match.context = context_window
            match.metadata.update({
                "context_type": context_type.value,
                "context_analysis": self._analyze_specific_context(match, context_window)
            })
            
            # 신뢰도가 임계값 이상인 경우만 유지
            if adjusted_confidence >= 0.3:  # LOW 신뢰도 이상
                enhanced_matches.append(match)
        
        return enhanced_matches
    
    def _get_context_window(self, text: str, start_pos: int, end_pos: int, window_size: int = 100) -> str:
        """PII 주변 컨텍스트 윈도우 추출"""
        start = max(0, start_pos - window_size)
        end = min(len(text), end_pos + window_size)
        return text[start:end]
    
    def _detect_context_type(self, context: str) -> ContextType:
        """컨텍스트 타입 감지"""
        context_lower = context.lower()
        
        # 각 컨텍스트 타입별 점수 계산
        scores = {}
        for context_type, patterns in self.context_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, context_lower, re.IGNORECASE):
                    score += 1
            scores[context_type] = score
        
        # 가장 높은 점수의 컨텍스트 타입 반환
        if scores:
            best_type = max(scores, key=scores.get)
            if scores[best_type] > 0:
                return best_type
        
        return ContextType.UNKNOWN
    
    def _confidence_to_float(self, confidence) -> float:
        """confidence enum을 float로 변환"""
        confidence_mapping = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.8,
            "critical": 1.0
        }
        if hasattr(confidence, 'value'):
            return confidence_mapping.get(confidence.value.lower(), 0.5)
        elif isinstance(confidence, str):
            return confidence_mapping.get(confidence.lower(), 0.5)
        else:
            return float(confidence) if isinstance(confidence, (int, float)) else 0.5
    
    def _adjust_confidence_by_context(self, match: Any, context: str, context_type: ContextType) -> float:
        """컨텍스트에 따른 신뢰도 조정"""
        # confidence 값을 float로 변환
        if hasattr(match.confidence, 'value'):
            base_confidence = self._confidence_to_float(match.confidence)
        else:
            base_confidence = float(match.confidence) if isinstance(match.confidence, (int, float)) else 0.5
        
        adjustment = 0.0
        
        # 컨텍스트 타입별 신뢰도 조정
        if context_type == ContextType.FORM_FIELD:
            adjustment += 0.2  # 폼 필드는 높은 신뢰도
        elif context_type == ContextType.DOCUMENT:
            adjustment += 0.15  # 문서는 중간 신뢰도
        elif context_type == ContextType.CONVERSATION:
            adjustment += 0.1   # 대화는 약간의 신뢰도
        elif context_type == ContextType.DATABASE:
            adjustment += 0.25  # 데이터베이스는 매우 높은 신뢰도
        elif context_type == ContextType.LOG:
            adjustment += 0.3   # 로그는 매우 높은 신뢰도
        
        # 한국어 키워드 기반 추가 조정
        keyword_adjustment = self._calculate_keyword_adjustment(match, context)
        adjustment += keyword_adjustment
        
        # 최종 신뢰도 계산 (0.0 ~ 1.0 범위)
        final_confidence = min(base_confidence + adjustment, 1.0)
        
        return final_confidence
    
    def _calculate_keyword_adjustment(self, match: Any, context: str) -> float:
        """한국어 키워드 기반 신뢰도 조정"""
        adjustment = 0.0
        context_lower = context.lower()
        
        # PII 타입별 키워드 매칭
        pii_type = match.pii_type.value.lower()
        
        if pii_type in ["name", "이름"]:
            keywords = self.korean_context_keywords["name_context"]
            for keyword in keywords:
                if keyword in context_lower:
                    adjustment += 0.1
                    break
        
        elif pii_type in ["phone", "전화번호"]:
            keywords = self.korean_context_keywords["phone_context"]
            for keyword in keywords:
                if keyword in context_lower:
                    adjustment += 0.1
                    break
        
        elif pii_type in ["email", "이메일"]:
            keywords = self.korean_context_keywords["email_context"]
            for keyword in keywords:
                if keyword in context_lower:
                    adjustment += 0.1
                    break
        
        elif pii_type in ["address", "주소"]:
            keywords = self.korean_context_keywords["address_context"]
            for keyword in keywords:
                if keyword in context_lower:
                    adjustment += 0.1
                    break
        
        elif pii_type in ["ssn", "주민번호"]:
            keywords = self.korean_context_keywords["ssn_context"]
            for keyword in keywords:
                if keyword in context_lower:
                    adjustment += 0.15  # 민감한 정보는 더 높은 조정
                    break
        
        elif pii_type in ["credit_card", "카드"]:
            keywords = self.korean_context_keywords["card_context"]
            for keyword in keywords:
                if keyword in context_lower:
                    adjustment += 0.15
                    break
        
        elif pii_type in ["bank_account", "계좌"]:
            keywords = self.korean_context_keywords["account_context"]
            for keyword in keywords:
                if keyword in context_lower:
                    adjustment += 0.15
                    break
        
        return min(adjustment, 0.3)  # 최대 0.3까지만 조정
    
    def _analyze_specific_context(self, match: Any, context: str) -> Dict[str, Any]:
        """특정 PII에 대한 상세 컨텍스트 분석"""
        analysis = {
            "surrounding_words": self._extract_surrounding_words(context, match.matched_text),
            "sentence_structure": self._analyze_sentence_structure(context),
            "form_indicators": self._detect_form_indicators(context),
            "confidence_factors": self._get_confidence_factors(match, context)
        }
        
        return analysis
    
    def _extract_surrounding_words(self, context: str, matched_text: str) -> List[str]:
        """PII 주변 단어 추출"""
        # PII 텍스트 앞뒤로 단어 추출
        words = re.findall(r'\b\w+\b', context)
        matched_words = re.findall(r'\b\w+\b', matched_text)
        
        surrounding = []
        for i, word in enumerate(words):
            if word in matched_words:
                # 앞뒤 2개 단어씩 추출
                start = max(0, i - 2)
                end = min(len(words), i + 3)
                surrounding.extend(words[start:end])
                break
        
        return list(set(surrounding))  # 중복 제거
    
    def _analyze_sentence_structure(self, context: str) -> Dict[str, Any]:
        """문장 구조 분석"""
        sentences = re.split(r'[.!?]', context)
        
        return {
            "sentence_count": len(sentences),
            "avg_sentence_length": sum(len(s) for s in sentences) / len(sentences) if sentences else 0,
            "has_colon": ':' in context or '：' in context,
            "has_quotes": '"' in context or "'" in context,
            "has_parentheses": '(' in context and ')' in context
        }
    
    def _detect_form_indicators(self, context: str) -> List[str]:
        """폼 필드 지시자 감지"""
        form_indicators = []
        
        # 라벨 패턴
        label_patterns = [
            r'(\w+)\s*[:：]\s*',  # 라벨: 값
            r'(\w+)\s*=\s*',      # 라벨=값
            r'(\w+)\s*:\s*',      # 라벨: 값 (영어)
        ]
        
        for pattern in label_patterns:
            matches = re.findall(pattern, context)
            form_indicators.extend(matches)
        
        return list(set(form_indicators))
    
    def _get_confidence_factors(self, match: Any, context: str) -> Dict[str, float]:
        """신뢰도에 영향을 주는 요소들"""
        factors = {
            "length_factor": min(len(match.matched_text) / 20, 1.0),  # 길이 기반
            "pattern_factor": 1.0,  # 패턴 매칭 품질
            "context_factor": 1.0,  # 컨텍스트 일치도
            "frequency_factor": 1.0  # 빈도 기반
        }
        
        # 컨텍스트 일치도 계산
        context_lower = context.lower()
        pii_text_lower = match.matched_text.lower()
        
        if pii_text_lower in context_lower:
            factors["context_factor"] = 1.2  # 컨텍스트 내 존재
        
        # 패턴 품질 평가
        if hasattr(match, 'pattern') and match.pattern:
            if 'korean_validator' in match.pattern:
                factors["pattern_factor"] = 1.3  # 한국어 검증기 패턴
            elif 'presidio' in match.pattern:
                factors["pattern_factor"] = 1.2  # Presidio 패턴
            elif 'regex' in match.pattern:
                factors["pattern_factor"] = 1.1  # 정규식 패턴
        
        return factors
    
    def get_context_summary(self, text: str) -> Dict[str, Any]:
        """전체 텍스트의 컨텍스트 요약"""
        context_type = self._detect_context_type(text)
        
        return {
            "detected_context_type": context_type.value,
            "text_length": len(text),
            "word_count": len(re.findall(r'\b\w+\b', text)),
            "sentence_count": len(re.split(r'[.!?]', text)),
            "has_korean": bool(re.search(r'[가-힣]', text)),
            "has_english": bool(re.search(r'[a-zA-Z]', text)),
            "has_numbers": bool(re.search(r'\d', text)),
            "has_special_chars": bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', text)),
            "form_indicators": self._detect_form_indicators(text)
        }
