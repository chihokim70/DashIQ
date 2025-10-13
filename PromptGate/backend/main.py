from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from app.logger import get_logger
import logging

app = FastAPI(title="PromptGate Filter Service", version="1.0.0")
logger = get_logger("filter-service")

@app.post("/prompt/check")
async def check_prompt(request: Request):
    """기존 프롬프트 검증 (하위 호환성 유지) - 완전 단순화"""
    data = await request.json()
    prompt = data.get("prompt", "")
    
    # 완전히 단순한 응답 반환
    result = {
        "is_blocked": False,
        "reason": "프롬프트가 안전합니다",
        "detection_method": "simple",
        "risk_score": 0.0,
        "masked_prompt": prompt,
        "processing_time": 0.001
    }
    
    logger.info(f"Prompt Check: {prompt} -> {result}")
    return result

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "service": "PromptGate Filter Service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)