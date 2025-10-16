import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Shield, AlertTriangle } from 'lucide-react';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  isBlocked?: boolean;
  blockReason?: string;
  llmProvider?: string;
}

interface ChatInterfaceProps {
  className?: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ className = '' }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: '안녕하세요! 저는 AiGov의 AI 어시스턴트입니다. 어떤 도움이 필요하신가요?',
      role: 'assistant',
      timestamp: new Date(),
      llmProvider: 'ChatGPT'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedLLM, setSelectedLLM] = useState('chatgpt');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      role: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // 백엔드 API 호출 (프롬프트 필터링 + LLM 프록시)
      const response = await fetch('/api/chat/send-message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          llmProvider: selectedLLM,
          userId: 'current_user' // 실제로는 인증된 사용자 ID
        }),
      });

      const data = await response.json();

      if (data.isBlocked) {
        // 프롬프트가 차단된 경우
        const blockedMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: `⚠️ 보안 정책에 의해 메시지가 차단되었습니다.\n\n사유: ${data.reason}`,
          role: 'assistant',
          timestamp: new Date(),
          isBlocked: true,
          blockReason: data.reason,
          llmProvider: 'Security Filter'
        };
        setMessages(prev => [...prev, blockedMessage]);
      } else {
        // 정상 응답
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: data.response,
          role: 'assistant',
          timestamp: new Date(),
          llmProvider: data.llmProvider || selectedLLM
        };
        setMessages(prev => [...prev, assistantMessage]);
      }
    } catch (error) {
      console.error('메시지 전송 오류:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: '죄송합니다. 오류가 발생했습니다. 다시 시도해 주세요.',
        role: 'assistant',
        timestamp: new Date(),
        llmProvider: 'Error'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('ko-KR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className={`flex flex-col h-full bg-white ${className}`}>
      {/* 헤더 */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-gray-900">AiGov AI Assistant</h1>
            <p className="text-sm text-gray-500">보안 필터링된 AI 채팅</p>
          </div>
        </div>
        
        {/* LLM 선택기 */}
        <div className="flex items-center space-x-2">
          <label className="text-sm text-gray-600">AI 모델:</label>
          <select
            value={selectedLLM}
            onChange={(e) => setSelectedLLM(e.target.value)}
            className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="chatgpt">ChatGPT</option>
            <option value="claude">Claude</option>
            <option value="gemini">Gemini</option>
          </select>
        </div>
      </div>

      {/* 메시지 목록 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : message.isBlocked
                  ? 'bg-red-50 border border-red-200 text-red-800'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <div className="flex items-start space-x-2">
                {message.role === 'assistant' && (
                  <div className="flex-shrink-0">
                    {message.isBlocked ? (
                      <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5" />
                    ) : (
                      <Bot className="w-4 h-4 text-gray-500 mt-0.5" />
                    )}
                  </div>
                )}
                <div className="flex-1">
                  <div className="whitespace-pre-wrap">{message.content}</div>
                  <div className="flex items-center justify-between mt-1">
                    <span className="text-xs opacity-70">
                      {formatTime(message.timestamp)}
                    </span>
                    {message.llmProvider && (
                      <span className="text-xs opacity-70">
                        {message.llmProvider}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 px-4 py-2 rounded-lg">
              <div className="flex items-center space-x-2">
                <Bot className="w-4 h-4 text-gray-500" />
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* 입력 영역 */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <div className="flex items-end space-x-2">
          <div className="flex-1">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="메시지를 입력하세요... (Shift+Enter로 줄바꿈)"
              className="w-full px-3 py-2 border border-gray-300 rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={1}
              style={{ minHeight: '40px', maxHeight: '120px' }}
              disabled={isLoading}
            />
          </div>
          <button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-1"
          >
            <Send className="w-4 h-4" />
            <span>전송</span>
          </button>
        </div>
        
        {/* 보안 상태 표시 */}
        <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
          <div className="flex items-center space-x-1">
            <Shield className="w-3 h-3" />
            <span>모든 메시지는 보안 필터링됩니다</span>
          </div>
          <span>메시지 {messages.length}개</span>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;



