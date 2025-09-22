# main.py

from fastapi import FastAPI, Request, HTTPException
from api import proxy
from pydantic import BaseModel
import httpx # 비동기 HTTP 요청을 위한 라이브러리
import os
import logging
import asyncio

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime )s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- 설정 및 환경 변수 --- #
# 외부 AI 서비스 API 키 (예시)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "your_claude_api_key")

# 외부 AI 서비스 엔드포인트 (예시)
OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"
CLAUDE_CHAT_URL = "https://api.anthropic.com/v1/messages"

# Rebuff SDK 초기화 (설치 필요: pip install rebuff-sdk )
# from rebuff import Rebuff
# rebuff_client = Rebuff(api_key="your_rebuff_api_key") # Rebuff API 키 필요

# --- 데이터 모델 정의 --- #
class PromptRequest(BaseModel):
    user_id: str
    ai_service: str # "openai", "claude" 등
    prompt: str
    # 추가적인 메타데이터 필드
    session_id: str = None
    device_info: str = None

# --- PromptGate 핵심 기능 구현 (Placeholder) --- #

async def filter_prompt(prompt: str, user_id: str) -> (bool, str, str):
    """
    프롬프트 필터링 로직을 구현합니다.
    프롬프트 인젝션 탐지, 금지 키워드 차단 등을 수행합니다.
    반환값: (필터링 성공 여부, 필터링된 프롬프트, 탐지된 위협 유형 또는 메시지)
    """
    logger.info(f"[Filter] Filtering prompt for user {user_id}: {prompt[:50]}...")
    # TODO: Rebuff Python-SDK 연동 및 프롬프트 인젝션 탐지 로직 추가
    # is_injection = rebuff_client.detect_injection(prompt)
    # if is_injection:
    #     return False, prompt, "Prompt Injection Detected"

    # TODO: 금지 키워드/문구 차단 로직 추가
    forbidden_keywords = ["기밀", "내부 문서 유출", "개인 정보 추출"]
    for keyword in forbidden_keywords:
        if keyword in prompt:
            return False, prompt, f"Forbidden keyword '{keyword}' detected"

    return True, prompt, "No threats detected"

async def mask_sensitive_info(prompt: str) -> (str, dict):
    """
    프롬프트 내 민감 정보를 마스킹합니다.
    반환값: (마스킹된 프롬프트, 마스킹된 정보 유형 및 원본 값 딕셔너리)
    """
    logger.info(f"[Mask] Masking sensitive info in prompt: {prompt[:50]}...")
    masked_prompt = prompt
    masked_details = {}

    # TODO: 주민등록번호, 전화번호, 이메일 등 PII 탐지 및 마스킹 로직 추가
    # 예시: 간단한 이메일 마스킹
    import re
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    found_emails = re.findall(email_pattern, masked_prompt)
    for email in found_emails:
        masked_prompt = masked_prompt.replace(email, "[MASKED_EMAIL]")
        masked_details["email"] = email # 실제로는 원본 값 저장 시 주의 필요

    # TODO: 기업 기밀 용어 탐지 및 마스킹 로직 추가
    confidential_terms = ["Project X", "Confidential Data"]
    for term in confidential_terms:
        if term in masked_prompt:
            masked_prompt = masked_prompt.replace(term, "[MASKED_CONFIDENTIAL]")
            masked_details["confidential_term"] = term

    return masked_prompt, masked_details

async def log_ai_usage(log_data: dict):
    """
    AI 사용 로그를 기록하고 DashIQ로 전송합니다.
    """
    logger.info(f"[Log] Logging AI usage: {log_data}")
    # TODO: DashIQ 모듈로 로그 전송 로직 구현 (HTTP 요청, 메시지 큐 등)
    # 예시: 간단히 파일에 저장하거나 콘솔에 출력
    with open("ai_usage.log", "a") as f:
        f.write(f"{log_data}\n")
    logger.info("Log saved to ai_usage.log")

# --- FastAPI 애플리케이션 인스턴스 생성 --- #
app = FastAPI(title="KRA-AiGov PromptGate", version="0.1.0")

# --- API 엔드포인트 정의 --- #
@app.post("/process_prompt")
async def process_prompt(request: PromptRequest):
    original_prompt = request.prompt
    user_id = request.user_id
    ai_service = request.ai_service

    logger.info(f"Received request from {user_id} for {ai_service}: {original_prompt[:50]}...")

    # 1. 프롬프트 필터링
    is_allowed, filtered_prompt, filter_message = await filter_prompt(original_prompt, user_id)
    if not is_allowed:
        log_data = {
            "user_id": user_id,
            "ai_service": ai_service,
            "original_prompt": original_prompt,
            "masked_prompt": "N/A",
            "ai_response": "N/A",
            "status": "BLOCKED",
            "reason": filter_message,
            "timestamp": asyncio.current_task()._loop.time() # 임시 타임스탬프
        }
        await log_ai_usage(log_data)
        raise HTTPException(status_code=403, detail=f"Prompt blocked: {filter_message}")

    # 2. 민감 정보 마스킹
    masked_prompt, masked_details = await mask_sensitive_info(filtered_prompt)

    # 3. 외부 AI 서비스로 요청 전송 (Placeholder)
    ai_response = ""
    status = "SUCCESS"
    try:
        async with httpx.AsyncClient( ) as client:
            if ai_service == "openai":
                headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
                payload = {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": masked_prompt}]}
                response = await client.post(OPENAI_CHAT_URL, headers=headers, json=payload, timeout=60)
                response.raise_for_status()
                ai_response = response.json()["choices"][0]["message"]["content"]
            elif ai_service == "claude":
                headers = {"x-api-key": CLAUDE_API_KEY, "Content-Type": "application/json", "anthropic-version": "2023-06-01"}
                payload = {"model": "claude-3-opus-20240229", "messages": [{"role": "user", "content": masked_prompt}]}
                response = await client.post(CLAUDE_CHAT_URL, headers=headers, json=payload, timeout=60)
                response.raise_for_status()
                ai_response = response.json()["content"][0]["text"]
            else:
                raise HTTPException(status_code=400, detail="Unsupported AI service")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error during AI service call: {e.response.status_code} - {e.response.text}" )
        ai_response = f"Error: AI service returned status {e.response.status_code}"
        status = "AI_SERVICE_ERROR"
        raise HTTPException(status_code=500, detail="Failed to get response from AI service")
    except httpx.RequestError as e:
        logger.error(f"Request error during AI service call: {e}" )
        ai_response = f"Error: Could not connect to AI service"
        status = "NETWORK_ERROR"
        raise HTTPException(status_code=500, detail="Failed to connect to AI service")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        ai_response = f"Error: An unexpected error occurred"
        status = "UNEXPECTED_ERROR"
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

    # 4. 응답 필터링 (선택 사항: MVP 이후 고려)
    # is_response_allowed, final_response, response_filter_message = await filter_response(ai_response)
    # if not is_response_allowed:
    #     ai_response = "Response blocked due to policy violation."
    #     status = "RESPONSE_BLOCKED"

    # 5. AI 사용 로그 기록
    log_data = {
        "user_id": user_id,
        "ai_service": ai_service,
        "original_prompt": original_prompt,
        "masked_prompt": masked_prompt,
        "masked_details": masked_details,
        "ai_response": ai_response,
        "status": status,
        "filter_message": filter_message if not is_allowed else "N/A",
        "timestamp": asyncio.current_task()._loop.time() # 임시 타임스탬프
    }
    await log_ai_usage(log_data)

    return {"status": "success", "response": ai_response}

# --- 애플리케이션 실행 (개발용) --- #
# 이 파일이 직접 실행될 때만 uvicorn을 실행합니다.
# 실제 배포 시에는 `uvicorn main:app --host 0.0.0.0 --port 8000` 명령어를 사용합니다.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

