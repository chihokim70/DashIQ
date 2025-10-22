import { Avatar, AvatarFallback } from './ui/avatar';
import { Bot, User, Shield, AlertTriangle } from 'lucide-react';
import { cn } from './ui/utils';
import { Badge } from './ui/badge';

interface ChatMessageProps {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
  filtered?: boolean;
  model?: string;
}

export function ChatMessage({ role, content, timestamp, filtered, model }: ChatMessageProps) {
  const isUser = role === 'user';
  const isSystem = role === 'system';

  return (
    <div
      className={cn(
        "flex gap-4 px-6 py-6",
        isUser ? "bg-white" : "bg-gray-50"
      )}
    >
      {/* Avatar */}
      <div className="flex-shrink-0">
        <Avatar className="w-8 h-8">
          <AvatarFallback className={isUser ? "bg-blue-100" : "bg-purple-100"}>
            {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
          </AvatarFallback>
        </Avatar>
      </div>

      {/* Message Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-2">
          <span className={cn(
            isUser ? "text-blue-900" : "text-purple-900"
          )}>
            {isUser ? '사용자' : 'AI 어시스턴트'}
          </span>
          {timestamp && (
            <span className="text-xs text-gray-500">{timestamp}</span>
          )}
          {model && (
            <Badge variant="outline" className="text-xs">
              {model}
            </Badge>
          )}
          {filtered && (
            <Badge variant="secondary" className="text-xs gap-1">
              <Shield className="w-3 h-3" />
              보안 필터링됨
            </Badge>
          )}
        </div>
        <div className="text-gray-900 whitespace-pre-wrap">{content}</div>
      </div>
    </div>
  );
}
