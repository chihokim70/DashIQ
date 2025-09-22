from loguru import logger
from app.services.logger import logger
from typing import Dict
from app.core.security import SensitiveDataFilter
sensitive_filter = SensitiveDataFilter()
# 예시 사용
# masked_request = sensitive_filter.filter_request(req_json)

# Rebuff SDK import
from app.lib.rebuff.sdk import Rebuff  # ← 상대경로로 조정 필요 (위치에 따라 다름)

# Rebuff SDK 인스턴스 생성
rebuff_sdk = Rebuff(
    provider="openai",           # 'openai', 'anthropic' 등
    api_key=None,                # API Key가 필요 없는 로컬 모드
    vector_db="local"            # 'local'로 설정 시 벡터 DB 비활성
)

class PromptFilter:
    def __init__(self):
        self.rebuff = rebuff_sdk

    def check_prompt(self, prompt: str) -> Dict:
        try:
            result = self.rebuff.detect_prompt_injection(prompt)
            return {
                "is_blocked": result.get("is_prompt_injection", False),
                "score": result.get("score", 0),
                "reasons": result.get("reasons", [])
            }
        except Exception as e:
            logger.error(f"[PromptFilter] 검사 실패: {str(e)}")
            return {
                "is_blocked": False,
                "error": str(e)
            }
