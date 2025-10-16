import React from 'react';
import { Bot, Zap, Shield } from 'lucide-react';

interface LLMProvider {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  status: 'available' | 'maintenance' | 'unavailable';
}

interface LLMSelectorProps {
  selectedProvider: string;
  onProviderChange: (providerId: string) => void;
  className?: string;
}

const LLMSelector: React.FC<LLMSelectorProps> = ({
  selectedProvider,
  onProviderChange,
  className = ''
}) => {
  const providers: LLMProvider[] = [
    {
      id: 'chatgpt',
      name: 'ChatGPT',
      description: 'OpenAI의 GPT 모델',
      icon: <Bot className="w-4 h-4" />,
      status: 'available'
    },
    {
      id: 'claude',
      name: 'Claude',
      description: 'Anthropic의 Claude 모델',
      icon: <Zap className="w-4 h-4" />,
      status: 'available'
    },
    {
      id: 'gemini',
      name: 'Gemini',
      description: 'Google의 Gemini 모델',
      icon: <Shield className="w-4 h-4" />,
      status: 'maintenance'
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available':
        return 'text-green-600 bg-green-100';
      case 'maintenance':
        return 'text-yellow-600 bg-yellow-100';
      case 'unavailable':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'available':
        return '사용 가능';
      case 'maintenance':
        return '점검 중';
      case 'unavailable':
        return '사용 불가';
      default:
        return '알 수 없음';
    }
  };

  return (
    <div className={`bg-white border border-gray-200 rounded-lg p-4 ${className}`}>
      <h3 className="text-sm font-medium text-gray-900 mb-3">AI 모델 선택</h3>
      
      <div className="space-y-2">
        {providers.map((provider) => (
          <label
            key={provider.id}
            className={`flex items-center p-3 border rounded-lg cursor-pointer transition-colors ${
              selectedProvider === provider.id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
            } ${provider.status === 'unavailable' ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <input
              type="radio"
              name="llm-provider"
              value={provider.id}
              checked={selectedProvider === provider.id}
              onChange={(e) => onProviderChange(e.target.value)}
              disabled={provider.status === 'unavailable'}
              className="sr-only"
            />
            
            <div className="flex items-center flex-1">
              <div className="flex-shrink-0 mr-3">
                {provider.icon}
              </div>
              
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-900">
                    {provider.name}
                  </span>
                  <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(provider.status)}`}>
                    {getStatusText(provider.status)}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {provider.description}
                </p>
              </div>
            </div>
          </label>
        ))}
      </div>

      {/* 보안 정보 */}
      <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-start space-x-2">
          <Shield className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
          <div className="text-xs text-blue-800">
            <p className="font-medium">보안 필터링 적용</p>
            <p className="mt-1">
              모든 메시지는 보안 정책에 따라 필터링되며, 
              민감한 정보는 자동으로 차단됩니다.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LLMSelector;



