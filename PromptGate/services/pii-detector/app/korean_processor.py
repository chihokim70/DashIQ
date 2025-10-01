"""
가벼운 한국어 처리 모듈
Konlpy 기반으로 spaCy 없이 한국어 엔티티 추출
"""

import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class KoreanEntityType(Enum):
    """한국어 엔티티 타입"""
    PERSON = "person"           # 인명
    ORGANIZATION = "organization"  # 기관/회사
    LOCATION = "location"       # 장소
    DATE = "date"              # 날짜
    TIME = "time"              # 시간
    MONEY = "money"            # 금액
    PERCENT = "percent"        # 퍼센트
    UNKNOWN = "unknown"        # 알 수 없음

@dataclass
class KoreanEntity:
    """한국어 엔티티 정보"""
    entity_type: KoreanEntityType
    text: str
    start_pos: int
    end_pos: int
    confidence: float
    metadata: Dict[str, Any] = None

class LightweightKoreanProcessor:
    """가벼운 한국어 처리기 - Konlpy 기반"""
    
    def __init__(self):
        self.okt = None
        self.korean_surnames = self._init_korean_surnames()
        self.korean_organizations = self._init_korean_organizations()
        self.korean_locations = self._init_korean_locations()
        self._initialize_konlpy()
    
    def _initialize_konlpy(self):
        """Konlpy 초기화"""
        try:
            from konlpy.tag import Okt
            self.okt = Okt()
            logger.info("Konlpy Okt 초기화 성공")
        except ImportError:
            logger.warning("Konlpy 설치되지 않음. 한국어 처리 기능 제한됨")
            self.okt = None
        except Exception as e:
            logger.error(f"Konlpy 초기화 실패: {e}")
            self.okt = None
    
    def _init_korean_surnames(self) -> set:
        """한국 성씨 목록 초기화"""
        return {
            "김", "이", "박", "최", "정", "강", "조", "윤", "장", "임", "한", "오", "서", "신", "권", "황", "안", "송", "전", "고",
            "문", "양", "손", "배", "조", "백", "허", "유", "남", "심", "노", "정", "하", "곽", "성", "차", "주", "우", "구", "나",
            "신", "엄", "원", "천", "방", "공", "강", "현", "함", "변", "염", "여", "추", "노", "도", "소", "석", "선", "설", "마",
            "길", "연", "위", "표", "명", "기", "반", "금", "옥", "육", "인", "맹", "제", "모", "장", "남", "탁", "국", "여", "진",
            "어", "은", "편", "구", "용", "예", "경", "나", "동", "감", "봉", "사", "부", "지", "엄", "채", "최", "계", "피", "두",
            "복", "옹", "음", "빈", "동", "온", "단", "전", "화", "초", "호", "범", "위", "만", "유", "여", "남", "궉", "봉", "황",
            "간", "점", "영", "남", "궁", "팽", "윤", "나", "남", "궉", "봉", "황", "간", "점", "영", "남", "궁", "팽", "윤"
        }
    
    def _init_korean_organizations(self) -> set:
        """한국 기관/회사명 패턴 초기화"""
        return {
            "회사", "기업", "법인", "주식회사", "유한회사", "합자회사", "합명회사",
            "학교", "대학교", "고등학교", "중학교", "초등학교", "유치원",
            "병원", "의원", "클리닉", "센터", "연구소", "연구원",
            "은행", "증권", "보험", "카드", "금융", "투자",
            "정부", "청", "부", "처", "원", "위원회", "공단", "공사",
            "시", "도", "구", "군", "동", "리", "읍", "면"
        }
    
    def _init_korean_locations(self) -> set:
        """한국 지역명 초기화"""
        return {
            "서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
            "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주",
            "종로구", "중구", "용산구", "성동구", "광진구", "동대문구", "중랑구",
            "성북구", "강북구", "도봉구", "노원구", "은평구", "서대문구", "마포구",
            "양천구", "강서구", "구로구", "금천구", "영등포구", "동작구", "관악구",
            "서초구", "강남구", "송파구", "강동구"
        }
    
    def extract_korean_entities(self, text: str) -> List[KoreanEntity]:
        """한국어 엔티티 추출"""
        entities = []
        
        if not self.okt:
            logger.warning("Konlpy가 초기화되지 않음. 기본 패턴 매칭만 사용")
            return self._extract_with_patterns(text)
        
        try:
            # 1. Konlpy 기반 엔티티 추출
            konlpy_entities = self._extract_with_konlpy(text)
            entities.extend(konlpy_entities)
            
            # 2. 패턴 기반 엔티티 추출 (보완)
            pattern_entities = self._extract_with_patterns(text)
            entities.extend(pattern_entities)
            
            # 3. 중복 제거 및 정렬
            entities = self._deduplicate_entities(entities)
            entities.sort(key=lambda x: x.start_pos)
            
            logger.debug(f"한국어 엔티티 추출 완료: {len(entities)}개")
            
        except Exception as e:
            logger.error(f"한국어 엔티티 추출 실패: {e}")
            # 실패 시 패턴 기반 추출만 사용
            entities = self._extract_with_patterns(text)
        
        return entities
    
    def _extract_with_konlpy(self, text: str) -> List[KoreanEntity]:
        """Konlpy를 사용한 엔티티 추출"""
        entities = []
        
        try:
            # 형태소 분석
            morphs = self.okt.morphs(text)
            pos_tags = self.okt.pos(text)
            
            # 명사 추출
            nouns = self.okt.nouns(text)
            
            # 인명 추출
            person_entities = self._extract_persons_from_nouns(nouns, text)
            entities.extend(person_entities)
            
            # 기관명 추출
            org_entities = self._extract_organizations_from_nouns(nouns, text)
            entities.extend(org_entities)
            
            # 장소명 추출
            location_entities = self._extract_locations_from_nouns(nouns, text)
            entities.extend(location_entities)
            
            # 날짜/시간 추출
            datetime_entities = self._extract_datetime_from_pos(pos_tags, text)
            entities.extend(datetime_entities)
            
            # 금액 추출
            money_entities = self._extract_money_from_pos(pos_tags, text)
            entities.extend(money_entities)
            
        except Exception as e:
            logger.error(f"Konlpy 엔티티 추출 실패: {e}")
        
        return entities
    
    def _extract_persons_from_nouns(self, nouns: List[str], text: str) -> List[KoreanEntity]:
        """명사에서 인명 추출"""
        entities = []
        
        for noun in nouns:
            if self._is_potential_korean_name(noun):
                # 텍스트에서 위치 찾기
                start_pos = text.find(noun)
                if start_pos != -1:
                    entity = KoreanEntity(
                        entity_type=KoreanEntityType.PERSON,
                        text=noun,
                        start_pos=start_pos,
                        end_pos=start_pos + len(noun),
                        confidence=self._calculate_name_confidence(noun),
                        metadata={"extraction_method": "konlpy_nouns"}
                    )
                    entities.append(entity)
        
        return entities
    
    def _is_potential_korean_name(self, word: str) -> bool:
        """한국 이름 가능성 체크"""
        if len(word) < 2 or len(word) > 4:
            return False
        
        # 한국어 문자만 포함
        if not all(ord(c) >= 0xAC00 and ord(c) <= 0xD7A3 for c in word):
            return False
        
        # 성씨 체크
        if word[0] in self.korean_surnames:
            return True
        
        # 일반적인 이름 패턴 체크
        if len(word) == 2 and word[0] in self.korean_surnames:
            return True
        
        return False
    
    def _calculate_name_confidence(self, name: str) -> float:
        """이름 신뢰도 계산"""
        confidence = 0.5  # 기본 신뢰도
        
        # 성씨 매칭
        if name[0] in self.korean_surnames:
            confidence += 0.3
        
        # 길이 기반 조정
        if 2 <= len(name) <= 3:
            confidence += 0.1
        elif len(name) == 4:
            confidence += 0.05
        
        # 숫자나 특수문자 포함 시 감소
        if re.search(r'[0-9\W]', name):
            confidence -= 0.3
        
        return min(confidence, 1.0)
    
    def _extract_organizations_from_nouns(self, nouns: List[str], text: str) -> List[KoreanEntity]:
        """명사에서 기관명 추출"""
        entities = []
        
        for noun in nouns:
            if self._is_potential_organization(noun):
                start_pos = text.find(noun)
                if start_pos != -1:
                    entity = KoreanEntity(
                        entity_type=KoreanEntityType.ORGANIZATION,
                        text=noun,
                        start_pos=start_pos,
                        end_pos=start_pos + len(noun),
                        confidence=self._calculate_org_confidence(noun),
                        metadata={"extraction_method": "konlpy_nouns"}
                    )
                    entities.append(entity)
        
        return entities
    
    def _is_potential_organization(self, word: str) -> bool:
        """기관명 가능성 체크"""
        # 기관명 키워드 포함 체크
        for org_keyword in self.korean_organizations:
            if org_keyword in word:
                return True
        
        # 길이 체크 (기관명은 보통 3글자 이상)
        if len(word) >= 3:
            return True
        
        return False
    
    def _calculate_org_confidence(self, org: str) -> float:
        """기관명 신뢰도 계산"""
        confidence = 0.4  # 기본 신뢰도
        
        # 기관명 키워드 매칭
        for keyword in self.korean_organizations:
            if keyword in org:
                confidence += 0.2
                break
        
        # 길이 기반 조정
        if len(org) >= 4:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _extract_locations_from_nouns(self, nouns: List[str], text: str) -> List[KoreanEntity]:
        """명사에서 장소명 추출"""
        entities = []
        
        for noun in nouns:
            if self._is_potential_location(noun):
                start_pos = text.find(noun)
                if start_pos != -1:
                    entity = KoreanEntity(
                        entity_type=KoreanEntityType.LOCATION,
                        text=noun,
                        start_pos=start_pos,
                        end_pos=start_pos + len(noun),
                        confidence=self._calculate_location_confidence(noun),
                        metadata={"extraction_method": "konlpy_nouns"}
                    )
                    entities.append(entity)
        
        return entities
    
    def _is_potential_location(self, word: str) -> bool:
        """장소명 가능성 체크"""
        # 지역명 키워드 포함 체크
        for location in self.korean_locations:
            if location in word:
                return True
        
        # 구/군/시 키워드 체크
        if any(keyword in word for keyword in ["구", "군", "시", "동", "로", "길"]):
            return True
        
        return False
    
    def _calculate_location_confidence(self, location: str) -> float:
        """장소명 신뢰도 계산"""
        confidence = 0.4  # 기본 신뢰도
        
        # 지역명 키워드 매칭
        for keyword in self.korean_locations:
            if keyword in location:
                confidence += 0.3
                break
        
        # 구/군/시 키워드 매칭
        if any(keyword in location for keyword in ["구", "군", "시", "동", "로", "길"]):
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _extract_datetime_from_pos(self, pos_tags: List[Tuple[str, str]], text: str) -> List[KoreanEntity]:
        """품사 태그에서 날짜/시간 추출"""
        entities = []
        
        # 날짜 패턴
        date_patterns = [
            r'\d{4}년\s*\d{1,2}월\s*\d{1,2}일',
            r'\d{1,2}월\s*\d{1,2}일',
            r'\d{4}-\d{1,2}-\d{1,2}',
            r'\d{1,2}/\d{1,2}/\d{4}',
        ]
        
        for pattern in date_patterns:
            for match in re.finditer(pattern, text):
                entity = KoreanEntity(
                    entity_type=KoreanEntityType.DATE,
                    text=match.group(),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.8,
                    metadata={"extraction_method": "regex_pattern"}
                )
                entities.append(entity)
        
        # 시간 패턴
        time_patterns = [
            r'\d{1,2}시\s*\d{1,2}분',
            r'\d{1,2}:\d{1,2}',
            r'\d{1,2}시',
        ]
        
        for pattern in time_patterns:
            for match in re.finditer(pattern, text):
                entity = KoreanEntity(
                    entity_type=KoreanEntityType.TIME,
                    text=match.group(),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.7,
                    metadata={"extraction_method": "regex_pattern"}
                )
                entities.append(entity)
        
        return entities
    
    def _extract_money_from_pos(self, pos_tags: List[Tuple[str, str]], text: str) -> List[KoreanEntity]:
        """품사 태그에서 금액 추출"""
        entities = []
        
        # 금액 패턴
        money_patterns = [
            r'\d+원',
            r'\d+,\d+원',
            r'\d+만원',
            r'\d+억원',
            r'\d+천원',
            r'\$?\d+\.?\d*',
        ]
        
        for pattern in money_patterns:
            for match in re.finditer(pattern, text):
                entity = KoreanEntity(
                    entity_type=KoreanEntityType.MONEY,
                    text=match.group(),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.8,
                    metadata={"extraction_method": "regex_pattern"}
                )
                entities.append(entity)
        
        return entities
    
    def _extract_with_patterns(self, text: str) -> List[KoreanEntity]:
        """패턴 기반 엔티티 추출 (Konlpy 없이)"""
        entities = []
        
        # 인명 패턴
        name_patterns = [
            r'\b[가-힣]{2,4}(씨|님|선생님|교수님|부장님|과장님|대리님)\b',
            r'\b(성함|이름|성명)\s*[:：]\s*[가-힣]{2,4}\b',
        ]
        
        for pattern in name_patterns:
            for match in re.finditer(pattern, text):
                entity = KoreanEntity(
                    entity_type=KoreanEntityType.PERSON,
                    text=match.group(),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.7,
                    metadata={"extraction_method": "regex_pattern"}
                )
                entities.append(entity)
        
        # 기관명 패턴
        org_patterns = [
            r'\b[가-힣]+(회사|기업|법인|학교|병원|은행|정부|청|부|처|원)\b',
        ]
        
        for pattern in org_patterns:
            for match in re.finditer(pattern, text):
                entity = KoreanEntity(
                    entity_type=KoreanEntityType.ORGANIZATION,
                    text=match.group(),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.6,
                    metadata={"extraction_method": "regex_pattern"}
                )
                entities.append(entity)
        
        # 장소명 패턴
        location_patterns = [
            r'\b(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)\s+[가-힣\s\d-]+\b',
        ]
        
        for pattern in location_patterns:
            for match in re.finditer(pattern, text):
                entity = KoreanEntity(
                    entity_type=KoreanEntityType.LOCATION,
                    text=match.group(),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.8,
                    metadata={"extraction_method": "regex_pattern"}
                )
                entities.append(entity)
        
        return entities
    
    def _deduplicate_entities(self, entities: List[KoreanEntity]) -> List[KoreanEntity]:
        """중복 엔티티 제거"""
        unique_entities = []
        seen = set()
        
        for entity in entities:
            key = (entity.entity_type, entity.start_pos, entity.end_pos)
            if key not in seen:
                unique_entities.append(entity)
                seen.add(key)
        
        return unique_entities
    
    def get_entity_summary(self, entities: List[KoreanEntity]) -> Dict[str, Any]:
        """엔티티 요약 정보"""
        summary = {
            "total_entities": len(entities),
            "entity_types": {},
            "extraction_methods": {},
            "confidence_distribution": {
                "high": 0,
                "medium": 0,
                "low": 0
            }
        }
        
        for entity in entities:
            # 엔티티 타입별 카운트
            entity_type = entity.entity_type.value
            summary["entity_types"][entity_type] = summary["entity_types"].get(entity_type, 0) + 1
            
            # 추출 방법별 카운트
            method = entity.metadata.get("extraction_method", "unknown")
            summary["extraction_methods"][method] = summary["extraction_methods"].get(method, 0) + 1
            
            # 신뢰도 분포
            if entity.confidence >= 0.8:
                summary["confidence_distribution"]["high"] += 1
            elif entity.confidence >= 0.6:
                summary["confidence_distribution"]["medium"] += 1
            else:
                summary["confidence_distribution"]["low"] += 1
        
        return summary
