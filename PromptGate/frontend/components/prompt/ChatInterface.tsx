import React, { useState, useRef, useEffect } from 'react';
import { ChatSidebar } from './ChatSidebar';
import { ChatHeader } from './ChatHeader';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { WelcomeScreen } from './WelcomeScreen';
import { ScrollArea } from '../ui/scroll-area';
import { DashboardStats } from '../dashboard/DashboardStats';
import { DashboardCharts } from '../dashboard/DashboardCharts';
import { RecentActivity } from '../dashboard/RecentActivity';
import { SecuritySettings } from '../settings/SecuritySettings';
import { LLMSettings } from '../settings/LLMSettings';
import { UserSettings } from '../settings/UserSettings';

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
  const [currentPage, setCurrentPage] = useState(() => {
    if (showDashboard) return 'dashboard';
    if (showSettings) return 'settings';
    return 'chat';
  });
  const scrollRef = useRef<HTMLDivElement>(null);

  const hasMessages = messages.length > 0;

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleNavigate = (page: string) => {
    setCurrentPage(page);
    if (page === 'dashboard') {
      window.location.href = '/dashboard';
    } else if (page === 'settings') {
      window.location.href = '/settings';
    } else {
      window.location.href = '/';
    }
  };

  const handleSend = async (message: string, model: string) => {
    const timestamp = new Date().toLocaleTimeString('ko-KR', {
      hour: '2-digit',
      minute: '2-digit',
    });

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: message,
      timestamp,
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Call backend filter service
      const filterResponse = await fetch('http://localhost:8001/prompt/check', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: message,
          user_id: 'current_user',
        }),
      });

      const filterResult = await filterResponse.json();
      
      // Simulate AI response
      setTimeout(() => {
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: filterResult.is_blocked
            ? '죄송합니다. 귀하의 요청에 보안 정책에 위배되는 내용이 포함되어 있어 일부 내용이 필터링되었습니다. 보안 정책을 준수하는 범위 내에서 다시 질문해 주시기 바랍니다.'
            : `네, 귀하의 질문에 답변드리겠습니다.\n\n"${message}"\n\n이것은 ${model} 모델을 통해 생성된 응답입니다. 모든 내용은 기업 보안 정책에 따라 검토되었으며, 안전하게 제공됩니다.\n\n추가로 궁금하신 점이 있으시면 언제든 문의해 주세요.`,
          timestamp: new Date().toLocaleTimeString('ko-KR', {
            hour: '2-digit',
            minute: '2-digit',
          }),
          filtered: filterResult.is_blocked,
          model: model.toUpperCase(),
        };

        setMessages((prev) => [...prev, assistantMessage]);
        setIsLoading(false);
      }, 1500);
    } catch (error) {
      console.error('Error calling filter service:', error);
      setIsLoading(false);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <ChatHeader 
        sidebarOpen={sidebarOpen}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
      />

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        {sidebarOpen && (
          <div className="w-72 flex-shrink-0" style={{backgroundColor: '#111827', width: '18rem'}}>
            <ChatSidebar onNavigate={handleNavigate} currentPage={currentPage} />
          </div>
        )}

        {/* Chat Area */}
        <div className="flex-1 flex flex-col bg-white">
          {showDashboard || currentPage === 'dashboard' ? (
            <>
              {/* Dashboard Content */}
              <div className="flex-1 overflow-y-auto px-6 py-6">
                <div className="max-w-7xl mx-auto">
                  <div className="mb-8">
                    <h1 className="text-2xl font-bold text-gray-900 mb-2">대시보드</h1>
                    <p className="text-gray-600">AI 사용 현황 및 보안 모니터링</p>
                  </div>
                  
                  <DashboardStats />
                  <DashboardCharts />
                  <RecentActivity />
                </div>
              </div>
            </>
          ) : showSettings || currentPage === 'settings' ? (
            <>
              {/* Settings Content */}
              <div className="flex-1 overflow-y-auto px-6 py-6">
                <div className="max-w-4xl mx-auto">
                  <div className="mb-8">
                    <h1 className="text-2xl font-bold text-gray-900 mb-2">설정</h1>
                    <p className="text-gray-600">시스템 및 개인 설정을 관리합니다</p>
                  </div>
                  
                  <div className="space-y-8">
                    <UserSettings />
                    <LLMSettings />
                    <SecuritySettings />
                  </div>
                </div>
              </div>
            </>
          ) : hasMessages ? (
            <>
              {/* Messages */}
              <div
                ref={scrollRef}
                className="flex-1 overflow-y-auto px-6 py-4"
              >
                <div className="max-w-4xl mx-auto space-y-6">
                  {messages.map((msg) => (
                    <ChatMessage key={msg.id} {...msg} />
                  ))}
                  {isLoading && (
                    <div className="flex gap-4 p-4 bg-white rounded-lg shadow-sm border border-gray-200">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                      </div>
                      <div className="flex-1">
                        <div className="text-blue-900 mb-2 font-medium">AI 어시스턴트</div>
                        <div className="text-gray-600">응답 생성 중...</div>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Input - Bottom */}
              <div className="border-t border-gray-200 bg-white px-6 py-4">
                <ChatInput onSend={handleSend} disabled={isLoading} />
              </div>
            </>
          ) : (
            <>
              {/* Welcome Screen */}
              <div className="flex-1 flex items-center justify-center overflow-y-auto px-6">
                <WelcomeScreen />
              </div>

              {/* Input - Centered */}
              <div className="border-t border-gray-200 bg-white px-6 py-8">
                <ChatInput onSend={handleSend} disabled={isLoading} centered />
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}