"""
DB 기반 정책 관리 시스템
Admin Portal에서 정의한 정책을 DB에 저장하고 OPA가 읽어서 실행
"""

import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.schema import get_db
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
import os

logger = logging.getLogger(__name__)

class PolicyRuleType(Enum):
    DENY_PATTERN = "deny_pattern"
    PII_PATTERN = "pii_pattern"
    SECRET_PATTERN = "secret_pattern"
    LENGTH_LIMIT = "length_limit"
    LANGUAGE_LIMIT = "language_limit"
    CUSTOM_RULE = "custom_rule"

class PolicySeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class PolicyRuleData:
    tenant_id: str
    rule_name: str
    rule_type: PolicyRuleType
    rule_pattern: str
    rule_value: str
    severity: PolicySeverity
    action: str
    is_active: bool = True
    policy_id: Optional[int] = None
    created_by: Optional[int] = None

@dataclass
class PolicyActionData:
    tenant_id: str
    action_name: str
    action_type: str
    action_config: Dict[str, Any]
    is_active: bool = True
    policy_id: Optional[int] = None
    created_by: Optional[int] = None

class DatabasePolicyManager:
    """DB 기반 정책 관리자"""
    
    def __init__(self):
        self.policy_engine = None
        logger.info("DB 기반 정책 관리자 초기화 완료")
    
    async def initialize(self):
        """정책 관리자 초기화"""
        try:
            self.policy_engine = PolicyEngine()
            await self.policy_engine.initialize()
            logger.info("DB 기반 정책 관리자 초기화 성공")
            return True
        except Exception as e:
            logger.error(f"정책 관리자 초기화 실패: {e}")
            return False
    
    def create_policy_rule(self, db: Session, rule_data: PolicyRuleData) -> bool:
        """정책 규칙 생성"""
        try:
            policy_rule = PolicyRule(
                tenant_id=rule_data.tenant_id,
                rule_name=rule_data.rule_name,
                rule_type=rule_data.rule_type.value,
                rule_pattern=rule_data.rule_pattern,
                rule_value=rule_data.rule_value,
                severity=rule_data.severity.value,
                action=rule_data.action,
                is_active=rule_data.is_active,
                policy_id=rule_data.policy_id,
                created_by=rule_data.created_by
            )
            
            db.add(policy_rule)
            db.commit()
            
            # 감사 로그 기록
            self._log_policy_action(
                db=db,
                tenant_id=rule_data.tenant_id,
                policy_id=policy_rule.id,
                action_type="create",
                action_details={"rule_name": rule_data.rule_name, "rule_type": rule_data.rule_type.value},
                user_id=rule_data.created_by
            )
            
            logger.info(f"정책 규칙 생성 완료: {rule_data.rule_name}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"정책 규칙 생성 실패: {e}")
            return False
    
    def update_policy_rule(self, db: Session, rule_id: int, rule_data: PolicyRuleData) -> bool:
        """정책 규칙 업데이트"""
        try:
            policy_rule = db.query(PolicyRule).filter(PolicyRule.id == rule_id).first()
            if not policy_rule:
                logger.error(f"정책 규칙을 찾을 수 없습니다: {rule_id}")
                return False
            
            # 기존 값 저장 (감사 로그용)
            old_values = {
                "rule_name": policy_rule.rule_name,
                "rule_pattern": policy_rule.rule_pattern,
                "rule_value": policy_rule.rule_value,
                "severity": policy_rule.severity,
                "action": policy_rule.action,
                "is_active": policy_rule.is_active
            }
            
            # 값 업데이트
            policy_rule.rule_name = rule_data.rule_name
            policy_rule.rule_type = rule_data.rule_type.value
            policy_rule.rule_pattern = rule_data.rule_pattern
            policy_rule.rule_value = rule_data.rule_value
            policy_rule.severity = rule_data.severity.value
            policy_rule.action = rule_data.action
            policy_rule.is_active = rule_data.is_active
            policy_rule.updated_at = datetime.utcnow()
            
            db.commit()
            
            # 감사 로그 기록
            self._log_policy_action(
                db=db,
                tenant_id=policy_rule.tenant_id,
                policy_id=policy_rule.id,
                action_type="update",
                action_details={
                    "rule_name": rule_data.rule_name,
                    "old_values": old_values,
                    "new_values": {
                        "rule_name": rule_data.rule_name,
                        "rule_pattern": rule_data.rule_pattern,
                        "rule_value": rule_data.rule_value,
                        "severity": rule_data.severity.value,
                        "action": rule_data.action,
                        "is_active": rule_data.is_active
                    }
                },
                user_id=rule_data.created_by
            )
            
            logger.info(f"정책 규칙 업데이트 완료: {rule_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"정책 규칙 업데이트 실패: {e}")
            return False
    
    def delete_policy_rule(self, db: Session, rule_id: int, user_id: int) -> bool:
        """정책 규칙 삭제"""
        try:
            policy_rule = db.query(PolicyRule).filter(PolicyRule.id == rule_id).first()
            if not policy_rule:
                logger.error(f"정책 규칙을 찾을 수 없습니다: {rule_id}")
                return False
            
            tenant_id = policy_rule.tenant_id
            rule_name = policy_rule.rule_name
            
            db.delete(policy_rule)
            db.commit()
            
            # 감사 로그 기록
            self._log_policy_action(
                db=db,
                tenant_id=tenant_id,
                policy_id=rule_id,
                action_type="delete",
                action_details={"rule_name": rule_name},
                user_id=user_id
            )
            
            logger.info(f"정책 규칙 삭제 완료: {rule_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"정책 규칙 삭제 실패: {e}")
            return False
    
    def get_policy_rules(self, db: Session, tenant_id: str, is_active: bool = True) -> List[PolicyRule]:
        """테넌트별 정책 규칙 조회"""
        try:
            query = db.query(PolicyRule).filter(PolicyRule.tenant_id == tenant_id)
            if is_active is not None:
                query = query.filter(PolicyRule.is_active == is_active)
            
            return query.order_by(PolicyRule.created_at.desc()).all()
            
        except Exception as e:
            logger.error(f"정책 규칙 조회 실패: {e}")
            return []
    
    def get_policy_rule(self, db: Session, rule_id: int) -> Optional[PolicyRule]:
        """정책 규칙 상세 조회"""
        try:
            return db.query(PolicyRule).filter(PolicyRule.id == rule_id).first()
        except Exception as e:
            logger.error(f"정책 규칙 상세 조회 실패: {e}")
            return None
    
    def create_policy_action(self, db: Session, action_data: PolicyActionData) -> bool:
        """정책 액션 생성"""
        try:
            policy_action = PolicyAction(
                tenant_id=action_data.tenant_id,
                action_name=action_data.action_name,
                action_type=action_data.action_type,
                action_config=json.dumps(action_data.action_config),
                is_active=action_data.is_active,
                policy_id=action_data.policy_id,
                created_by=action_data.created_by
            )
            
            db.add(policy_action)
            db.commit()
            
            logger.info(f"정책 액션 생성 완료: {action_data.action_name}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"정책 액션 생성 실패: {e}")
            return False
    
    def get_policy_actions(self, db: Session, tenant_id: str, is_active: bool = True) -> List[PolicyAction]:
        """테넌트별 정책 액션 조회"""
        try:
            query = db.query(PolicyAction).filter(PolicyAction.tenant_id == tenant_id)
            if is_active is not None:
                query = query.filter(PolicyAction.is_active == is_active)
            
            return query.order_by(PolicyAction.created_at.desc()).all()
            
        except Exception as e:
            logger.error(f"정책 액션 조회 실패: {e}")
            return []
    
    async def deploy_policy_to_opa(self, db: Session, tenant_id: str) -> bool:
        """DB의 정책을 OPA에 배포"""
        try:
            # DB에서 정책 규칙 조회
            rules = self.get_policy_rules(db, tenant_id, is_active=True)
            actions = self.get_policy_actions(db, tenant_id, is_active=True)
            
            # OPA 정책 형식으로 변환
            opa_policy = self._convert_to_opa_policy(rules, actions)
            
            # OPA에 정책 업로드
            if self.policy_engine:
                await self.policy_engine.add_policy(tenant_id, opa_policy)
            
            # 감사 로그 기록
            self._log_policy_action(
                db=db,
                tenant_id=tenant_id,
                policy_id=None,
                action_type="deploy",
                action_details={"rules_count": len(rules), "actions_count": len(actions)},
                user_id=None
            )
            
            logger.info(f"정책 배포 완료: {tenant_id}")
            return True
            
        except Exception as e:
            logger.error(f"정책 배포 실패: {e}")
            return False
    
    def _convert_to_opa_policy(self, rules: List[PolicyRule], actions: List[PolicyAction]) -> Dict[str, Any]:
        """DB 정책을 OPA 정책 형식으로 변환"""
        opa_policy = {
            "rules": {
                "deny_patterns": [],
                "pii_patterns": [],
                "secret_patterns": [],
                "max_prompt_length": 4000,
                "allowed_languages": ["ko", "en"]
            },
            "actions": {
                "suspicious": "sanitize",
                "pii_found": "mask",
                "secrets_found": "deny",
                "injection_detected": "deny",
                "default": "allow"
            }
        }
        
        # 규칙 변환
        for rule in rules:
            if rule.rule_type == PolicyRuleType.DENY_PATTERN.value:
                opa_policy["rules"]["deny_patterns"].append(rule.rule_pattern)
            elif rule.rule_type == PolicyRuleType.PII_PATTERN.value:
                opa_policy["rules"]["pii_patterns"].append(rule.rule_pattern)
            elif rule.rule_type == PolicyRuleType.SECRET_PATTERN.value:
                opa_policy["rules"]["secret_patterns"].append(rule.rule_pattern)
            elif rule.rule_type == PolicyRuleType.LENGTH_LIMIT.value:
                opa_policy["rules"]["max_prompt_length"] = int(rule.rule_value)
            elif rule.rule_type == PolicyRuleType.LANGUAGE_LIMIT.value:
                opa_policy["rules"]["allowed_languages"] = json.loads(rule.rule_value)
        
        # 액션 변환
        for action in actions:
            try:
                action_config = json.loads(action.action_config)
                opa_policy["actions"][action.action_name] = action.action_type
            except:
                opa_policy["actions"][action.action_name] = action.action_type
        
        return opa_policy
    
    def _log_policy_action(self, db: Session, tenant_id: str, policy_id: Optional[int], 
                          action_type: str, action_details: Dict[str, Any], user_id: Optional[int]):
        """정책 액션 감사 로그 기록"""
        try:
            audit_log = PolicyAuditLog(
                tenant_id=tenant_id,
                policy_id=policy_id,
                action_type=action_type,
                action_details=json.dumps(action_details),
                user_id=user_id
            )
            
            db.add(audit_log)
            db.commit()
            
        except Exception as e:
            logger.error(f"감사 로그 기록 실패: {e}")
    
    def get_policy_audit_logs(self, db: Session, tenant_id: str, limit: int = 100) -> List[PolicyAuditLog]:
        """정책 감사 로그 조회"""
        try:
            return db.query(PolicyAuditLog)\
                .filter(PolicyAuditLog.tenant_id == tenant_id)\
                .order_by(PolicyAuditLog.created_at.desc())\
                .limit(limit)\
                .all()
        except Exception as e:
            logger.error(f"감사 로그 조회 실패: {e}")
            return []
    
    async def evaluate_policy_from_db(self, db: Session, context: RequestContext, prompt: str, 
                                    filter_results: List[Dict[str, Any]] = None) -> PolicyResult:
        """DB에서 정책을 읽어서 평가"""
        try:
            # DB에서 정책 규칙 조회
            rules = self.get_policy_rules(db, context.tenant_id, is_active=True)
            actions = self.get_policy_actions(db, context.tenant_id, is_active=True)
            
            # OPA 정책 형식으로 변환
            opa_policy = self._convert_to_opa_policy(rules, actions)
            
            # 임시로 정책 엔진에 로드
            if self.policy_engine:
                await self.policy_engine.add_policy(context.tenant_id, opa_policy)
                return await self.policy_engine.evaluate(context, prompt, filter_results)
            else:
                # Fallback: 로컬 평가
                return await self._evaluate_locally(rules, actions, context, prompt, filter_results)
                
        except Exception as e:
            logger.error(f"DB 정책 평가 실패: {e}")
            return PolicyResult(
                action=PolicyActionEnum.DENY,
                reason=f"Policy evaluation failed: {str(e)}",
                confidence=0.0
            )
    
    async def _evaluate_locally(self, rules: List[PolicyRule], actions: List[PolicyAction],
                              context: RequestContext, prompt: str, filter_results: List[Dict[str, Any]] = None) -> PolicyResult:
        """로컬 정책 평가 (Fallback)"""
        import re
        
        violations = []
        
        for rule in rules:
            if rule.rule_type == PolicyRuleType.DENY_PATTERN.value:
                if re.search(rule.rule_pattern, prompt, re.IGNORECASE):
                    violations.append(f"deny_pattern: {rule.rule_name}")
            elif rule.rule_type == PolicyRuleType.PII_PATTERN.value:
                if re.search(rule.rule_pattern, prompt):
                    violations.append(f"pii_pattern: {rule.rule_name}")
            elif rule.rule_type == PolicyRuleType.SECRET_PATTERN.value:
                if re.search(rule.rule_pattern, prompt):
                    violations.append(f"secret_pattern: {rule.rule_name}")
            elif rule.rule_type == PolicyRuleType.LENGTH_LIMIT.value:
                if len(prompt) > int(rule.rule_value):
                    violations.append(f"length_limit: {rule.rule_name}")
        
        # 액션 결정
        if violations:
            if any("secret_pattern" in v for v in violations):
                return PolicyResult(action=PolicyActionEnum.DENY, reason="Secret pattern detected", violations=violations)
            elif any("pii_pattern" in v for v in violations):
                return PolicyResult(action=PolicyActionEnum.MASK, reason="PII pattern detected", violations=violations)
            elif any("deny_pattern" in v for v in violations):
                return PolicyResult(action=PolicyActionEnum.DENY, reason="Deny pattern detected", violations=violations)
            else:
                return PolicyResult(action=PolicyActionEnum.ALERT, reason="Policy violations detected", violations=violations)
        else:
            return PolicyResult(action=PolicyActionEnum.ALLOW, reason="Policy evaluation passed")

# 전역 DB 정책 관리자 인스턴스
_db_policy_manager_instance: Optional[DatabasePolicyManager] = None

async def get_db_policy_manager() -> DatabasePolicyManager:
    """DB 정책 관리자 인스턴스 반환 (싱글톤)"""
    global _db_policy_manager_instance
    
    if _db_policy_manager_instance is None:
        _db_policy_manager_instance = DatabasePolicyManager()
        await _db_policy_manager_instance.initialize()
    
    return _db_policy_manager_instance

async def close_db_policy_manager():
    """DB 정책 관리자 정리"""
    global _db_policy_manager_instance
    
    if _db_policy_manager_instance:
        _db_policy_manager_instance = None
        logger.info("DB 정책 관리자 정리 완료")
