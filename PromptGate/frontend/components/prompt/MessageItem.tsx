import React from 'react';
import { Bot, User, AlertTriangle, Clock } from 'lucide-react';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  isBlocked?: boolean;
  blockReason?: string;
  llmProvider?: string;
}

interface MessageItemProps {
  message: Message;
}

const MessageItem: React.FC<MessageItemProps> = ({ message }) => {
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('ko-KR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const getMessageIcon = () => {
    if (message.role === 'user') {
      return <User className="w-4 h-4 text-blue-600" />;
    }
    
    if (message.isBlocked) {
      return <AlertTriangle className="w-4 h-4 text-red-500" />;
    }
    
    return <Bot className="w-4 h-4 text-gray-500" />;
  };

  const getMessageStyles = () => {
    if (message.role === 'user') {
      return 'bg-blue-600 text-white';
    }
    
    if (message.isBlocked) {
      return 'bg-red-50 border border-red-200 text-red-800';
    }
    
    return 'bg-gray-100 text-gray-900';
  };

  return (
    <div
      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div
        className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg shadow-sm ${getMessageStyles()}`}
      >
        <div className="flex items-start space-x-2">
          <div className="flex-shrink-0 mt-0.5">
            {getMessageIcon()}
          </div>
          <div className="flex-1">
            <div className="whitespace-pre-wrap text-sm leading-relaxed">
              {message.content}
            </div>
            <div className="flex items-center justify-between mt-2 text-xs opacity-70">
              <div className="flex items-center space-x-1">
                <Clock className="w-3 h-3" />
                <span>{formatTime(message.timestamp)}</span>
              </div>
              {message.llmProvider && (
                <span className="px-2 py-0.5 bg-gray-200 rounded-full text-xs">
                  {message.llmProvider}
                </span>
              )}
            </div>
            {message.isBlocked && message.blockReason && (
              <div className="mt-2 p-2 bg-red-100 rounded text-xs text-red-700">
                <strong>차단 사유:</strong> {message.blockReason}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MessageItem;







