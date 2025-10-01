"""
한국어 PII 검증기 모듈
spaCy 없이 정규식 + 검증기로 한국형 PII 탐지
"""

import re
import phonenumbers
from email_validator import validate_email, EmailNotValidError
from stdnum import kr
from typing import List, Tuple, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class KoreanPIIValidator:
    """한국어 PII 검증기"""
    
    def __init__(self):
        self.korean_surnames = {
            "김", "이", "박", "최", "정", "강", "조", "윤", "장", "임", "한", "오", "서", "신", "권", "황", "안", "송", "전", "고",
            "문", "양", "손", "배", "조", "백", "허", "유", "남", "심", "노", "정", "하", "곽", "성", "차", "주", "우", "구", "나",
            "신", "엄", "원", "천", "방", "공", "강", "현", "함", "변", "염", "여", "추", "노", "도", "소", "석", "선", "설", "마",
            "길", "연", "위", "표", "명", "기", "반", "금", "옥", "육", "인", "맹", "제", "모", "장", "남", "탁", "국", "여", "진",
            "어", "은", "편", "구", "용", "예", "경", "나", "동", "감", "봉", "사", "부", "지", "엄", "채", "최", "계", "피", "두",
            "복", "옹", "음", "빈", "동", "온", "단", "전", "화", "초", "호", "범", "위", "만", "유", "여", "남", "궉", "봉", "황",
            "간", "점", "영", "남", "궁", "팽", "윤", "나", "남", "궉", "봉", "황", "간", "점", "영", "남", "궁", "팽", "윤"
        }
        
        # 한국어 특화 패턴
        self.patterns = self._init_korean_patterns()
    
    def _init_korean_patterns(self) -> Dict[str, List[Tuple[str, float]]]:
        """한국어 특화 PII 패턴 초기화"""
        return {
            "KOREAN_NAME": [
                # 기본 한국 이름 패턴
                (r"\b[가-힣]{2,4}\b", 0.3),
                # 성씨 + 이름 패턴
                (r"\b(김|이|박|최|정|강|조|윤|장|임|한|오|서|신|권|황|안|송|전|고)[가-힣]{1,3}\b", 0.6),
                # 호칭과 함께
                (r"\b[가-힣]{2,4}(씨|님|선생님|교수님|부장님|과장님|대리님)\b", 0.8),
                # 성함/이름 키워드와 함께
                (r"\b(성함|이름|성명)\s*[:：]\s*[가-힣]{2,4}\b", 0.9),
            ],
            "KOREAN_ADDRESS": [
                # 시/도 + 구/군 패턴
                (r"\b(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)\s+[가-힣\s\d-]+(구|군|시|동|로|길|번지)\b", 0.8),
                # 구/군 + 동/로 패턴
                (r"\b[가-힣]{2,4}(구|군|시|동|로|길)\s*\d+", 0.7),
                # 우편번호 패턴
                (r"\b우편번호\s*[:：]\s*\d{5}\b", 0.9),
                # 주소 키워드와 함께
                (r"\b(주소|거주지|살고)\s*[:：]\s*[가-힣\s\d-]+", 0.8),
            ],
            "KOREAN_PHONE": [
                # 한국 휴대폰 번호
                (r"\b01[016789]-?\d{3,4}-?\d{4}\b", 0.8),
                (r"\b01[016789]\d{7,8}\b", 0.8),
                # 한국 일반 전화번호
                (r"\b0\d{1,2}-?\d{3,4}-?\d{4}\b", 0.6),
                # 전화번호 키워드와 함께
                (r"\b(전화|연락처|핸드폰|휴대폰)\s*[:：]\s*0\d{1,2}-?\d{3,4}-?\d{4}\b", 0.9),
            ],
            "KOREAN_SSN": [
                # 주민등록번호 (13자리)
                (r"\b\d{6}-[1-4]\d{6}\b", 0.9),
                (r"\b\d{6}[1-4]\d{6}\b", 0.9),
                # 외국인등록번호
                (r"\b\d{6}-[5-8]\d{6}\b", 0.9),
                (r"\b\d{6}[5-8]\d{6}\b", 0.9),
            ],
            "KOREAN_BUSINESS_NUMBER": [
                # 사업자등록번호
                (r"\b\d{3}-\d{2}-\d{5}\b", 0.8),
                (r"\b\d{3}-\d{2}-\d{5}\b", 0.8),
            ],
            "KOREAN_BANK_ACCOUNT": [
                # 한국 은행 계좌번호
                (r"\b\d{3}-\d{2}-\d{6,15}\b", 0.7),
                # 계좌번호 키워드와 함께
                (r"\b(계좌|통장|입금|출금)\s*[:：]\s*\d{3}-\d{2}-\d{6,15}\b", 0.9),
            ],
            "KOREAN_EMAIL": [
                # 한국 도메인 이메일
                (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(co\.kr|go\.kr|ac\.kr|or\.kr|kr)\b", 0.8),
                # 일반 이메일
                (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", 0.6),
            ],
            "KOREAN_CREDIT_CARD": [
                # 신용카드 번호 (16자리)
                (r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", 0.7),
                # 카드 키워드와 함께
                (r"\b(카드|결제|신용카드|체크카드)\s*[:：]\s*\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", 0.9),
            ]
        }
    
    def validate_korean_name(self, text: str) -> List[Tuple[str, int, int, float]]:
        """한국 이름 검증"""
        matches = []
        
        for pattern, base_confidence in self.patterns["KOREAN_NAME"]:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                name = match.group()
                start_pos = match.start()
                end_pos = match.end()
                
                # 추가 검증 로직
                confidence = self._validate_name_confidence(name, base_confidence)
                
                if confidence > 0.5:  # 임계값 이상만 반환
                    matches.append((name, start_pos, end_pos, confidence))
        
        return matches
    
    def _validate_name_confidence(self, name: str, base_confidence: float) -> float:
        """이름 신뢰도 검증"""
        confidence = base_confidence
        
        # 성씨 검증
        if len(name) >= 2 and name[0] in self.korean_surnames:
            confidence += 0.2
        
        # 길이 검증 (한국 이름은 보통 2-4글자)
        if 2 <= len(name) <= 4:
            confidence += 0.1
        elif len(name) > 4:
            confidence -= 0.2
        
        # 숫자나 특수문자 포함 시 신뢰도 감소
        if re.search(r'[0-9\W]', name):
            confidence -= 0.3
        
        return min(confidence, 1.0)
    
    def validate_korean_phone(self, text: str) -> List[Tuple[str, int, int, float]]:
        """한국 전화번호 검증"""
        matches = []
        
        for pattern, base_confidence in self.patterns["KOREAN_PHONE"]:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                phone = match.group()
                start_pos = match.start()
                end_pos = match.end()
                
                # libphonenumbers로 검증
                confidence = self._validate_phone_confidence(phone, base_confidence)
                
                if confidence > 0.5:
                    matches.append((phone, start_pos, end_pos, confidence))
        
        return matches
    
    def _validate_phone_confidence(self, phone: str, base_confidence: float) -> float:
        """전화번호 신뢰도 검증"""
        confidence = base_confidence
        
        try:
            # libphonenumbers로 한국 전화번호 검증
            parsed_phone = phonenumbers.parse(phone, "KR")
            if phonenumbers.is_valid_number(parsed_phone):
                confidence += 0.2
            else:
                confidence -= 0.3
        except Exception:
            confidence -= 0.2
        
        return min(confidence, 1.0)
    
    def validate_korean_ssn(self, text: str) -> List[Tuple[str, int, int, float]]:
        """한국 주민등록번호 검증"""
        matches = []
        
        for pattern, base_confidence in self.patterns["KOREAN_SSN"]:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                ssn = match.group()
                start_pos = match.start()
                end_pos = match.end()
                
                # 체크섬 검증
                confidence = self._validate_ssn_confidence(ssn, base_confidence)
                
                if confidence > 0.7:  # 주민번호는 높은 임계값
                    matches.append((ssn, start_pos, end_pos, confidence))
        
        return matches
    
    def _validate_ssn_confidence(self, ssn: str, base_confidence: float) -> float:
        """주민등록번호 신뢰도 검증"""
        confidence = base_confidence
        
        # 하이픈 제거
        clean_ssn = re.sub(r'[-\s]', '', ssn)
        
        if len(clean_ssn) == 13:
            try:
                # 체크섬 검증 (간단한 버전)
                digits = [int(d) for d in clean_ssn]
                
                # 성별 코드 검증 (7번째 자리)
                gender_code = digits[6]
                if gender_code in [1, 2, 3, 4]:
                    confidence += 0.1
                else:
                    confidence -= 0.3
                
                # 생년월일 검증 (앞 6자리)
                year = int(clean_ssn[:2])
                month = int(clean_ssn[2:4])
                day = int(clean_ssn[4:6])
                
                if 1 <= month <= 12 and 1 <= day <= 31:
                    confidence += 0.1
                else:
                    confidence -= 0.3
                    
            except (ValueError, IndexError):
                confidence -= 0.3
        else:
            confidence -= 0.3
        
        return min(confidence, 1.0)
    
    def validate_korean_email(self, text: str) -> List[Tuple[str, int, int, float]]:
        """한국 이메일 검증"""
        matches = []
        
        for pattern, base_confidence in self.patterns["KOREAN_EMAIL"]:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                email = match.group()
                start_pos = match.start()
                end_pos = match.end()
                
                # email-validator로 검증
                confidence = self._validate_email_confidence(email, base_confidence)
                
                if confidence > 0.5:
                    matches.append((email, start_pos, end_pos, confidence))
        
        return matches
    
    def _validate_email_confidence(self, email: str, base_confidence: float) -> float:
        """이메일 신뢰도 검증"""
        confidence = base_confidence
        
        try:
            # email-validator로 검증
            validate_email(email)
            confidence += 0.2
        except EmailNotValidError:
            confidence -= 0.3
        
        return min(confidence, 1.0)
    
    def validate_korean_credit_card(self, text: str) -> List[Tuple[str, int, int, float]]:
        """한국 신용카드 번호 검증"""
        matches = []
        
        for pattern, base_confidence in self.patterns["KOREAN_CREDIT_CARD"]:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                card = match.group()
                start_pos = match.start()
                end_pos = match.end()
                
                # Luhn 알고리즘으로 검증
                confidence = self._validate_card_confidence(card, base_confidence)
                
                if confidence > 0.6:
                    matches.append((card, start_pos, end_pos, confidence))
        
        return matches
    
    def _validate_card_confidence(self, card: str, base_confidence: float) -> float:
        """신용카드 신뢰도 검증 (Luhn 알고리즘)"""
        confidence = base_confidence
        
        # 숫자만 추출
        digits = re.sub(r'[^\d]', '', card)
        
        if len(digits) == 16:
            # Luhn 알고리즘 검증
            if self._luhn_check(digits):
                confidence += 0.2
            else:
                confidence -= 0.3
        else:
            confidence -= 0.2
        
        return min(confidence, 1.0)
    
    def _luhn_check(self, digits: str) -> bool:
        """Luhn 알고리즘 체크섬 검증"""
        def luhn_checksum(card_num):
            def digits_of(n):
                return [int(d) for d in str(n)]
            digits = digits_of(card_num)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d*2))
            return checksum % 10
        
        return luhn_checksum(digits) == 0
    
    def validate_korean_address(self, text: str) -> List[Tuple[str, int, int, float]]:
        """한국 주소 검증"""
        matches = []
        
        for pattern, base_confidence in self.patterns["KOREAN_ADDRESS"]:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                address = match.group()
                start_pos = match.start()
                end_pos = match.end()
                
                # 주소 신뢰도 검증
                confidence = self._validate_address_confidence(address, base_confidence)
                
                if confidence > 0.5:
                    matches.append((address, start_pos, end_pos, confidence))
        
        return matches
    
    def _validate_address_confidence(self, address: str, base_confidence: float) -> float:
        """주소 신뢰도 검증"""
        confidence = base_confidence
        
        # 한국 시/도 이름 포함 여부
        korean_regions = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종", 
                         "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]
        
        if any(region in address for region in korean_regions):
            confidence += 0.2
        
        # 구/군/시 키워드 포함 여부
        if any(keyword in address for keyword in ["구", "군", "시", "동", "로", "길"]):
            confidence += 0.1
        
        # 숫자 포함 여부 (번지, 우편번호 등)
        if re.search(r'\d', address):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def validate_all(self, text: str) -> Dict[str, List[Tuple[str, int, int, float]]]:
        """모든 한국어 PII 검증"""
        results = {
            "names": self.validate_korean_name(text),
            "phones": self.validate_korean_phone(text),
            "ssns": self.validate_korean_ssn(text),
            "emails": self.validate_korean_email(text),
            "credit_cards": self.validate_korean_credit_card(text),
            "addresses": self.validate_korean_address(text),
        }
        
        return results
