"""
DB 기반 필터링 엔진
기존 설계 문서의 DB 스키마를 사용하여 필터링 기능 구현
"""

import re
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

class FilterRuleType(Enum):
    STATIC = "static"
    SECRET = "secret"
    PII = "pii"
    REBUFF = "rebuff"
    ML = "ml"
    EMBEDDING = "embedding"

class FilterAction(Enum):
    BLOCK = "block"
    REDACT = "redact"
    REQUIRE_APPROVAL = "require_approval"
    LOG_ONLY = "log_only"

@dataclass
class FilterResult:
    is_blocked: bool = False
    action: FilterAction = FilterAction.LOG_ONLY
    reason: str = ""
    risk_score: float = 0.0
    detection_method: str = ""
    masked_prompt: str = ""
    processing_time: float = 0.0
    matched_rules: List[Dict[str, Any]] = field(default_factory=list)
    policy_violations: List[str] = field(default_factory=list)

@dataclass
class RequestContext:
    tenant_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    user_roles: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

class DatabaseFilterEngine:
    """DB 기반 필터링 엔진"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.cache = {}  # 간단한 메모리 캐시
        self.cache_ttl = 300  # 5분 캐시
        logger.info("DB 기반 필터링 엔진 초기화 완료")
    
    def get_db_session(self) -> Session:
        """데이터베이스 세션 반환"""
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        return SessionLocal()
    
    async def get_active_filter_rules(self, tenant_id: str) -> List[Dict[str, Any]]:
        """활성 필터 규칙 조회 (캐시 포함)"""
        cache_key = f"filter_rules_{tenant_id}"
        
        # 캐시 확인
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if (datetime.now() - timestamp).seconds < self.cache_ttl:
                return cached_data
        
        # DB에서 조회
        db = self.get_db_session()
        try:
            query = text("""
                SELECT fr.id, fr.type, fr.pattern, fr.threshold, fr.action, fr.context,
                       pb.name as bundle_name, pb.version as bundle_version
                FROM filter_rules fr
                JOIN policy_bundles pb ON fr.bundle_id = pb.id
                WHERE fr.tenant_id = :tenant_id 
                AND fr.enabled = true 
                AND pb.status = 'active'
                AND pb.channel = 'prod'
                ORDER BY fr.type, fr.id
            """)
            
            result = db.execute(query, {"tenant_id": tenant_id})
            rules = []
            
            for row in result:
                rules.append({
                    "id": row.id,
                    "type": row.type,
                    "pattern": row.pattern,
                    "threshold": float(row.threshold) if row.threshold else None,
                    "action": row.action,
                    "context": json.loads(row.context) if row.context else {},
                    "bundle_name": row.bundle_name,
                    "bundle_version": row.bundle_version
                })
            
            # 캐시에 저장
            self.cache[cache_key] = (rules, datetime.now())
            
            logger.info(f"테넌트 {tenant_id}의 활성 필터 규칙 {len(rules)}개 로드")
            return rules
            
        except Exception as e:
            logger.error(f"필터 규칙 조회 실패: {e}")
            return []
        finally:
            db.close()
    
    async def get_allowlist(self, tenant_id: str) -> List[Dict[str, Any]]:
        """허용 목록 조회"""
        cache_key = f"allowlist_{tenant_id}"
        
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if (datetime.now() - timestamp).seconds < self.cache_ttl:
                return cached_data
        
        db = self.get_db_session()
        try:
            query = text("""
                SELECT al.kind, al.value, al.scope, al.expire_at
                FROM allowlists al
                JOIN policy_bundles pb ON al.bundle_id = pb.id
                WHERE al.tenant_id = :tenant_id 
                AND pb.status = 'active'
                AND pb.channel = 'prod'
                AND (al.expire_at IS NULL OR al.expire_at > now())
                ORDER BY al.kind, al.value
            """)
            
            result = db.execute(query, {"tenant_id": tenant_id})
            allowlist = []
            
            for row in result:
                allowlist.append({
                    "kind": row.kind,
                    "value": row.value,
                    "scope": row.scope,
                    "expire_at": row.expire_at
                })
            
            self.cache[cache_key] = (allowlist, datetime.now())
            return allowlist
            
        except Exception as e:
            logger.error(f"허용 목록 조회 실패: {e}")
            return []
        finally:
            db.close()
    
    async def get_blocklist(self, tenant_id: str) -> List[Dict[str, Any]]:
        """차단 목록 조회"""
        cache_key = f"blocklist_{tenant_id}"
        
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if (datetime.now() - timestamp).seconds < self.cache_ttl:
                return cached_data
        
        db = self.get_db_session()
        try:
            query = text("""
                SELECT bl.kind, bl.value, bl.scope, bl.expire_at
                FROM blocklists bl
                JOIN policy_bundles pb ON bl.bundle_id = pb.id
                WHERE bl.tenant_id = :tenant_id 
                AND pb.status = 'active'
                AND pb.channel = 'prod'
                AND (bl.expire_at IS NULL OR bl.expire_at > now())
                ORDER BY bl.kind, bl.value
            """)
            
            result = db.execute(query, {"tenant_id": tenant_id})
            blocklist = []
            
            for row in result:
                blocklist.append({
                    "kind": row.kind,
                    "value": row.value,
                    "scope": row.scope,
                    "expire_at": row.expire_at
                })
            
            self.cache[cache_key] = (blocklist, datetime.now())
            return blocklist
            
        except Exception as e:
            logger.error(f"차단 목록 조회 실패: {e}")
            return []
        finally:
            db.close()
    
    async def evaluate_prompt(self, prompt: str, context: RequestContext) -> FilterResult:
        """프롬프트 평가 (DB 기반)"""
        start_time = datetime.now()
        
        try:
            # 1. 허용 목록 확인
            allowlist = await self.get_allowlist(context.tenant_id)
            if await self._check_allowlist(prompt, allowlist):
                return FilterResult(
                    is_blocked=False,
                    action=FilterAction.LOG_ONLY,
                    reason="Allowlist match",
                    detection_method="allowlist",
                    masked_prompt=prompt,
                    processing_time=(datetime.now() - start_time).total_seconds()
                )
            
            # 2. 차단 목록 확인
            blocklist = await self.get_blocklist(context.tenant_id)
            blocklist_match = await self._check_blocklist(prompt, blocklist)
            if blocklist_match:
                return FilterResult(
                    is_blocked=True,
                    action=FilterAction.BLOCK,
                    reason=f"Blocklist match: {blocklist_match}",
                    detection_method="blocklist",
                    masked_prompt=prompt,
                    processing_time=(datetime.now() - start_time).total_seconds(),
                    matched_rules=[{"type": "blocklist", "match": blocklist_match}]
                )
            
            # 3. 필터 규칙 평가
            filter_rules = await self.get_active_filter_rules(context.tenant_id)
            filter_result = await self._evaluate_filter_rules(prompt, filter_rules)
            
            # 4. 결과 통합
            processing_time = (datetime.now() - start_time).total_seconds()
            filter_result.processing_time = processing_time
            filter_result.masked_prompt = await self._apply_masking(prompt, filter_result.matched_rules)
            
            # 5. 로그 저장
            await self._log_decision(context, prompt, filter_result)
            
            return filter_result
            
        except Exception as e:
            logger.error(f"프롬프트 평가 실패: {e}")
            return FilterResult(
                is_blocked=True,
                action=FilterAction.BLOCK,
                reason=f"Evaluation error: {str(e)}",
                detection_method="error",
                masked_prompt=prompt,
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    async def _check_allowlist(self, prompt: str, allowlist: List[Dict[str, Any]]) -> bool:
        """허용 목록 확인"""
        for item in allowlist:
            if item["kind"] == "pattern":
                if re.search(item["value"], prompt, re.IGNORECASE):
                    return True
            elif item["kind"] == "domain":
                if item["value"] in prompt.lower():
                    return True
        return False
    
    async def _check_blocklist(self, prompt: str, blocklist: List[Dict[str, Any]]) -> Optional[str]:
        """차단 목록 확인"""
        for item in blocklist:
            if item["kind"] == "pattern":
                if re.search(item["value"], prompt, re.IGNORECASE):
                    return item["value"]
            elif item["kind"] == "domain":
                if item["value"] in prompt.lower():
                    return item["value"]
        return None
    
    async def _evaluate_filter_rules(self, prompt: str, rules: List[Dict[str, Any]]) -> FilterResult:
        """필터 규칙 평가"""
        matched_rules = []
        highest_risk_score = 0.0
        block_action = None
        detection_methods = []
        
        for rule in rules:
            try:
                if rule["type"] == FilterRuleType.STATIC.value:
                    match_result = await self._evaluate_static_rule(prompt, rule)
                    if match_result:
                        matched_rules.append(match_result)
                        highest_risk_score = max(highest_risk_score, match_result.get("risk_score", 0.0))
                        if rule["action"] == FilterAction.BLOCK.value:
                            block_action = FilterAction.BLOCK
                        detection_methods.append("static")
                
                elif rule["type"] == FilterRuleType.SECRET.value:
                    match_result = await self._evaluate_secret_rule(prompt, rule)
                    if match_result:
                        matched_rules.append(match_result)
                        highest_risk_score = max(highest_risk_score, match_result.get("risk_score", 0.0))
                        if rule["action"] == FilterAction.BLOCK.value:
                            block_action = FilterAction.BLOCK
                        detection_methods.append("secret")
                
                elif rule["type"] == FilterRuleType.PII.value:
                    match_result = await self._evaluate_pii_rule(prompt, rule)
                    if match_result:
                        matched_rules.append(match_result)
                        highest_risk_score = max(highest_risk_score, match_result.get("risk_score", 0.0))
                        if rule["action"] == FilterAction.REDACT.value:
                            block_action = FilterAction.REDACT
                        detection_methods.append("pii")
                
                elif rule["type"] == FilterRuleType.REBUFF.value:
                    match_result = await self._evaluate_rebuff_rule(prompt, rule)
                    if match_result:
                        matched_rules.append(match_result)
                        highest_risk_score = max(highest_risk_score, match_result.get("risk_score", 0.0))
                        if rule["action"] == FilterAction.BLOCK.value:
                            block_action = FilterAction.BLOCK
                        detection_methods.append("rebuff")
                
            except Exception as e:
                logger.error(f"규칙 평가 실패 (ID: {rule['id']}): {e}")
                continue
        
        # 결과 결정
        if block_action == FilterAction.BLOCK:
            is_blocked = True
            action = FilterAction.BLOCK
            reason = f"Blocked by {len(matched_rules)} rules"
        elif block_action == FilterAction.REDACT:
            is_blocked = False
            action = FilterAction.REDACT
            reason = f"Redacted by {len(matched_rules)} rules"
        elif matched_rules:
            is_blocked = False
            action = FilterAction.REQUIRE_APPROVAL
            reason = f"Requires approval due to {len(matched_rules)} matches"
        else:
            is_blocked = False
            action = FilterAction.LOG_ONLY
            reason = "No matches found"
        
        return FilterResult(
            is_blocked=is_blocked,
            action=action,
            reason=reason,
            risk_score=highest_risk_score,
            detection_method=",".join(detection_methods),
            matched_rules=matched_rules
        )
    
    async def _evaluate_static_rule(self, prompt: str, rule: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """정적 규칙 평가"""
        try:
            if re.search(rule["pattern"], prompt, re.IGNORECASE):
                return {
                    "rule_id": rule["id"],
                    "rule_type": rule["type"],
                    "pattern": rule["pattern"],
                    "action": rule["action"],
                    "risk_score": 0.8,
                    "match": "Static pattern match"
                }
        except re.error as e:
            logger.error(f"정적 규칙 패턴 오류 (ID: {rule['id']}): {e}")
        return None
    
    async def _evaluate_secret_rule(self, prompt: str, rule: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """시크릿 규칙 평가"""
        try:
            matches = re.findall(rule["pattern"], prompt)
            if matches:
                return {
                    "rule_id": rule["id"],
                    "rule_type": rule["type"],
                    "pattern": rule["pattern"],
                    "action": rule["action"],
                    "risk_score": 0.9,
                    "match": f"Secret pattern match: {len(matches)} found",
                    "matches": matches[:3]  # 처음 3개만 저장
                }
        except re.error as e:
            logger.error(f"시크릿 규칙 패턴 오류 (ID: {rule['id']}): {e}")
        return None
    
    async def _evaluate_pii_rule(self, prompt: str, rule: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """PII 규칙 평가"""
        try:
            matches = re.findall(rule["pattern"], prompt)
            if matches:
                return {
                    "rule_id": rule["id"],
                    "rule_type": rule["type"],
                    "pattern": rule["pattern"],
                    "action": rule["action"],
                    "risk_score": 0.7,
                    "match": f"PII pattern match: {len(matches)} found",
                    "matches": matches[:3]  # 처음 3개만 저장
                }
        except re.error as e:
            logger.error(f"PII 규칙 패턴 오류 (ID: {rule['id']}): {e}")
        return None
    
    async def _evaluate_rebuff_rule(self, prompt: str, rule: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Rebuff 규칙 평가 (기존 Rebuff SDK 사용)"""
        try:
            # 기존 Rebuff SDK 통합 사용
            from app.rebuff_integration import rebuff_integration
            result = await rebuff_integration.detect_prompt_injection(prompt)
            
            if result["is_injection"]:
                return {
                    "rule_id": rule["id"],
                    "rule_type": rule["type"],
                    "pattern": "rebuff_sdk",
                    "action": rule["action"],
                    "risk_score": result["score"],
                    "match": f"Rebuff injection detected: {', '.join(result['reasons'])}",
                    "rebuff_result": result
                }
        except Exception as e:
            logger.error(f"Rebuff 규칙 평가 실패 (ID: {rule['id']}): {e}")
        return None
    
    async def _apply_masking(self, prompt: str, matched_rules: List[Dict[str, Any]]) -> str:
        """마스킹 적용"""
        masked_prompt = prompt
        
        for rule in matched_rules:
            if rule["action"] == FilterAction.REDACT.value:
                try:
                    if rule["rule_type"] == FilterRuleType.PII.value:
                        # PII 마스킹
                        pattern = rule["pattern"]
                        masked_prompt = re.sub(pattern, "***", masked_prompt)
                    elif rule["rule_type"] == FilterRuleType.SECRET.value:
                        # 시크릿 마스킹
                        pattern = rule["pattern"]
                        masked_prompt = re.sub(pattern, "***", masked_prompt)
                except Exception as e:
                    logger.error(f"마스킹 적용 실패: {e}")
        
        return masked_prompt
    
    async def _log_decision(self, context: RequestContext, prompt: str, result: FilterResult):
        """결정 로그 저장"""
        try:
            db = self.get_db_session()
            
            # decision_logs 테이블에 저장
            query = text("""
                INSERT INTO decision_logs 
                (tenant_id, user_id, ts, route, input_digest, summary, decision, reasons, 
                 bundle_name, bundle_version, policy_channel, latency_ms)
                VALUES 
                (:tenant_id, :user_id, :ts, :route, :input_digest, :summary, :decision, :reasons,
                 :bundle_name, :bundle_version, :policy_channel, :latency_ms)
            """)
            
            # 입력 다이제스트 생성 (민감정보 제외)
            import hashlib
            input_digest = hashlib.sha256(prompt.encode()).hexdigest()[:16]
            
            db.execute(query, {
                "tenant_id": context.tenant_id,
                "user_id": context.user_id,
                "ts": context.timestamp,
                "route": "/prompt/check",
                "input_digest": input_digest,
                "summary": json.dumps({
                    "risk_score": result.risk_score,
                    "detection_method": result.detection_method,
                    "matched_rules_count": len(result.matched_rules)
                }),
                "decision": "deny" if result.is_blocked else "allow",
                "reasons": [result.reason],
                "bundle_name": "promptgate-default",
                "bundle_version": "1.0.0",
                "policy_channel": "prod",
                "latency_ms": int(result.processing_time * 1000)
            })
            
            db.commit()
            logger.debug(f"결정 로그 저장 완료: {context.tenant_id}")
            
        except Exception as e:
            logger.error(f"결정 로그 저장 실패: {e}")
        finally:
            db.close()
    
    def clear_cache(self):
        """캐시 클리어"""
        self.cache.clear()
        logger.info("필터링 엔진 캐시 클리어 완료")
    
    async def get_secret_patterns(self, tenant_id: int = 1) -> Dict[str, List[tuple]]:
        """DB에서 시크릿 패턴 조회"""
        try:
            query = text("""
                SELECT pattern, action, context
                FROM filter_rules 
                WHERE tenant_id = :tenant_id 
                AND type = 'secret' 
                AND enabled = true
                ORDER BY id
            """)
            
            result = self.engine.execute(query, {"tenant_id": tenant_id})
            patterns = result.fetchall()
            
            if not patterns:
                logger.warning(f"테넌트 {tenant_id}에 대한 시크릿 패턴을 찾을 수 없습니다.")
                return {}
            
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
            
            for pattern_row in patterns:
                pattern = pattern_row[0]
                action = pattern_row[1]
                context = pattern_row[2] if pattern_row[2] else {}
                
                # 액션에 따른 심각도 결정
                if action == "block":
                    severity = "HIGH"
                elif action == "redact":
                    severity = "MEDIUM"
                else:
                    severity = "LOW"
                
                # 컨텍스트에서 시크릿 타입 추출
                secret_type = context.get("secret_type", "API_KEY") if isinstance(context, dict) else "API_KEY"
                
                # 패턴 추가
                if secret_type in secret_patterns:
                    secret_patterns[secret_type].append((pattern, severity))
                else:
                    secret_patterns["API_KEY"].append((pattern, severity))
            
            logger.info(f"DB에서 {len(patterns)}개의 시크릿 패턴 로드 완료")
            return secret_patterns
            
        except Exception as e:
            logger.error(f"시크릿 패턴 조회 실패: {e}")
            return {}
    
    async def get_pii_patterns(self, tenant_id: int = 1) -> Dict[str, List[tuple]]:
        """DB에서 PII 패턴 조회"""
        try:
            query = text("""
                SELECT pattern, action, context
                FROM filter_rules 
                WHERE tenant_id = :tenant_id 
                AND type = 'pii' 
                AND enabled = true
                ORDER BY id
            """)
            
            result = self.engine.execute(query, {"tenant_id": tenant_id})
            patterns = result.fetchall()
            
            if not patterns:
                logger.warning(f"테넌트 {tenant_id}에 대한 PII 패턴을 찾을 수 없습니다.")
                return {}
            
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
            
            for pattern_row in patterns:
                pattern = pattern_row[0]
                action = pattern_row[1]
                context = pattern_row[2] if pattern_row[2] else {}
                
                # 액션에 따른 심각도 결정
                if action == "block":
                    severity = "HIGH"
                elif action == "redact":
                    severity = "MEDIUM"
                else:
                    severity = "LOW"
                
                # 컨텍스트에서 PII 타입 추출
                pii_type = context.get("pii_type", "NAME") if isinstance(context, dict) else "NAME"
                
                # 패턴 추가
                if pii_type in pii_patterns:
                    pii_patterns[pii_type].append((pattern, severity))
                else:
                    pii_patterns["NAME"].append((pattern, severity))
            
            logger.info(f"DB에서 {len(patterns)}개의 PII 패턴 로드 완료")
            return pii_patterns
            
        except Exception as e:
            logger.error(f"PII 패턴 조회 실패: {e}")
            return {}

# 전역 인스턴스
_db_filter_engine_instance: Optional[DatabaseFilterEngine] = None

def get_db_filter_engine() -> DatabaseFilterEngine:
    """DB 필터링 엔진 인스턴스 반환"""
    global _db_filter_engine_instance
    
    if _db_filter_engine_instance is None:
        database_url = os.getenv("DATABASE_URL", "postgresql://aigov_user:aigov_password@localhost:5432/aigov_admin")
        _db_filter_engine_instance = DatabaseFilterEngine(database_url)
    
    return _db_filter_engine_instance
