"""
고급 Secret Scanner 구현
TruffleHog, Gitleaks, detect-secrets 통합
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

# Secret Scanner 라이브러리 import
try:
    import trufflehog
    TRUFFLEHOG_AVAILABLE = True
except ImportError:
    logging.warning("TruffleHog를 찾을 수 없습니다. 기본 탐지 모드로 작동합니다.")
    TRUFFLEHOG_AVAILABLE = False

try:
    import gitleaks
    GITLEAKS_AVAILABLE = True
except ImportError:
    logging.warning("Gitleaks를 찾을 수 없습니다. 기본 탐지 모드로 작동합니다.")
    GITLEAKS_AVAILABLE = False

try:
    from detect_secrets import scan
    DETECT_SECRETS_AVAILABLE = True
except ImportError:
    logging.warning("detect-secrets를 찾을 수 없습니다. 기본 탐지 모드로 작동합니다.")
    DETECT_SECRETS_AVAILABLE = False

try:
    import ahocorasick
    AHOCORASICK_AVAILABLE = True
except ImportError:
    logging.warning("pyahocorasick를 찾을 수 없습니다. 기본 탐지 모드로 작동합니다.")
    AHOCORASICK_AVAILABLE = False

logger = logging.getLogger(__name__)

class SecretType(Enum):
    API_KEY = "api_key"
    PASSWORD = "password"
    TOKEN = "token"
    PRIVATE_KEY = "private_key"
    CERTIFICATE = "certificate"
    DATABASE_URL = "database_url"
    CLOUD_CREDENTIALS = "cloud_credentials"
    CRYPTOGRAPHIC_KEY = "cryptographic_key"
    UNKNOWN = "unknown"

class SecretSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecretMatch:
    secret_type: SecretType
    severity: SecretSeverity
    pattern: str
    matched_text: str
    start_pos: int
    end_pos: int
    confidence: float
    scanner: str
    context: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SecretScanResult:
    has_secrets: bool = False
    secrets: List[SecretMatch] = field(default_factory=list)
    total_secrets: int = 0
    high_risk_secrets: int = 0
    processing_time: float = 0.0
    scanner_status: Dict[str, bool] = field(default_factory=dict)
    error_messages: List[str] = field(default_factory=list)

class SecretPattern:
    """시크릿 패턴 정의"""
    
    PATTERNS = {
        SecretType.API_KEY: [
            # AWS Access Key
            (r"AKIA[0-9A-Z]{16}", SecretSeverity.HIGH),
            # OpenAI API Key
            (r"sk-[a-zA-Z0-9]{48}", SecretSeverity.HIGH),
            # Google API Key
            (r"AIza[0-9A-Za-z\\-_]{35}", SecretSeverity.HIGH),
            # GitHub Token
            (r"ghp_[a-zA-Z0-9]{36}", SecretSeverity.HIGH),
            # Generic API Key
            (r"api[_-]?key[_-]?[=:]\s*['\"]?[a-zA-Z0-9]{20,}['\"]?", SecretSeverity.MEDIUM),
        ],
        SecretType.PASSWORD: [
            # Password in connection strings
            (r"password[=:]\s*['\"]?[^\\s]{8,}['\"]?", SecretSeverity.HIGH),
            (r"pwd[=:]\s*['\"]?[^\\s]{8,}['\"]?", SecretSeverity.HIGH),
            # Basic auth
            (r"://[^:]+:[^@]+@", SecretSeverity.HIGH),
        ],
        SecretType.TOKEN: [
            # JWT Token
            (r"eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*", SecretSeverity.MEDIUM),
            # Bearer Token
            (r"Bearer\s+[a-zA-Z0-9\\-_]{20,}", SecretSeverity.MEDIUM),
            # OAuth Token
            (r"oauth[_-]?token[=:]\s*['\"]?[a-zA-Z0-9\\-_]{20,}['\"]?", SecretSeverity.MEDIUM),
        ],
        SecretType.PRIVATE_KEY: [
            # RSA Private Key
            (r"-----BEGIN RSA PRIVATE KEY-----", SecretSeverity.CRITICAL),
            # EC Private Key
            (r"-----BEGIN EC PRIVATE KEY-----", SecretSeverity.CRITICAL),
            # OpenSSH Private Key
            (r"-----BEGIN OPENSSH PRIVATE KEY-----", SecretSeverity.CRITICAL),
            # Generic Private Key
            (r"-----BEGIN PRIVATE KEY-----", SecretSeverity.CRITICAL),
        ],
        SecretType.DATABASE_URL: [
            # PostgreSQL
            (r"postgresql://[^:]+:[^@]+@[^/]+/[^\\s]+", SecretSeverity.HIGH),
            # MySQL
            (r"mysql://[^:]+:[^@]+@[^/]+/[^\\s]+", SecretSeverity.HIGH),
            # MongoDB
            (r"mongodb://[^:]+:[^@]+@[^/]+/[^\\s]+", SecretSeverity.HIGH),
            # Redis
            (r"redis://[^:]+:[^@]+@[^/]+/[^\\s]+", SecretSeverity.HIGH),
        ],
        SecretType.CLOUD_CREDENTIALS: [
            # Azure Service Principal
            (r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", SecretSeverity.HIGH),
            # Google Service Account
            (r'"type":\s*"service_account"', SecretSeverity.HIGH),
        ],
        SecretType.CRYPTOGRAPHIC_KEY: [
            # AES Key
            (r"[0-9a-fA-F]{32}", SecretSeverity.MEDIUM),
            # Base64 encoded key
            (r"[A-Za-z0-9+/]{40,}={0,2}", SecretSeverity.LOW),
        ]
    }

class AdvancedSecretScanner:
    """고급 Secret Scanner 클래스"""
    
    def __init__(self):
        self.patterns = SecretPattern.PATTERNS
        self.aho_corasick_tree = None
        self.scanner_status = {
            "trufflehog": TRUFFLEHOG_AVAILABLE,
            "gitleaks": GITLEAKS_AVAILABLE,
            "detect_secrets": DETECT_SECRETS_AVAILABLE,
            "ahocorasick": AHOCORASICK_AVAILABLE
        }
        
        # Aho-Corasick 트리 초기화
        if AHOCORASICK_AVAILABLE:
            self._build_aho_corasick_tree()
        
        logger.info(f"Secret Scanner 초기화 완료. 상태: {self.scanner_status}")
    
    def _build_aho_corasick_tree(self):
        """Aho-Corasick 트리 구축"""
        if not AHOCORASICK_AVAILABLE:
            return
        
        try:
            self.aho_corasick_tree = ahocorasick.Automaton()
            
            # 모든 패턴을 트리에 추가
            for secret_type, patterns in self.patterns.items():
                for pattern, severity in patterns:
                    # 간단한 키워드 추출 (정규식의 일부만)
                    keywords = self._extract_keywords(pattern)
                    for keyword in keywords:
                        self.aho_corasick_tree.add_word(keyword, (secret_type, pattern, severity))
            
            self.aho_corasick_tree.make_automaton()
            logger.info("Aho-Corasick 트리 구축 완료")
            
        except Exception as e:
            logger.error(f"Aho-Corasick 트리 구축 실패: {e}")
            self.aho_corasick_tree = None
    
    def _extract_keywords(self, pattern: str) -> List[str]:
        """정규식 패턴에서 키워드 추출"""
        keywords = []
        
        # 일반적인 키워드들
        common_keywords = [
            "AKIA", "sk-", "AIza", "ghp_", "api", "key", "password", "pwd",
            "token", "oauth", "Bearer", "eyJ", "BEGIN", "PRIVATE", "KEY",
            "postgresql", "mysql", "mongodb", "redis", "service_account"
        ]
        
        for keyword in common_keywords:
            if keyword.lower() in pattern.lower():
                keywords.append(keyword)
        
        return keywords
    
    async def scan_text(self, text: str, context: str = "") -> SecretScanResult:
        """텍스트에서 시크릿 스캔"""
        start_time = time.time()
        secrets = []
        error_messages = []
        
        try:
            # 1. 기본 정규식 패턴 스캔
            regex_secrets = await self._scan_with_regex(text, context)
            secrets.extend(regex_secrets)
            
            # 2. Aho-Corasick 스캔
            if self.aho_corasick_tree:
                ac_secrets = await self._scan_with_aho_corasick(text, context)
                secrets.extend(ac_secrets)
            
            # 3. TruffleHog 스캔
            if TRUFFLEHOG_AVAILABLE:
                try:
                    trufflehog_secrets = await self._scan_with_trufflehog(text, context)
                    secrets.extend(trufflehog_secrets)
                except Exception as e:
                    error_messages.append(f"TruffleHog 스캔 실패: {e}")
            
            # 4. Gitleaks 스캔
            if GITLEAKS_AVAILABLE:
                try:
                    gitleaks_secrets = await self._scan_with_gitleaks(text, context)
                    secrets.extend(gitleaks_secrets)
                except Exception as e:
                    error_messages.append(f"Gitleaks 스캔 실패: {e}")
            
            # 5. detect-secrets 스캔
            if DETECT_SECRETS_AVAILABLE:
                try:
                    detect_secrets_result = await self._scan_with_detect_secrets(text, context)
                    secrets.extend(detect_secrets_result)
                except Exception as e:
                    error_messages.append(f"detect-secrets 스캔 실패: {e}")
            
            # 중복 제거 및 정렬
            secrets = self._deduplicate_secrets(secrets)
            secrets.sort(key=lambda x: x.severity.value, reverse=True)
            
            # 결과 집계
            high_risk_count = sum(1 for s in secrets if s.severity in [SecretSeverity.HIGH, SecretSeverity.CRITICAL])
            
            processing_time = time.time() - start_time
            
            return SecretScanResult(
                has_secrets=len(secrets) > 0,
                secrets=secrets,
                total_secrets=len(secrets),
                high_risk_secrets=high_risk_count,
                processing_time=processing_time,
                scanner_status=self.scanner_status,
                error_messages=error_messages
            )
            
        except Exception as e:
            logger.error(f"Secret 스캔 실패: {e}")
            return SecretScanResult(
                has_secrets=False,
                secrets=[],
                processing_time=time.time() - start_time,
                scanner_status=self.scanner_status,
                error_messages=[f"스캔 실패: {e}"]
            )
    
    async def _scan_with_regex(self, text: str, context: str) -> List[SecretMatch]:
        """정규식을 사용한 시크릿 스캔"""
        secrets = []
        
        for secret_type, patterns in self.patterns.items():
            for pattern, severity in patterns:
                try:
                    matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
                    for match in matches:
                        secret = SecretMatch(
                            secret_type=secret_type,
                            severity=severity,
                            pattern=pattern,
                            matched_text=match.group(),
                            start_pos=match.start(),
                            end_pos=match.end(),
                            confidence=0.8,
                            scanner="regex",
                            context=context,
                            metadata={"pattern_type": "regex"}
                        )
                        secrets.append(secret)
                except Exception as e:
                    logger.warning(f"정규식 패턴 스캔 실패 ({pattern}): {e}")
        
        return secrets
    
    async def _scan_with_aho_corasick(self, text: str, context: str) -> List[SecretMatch]:
        """Aho-Corasick 알고리즘을 사용한 시크릿 스캔"""
        secrets = []
        
        if not self.aho_corasick_tree:
            return secrets
        
        try:
            for end_index, (secret_type, pattern, severity) in self.aho_corasick_tree.iter(text):
                start_index = end_index - len(text[end_index:]) + 1
                matched_text = text[start_index:end_index + 1]
                
                # 정규식으로 재검증
                if re.search(pattern, matched_text, re.IGNORECASE):
                    secret = SecretMatch(
                        secret_type=secret_type,
                        severity=severity,
                        pattern=pattern,
                        matched_text=matched_text,
                        start_pos=start_index,
                        end_pos=end_index + 1,
                        confidence=0.9,
                        scanner="aho_corasick",
                        context=context,
                        metadata={"pattern_type": "aho_corasick"}
                    )
                    secrets.append(secret)
        except Exception as e:
            logger.warning(f"Aho-Corasick 스캔 실패: {e}")
        
        return secrets
    
    async def _scan_with_trufflehog(self, text: str, context: str) -> List[SecretMatch]:
        """TruffleHog를 사용한 시크릿 스캔"""
        secrets = []
        
        try:
            # TruffleHog API 호출 (실제 구현 시 API 엔드포인트 사용)
            # 여기서는 모의 구현
            logger.info("TruffleHog 스캔 실행 (모의 구현)")
            
            # 실제 구현 시:
            # results = trufflehog.scan_text(text)
            # for result in results:
            #     secret = SecretMatch(...)
            #     secrets.append(secret)
            
        except Exception as e:
            logger.error(f"TruffleHog 스캔 실패: {e}")
        
        return secrets
    
    async def _scan_with_gitleaks(self, text: str, context: str) -> List[SecretMatch]:
        """Gitleaks를 사용한 시크릿 스캔"""
        secrets = []
        
        try:
            # Gitleaks API 호출 (실제 구현 시 API 엔드포인트 사용)
            logger.info("Gitleaks 스캔 실행 (모의 구현)")
            
            # 실제 구현 시:
            # results = gitleaks.scan_text(text)
            # for result in results:
            #     secret = SecretMatch(...)
            #     secrets.append(secret)
            
        except Exception as e:
            logger.error(f"Gitleaks 스캔 실패: {e}")
        
        return secrets
    
    async def _scan_with_detect_secrets(self, text: str, context: str) -> List[SecretMatch]:
        """detect-secrets를 사용한 시크릿 스캔"""
        secrets = []
        
        try:
            # detect-secrets 스캔
            results = scan.scan_text(text)
            
            for result in results:
                secret_type = SecretType.UNKNOWN
                severity = SecretSeverity.MEDIUM
                
                # detect-secrets 결과를 SecretMatch로 변환
                secret = SecretMatch(
                    secret_type=secret_type,
                    severity=severity,
                    pattern="detect_secrets",
                    matched_text=str(result),
                    start_pos=0,
                    end_pos=len(str(result)),
                    confidence=0.7,
                    scanner="detect_secrets",
                    context=context,
                    metadata={"detect_secrets_result": result}
                )
                secrets.append(secret)
                
        except Exception as e:
            logger.error(f"detect-secrets 스캔 실패: {e}")
        
        return secrets
    
    def _deduplicate_secrets(self, secrets: List[SecretMatch]) -> List[SecretMatch]:
        """중복 시크릿 제거"""
        seen = set()
        unique_secrets = []
        
        for secret in secrets:
            # 위치와 내용을 기반으로 중복 판단
            key = (secret.start_pos, secret.end_pos, secret.matched_text)
            if key not in seen:
                seen.add(key)
                unique_secrets.append(secret)
        
        return unique_secrets
    
    def get_scanner_status(self) -> Dict[str, Any]:
        """스캐너 상태 반환"""
        return {
            "scanner_status": self.scanner_status,
            "total_patterns": sum(len(patterns) for patterns in self.patterns.values()),
            "pattern_types": list(self.patterns.keys()),
            "aho_corasick_available": self.aho_corasick_tree is not None
        }

# 전역 Secret Scanner 인스턴스
_secret_scanner_instance: Optional[AdvancedSecretScanner] = None

async def get_secret_scanner() -> AdvancedSecretScanner:
    """Secret Scanner 인스턴스 반환 (싱글톤)"""
    global _secret_scanner_instance
    
    if _secret_scanner_instance is None:
        _secret_scanner_instance = AdvancedSecretScanner()
    
    return _secret_scanner_instance

async def close_secret_scanner():
    """Secret Scanner 정리"""
    global _secret_scanner_instance
    
    if _secret_scanner_instance:
        _secret_scanner_instance = None
        logger.info("Secret Scanner 정리 완료")
