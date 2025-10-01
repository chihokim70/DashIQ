"""
ML Classifier 구현
머신러닝 기반 프롬프트 위험도 분류기
"""

import asyncio
import logging
import time
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import os
import json
import pickle
from datetime import datetime

logger = logging.getLogger(__name__)

class RiskCategory(Enum):
    """위험도 카테고리"""
    SAFE = "safe"
    LOW_RISK = "low_risk"
    MEDIUM_RISK = "medium_risk"
    HIGH_RISK = "high_risk"
    CRITICAL = "critical"

class ThreatType(Enum):
    """위협 유형"""
    PROMPT_INJECTION = "prompt_injection"
    DATA_EXTRACTION = "data_extraction"
    ROLE_MANIPULATION = "role_manipulation"
    SYSTEM_BYPASS = "system_bypass"
    MALICIOUS_CODE = "malicious_code"
    SOCIAL_ENGINEERING = "social_engineering"
    UNKNOWN = "unknown"

@dataclass
class MLClassificationResult:
    """ML 분류 결과"""
    risk_category: RiskCategory
    risk_score: float
    threat_types: List[ThreatType]
    confidence: float
    processing_time: float
    model_used: str
    features_extracted: Dict[str, Any] = field(default_factory=dict)
    error_messages: List[str] = field(default_factory=list)

class MLClassifier:
    """머신러닝 기반 프롬프트 분류기"""
    
    def __init__(self):
        self.is_initialized = False
        self.models = {}
        self.vectorizer = None
        self.feature_extractors = {}
        
        # 모델 상태
        self.model_status = {
            "transformer_model": False,
            "traditional_model": False,
            "ensemble_model": False,
            "feature_extractor": False
        }
        
        # 초기화 시도
        self._initialize_models()
    
    def _initialize_models(self):
        """모델 초기화"""
        try:
            # 1. Transformer 모델 초기화
            self._initialize_transformer_model()
            
            # 2. 전통적인 ML 모델 초기화
            self._initialize_traditional_model()
            
            # 3. 특성 추출기 초기화
            self._initialize_feature_extractors()
            
            # 4. 앙상블 모델 초기화
            self._initialize_ensemble_model()
            
            self.is_initialized = any(self.model_status.values())
            
            if self.is_initialized:
                logger.info(f"ML Classifier 초기화 완료: {self.model_status}")
            else:
                logger.warning("ML Classifier 초기화 실패 - 모든 모델 로드 실패")
                
        except Exception as e:
            logger.error(f"ML Classifier 초기화 중 오류: {e}")
            self.is_initialized = False
    
    def _initialize_transformer_model(self):
        """Transformer 모델 초기화"""
        try:
            # Transformers 라이브러리 사용
            from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
            
            # 한국어 텍스트 분류 모델 (KLUE RoBERTa)
            model_name = "klue/roberta-base"
            
            self.models["transformer"] = pipeline(
                "text-classification",
                model=model_name,
                tokenizer=model_name,
                return_all_scores=True
            )
            
            self.model_status["transformer_model"] = True
            logger.info("Transformer 모델 초기화 성공")
            
        except ImportError:
            logger.warning("Transformers 라이브러리가 설치되지 않음")
        except Exception as e:
            logger.error(f"Transformer 모델 초기화 실패: {e}")
    
    def _initialize_traditional_model(self):
        """전통적인 ML 모델 초기화"""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.naive_bayes import MultinomialNB
            
            # TF-IDF 벡터화기
            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 3),
                stop_words=None,  # 한국어는 별도 처리
                min_df=2,
                max_df=0.95
            )
            
            # 랜덤 포레스트 분류기
            self.models["random_forest"] = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            
            # 나이브 베이즈 분류기
            self.models["naive_bayes"] = MultinomialNB(alpha=0.1)
            
            self.model_status["traditional_model"] = True
            logger.info("전통적인 ML 모델 초기화 성공")
            
        except ImportError:
            logger.warning("scikit-learn 라이브러리가 설치되지 않음")
        except Exception as e:
            logger.error(f"전통적인 ML 모델 초기화 실패: {e}")
    
    def _initialize_feature_extractors(self):
        """특성 추출기 초기화"""
        try:
            import re
            
            # 텍스트 특성 추출기
            self.feature_extractors["text_features"] = {
                "length": lambda text: len(text),
                "word_count": lambda text: len(text.split()),
                "sentence_count": lambda text: len(re.split(r'[.!?]+', text)),
                "has_numbers": lambda text: bool(re.search(r'\d', text)),
                "has_special_chars": lambda text: bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', text)),
                "has_uppercase": lambda text: bool(re.search(r'[A-Z]', text)),
                "has_lowercase": lambda text: bool(re.search(r'[a-z]', text)),
                "has_korean": lambda text: bool(re.search(r'[가-힣]', text)),
                "has_english": lambda text: bool(re.search(r'[a-zA-Z]', text)),
                "avg_word_length": lambda text: np.mean([len(word) for word in text.split()]) if text.split() else 0
            }
            
            # 악의적 패턴 특성 추출기
            self.feature_extractors["malicious_patterns"] = {
                "ignore_instructions": lambda text: len(re.findall(r'ignore.*instructions?', text, re.IGNORECASE)),
                "forget_everything": lambda text: len(re.findall(r'forget.*everything', text, re.IGNORECASE)),
                "system_prompt": lambda text: len(re.findall(r'system.*prompt', text, re.IGNORECASE)),
                "role_play": lambda text: len(re.findall(r'role.*play|pretend.*to.*be', text, re.IGNORECASE)),
                "jailbreak": lambda text: len(re.findall(r'jailbreak|bypass', text, re.IGNORECASE)),
                "admin_access": lambda text: len(re.findall(r'admin|root|sudo', text, re.IGNORECASE)),
                "code_execution": lambda text: len(re.findall(r'execute|run.*code|eval', text, re.IGNORECASE)),
                "data_extraction": lambda text: len(re.findall(r'show.*all|list.*all|dump.*data', text, re.IGNORECASE))
            }
            
            self.model_status["feature_extractor"] = True
            logger.info("특성 추출기 초기화 성공")
            
        except Exception as e:
            logger.error(f"특성 추출기 초기화 실패: {e}")
    
    def _initialize_ensemble_model(self):
        """앙상블 모델 초기화"""
        try:
            # 가중치 기반 앙상블
            self.models["ensemble"] = {
                "weights": {
                    "transformer": 0.6,
                    "random_forest": 0.25,
                    "naive_bayes": 0.15
                },
                "thresholds": {
                    "safe": 0.2,
                    "low_risk": 0.4,
                    "medium_risk": 0.6,
                    "high_risk": 0.8,
                    "critical": 0.9
                }
            }
            
            self.model_status["ensemble_model"] = True
            logger.info("앙상블 모델 초기화 성공")
            
        except Exception as e:
            logger.error(f"앙상블 모델 초기화 실패: {e}")
    
    async def classify_prompt(self, prompt: str) -> MLClassificationResult:
        """프롬프트 분류"""
        start_time = time.time()
        
        try:
            # 1. 특성 추출
            features = self._extract_features(prompt)
            
            # 2. 모델별 예측
            predictions = {}
            
            # Transformer 모델 예측
            if self.model_status["transformer_model"]:
                predictions["transformer"] = await self._predict_with_transformer(prompt)
            
            # 전통적인 ML 모델 예측
            if self.model_status["traditional_model"]:
                predictions["traditional"] = await self._predict_with_traditional_ml(prompt, features)
            
            # 3. 앙상블 예측
            if self.model_status["ensemble_model"]:
                ensemble_result = self._ensemble_predictions(predictions)
            else:
                # 단일 모델 결과 사용
                ensemble_result = self._get_best_prediction(predictions)
            
            processing_time = time.time() - start_time
            
            return MLClassificationResult(
                risk_category=ensemble_result["risk_category"],
                risk_score=ensemble_result["risk_score"],
                threat_types=ensemble_result["threat_types"],
                confidence=ensemble_result["confidence"],
                processing_time=processing_time,
                model_used=ensemble_result["model_used"],
                features_extracted=features
            )
            
        except Exception as e:
            logger.error(f"프롬프트 분류 실패: {e}")
            return MLClassificationResult(
                risk_category=RiskCategory.UNKNOWN,
                risk_score=0.0,
                threat_types=[ThreatType.UNKNOWN],
                confidence=0.0,
                processing_time=time.time() - start_time,
                model_used="error",
                error_messages=[str(e)]
            )
    
    def _extract_features(self, prompt: str) -> Dict[str, Any]:
        """특성 추출"""
        features = {}
        
        # 텍스트 특성 추출
        if "text_features" in self.feature_extractors:
            for name, extractor in self.feature_extractors["text_features"].items():
                try:
                    features[f"text_{name}"] = extractor(prompt)
                except Exception as e:
                    features[f"text_{name}"] = 0
                    logger.warning(f"텍스트 특성 추출 실패 ({name}): {e}")
        
        # 악의적 패턴 특성 추출
        if "malicious_patterns" in self.feature_extractors:
            for name, extractor in self.feature_extractors["malicious_patterns"].items():
                try:
                    features[f"pattern_{name}"] = extractor(prompt)
                except Exception as e:
                    features[f"pattern_{name}"] = 0
                    logger.warning(f"패턴 특성 추출 실패 ({name}): {e}")
        
        return features
    
    async def _predict_with_transformer(self, prompt: str) -> Dict[str, Any]:
        """Transformer 모델로 예측"""
        try:
            # 실제 구현에서는 사전 훈련된 모델 사용
            # 여기서는 시뮬레이션
            await asyncio.sleep(0.1)  # 비동기 처리 시뮬레이션
            
            # 간단한 휴리스틱 기반 예측 (실제로는 모델 예측)
            risk_score = self._calculate_heuristic_risk_score(prompt)
            
            return {
                "risk_score": risk_score,
                "confidence": 0.8,
                "model": "transformer"
            }
            
        except Exception as e:
            logger.error(f"Transformer 예측 실패: {e}")
            return {"risk_score": 0.0, "confidence": 0.0, "model": "transformer"}
    
    async def _predict_with_traditional_ml(self, prompt: str, features: Dict[str, Any]) -> Dict[str, Any]:
        """전통적인 ML 모델로 예측"""
        try:
            # 실제 구현에서는 훈련된 모델 사용
            # 여기서는 시뮬레이션
            await asyncio.sleep(0.05)
            
            # 특성 기반 위험도 계산
            risk_score = self._calculate_feature_based_risk_score(features)
            
            return {
                "risk_score": risk_score,
                "confidence": 0.7,
                "model": "traditional"
            }
            
        except Exception as e:
            logger.error(f"전통적인 ML 예측 실패: {e}")
            return {"risk_score": 0.0, "confidence": 0.0, "model": "traditional"}
    
    def _calculate_heuristic_risk_score(self, prompt: str) -> float:
        """휴리스틱 기반 위험도 점수 계산"""
        import re
        
        risk_indicators = [
            (r'ignore.*instructions?', 0.3),
            (r'forget.*everything', 0.3),
            (r'system.*prompt', 0.2),
            (r'role.*play', 0.2),
            (r'jailbreak', 0.4),
            (r'admin|root|sudo', 0.3),
            (r'execute|run.*code', 0.4),
            (r'show.*all|list.*all', 0.3),
            (r'bypass.*security', 0.4),
            (r'override.*system', 0.3)
        ]
        
        total_score = 0.0
        for pattern, weight in risk_indicators:
            matches = len(re.findall(pattern, prompt, re.IGNORECASE))
            total_score += matches * weight
        
        return min(total_score, 1.0)
    
    def _calculate_feature_based_risk_score(self, features: Dict[str, Any]) -> float:
        """특성 기반 위험도 점수 계산"""
        score = 0.0
        
        # 패턴 특성 가중치
        pattern_weights = {
            "pattern_ignore_instructions": 0.3,
            "pattern_forget_everything": 0.3,
            "pattern_system_prompt": 0.2,
            "pattern_role_play": 0.2,
            "pattern_jailbreak": 0.4,
            "pattern_admin_access": 0.3,
            "pattern_code_execution": 0.4,
            "pattern_data_extraction": 0.3
        }
        
        for feature_name, weight in pattern_weights.items():
            if feature_name in features:
                score += features[feature_name] * weight
        
        return min(score, 1.0)
    
    def _ensemble_predictions(self, predictions: Dict[str, Any]) -> Dict[str, Any]:
        """앙상블 예측"""
        if not predictions:
            return {
                "risk_category": RiskCategory.UNKNOWN,
                "risk_score": 0.0,
                "threat_types": [ThreatType.UNKNOWN],
                "confidence": 0.0,
                "model_used": "ensemble"
            }
        
        # 가중 평균 계산
        weights = self.models["ensemble"]["weights"]
        total_score = 0.0
        total_confidence = 0.0
        total_weight = 0.0
        
        for model_name, prediction in predictions.items():
            if model_name in weights:
                weight = weights[model_name]
                total_score += prediction["risk_score"] * weight
                total_confidence += prediction["confidence"] * weight
                total_weight += weight
        
        if total_weight > 0:
            final_score = total_score / total_weight
            final_confidence = total_confidence / total_weight
        else:
            final_score = 0.0
            final_confidence = 0.0
        
        # 위험도 카테고리 결정
        thresholds = self.models["ensemble"]["thresholds"]
        risk_category = self._determine_risk_category(final_score, thresholds)
        
        # 위협 유형 결정
        threat_types = self._determine_threat_types(final_score)
        
        return {
            "risk_category": risk_category,
            "risk_score": final_score,
            "threat_types": threat_types,
            "confidence": final_confidence,
            "model_used": "ensemble"
        }
    
    def _get_best_prediction(self, predictions: Dict[str, Any]) -> Dict[str, Any]:
        """최고 신뢰도 예측 선택"""
        if not predictions:
            return {
                "risk_category": RiskCategory.UNKNOWN,
                "risk_score": 0.0,
                "threat_types": [ThreatType.UNKNOWN],
                "confidence": 0.0,
                "model_used": "none"
            }
        
        # 가장 높은 신뢰도 모델 선택
        best_model = max(predictions.keys(), key=lambda k: predictions[k]["confidence"])
        prediction = predictions[best_model]
        
        risk_category = self._determine_risk_category(prediction["risk_score"])
        threat_types = self._determine_threat_types(prediction["risk_score"])
        
        return {
            "risk_category": risk_category,
            "risk_score": prediction["risk_score"],
            "threat_types": threat_types,
            "confidence": prediction["confidence"],
            "model_used": best_model
        }
    
    def _determine_risk_category(self, risk_score: float, thresholds: Optional[Dict] = None) -> RiskCategory:
        """위험도 카테고리 결정"""
        if thresholds is None:
            thresholds = {
                "safe": 0.2,
                "low_risk": 0.4,
                "medium_risk": 0.6,
                "high_risk": 0.8,
                "critical": 0.9
            }
        
        if risk_score >= thresholds["critical"]:
            return RiskCategory.CRITICAL
        elif risk_score >= thresholds["high_risk"]:
            return RiskCategory.HIGH_RISK
        elif risk_score >= thresholds["medium_risk"]:
            return RiskCategory.MEDIUM_RISK
        elif risk_score >= thresholds["low_risk"]:
            return RiskCategory.LOW_RISK
        else:
            return RiskCategory.SAFE
    
    def _determine_threat_types(self, risk_score: float) -> List[ThreatType]:
        """위협 유형 결정"""
        threat_types = []
        
        if risk_score >= 0.8:
            threat_types.extend([
                ThreatType.PROMPT_INJECTION,
                ThreatType.SYSTEM_BYPASS,
                ThreatType.MALICIOUS_CODE
            ])
        elif risk_score >= 0.6:
            threat_types.extend([
                ThreatType.PROMPT_INJECTION,
                ThreatType.ROLE_MANIPULATION
            ])
        elif risk_score >= 0.4:
            threat_types.append(ThreatType.SOCIAL_ENGINEERING)
        elif risk_score >= 0.2:
            threat_types.append(ThreatType.DATA_EXTRACTION)
        
        return threat_types if threat_types else [ThreatType.UNKNOWN]
    
    def get_status(self) -> Dict[str, Any]:
        """ML Classifier 상태 조회"""
        return {
            "initialized": self.is_initialized,
            "model_status": self.model_status,
            "available_models": list(self.models.keys()),
            "feature_extractors": list(self.feature_extractors.keys()),
            "timestamp": datetime.now().isoformat()
        }

# 싱글톤 패턴을 위한 전역 변수
_ml_classifier_instance: Optional[MLClassifier] = None

async def get_ml_classifier() -> MLClassifier:
    """ML Classifier 싱글톤 인스턴스 반환"""
    global _ml_classifier_instance
    
    if _ml_classifier_instance is None:
        _ml_classifier_instance = MLClassifier()
        logger.info("ML Classifier 싱글톤 인스턴스 생성 완료")
    
    return _ml_classifier_instance

async def close_ml_classifier():
    """ML Classifier 정리"""
    global _ml_classifier_instance
    
    if _ml_classifier_instance:
        logger.info("ML Classifier 정리 완료")
        _ml_classifier_instance = None
