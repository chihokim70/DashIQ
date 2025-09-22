from fastapi import APIRouter, Request, HTTPException
from app.core.filter import PromptFilter
from app.services.logger import logger, log_to_elasticsearch
from datetime import datetime

router = APIRouter()
prompt_filter = PromptFilter()

@router.post("/proxy")
async def proxy_prompt(request: Request):
    try:
        req_json = await request.json()
        prompt = req_json.get("prompt", "")

        # ✅ 프롬프트 검사
        result = prompt_filter.check_prompt(prompt)

        # ✅ 로그 저장 (Elasticsearch)
        log_to_elasticsearch("prompt-logs", {
            "prompt": prompt,
            "blocked": result.get("is_blocked"),
            "score": result.get("score"),
            "reasons": result.get("reasons"),
            "timestamp": str(datetime.utcnow())
        })

        if result.get("is_blocked"):
            logger.info("프롬프트 검사 결과: 보안정책에 의해 차단됨")
            return {
                "status": "blocked",
                "score": result.get("score"),
                "reasons": result.get("reasons")
            }

        # 🧠 실제 AI 호출은 추후 여기 추가
        return {
            "status": "allowed",
            "original_prompt": prompt
        }

    except Exception as e:
        logger.error(f"[proxy] 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
