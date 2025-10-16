import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, Smile } from 'lucide-react';

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  placeholder?: string;
  disabled?: boolean;
}

const MessageInput: React.FC<MessageInputProps> = ({
  onSendMessage,
  isLoading,
  placeholder = "메시지를 입력하세요...",
  disabled = false
}) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    if (message.trim() && !isLoading && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
      adjustTextareaHeight();
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
  };

  useEffect(() => {
    adjustTextareaHeight();
  }, [message]);

  return (
    <div className="bg-white border-t border-gray-200 p-4">
      <div className="flex items-end space-x-2">
        {/* 첨부파일 버튼 */}
        <button
          className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
          disabled={disabled}
        >
          <Paperclip className="w-5 h-5" />
        </button>

        {/* 메시지 입력 영역 */}
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
            className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
            rows={1}
            style={{ minHeight: '40px', maxHeight: '120px' }}
            disabled={disabled}
          />
          
          {/* 이모지 버튼 */}
          <button
            className="absolute right-2 top-2 p-1 text-gray-400 hover:text-gray-600 transition-colors"
            disabled={disabled}
          >
            <Smile className="w-4 h-4" />
          </button>
        </div>

        {/* 전송 버튼 */}
        <button
          onClick={handleSend}
          disabled={!message.trim() || isLoading || disabled}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-1 transition-colors"
        >
          <Send className="w-4 h-4" />
          <span className="hidden sm:inline">전송</span>
        </button>
      </div>

      {/* 도움말 텍스트 */}
      <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
        <span>Enter로 전송, Shift+Enter로 줄바꿈</span>
        <span>{message.length}/2000</span>
      </div>
    </div>
  );
};

export default MessageInput;



