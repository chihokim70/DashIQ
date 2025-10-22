import { useState } from 'react';
import { Send, Paperclip } from 'lucide-react';
import { Button } from '../ui/button';
import { Textarea } from '../ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';

interface ChatInputProps {
  onSend: (message: string, model: string) => void;
  disabled?: boolean;
  centered?: boolean;
}

export function ChatInput({ onSend, disabled, centered }: ChatInputProps) {
  const [message, setMessage] = useState('');
  const [selectedModel, setSelectedModel] = useState('gpt-4');

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSend(message, selectedModel);
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (centered) {
    return (
      <div className="w-full max-w-3xl mx-auto px-4">
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-4">
          <Textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="무엇이든 물어보세요... (Enter로 전송, Shift+Enter로 줄바꿈)"
            className="min-h-[120px] border-0 resize-none focus-visible:ring-0 focus-visible:ring-offset-0"
            disabled={disabled}
          />
          <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
            <div className="flex items-center gap-2">
              <Select value={selectedModel} onValueChange={setSelectedModel}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="gpt-4">GPT-4</SelectItem>
                  <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo</SelectItem>
                  <SelectItem value="claude-3">Claude 3</SelectItem>
                  <SelectItem value="claude-2">Claude 2</SelectItem>
                </SelectContent>
              </Select>
              <Button variant="ghost" size="icon" disabled={disabled}>
                <Paperclip className="w-4 h-4" />
              </Button>
            </div>
            <Button onClick={handleSend} disabled={disabled || !message.trim()}>
              <Send className="w-4 h-4 mr-2" />
              전송
            </Button>
          </div>
        </div>
        <div className="text-center text-xs text-gray-500 mt-3">
          모든 프롬프트는 보안 정책에 따라 필터링됩니다
        </div>
      </div>
    );
  }

  return (
    <div className="border-t border-gray-200 bg-white p-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-end gap-2">
          <div className="flex-1 bg-gray-50 rounded-lg border border-gray-200">
            <Textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="메시지를 입력하세요... (Enter로 전송, Shift+Enter로 줄바꿈)"
              className="border-0 bg-transparent resize-none focus-visible:ring-0 focus-visible:ring-offset-0 min-h-[60px]"
              disabled={disabled}
            />
            <div className="flex items-center justify-between px-3 pb-2">
              <div className="flex items-center gap-2">
                <Select value={selectedModel} onValueChange={setSelectedModel}>
                  <SelectTrigger className="w-[160px] h-8">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="gpt-4">GPT-4</SelectItem>
                    <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo</SelectItem>
                    <SelectItem value="claude-3">Claude 3</SelectItem>
                    <SelectItem value="claude-2">Claude 2</SelectItem>
                  </SelectContent>
                </Select>
                <Button variant="ghost" size="icon" className="h-8 w-8" disabled={disabled}>
                  <Paperclip className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
          <Button onClick={handleSend} disabled={disabled || !message.trim()} size="lg">
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
