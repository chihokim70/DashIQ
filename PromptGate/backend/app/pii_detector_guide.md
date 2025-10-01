# PII Detector 구현 가이드

## 개요
PII (개인 식별 정보) 탐지기를 구현하기 위한 종합 가이드입니다. 오픈소스 도구와 자체 개발을 결합한 하이브리드 접근법을 제안합니다.

## 1. 오픈소스 도구 활용

### 1.1 Microsoft Presidio (권장)
**특징:**
- Microsoft에서 개발한 오픈소스 프레임워크
- 텍스트, 이미지, 구조화된 데이터에서 PII 탐지
- 마스킹, 익명화 기능 내장
- 사용자 정의 파이프라인 지원

**설치:**
```bash
pip install presidio-analyzer presidio-anonymizer presidio-image-redactor
```

**사용 예시:**
```python
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# PII 탐지
results = analyzer.analyze(text="My name is John Doe", language='en')

# 익명화
anonymized_text = anonymizer.anonymize(text="My name is John Doe", analyzer_results=results)
```

**장점:**
- 검증된 성능
- 다양한 PII 타입 지원
- 익명화 기능 내장
- 활발한 커뮤니티

**단점:**
- 한국어 지원 제한적
- 커스터마이징 복잡

### 1.2 spaCy (NLP 기반)
**특징:**
- 고성능 자연어 처리 라이브러리
- Named Entity Recognition (NER) 지원
- 한국어 모델 사용 가능

**설치:**
```bash
pip install spacy
python -m spacy download ko_core_news_sm  # 한국어 모델
python -m spacy download en_core_web_sm   # 영어 모델
```

**사용 예시:**
```python
import spacy

nlp = spacy.load("ko_core_news_sm")
doc = nlp("김철수는 서울에 살고 있습니다.")

for ent in doc.ents:
    print(f"{ent.text}: {ent.label_}")
```

**장점:**
- 빠른 처리 속도
- 정확한 NER
- 한국어 지원

**단점:**
- PII 전용 기능 없음
- 커스터마이징 필요

### 1.3 NLTK (자연어 처리)
**특징:**
- 포괄적인 자연어 처리 도구
- 교육용으로 널리 사용
- 다양한 언어 지원

**설치:**
```bash
pip install nltk
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('maxent_ne_chunker'); nltk.download('words')"
```

**사용 예시:**
```python
import nltk
from nltk import ne_chunk, pos_tag, word_tokenize

text = "John Doe lives in New York"
tokens = word_tokenize(text)
pos_tags = pos_tag(tokens)
named_entities = ne_chunk(pos_tags)
```

**장점:**
- 다양한 기능
- 교육 자료 풍부
- 무료

**단점:**
- 느린 처리 속도
- PII 전용 기능 없음

### 1.4 기타 오픈소스 도구

#### Octopii (이미지 PII 탐지)
- RedHunt Labs에서 개발
- OCR과 CNN 모델 활용
- 신분증, 여권, 신용카드 탐지

#### Tokern (데이터 웨어하우스)
- 데이터 카탈로그 통합
- 민감한 데이터 태깅
- Amundsen, Datahub 지원

## 2. 자체 개발 접근법

### 2.1 정규식 기반 패턴 매칭
**한국어 PII 패턴:**

```python
import re

# 주민등록번호
ssn_pattern = r"\b\d{6}-[1-4]\d{6}\b"

# 휴대폰 번호
phone_pattern = r"\b01[016789]-?\d{3,4}-?\d{4}\b"

# 이메일
email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"

# 신용카드 번호
credit_card_pattern = r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"
```

**장점:**
- 빠른 처리 속도
- 정확한 패턴 매칭
- 한국어 특화 가능

**단점:**
- 복잡한 패턴 처리 어려움
- 컨텍스트 인식 불가

### 2.2 머신러닝 기반 탐지
**BERT 기반 NER:**

```python
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline

tokenizer = AutoTokenizer.from_pretrained("klue/bert-base")
model = AutoModelForTokenClassification.from_pretrained("klue/bert-base")

ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer)
results = ner_pipeline("김철수는 서울에 살고 있습니다.")
```

**장점:**
- 높은 정확도
- 컨텍스트 인식
- 한국어 모델 사용 가능

**단점:**
- 느린 처리 속도
- 리소스 사용량 큼
- 학습 데이터 필요

### 2.3 하이브리드 접근법 (권장)
**다중 스캐너 통합:**

```python
class HybridPIIDetector:
    def __init__(self):
        self.regex_scanner = RegexPIIScanner()
        self.spacy_scanner = SpacyPIIScanner()
        self.presidio_scanner = PresidioPIIScanner()
        self.ml_scanner = MLPIIScanner()
    
    async def scan_text(self, text: str) -> PIIScanResult:
        # 1. 정규식 스캔 (빠른 1차 필터링)
        regex_results = await self.regex_scanner.scan(text)
        
        # 2. NLP 스캔 (컨텍스트 인식)
        nlp_results = await self.spacy_scanner.scan(text)
        
        # 3. Presidio 스캔 (검증된 탐지)
        presidio_results = await self.presidio_scanner.scan(text)
        
        # 4. ML 스캔 (고급 탐지)
        ml_results = await self.ml_scanner.scan(text)
        
        # 결과 통합 및 중복 제거
        return self._merge_results([regex_results, nlp_results, presidio_results, ml_results])
```

## 3. 구현 단계별 가이드

### 3.1 기본 구조 설계
```python
# 1. PII 타입 정의
class PIIType(Enum):
    NAME = "name"
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    # ... 기타 타입

# 2. 탐지 결과 구조
@dataclass
class PIIMatch:
    pii_type: PIIType
    confidence: float
    matched_text: str
    start_pos: int
    end_pos: int
    metadata: Dict[str, Any]

# 3. 스캔 결과 구조
@dataclass
class PIIScanResult:
    has_pii: bool
    pii_matches: List[PIIMatch]
    total_pii: int
    risk_score: float
    processing_time: float
```

### 3.2 패턴 매칭 구현
```python
class RegexPIIScanner:
    def __init__(self):
        self.patterns = {
            PIIType.SSN: [
                (r"\b\d{6}-[1-4]\d{6}\b", 0.9),
                (r"\b\d{6}[1-4]\d{6}\b", 0.8),
            ],
            PIIType.PHONE: [
                (r"\b01[016789]-?\d{3,4}-?\d{4}\b", 0.9),
                (r"\b0\d{1,2}-?\d{3,4}-?\d{4}\b", 0.7),
            ],
            # ... 기타 패턴
        }
    
    async def scan(self, text: str) -> List[PIIMatch]:
        matches = []
        for pii_type, patterns in self.patterns.items():
            for pattern, confidence in patterns:
                for match in re.finditer(pattern, text):
                    matches.append(PIIMatch(
                        pii_type=pii_type,
                        confidence=confidence,
                        matched_text=match.group(),
                        start_pos=match.start(),
                        end_pos=match.end()
                    ))
        return matches
```

### 3.3 NLP 기반 탐지 구현
```python
class SpacyPIIScanner:
    def __init__(self):
        try:
            self.nlp = spacy.load("ko_core_news_sm")
        except OSError:
            self.nlp = spacy.load("en_core_web_sm")
    
    async def scan(self, text: str) -> List[PIIMatch]:
        matches = []
        doc = self.nlp(text)
        
        for ent in doc.ents:
            pii_type = self._map_entity_to_pii_type(ent.label_)
            if pii_type != PIIType.UNKNOWN:
                matches.append(PIIMatch(
                    pii_type=pii_type,
                    confidence=ent._.prob if hasattr(ent._, 'prob') else 0.5,
                    matched_text=ent.text,
                    start_pos=ent.start_char,
                    end_pos=ent.end_char
                ))
        
        return matches
```

### 3.4 결과 통합 및 중복 제거
```python
class PIIDetector:
    def __init__(self):
        self.scanners = [
            RegexPIIScanner(),
            SpacyPIIScanner(),
            PresidioPIIScanner(),
        ]
    
    async def scan_text(self, text: str) -> PIIScanResult:
        all_matches = []
        
        # 모든 스캐너 실행
        for scanner in self.scanners:
            matches = await scanner.scan(text)
            all_matches.extend(matches)
        
        # 중복 제거
        unique_matches = self._deduplicate_matches(all_matches)
        
        # 위험 점수 계산
        risk_score = self._calculate_risk_score(unique_matches)
        
        return PIIScanResult(
            has_pii=len(unique_matches) > 0,
            pii_matches=unique_matches,
            total_pii=len(unique_matches),
            risk_score=risk_score,
            processing_time=time.time() - start_time
        )
    
    def _deduplicate_matches(self, matches: List[PIIMatch]) -> List[PIIMatch]:
        # 위치 기반 중복 제거
        unique_matches = []
        seen_positions = set()
        
        for match in matches:
            position_key = (match.start_pos, match.end_pos, match.pii_type)
            if position_key not in seen_positions:
                seen_positions.add(position_key)
                unique_matches.append(match)
        
        return unique_matches
```

## 4. 성능 최적화

### 4.1 비동기 처리
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncPIIDetector:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def scan_text(self, text: str) -> PIIScanResult:
        # 병렬 스캔
        tasks = [
            self._scan_with_regex(text),
            self._scan_with_spacy(text),
            self._scan_with_presidio(text),
        ]
        
        results = await asyncio.gather(*tasks)
        return self._merge_results(results)
```

### 4.2 캐싱
```python
from functools import lru_cache
import hashlib

class CachedPIIDetector:
    def __init__(self):
        self.cache = {}
    
    @lru_cache(maxsize=1000)
    def _get_text_hash(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()
    
    async def scan_text(self, text: str) -> PIIScanResult:
        text_hash = self._get_text_hash(text)
        
        if text_hash in self.cache:
            return self.cache[text_hash]
        
        result = await self._perform_scan(text)
        self.cache[text_hash] = result
        
        return result
```

### 4.3 배치 처리
```python
class BatchPIIDetector:
    async def scan_batch(self, texts: List[str]) -> List[PIIScanResult]:
        # 배치 크기 제한
        batch_size = 100
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_results = await asyncio.gather(*[
                self.scan_text(text) for text in batch
            ])
            results.extend(batch_results)
        
        return results
```

## 5. 테스트 및 검증

### 5.1 단위 테스트
```python
import pytest

class TestPIIDetector:
    def test_ssn_detection(self):
        detector = PIIDetector()
        text = "주민등록번호는 123456-1234567입니다."
        result = asyncio.run(detector.scan_text(text))
        
        assert result.has_pii == True
        assert len(result.pii_matches) == 1
        assert result.pii_matches[0].pii_type == PIIType.SSN
    
    def test_phone_detection(self):
        detector = PIIDetector()
        text = "연락처는 010-1234-5678입니다."
        result = asyncio.run(detector.scan_text(text))
        
        assert result.has_pii == True
        assert result.pii_matches[0].pii_type == PIIType.PHONE
```

### 5.2 성능 테스트
```python
import time
import statistics

class PerformanceTest:
    async def test_scan_performance(self):
        detector = PIIDetector()
        test_texts = [
            "김철수는 010-1234-5678로 연락하세요.",
            "이메일은 kim@example.com입니다.",
            "주민등록번호는 123456-1234567입니다.",
        ]
        
        times = []
        for text in test_texts:
            start_time = time.time()
            result = await detector.scan_text(text)
            end_time = time.time()
            times.append(end_time - start_time)
        
        avg_time = statistics.mean(times)
        max_time = max(times)
        
        print(f"평균 처리 시간: {avg_time:.3f}초")
        print(f"최대 처리 시간: {max_time:.3f}초")
```

## 6. 배포 및 운영

### 6.1 Docker 컨테이너화
```dockerfile
FROM python:3.9-slim

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-kor \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
COPY requirements_pii.txt .
RUN pip install -r requirements_pii.txt

# spaCy 모델 다운로드
RUN python -m spacy download ko_core_news_sm
RUN python -m spacy download en_core_web_sm

# 애플리케이션 코드 복사
COPY app/ ./app/

# 실행
CMD ["python", "-m", "app.pii_detector"]
```

### 6.2 모니터링
```python
import logging
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge

# 메트릭 정의
pii_scan_counter = Counter('pii_scans_total', 'Total PII scans')
pii_detection_counter = Counter('pii_detections_total', 'Total PII detections', ['pii_type'])
pii_scan_duration = Histogram('pii_scan_duration_seconds', 'PII scan duration')
pii_risk_score = Gauge('pii_risk_score', 'PII risk score')

class MonitoredPIIDetector:
    async def scan_text(self, text: str) -> PIIScanResult:
        pii_scan_counter.inc()
        
        with pii_scan_duration.time():
            result = await self._perform_scan(text)
        
        # PII 타입별 카운트
        for match in result.pii_matches:
            pii_detection_counter.labels(pii_type=match.pii_type.value).inc()
        
        # 위험 점수 설정
        pii_risk_score.set(result.risk_score)
        
        return result
```

## 7. 결론 및 권장사항

### 7.1 구현 우선순위
1. **1단계**: 정규식 기반 기본 패턴 매칭
2. **2단계**: Presidio 통합
3. **3단계**: spaCy NER 추가
4. **4단계**: 머신러닝 모델 통합
5. **5단계**: 성능 최적화 및 모니터링

### 7.2 기술 스택 권장사항
- **핵심**: Python 3.9+, FastAPI
- **PII 탐지**: Presidio + spaCy + 정규식
- **한국어 처리**: KoNLPy, mecab-python3
- **성능**: asyncio, Redis 캐싱
- **모니터링**: Prometheus, Grafana

### 7.3 주의사항
- **개인정보보호법 준수**: 탐지된 PII는 즉시 마스킹/삭제
- **성능 최적화**: 대용량 데이터 처리 시 배치 처리 필수
- **정확도 검증**: 정기적인 테스트 데이터로 성능 평가
- **보안**: PII 데이터는 암호화하여 저장/전송

이 가이드를 참고하여 조직의 요구사항에 맞는 PII 탐지기를 구현하시기 바랍니다.

