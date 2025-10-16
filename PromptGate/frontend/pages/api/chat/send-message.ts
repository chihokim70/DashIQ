import { NextApiRequest, NextApiResponse } from 'next';
// import { evaluate_prompt } from '@/lib/filter-helpers';

interface ChatRequest {
  message: string;
  llmProvider: string;
  userId: string;
}

interface ChatResponse {
  response?: string;
  isBlocked: boolean;
  reason?: string;
  llmProvider?: string;
  processingTime?: number;
}

// LLM API 클라이언트들 (실제 구현에서는 각 LLM의 API 키가 필요)
const LLM_CLIENTS = {
  chatgpt: {
    name: 'ChatGPT',
    apiKey: process.env.OPENAI_API_KEY,
    endpoint: 'https://api.openai.com/v1/chat/completions'
  },
  claude: {
    name: 'Claude',
    apiKey: process.env.ANTHROPIC_API_KEY,
    endpoint: 'https://api.anthropic.com/v1/messages'
  },
  gemini: {
    name: 'Gemini',
    apiKey: process.env.GOOGLE_API_KEY,
    endpoint: 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'
  }
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<ChatResponse>
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ 
      isBlocked: true, 
      reason: 'Method not allowed' 
    });
  }

  try {
    const { message, llmProvider, userId }: ChatRequest = req.body;

    if (!message || !llmProvider || !userId) {
      return res.status(400).json({
        isBlocked: true,
        reason: 'Missing required fields'
      });
    }

    // 1. 프롬프트 보안 필터링 (백엔드 API 호출)
    console.log(`[Chat API] 프롬프트 필터링 시작: ${message.substring(0, 50)}...`);
    
    try {
      const filterResponse = await fetch('http://localhost:8001/prompt/check', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: message,
          user_id: parseInt(userId) || 1,
          session_id: `session_${Date.now()}`,
          ip_address: req.headers['x-forwarded-for'] as string || req.connection.remoteAddress || 'unknown',
          user_agent: req.headers['user-agent'] || 'unknown'
        }),
      });

      const filterResult = await filterResponse.json();

      // 2. 필터링 결과 확인
      if (filterResult.is_blocked) {
        console.log(`[Chat API] 프롬프트 차단됨: ${filterResult.reason}`);
        return res.status(200).json({
          isBlocked: true,
          reason: filterResult.reason,
          processingTime: filterResult.processing_time
        });
      }
    } catch (error) {
      console.error('[Chat API] 필터링 서비스 연결 실패:', error);
      // 필터링 서비스가 연결되지 않은 경우 경고하지만 계속 진행
      console.warn('[Chat API] 필터링 서비스 없이 진행합니다.');
    }

    // 3. LLM 클라이언트 확인
    const llmClient = LLM_CLIENTS[llmProvider as keyof typeof LLM_CLIENTS];
    if (!llmClient) {
      return res.status(400).json({
        isBlocked: true,
        reason: `지원하지 않는 LLM 프로바이더: ${llmProvider}`
      });
    }

    // 4. LLM API 호출 (실제 구현에서는 각 LLM의 API를 호출)
    console.log(`[Chat API] LLM 호출 시작: ${llmClient.name}`);
    
    let llmResponse: string;
    
    try {
      // 실제 LLM API 호출 로직 (현재는 Mock 응답)
      llmResponse = await callLLMAPI(llmClient, message);
    } catch (error) {
      console.error(`[Chat API] LLM 호출 실패:`, error);
      return res.status(500).json({
        isBlocked: true,
        reason: 'LLM 서비스 오류가 발생했습니다'
      });
    }

    // 5. 응답 반환
    console.log(`[Chat API] 응답 생성 완료: ${llmClient.name}`);
    
    return res.status(200).json({
      response: llmResponse,
      isBlocked: false,
      llmProvider: llmClient.name,
      processingTime: 0.5 // Mock 처리 시간
    });

  } catch (error) {
    console.error('[Chat API] 오류 발생:', error);
    return res.status(500).json({
      isBlocked: true,
      reason: '서버 오류가 발생했습니다'
    });
  }
}

// LLM API 호출 함수 (실제 구현)
async function callLLMAPI(client: any, message: string): Promise<string> {
  // 실제 구현에서는 각 LLM의 API를 호출
  // 현재는 Mock 응답을 반환
  
  const mockResponses = {
    chatgpt: `안녕하세요! ChatGPT입니다. "${message}"에 대한 답변을 드리겠습니다.\n\n이는 AiGov 보안 필터링을 통과한 안전한 응답입니다.`,
    claude: `안녕하세요! Claude입니다. "${message}"에 대해 답변드리겠습니다.\n\nAiGov의 보안 정책에 따라 검토된 안전한 응답입니다.`,
    gemini: `안녕하세요! Gemini입니다. "${message}"에 대한 답변입니다.\n\n보안 필터링을 통과한 신뢰할 수 있는 응답입니다.`
  };

  // 실제 API 호출 시뮬레이션 (지연)
  await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));

  return mockResponses[client.name.toLowerCase() as keyof typeof mockResponses] || 
         `안녕하세요! ${client.name}입니다. "${message}"에 대한 답변을 드리겠습니다.`;
}
