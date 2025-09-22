from fastapi import FastAPI, Request
from app.filter import evaluate_prompt
from app.logger import get_logger, log_to_elasticsearch
from app.api import router as api_router
from datetime import datetime

app = FastAPI(title="PromptGate Filter Service", version="1.0.0")
logger = get_logger("filter-service")

# API 라우터 등록
app.include_router(api_router, prefix="/api/v1", tags=["chat"])

@app.post("/prompt/check")
async def check_prompt(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    result = evaluate_prompt(prompt)

    log_to_elasticsearch(
        index="prompt-log",
        document={
             "timestamp": datetime.utcnow().isoformat(),
             "user_id": "root",
             "session_id": "session-001",  # 추후 확장
             "prompt": prompt,
             "masked_prompt": result.get("masked_prompt", ""),
             "is_blocked": result.get("is_blocked"),
             "block_type": result.get("block_type", "none"),
             "reason": result.get("reason", result.get("error", "")),
             "risk_score": result.get("risk_score", None),
             "ai_service": "openai",
             "ip": "127.0.0.1",
              "source": "proxy"
        }
    )  

    logger.info(f"Prompt Check: {prompt} -> {result}")
    return result
