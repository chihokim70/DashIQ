import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Shield, AlertTriangle, Settings, Menu, X } from 'lucide-react';
import MessageItem from '@/components/chat/MessageItem';
import MessageInput from '@/components/chat/MessageInput';
import LLMSelector from '@/components/chat/LLMSelector';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  isBlocked?: boolean;
  blockReason?: string;
  llmProvider?: string;
}

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: '안녕하세요! 저는 AiGov의 AI 어시스턴트입니다. 어떤 도움이 필요하신가요?\n\n모든 대화는 보안 정책에 따라 필터링되며, 안전하게 진행됩니다.',
      role: 'assistant',
      timestamp: new Date(),
      llmProvider: 'ChatGPT'
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedLLM, setSelectedLLM] = useState('chatgpt');
  const [showSidebar, setShowSidebar] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (message: string) => {
    if (!message.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: message,
      role: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // 백엔드 API 호출 (프롬프트 필터링 + LLM 프록시)
      const response = await fetch('/api/chat/send-message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          llmProvider: selectedLLM,
          userId: 'current_user' // 실제로는 인증된 사용자 ID
        }),
      });

      const data = await response.json();

      if (data.isBlocked) {
        // 프롬프트가 차단된 경우
        const blockedMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: `⚠️ 보안 정책에 의해 메시지가 차단되었습니다.\n\n사유: ${data.reason}\n\n다른 방식으로 질문해 주시거나, 관리자에게 문의해 주세요.`,
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
        content: '죄송합니다. 오류가 발생했습니다. 다시 시도해 주세요.\n\n문제가 지속되면 관리자에게 문의해 주세요.',
        role: 'assistant',
        timestamp: new Date(),
        llmProvider: 'Error'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: '1',
        content: '대화가 초기화되었습니다. 새로운 질문을 해주세요!',
        role: 'assistant',
        timestamp: new Date(),
        llmProvider: selectedLLM
      }
    ]);
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* 사이드바 */}
      <div className={`${showSidebar ? 'translate-x-0' : '-translate-x-full'} fixed inset-y-0 left-0 z-50 w-80 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0`}>
        <div className="flex flex-col h-full">
          {/* 사이드바 헤더 */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">AiGov Chat</h2>
            <button
              onClick={() => setShowSidebar(false)}
              className="lg:hidden p-1 text-gray-400 hover:text-gray-600"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* LLM 선택기 */}
          <div className="p-4">
            <LLMSelector
              selectedProvider={selectedLLM}
              onProviderChange={setSelectedLLM}
            />
          </div>

          {/* 채팅 관리 */}
          <div className="p-4 border-t border-gray-200">
            <button
              onClick={clearChat}
              className="w-full px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              대화 초기화
            </button>
          </div>

          {/* 통계 정보 */}
          <div className="flex-1 p-4">
            <div className="bg-gray-50 rounded-lg p-3">
              <h3 className="text-sm font-medium text-gray-900 mb-2">대화 통계</h3>
              <div className="space-y-2 text-xs text-gray-600">
                <div className="flex justify-between">
                  <span>총 메시지</span>
                  <span>{messages.length}개</span>
                </div>
                <div className="flex justify-between">
                  <span>차단된 메시지</span>
                  <span>{messages.filter(m => m.isBlocked).length}개</span>
                </div>
                <div className="flex justify-between">
                  <span>현재 모델</span>
                  <span className="capitalize">{selectedLLM}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 메인 채팅 영역 */}
      <div className="flex-1 flex flex-col">
        {/* 헤더 */}
        <div className="flex items-center justify-between p-4 bg-white border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setShowSidebar(true)}
              className="lg:hidden p-1 text-gray-400 hover:text-gray-600"
            >
              <Menu className="w-6 h-6" />
            </button>
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-gray-900">AiGov AI Assistant</h1>
                <p className="text-sm text-gray-500">보안 필터링된 AI 채팅</p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <div className="flex items-center space-x-1 text-sm text-gray-600">
              <Shield className="w-4 h-4" />
              <span>보안 활성화</span>
            </div>
            <button className="p-2 text-gray-400 hover:text-gray-600">
              <Settings className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* 메시지 목록 */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="max-w-4xl mx-auto">
            {messages.map((message) => (
              <MessageItem key={message.id} message={message} />
            ))}
            
            {isLoading && (
              <div className="flex justify-start mb-4">
                <div className="bg-gray-100 px-4 py-3 rounded-lg">
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
        </div>

        {/* 입력 영역 */}
        <MessageInput
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          placeholder="메시지를 입력하세요... (Shift+Enter로 줄바꿈)"
        />
      </div>

      {/* 모바일 오버레이 */}
      {showSidebar && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setShowSidebar(false)}
        />
      )}
    </div>
  );
};

export default ChatPage;