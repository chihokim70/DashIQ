import re
from typing import Dict, Any

class SensitiveDataFilter:
    def __init__(self):
        # 민감 정보 패턴 정의 (예: 이메일, 카드번호, 주민번호 등)
        self.patterns = {
            "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "card": r"\b(?:\d[ -]*?){13,16}\b",
            "ssn": r"\b\d{6}-\d{7}\b",
            "password": r"(?i)(password|passwd|pwd)[\s:=]+[^\s]+"
        }

    def mask_text(self, text: str) -> str:
        for label, pattern in self.patterns.items():
            text = re.sub(pattern, f"[MASKED_{label.upper()}]", text)
        return text

    def filter_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        filtered = {}
        for key, value in data.items():
            if isinstance(value, str):
                filtered[key] = self.mask_text(value)
            else:
                filtered[key] = value  # TODO: 리스트, 중첩 dict도 지원 가능
        return filtered

    def filter_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.filter_request(data)  # 동일 처리 (응답에도 마스킹 적용)
