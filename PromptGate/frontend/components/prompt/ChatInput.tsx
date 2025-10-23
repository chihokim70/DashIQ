import { useState } from 'react';
import { Send, Plus } from 'lucide-react';
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
      <div className="w-full max-w-3xl mx-auto px-4 py-6">
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
          <div className="p-4">
            <div className="flex items-center gap-3 mb-3">
              <Select value={selectedModel} onValueChange={setSelectedModel}>
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="gpt-4">GPT-4</SelectItem>
                  <SelectItem value="gpt-3.5">GPT-3.5</SelectItem>
                  <SelectItem value="claude">Claude</SelectItem>
                </SelectContent>
              </Select>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <Plus className="w-4 h-4" />
              </Button>
            </div>
            <Textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="무엇을 도와 드릴까요?"
              className="min-h-[120px] border-0 resize-none focus-visible:ring-0 focus-visible:ring-offset-0 text-base bg-transparent placeholder:text-gray-400"
              disabled={disabled}
            />
          </div>
          <div className="flex justify-end p-4 pt-0">
            <Button 
              onClick={handleSend} 
              disabled={disabled || !message.trim()}
              className="bg-green-600 hover:bg-green-700"
            >
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
    <div className="flex items-end gap-3 p-4 bg-white border-t border-gray-200">
      <div className="flex items-center gap-3">
        <Select value={selectedModel} onValueChange={setSelectedModel}>
          <SelectTrigger className="w-40">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="gpt-4">GPT-4</SelectItem>
            <SelectItem value="gpt-3.5">GPT-3.5</SelectItem>
            <SelectItem value="claude">Claude</SelectItem>
          </SelectContent>
        </Select>
        <Button variant="ghost" size="icon" className="h-8 w-8">
          <Plus className="w-4 h-4" />
        </Button>
      </div>
      <div className="flex-1">
        <div className="bg-white rounded-xl border border-gray-200 p-3">
          <Textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="무엇을 도와 드릴까요?"
            className="min-h-[60px] border-0 resize-none focus-visible:ring-0 focus-visible:ring-offset-0 bg-transparent placeholder:text-gray-400"
            disabled={disabled}
          />
        </div>
      </div>
      <Button 
        onClick={handleSend} 
        disabled={disabled || !message.trim()}
        className="bg-green-600 hover:bg-green-700"
      >
        <Send className="w-4 h-4" />
      </Button>
    </div>
  );
}