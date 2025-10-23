import React, { useState, useRef, useEffect } from 'react';
import { ChatSidebar } from './ChatSidebar';
import { ChatHeader } from './ChatHeader';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { WelcomeScreen } from './WelcomeScreen';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  filtered?: boolean;
  model?: string;
}

interface ChatInterfaceProps {
  showDashboard?: boolean;
  showSettings?: boolean;
}

export default function ChatInterface({ showDashboard = false, showSettings = false }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const scrollRef = useRef<HTMLDivElement>(null);

  const hasMessages = messages.length > 0;

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async (message: string, model: string) => {
    if (!message.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: message,
      timestamp: new Date().toLocaleTimeString('ko-KR'),
      model: model,
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat/send-message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          llmProvider: model,
          userId: 'test-user'
        }),
      });

      const data = await response.json();
      
      if (data.isBlocked) {
        const blockedMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'system',
          content: `⚠️ 보안 정책에 의해 차단되었습니다: ${data.reason}`,
          timestamp: new Date().toLocaleTimeString('ko-KR'),
          filtered: true,
        };
        setMessages(prev => [...prev, blockedMessage]);
      } else {
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.response,
          timestamp: new Date().toLocaleTimeString('ko-KR'),
          model: data.llmProvider,
        };
        setMessages(prev => [...prev, assistantMessage]);
      }
    } catch (error) {
      console.error('Error calling filter service:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'system',
        content: '❌ 오류가 발생했습니다. 다시 시도해주세요.',
        timestamp: new Date().toLocaleTimeString('ko-KR'),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-screen flex bg-white">
      {/* Sidebar */}
      {sidebarOpen && (
        <div className="w-64 bg-gray-900 text-white flex-shrink-0">
          <ChatSidebar />
        </div>
      )}
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <ChatHeader
          sidebarOpen={sidebarOpen}
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        />
        
        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          {hasMessages ? (
            <>
              {/* Messages */}
              <div
                ref={scrollRef}
                className="flex-1 overflow-y-auto"
              >
                <div className="max-w-3xl mx-auto px-4 py-6">
                  {messages.map((msg) => (
                    <ChatMessage key={msg.id} {...msg} />
                  ))}
                  {isLoading && (
                    <div className="flex gap-4 p-4">
                      <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                        <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
                      </div>
                      <div className="flex-1">
                        <div className="text-gray-900 mb-2 font-medium">AI 어시스턴트</div>
                        <div className="text-gray-600">응답 생성 중...</div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
              {/* Input - Bottom */}
              <div className="border-t border-gray-200 bg-white">
                <ChatInput onSend={handleSend} disabled={isLoading} />
              </div>
            </>
          ) : (
            <>
              {/* Welcome Screen */}
              <div className="flex-1 flex items-center justify-center">
                <WelcomeScreen />
              </div>
              {/* Input - Centered */}
              <div className="border-t border-gray-200 bg-white">
                <ChatInput onSend={handleSend} disabled={isLoading} centered />
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}