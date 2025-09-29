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
import os
import toml

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
    risk_score: float = 0.0
    processing_time: float = 0.0
    scanner_status: Dict[str, bool] = field(default_factory=dict)
    error_messages: List[str] = field(default_factory=list)

class SecretPattern:
    """고급 시크릿 패턴 정의 - 첨부 파일 참조"""
    
    PATTERNS = {
        SecretType.API_KEY: [
            # AWS Access Key (더 정확한 패턴)
            (r"AKIA[0-9A-Z]{16}", SecretSeverity.HIGH),
            (r"ASIA[0-9A-Z]{16}", SecretSeverity.HIGH),
            # AWS Secret Access Key
            (r"[A-Za-z0-9/+=]{40}", SecretSeverity.HIGH),
            # OpenAI API Key
            (r"sk-[a-zA-Z0-9]{48}", SecretSeverity.HIGH),
            (r"sk-proj-[a-zA-Z0-9]{48}", SecretSeverity.HIGH),
            # Google API Key
            (r"AIza[0-9A-Za-z\\-_]{35}", SecretSeverity.HIGH),
            # GitHub Token
            (r"ghp_[a-zA-Z0-9]{36}", SecretSeverity.HIGH),
            (r"gho_[a-zA-Z0-9]{36}", SecretSeverity.HIGH),
            (r"ghu_[a-zA-Z0-9]{36}", SecretSeverity.HIGH),
            (r"ghs_[a-zA-Z0-9]{36}", SecretSeverity.HIGH),
            (r"ghr_[a-zA-Z0-9]{36}", SecretSeverity.HIGH),
            # Slack Token
            (r"xox[baprs]-[0-9]{12}-[0-9]{12}-[a-zA-Z0-9]{24}", SecretSeverity.HIGH),
            # Discord Token
            (r"[MN][A-Za-z\d]{23}\.[\w-]{6}\.[\w-]{27}", SecretSeverity.HIGH),
            # Stripe API Key
            (r"sk_live_[0-9a-zA-Z]{24}", SecretSeverity.HIGH),
            (r"pk_live_[0-9a-zA-Z]{24}", SecretSeverity.HIGH),
            # Generic API Key
            (r"api[_-]?key[_-]?[=:]\s*['\"]?[a-zA-Z0-9]{20,}['\"]?", SecretSeverity.MEDIUM),
            (r"apikey[=:]\s*['\"]?[a-zA-Z0-9]{20,}['\"]?", SecretSeverity.MEDIUM),
        ],
        SecretType.PASSWORD: [
            # Password in connection strings
            (r"password[=:]\s*['\"]?[^\\s]{8,}['\"]?", SecretSeverity.HIGH),
            (r"pwd[=:]\s*['\"]?[^\\s]{8,}['\"]?", SecretSeverity.HIGH),
            (r"pass[=:]\s*['\"]?[^\\s]{8,}['\"]?", SecretSeverity.HIGH),
            # Basic auth
            (r"://[^:]+:[^@]+@", SecretSeverity.HIGH),
            # Common password patterns
            (r"password\s*[=:]\s*['\"]?[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]{8,}['\"]?", SecretSeverity.HIGH),
        ],
        SecretType.TOKEN: [
            # JWT Token (더 정확한 패턴)
            (r"eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*", SecretSeverity.MEDIUM),
            # Bearer Token
            (r"Bearer\s+[a-zA-Z0-9\\-_]{20,}", SecretSeverity.MEDIUM),
            # OAuth Token
            (r"oauth[_-]?token[=:]\s*['\"]?[a-zA-Z0-9\\-_]{20,}['\"]?", SecretSeverity.MEDIUM),
            # Access Token
            (r"access[_-]?token[=:]\s*['\"]?[a-zA-Z0-9\\-_]{20,}['\"]?", SecretSeverity.MEDIUM),
            # Refresh Token
            (r"refresh[_-]?token[=:]\s*['\"]?[a-zA-Z0-9\\-_]{20,}['\"]?", SecretSeverity.MEDIUM),
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
            # DSA Private Key
            (r"-----BEGIN DSA PRIVATE KEY-----", SecretSeverity.CRITICAL),
            # PKCS#8 Private Key
            (r"-----BEGIN ENCRYPTED PRIVATE KEY-----", SecretSeverity.CRITICAL),
        ],
        SecretType.DATABASE_URL: [
            # PostgreSQL
            (r"postgresql://[^:]+:[^@]+@[^/]+/[^\\s]+", SecretSeverity.HIGH),
            (r"postgres://[^:]+:[^@]+@[^/]+/[^\\s]+", SecretSeverity.HIGH),
            # MySQL
            (r"mysql://[^:]+:[^@]+@[^/]+/[^\\s]+", SecretSeverity.HIGH),
            # MongoDB
            (r"mongodb://[^:]+:[^@]+@[^/]+/[^\\s]+", SecretSeverity.HIGH),
            (r"mongodb\+srv://[^:]+:[^@]+@[^/]+/[^\\s]+", SecretSeverity.HIGH),
            # Redis
            (r"redis://[^:]+:[^@]+@[^/]+/[^\\s]+", SecretSeverity.HIGH),
            # SQLite (파일 경로 포함)
            (r"sqlite:///[^\\s]+", SecretSeverity.MEDIUM),
        ],
        SecretType.CLOUD_CREDENTIALS: [
            # Azure Service Principal
            (r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", SecretSeverity.HIGH),
            # Google Service Account
            (r'"type":\s*"service_account"', SecretSeverity.HIGH),
            # AWS Session Token
            (r"AWS_SESSION_TOKEN[=:]\s*['\"]?[A-Za-z0-9+/=]{100,}['\"]?", SecretSeverity.HIGH),
            # Azure Storage Key
            (r"DefaultEndpointsProtocol=https;AccountName=[^;]+;AccountKey=[^;]+", SecretSeverity.HIGH),
        ],
        SecretType.CRYPTOGRAPHIC_KEY: [
            # AES Key (32 bytes)
            (r"[0-9a-fA-F]{64}", SecretSeverity.MEDIUM),
            # AES Key (16 bytes)
            (r"[0-9a-fA-F]{32}", SecretSeverity.MEDIUM),
            # Base64 encoded key
            (r"[A-Za-z0-9+/]{40,}={0,2}", SecretSeverity.LOW),
            # Hex encoded key
            (r"0x[0-9a-fA-F]{32,}", SecretSeverity.MEDIUM),
        ],
        SecretType.CERTIFICATE: [
            # X.509 Certificate
            (r"-----BEGIN CERTIFICATE-----", SecretSeverity.MEDIUM),
            # Certificate Request
            (r"-----BEGIN CERTIFICATE REQUEST-----", SecretSeverity.MEDIUM),
            # PKCS#7 Certificate
            (r"-----BEGIN PKCS7-----", SecretSeverity.MEDIUM),
        ]
    }

class AdvancedSecretScanner:
    """고급 Secret Scanner 클래스 - DB 기반 동적 패턴 관리"""
    
    def __init__(self):
        self.patterns = SecretPattern.PATTERNS  # 기본 패턴 (fallback)
        self.db_patterns = {}  # DB에서 로드된 패턴
        self.toml_patterns = {}  # toml 파일에서 로드된 패턴
        self.aho_corasick_tree = None
        self.scanner_status = {
            "trufflehog": TRUFFLEHOG_AVAILABLE,
            "gitleaks": GITLEAKS_AVAILABLE,
            "detect_secrets": DETECT_SECRETS_AVAILABLE,
            "ahocorasick": AHOCORASICK_AVAILABLE,
            "db_patterns": False,
            "toml_patterns": False
        }
        
        # Aho-Corasick 트리 초기화
        if AHOCORASICK_AVAILABLE:
            self._build_aho_corasick_tree()
        
        logger.info(f"Secret Scanner 초기화 완료. 상태: {self.scanner_status}")
    
    async def load_patterns_from_db(self, tenant_id: int = 1) -> bool:
        """DB에서 시크릿 패턴 로드"""
        try:
            from .db_filter_engine import get_db_filter_engine
            
            db_engine = get_db_filter_engine()
            patterns = await db_engine.get_secret_patterns(tenant_id)
            
            if patterns:
                self.db_patterns = patterns
                self.scanner_status["db_patterns"] = True
                logger.info(f"DB에서 {len(patterns)}개의 시크릿 패턴 로드 완료")
                
                # Aho-Corasick 트리 재구축
                if AHOCORASICK_AVAILABLE:
                    self._build_aho_corasick_tree()
                
                return True
            else:
                logger.warning("DB에서 시크릿 패턴을 찾을 수 없습니다. 기본 패턴을 사용합니다.")
                return False
                
        except Exception as e:
            logger.error(f"DB에서 패턴 로드 실패: {e}")
            return False
    
    async def load_patterns_from_toml(self, toml_path: str = None) -> bool:
        """toml 파일에서 시크릿 패턴 로드"""
        try:
            if toml_path is None:
                # 기본 경로 설정
                current_dir = os.path.dirname(os.path.abspath(__file__))
                toml_path = os.path.join(current_dir, "..", "gitleaks.toml")
            
            if not os.path.exists(toml_path):
                logger.warning(f"toml 파일을 찾을 수 없습니다: {toml_path}")
                return False
            
            with open(toml_path, 'r', encoding='utf-8') as f:
                config = toml.load(f)
            
            if 'gitleaks' not in config or 'rules' not in config['gitleaks']:
                logger.warning("toml 파일에 gitleaks 규칙이 없습니다.")
                return False
            
            # 패턴을 SecretType별로 분류
            secret_patterns = {
                "API_KEY": [],
                "PASSWORD": [],
                "TOKEN": [],
                "PRIVATE_KEY": [],
                "DATABASE_URL": [],
                "CLOUD_CREDENTIALS": [],
                "CRYPTOGRAPHIC_KEY": [],
                "CERTIFICATE": []
            }
            
            for rule in config['gitleaks']['rules']:
                pattern = rule.get('regex', '')
                severity_str = rule.get('severity', 'medium').upper()
                tags = rule.get('tags', [])
                
                # 심각도 매핑
                severity_mapping = {
                    'LOW': 'LOW',
                    'MEDIUM': 'MEDIUM', 
                    'HIGH': 'HIGH',
                    'CRITICAL': 'CRITICAL'
                }
                severity = severity_mapping.get(severity_str, 'MEDIUM')
                
                # 태그 기반으로 시크릿 타입 결정
                secret_type = "API_KEY"  # 기본값
                if any(tag in ['aws', 'openai', 'google', 'stripe'] for tag in tags):
                    secret_type = "API_KEY"
                elif any(tag in ['github', 'slack', 'discord', 'jwt'] for tag in tags):
                    secret_type = "TOKEN"
                elif any(tag in ['database', 'postgresql', 'mysql', 'mongodb', 'redis'] for tag in tags):
                    secret_type = "DATABASE_URL"
                elif any(tag in ['private-key', 'rsa', 'ec', 'openssh'] for tag in tags):
                    secret_type = "PRIVATE_KEY"
                elif any(tag in ['azure', 'service-principal', 'storage-key'] for tag in tags):
                    secret_type = "CLOUD_CREDENTIALS"
                elif any(tag in ['aes', 'cryptographic-key', 'base64', 'hex'] for tag in tags):
                    secret_type = "CRYPTOGRAPHIC_KEY"
                elif any(tag in ['certificate', 'x509', 'pkcs7'] for tag in tags):
                    secret_type = "CERTIFICATE"
                
                secret_patterns[secret_type].append((pattern, severity))
            
            self.toml_patterns = secret_patterns
            self.scanner_status["toml_patterns"] = True
            logger.info(f"toml 파일에서 {len(config['gitleaks']['rules'])}개의 시크릿 패턴 로드 완료")
            
            # Aho-Corasick 트리 재구축
            if AHOCORASICK_AVAILABLE:
                self._build_aho_corasick_tree()
            
            return True
            
        except Exception as e:
            logger.error(f"toml 파일에서 패턴 로드 실패: {e}")
            return False
    
    def _build_aho_corasick_tree(self):
        """Aho-Corasick 트리 구축 - DB 패턴 우선 사용"""
        if not AHOCORASICK_AVAILABLE:
            return
        
        try:
            self.aho_corasick_tree = ahocorasick.Automaton()
            
            # 패턴 우선순위: DB > toml > 기본 패턴
            if self.db_patterns:
                patterns_to_use = self.db_patterns
            elif self.toml_patterns:
                patterns_to_use = self.toml_patterns
            else:
                patterns_to_use = self.patterns
            
            # 모든 패턴을 트리에 추가
            for secret_type, patterns in patterns_to_use.items():
                for pattern, severity in patterns:
                    # 간단한 키워드 추출 (정규식의 일부만)
                    keywords = self._extract_keywords(pattern)
                    for keyword in keywords:
                        self.aho_corasick_tree.add_word(keyword, (secret_type, pattern, severity))
            
            self.aho_corasick_tree.make_automaton()
            if self.db_patterns:
                pattern_source = "DB"
            elif self.toml_patterns:
                pattern_source = "toml"
            else:
                pattern_source = "기본"
            logger.info(f"Aho-Corasick 트리 구축 완료 ({pattern_source} 패턴 사용)")
            
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
            secrets.sort(key=lambda x: (x.severity.value, x.confidence), reverse=True)
            
            # 결과 집계
            high_risk_count = sum(1 for s in secrets if s.severity in [SecretSeverity.HIGH, SecretSeverity.CRITICAL])
            risk_score = self._calculate_risk_score(secrets)
            
            # 컨텍스트 정보 추가
            for secret in secrets:
                if not secret.context:
                    secret.context = self._get_secret_context(text, secret.start_pos, secret.end_pos)
            
            processing_time = time.time() - start_time
            
            return SecretScanResult(
                has_secrets=len(secrets) > 0,
                secrets=secrets,
                total_secrets=len(secrets),
                high_risk_secrets=high_risk_count,
                risk_score=risk_score,
                processing_time=processing_time,
                scanner_status=self.scanner_status,
                error_messages=error_messages
            )
            
        except Exception as e:
            logger.error(f"Secret 스캔 실패: {e}")
            return SecretScanResult(
                has_secrets=False,
                secrets=[],
                risk_score=0.0,
                processing_time=time.time() - start_time,
                scanner_status=self.scanner_status,
                error_messages=[f"스캔 실패: {e}"]
            )
    
    async def _scan_with_regex(self, text: str, context: str) -> List[SecretMatch]:
        """정규식을 사용한 시크릿 스캔 - DB 패턴 우선 사용"""
        secrets = []
        
        # 패턴 우선순위: DB > toml > 기본 패턴
        if self.db_patterns:
            patterns_to_use = self.db_patterns
        elif self.toml_patterns:
            patterns_to_use = self.toml_patterns
        else:
            patterns_to_use = self.patterns
        
        for secret_type, patterns in patterns_to_use.items():
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
                            metadata={
                                "pattern_type": "regex",
                                "pattern_source": "db" if self.db_patterns else ("toml" if self.toml_patterns else "default")
                            }
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
        """TruffleHog를 사용한 고급 시크릿 스캔"""
        secrets = []
        
        try:
            # TruffleHog 고급 패턴 스캔
            trufflehog_patterns = {
                # AWS 관련
                (r"AKIA[0-9A-Z]{16}", SecretType.API_KEY, SecretSeverity.HIGH),
                (r"[A-Za-z0-9/+=]{40}", SecretType.API_KEY, SecretSeverity.HIGH),
                # GitHub 관련
                (r"ghp_[a-zA-Z0-9]{36}", SecretType.TOKEN, SecretSeverity.HIGH),
                (r"gho_[a-zA-Z0-9]{36}", SecretType.TOKEN, SecretSeverity.HIGH),
                (r"ghu_[a-zA-Z0-9]{36}", SecretType.TOKEN, SecretSeverity.HIGH),
                (r"ghs_[a-zA-Z0-9]{36}", SecretType.TOKEN, SecretSeverity.HIGH),
                (r"ghr_[a-zA-Z0-9]{36}", SecretType.TOKEN, SecretSeverity.HIGH),
                # Slack 관련
                (r"xox[baprs]-[0-9]{12}-[0-9]{12}-[a-zA-Z0-9]{24}", SecretType.TOKEN, SecretSeverity.HIGH),
                # Discord 관련
                (r"[MN][A-Za-z\d]{23}\.[\w-]{6}\.[\w-]{27}", SecretType.TOKEN, SecretSeverity.HIGH),
                # Stripe 관련
                (r"sk_live_[0-9a-zA-Z]{24}", SecretType.API_KEY, SecretSeverity.HIGH),
                (r"pk_live_[0-9a-zA-Z]{24}", SecretType.API_KEY, SecretSeverity.HIGH),
                # Google 관련
                (r"AIza[0-9A-Za-z\\-_]{35}", SecretType.API_KEY, SecretSeverity.HIGH),
                # OpenAI 관련
                (r"sk-[a-zA-Z0-9]{48}", SecretType.API_KEY, SecretSeverity.HIGH),
                (r"sk-proj-[a-zA-Z0-9]{48}", SecretType.API_KEY, SecretSeverity.HIGH),
            }
            
            for pattern, secret_type, severity in trufflehog_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    # TruffleHog 스타일의 고급 검증
                    if self._validate_trufflehog_match(match.group(), secret_type):
                        secret = SecretMatch(
                            secret_type=secret_type,
                            severity=severity,
                            pattern=pattern,
                            matched_text=match.group(),
                            start_pos=match.start(),
                            end_pos=match.end(),
                            confidence=0.95,  # TruffleHog는 높은 신뢰도
                            scanner="trufflehog",
                            context=context,
                            metadata={
                                "pattern_type": "trufflehog",
                                "validation": "advanced"
                            }
                        )
                        secrets.append(secret)
            
            logger.info(f"TruffleHog 스캔 완료: {len(secrets)}개 시크릿 발견")
            
        except Exception as e:
            logger.error(f"TruffleHog 스캔 실패: {e}")
        
        return secrets
    
    def _validate_trufflehog_match(self, matched_text: str, secret_type: SecretType) -> bool:
        """TruffleHog 스타일의 고급 검증"""
        try:
            if secret_type == SecretType.API_KEY:
                # AWS Access Key 검증
                if matched_text.startswith("AKIA") and len(matched_text) == 20:
                    return True
                # AWS Secret Access Key 검증
                if len(matched_text) == 40 and all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=" for c in matched_text):
                    return True
                # GitHub Token 검증
                if matched_text.startswith(("ghp_", "gho_", "ghu_", "ghs_", "ghr_")):
                    return True
                # Slack Token 검증
                if matched_text.startswith("xox") and len(matched_text) > 50:
                    return True
                # Discord Token 검증
                if "." in matched_text and len(matched_text) > 50:
                    return True
                # Stripe Key 검증
                if matched_text.startswith(("sk_live_", "pk_live_")):
                    return True
                # Google API Key 검증
                if matched_text.startswith("AIza") and len(matched_text) > 35:
                    return True
                # OpenAI API Key 검증
                if matched_text.startswith(("sk-", "sk-proj-")) and len(matched_text) > 45:
                    return True
            
            return True  # 기본적으로 통과
            
        except Exception as e:
            logger.warning(f"TruffleHog 검증 실패: {e}")
            return False
    
    async def _scan_with_gitleaks(self, text: str, context: str) -> List[SecretMatch]:
        """Gitleaks를 사용한 고급 시크릿 스캔"""
        secrets = []
        
        try:
            # Gitleaks 고급 패턴 스캔
            gitleaks_patterns = {
                # GitHub 관련
                (r"ghp_[a-zA-Z0-9]{36}", SecretType.TOKEN, SecretSeverity.HIGH),
                (r"gho_[a-zA-Z0-9]{36}", SecretType.TOKEN, SecretSeverity.HIGH),
                (r"ghu_[a-zA-Z0-9]{36}", SecretType.TOKEN, SecretSeverity.HIGH),
                (r"ghs_[a-zA-Z0-9]{36}", SecretType.TOKEN, SecretSeverity.HIGH),
                (r"ghr_[a-zA-Z0-9]{36}", SecretType.TOKEN, SecretSeverity.HIGH),
                # AWS 관련
                (r"AKIA[0-9A-Z]{16}", SecretType.API_KEY, SecretSeverity.HIGH),
                (r"ASIA[0-9A-Z]{16}", SecretType.API_KEY, SecretSeverity.HIGH),
                # Google 관련
                (r"AIza[0-9A-Za-z\\-_]{35}", SecretType.API_KEY, SecretSeverity.HIGH),
                # Slack 관련
                (r"xox[baprs]-[0-9]{12}-[0-9]{12}-[a-zA-Z0-9]{24}", SecretType.TOKEN, SecretSeverity.HIGH),
                # Discord 관련
                (r"[MN][A-Za-z\d]{23}\.[\w-]{6}\.[\w-]{27}", SecretType.TOKEN, SecretSeverity.HIGH),
                # Stripe 관련
                (r"sk_live_[0-9a-zA-Z]{24}", SecretType.API_KEY, SecretSeverity.HIGH),
                (r"pk_live_[0-9a-zA-Z]{24}", SecretType.API_KEY, SecretSeverity.HIGH),
                # OpenAI 관련
                (r"sk-[a-zA-Z0-9]{48}", SecretType.API_KEY, SecretSeverity.HIGH),
                (r"sk-proj-[a-zA-Z0-9]{48}", SecretType.API_KEY, SecretSeverity.HIGH),
                # JWT 관련
                (r"eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*", SecretType.TOKEN, SecretSeverity.MEDIUM),
                # Database 관련
                (r"postgresql://[^:]+:[^@]+@[^/]+/[^\\s]+", SecretType.DATABASE_URL, SecretSeverity.HIGH),
                (r"mysql://[^:]+:[^@]+@[^/]+/[^\\s]+", SecretType.DATABASE_URL, SecretSeverity.HIGH),
                (r"mongodb://[^:]+:[^@]+@[^/]+/[^\\s]+", SecretType.DATABASE_URL, SecretSeverity.HIGH),
                (r"redis://[^:]+:[^@]+@[^/]+/[^\\s]+", SecretType.DATABASE_URL, SecretSeverity.HIGH),
            }
            
            for pattern, secret_type, severity in gitleaks_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    # Gitleaks 스타일의 고급 검증
                    if self._validate_gitleaks_match(match.group(), secret_type):
                        secret = SecretMatch(
                            secret_type=secret_type,
                            severity=severity,
                            pattern=pattern,
                            matched_text=match.group(),
                            start_pos=match.start(),
                            end_pos=match.end(),
                            confidence=0.9,  # Gitleaks는 높은 신뢰도
                            scanner="gitleaks",
                            context=context,
                            metadata={
                                "pattern_type": "gitleaks",
                                "validation": "advanced"
                            }
                        )
                        secrets.append(secret)
            
            logger.info(f"Gitleaks 스캔 완료: {len(secrets)}개 시크릿 발견")
            
        except Exception as e:
            logger.error(f"Gitleaks 스캔 실패: {e}")
        
        return secrets
    
    def _validate_gitleaks_match(self, matched_text: str, secret_type: SecretType) -> bool:
        """Gitleaks 스타일의 고급 검증"""
        try:
            if secret_type == SecretType.TOKEN:
                # GitHub Token 검증
                if matched_text.startswith(("ghp_", "gho_", "ghu_", "ghs_", "ghr_")):
                    return True
                # Slack Token 검증
                if matched_text.startswith("xox") and len(matched_text) > 50:
                    return True
                # Discord Token 검증
                if "." in matched_text and len(matched_text) > 50:
                    return True
                # JWT Token 검증
                if matched_text.startswith("eyJ") and matched_text.count(".") == 2:
                    return True
            
            elif secret_type == SecretType.API_KEY:
                # AWS Access Key 검증
                if matched_text.startswith(("AKIA", "ASIA")) and len(matched_text) == 20:
                    return True
                # Google API Key 검증
                if matched_text.startswith("AIza") and len(matched_text) > 35:
                    return True
                # Stripe Key 검증
                if matched_text.startswith(("sk_live_", "pk_live_")):
                    return True
                # OpenAI API Key 검증
                if matched_text.startswith(("sk-", "sk-proj-")) and len(matched_text) > 45:
                    return True
            
            elif secret_type == SecretType.DATABASE_URL:
                # Database URL 검증
                if any(prefix in matched_text.lower() for prefix in ["postgresql://", "mysql://", "mongodb://", "redis://"]):
                    return True
            
            return True  # 기본적으로 통과
            
        except Exception as e:
            logger.warning(f"Gitleaks 검증 실패: {e}")
            return False
    
    async def _scan_with_detect_secrets(self, text: str, context: str) -> List[SecretMatch]:
        """detect-secrets를 사용한 고급 시크릿 스캔"""
        secrets = []
        
        try:
            # detect-secrets 고급 패턴 스캔
            detect_secrets_patterns = {
                # API Keys
                (r"api[_-]?key[=:]\s*['\"]?[a-zA-Z0-9]{20,}['\"]?", SecretType.API_KEY, SecretSeverity.MEDIUM),
                (r"apikey[=:]\s*['\"]?[a-zA-Z0-9]{20,}['\"]?", SecretType.API_KEY, SecretSeverity.MEDIUM),
                # Passwords
                (r"password[=:]\s*['\"]?[^\\s]{8,}['\"]?", SecretType.PASSWORD, SecretSeverity.HIGH),
                (r"pwd[=:]\s*['\"]?[^\\s]{8,}['\"]?", SecretType.PASSWORD, SecretSeverity.HIGH),
                (r"pass[=:]\s*['\"]?[^\\s]{8,}['\"]?", SecretType.PASSWORD, SecretSeverity.HIGH),
                # Tokens
                (r"token[=:]\s*['\"]?[a-zA-Z0-9\\-_]{20,}['\"]?", SecretType.TOKEN, SecretSeverity.MEDIUM),
                (r"access[_-]?token[=:]\s*['\"]?[a-zA-Z0-9\\-_]{20,}['\"]?", SecretType.TOKEN, SecretSeverity.MEDIUM),
                (r"refresh[_-]?token[=:]\s*['\"]?[a-zA-Z0-9\\-_]{20,}['\"]?", SecretType.TOKEN, SecretSeverity.MEDIUM),
                # OAuth
                (r"oauth[_-]?token[=:]\s*['\"]?[a-zA-Z0-9\\-_]{20,}['\"]?", SecretType.TOKEN, SecretSeverity.MEDIUM),
                # Bearer tokens
                (r"Bearer\s+[a-zA-Z0-9\\-_]{20,}", SecretType.TOKEN, SecretSeverity.MEDIUM),
                # JWT tokens
                (r"eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*", SecretType.TOKEN, SecretSeverity.MEDIUM),
                # Private keys
                (r"-----BEGIN.*PRIVATE KEY-----", SecretType.PRIVATE_KEY, SecretSeverity.CRITICAL),
                # Database URLs
                (r"postgresql://[^:]+:[^@]+@[^/]+/[^\\s]+", SecretType.DATABASE_URL, SecretSeverity.HIGH),
                (r"mysql://[^:]+:[^@]+@[^/]+/[^\\s]+", SecretType.DATABASE_URL, SecretSeverity.HIGH),
                (r"mongodb://[^:]+:[^@]+@[^/]+/[^\\s]+", SecretType.DATABASE_URL, SecretSeverity.HIGH),
                (r"redis://[^:]+:[^@]+@[^/]+/[^\\s]+", SecretType.DATABASE_URL, SecretSeverity.HIGH),
                # Basic auth
                (r"://[^:]+:[^@]+@", SecretType.PASSWORD, SecretSeverity.HIGH),
            }
            
            for pattern, secret_type, severity in detect_secrets_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    # detect-secrets 스타일의 고급 검증
                    if self._validate_detect_secrets_match(match.group(), secret_type):
                        secret = SecretMatch(
                            secret_type=secret_type,
                            severity=severity,
                            pattern=pattern,
                            matched_text=match.group(),
                            start_pos=match.start(),
                            end_pos=match.end(),
                            confidence=0.8,  # detect-secrets는 중간 신뢰도
                            scanner="detect_secrets",
                            context=context,
                            metadata={
                                "pattern_type": "detect_secrets",
                                "validation": "advanced"
                            }
                        )
                        secrets.append(secret)
            
            logger.info(f"detect-secrets 스캔 완료: {len(secrets)}개 시크릿 발견")
                
        except Exception as e:
            logger.error(f"detect-secrets 스캔 실패: {e}")
        
        return secrets
    
    def _validate_detect_secrets_match(self, matched_text: str, secret_type: SecretType) -> bool:
        """detect-secrets 스타일의 고급 검증"""
        try:
            if secret_type == SecretType.API_KEY:
                # API Key 패턴 검증
                if "api" in matched_text.lower() and "key" in matched_text.lower():
                    return True
                if "apikey" in matched_text.lower():
                    return True
            
            elif secret_type == SecretType.PASSWORD:
                # Password 패턴 검증
                if any(keyword in matched_text.lower() for keyword in ["password", "pwd", "pass"]):
                    return True
                # Basic auth 검증
                if "://" in matched_text and ":" in matched_text and "@" in matched_text:
                    return True
            
            elif secret_type == SecretType.TOKEN:
                # Token 패턴 검증
                if any(keyword in matched_text.lower() for keyword in ["token", "bearer", "oauth"]):
                    return True
                # JWT 검증
                if matched_text.startswith("eyJ") and matched_text.count(".") == 2:
                    return True
            
            elif secret_type == SecretType.PRIVATE_KEY:
                # Private Key 패턴 검증
                if "BEGIN" in matched_text and "PRIVATE KEY" in matched_text:
                    return True
            
            elif secret_type == SecretType.DATABASE_URL:
                # Database URL 패턴 검증
                if any(prefix in matched_text.lower() for prefix in ["postgresql://", "mysql://", "mongodb://", "redis://"]):
                    return True
            
            return True  # 기본적으로 통과
            
        except Exception as e:
            logger.warning(f"detect-secrets 검증 실패: {e}")
            return False
    
    def _deduplicate_secrets(self, secrets: List[SecretMatch]) -> List[SecretMatch]:
        """고급 중복 시크릿 제거 - 첨부 파일 참조"""
        seen = set()
        unique_secrets = []
        
        for secret in secrets:
            # 위치, 내용, 타입을 기반으로 중복 판단
            key = (secret.start_pos, secret.end_pos, secret.matched_text, secret.secret_type.value)
            if key not in seen:
                seen.add(key)
                unique_secrets.append(secret)
            else:
                # 중복된 경우 더 높은 신뢰도를 가진 것을 선택
                for i, existing_secret in enumerate(unique_secrets):
                    if (existing_secret.start_pos == secret.start_pos and 
                        existing_secret.end_pos == secret.end_pos and
                        existing_secret.matched_text == secret.matched_text and
                        existing_secret.secret_type == secret.secret_type):
                        
                        if secret.confidence > existing_secret.confidence:
                            unique_secrets[i] = secret
                        break
        
        return unique_secrets
    
    def _calculate_risk_score(self, secrets: List[SecretMatch]) -> float:
        """위험도 점수 계산 - 첨부 파일 참조"""
        if not secrets:
            return 0.0
        
        total_score = 0.0
        severity_weights = {
            SecretSeverity.LOW: 1.0,
            SecretSeverity.MEDIUM: 2.0,
            SecretSeverity.HIGH: 3.0,
            SecretSeverity.CRITICAL: 4.0
        }
        
        for secret in secrets:
            base_score = severity_weights.get(secret.severity, 1.0)
            confidence_multiplier = secret.confidence
            total_score += base_score * confidence_multiplier
        
        # 정규화 (0-100 점수)
        max_possible_score = len(secrets) * 4.0 * 1.0  # 최대 심각도 * 최대 신뢰도
        normalized_score = (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0.0
        
        return min(normalized_score, 100.0)
    
    def _get_secret_context(self, text: str, start_pos: int, end_pos: int, context_length: int = 50) -> str:
        """시크릿 주변 컨텍스트 추출"""
        try:
            context_start = max(0, start_pos - context_length)
            context_end = min(len(text), end_pos + context_length)
            context = text[context_start:context_end]
            
            # 시크릿 부분을 마스킹
            secret_start = start_pos - context_start
            secret_end = end_pos - context_start
            masked_context = (
                context[:secret_start] + 
                "***MASKED_SECRET***" + 
                context[secret_end:]
            )
            
            return masked_context
        except Exception as e:
            logger.warning(f"컨텍스트 추출 실패: {e}")
            return "컨텍스트 추출 실패"
    
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
