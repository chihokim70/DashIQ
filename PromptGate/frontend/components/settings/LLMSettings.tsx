import { useState } from 'react';
import { Zap, Settings } from 'lucide-react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';

export function LLMSettings() {
  const [defaultModel, setDefaultModel] = useState('gpt-4');
  const [maxTokens, setMaxTokens] = useState('2048');
  const [temperature, setTemperature] = useState('0.7');
  const [apiKey, setApiKey] = useState('');

  const models = [
    { value: 'gpt-4', label: 'GPT-4', provider: 'OpenAI' },
    { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo', provider: 'OpenAI' },
    { value: 'claude-3', label: 'Claude 3', provider: 'Anthropic' },
    { value: 'claude-2', label: 'Claude 2', provider: 'Anthropic' },
  ];

  return (
    <Card className="p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-blue-50 rounded-lg">
          <Zap className="w-6 h-6 text-blue-600" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900">LLM 모델 설정</h3>
          <p className="text-sm text-gray-600">AI 모델 선택 및 파라미터를 관리합니다</p>
        </div>
      </div>

      <div className="space-y-6">
        {/* 기본 모델 선택 */}
        <div className="space-y-3">
          <Label htmlFor="default-model">기본 모델</Label>
          <Select value={defaultModel} onValueChange={setDefaultModel}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {models.map((model) => (
                <SelectItem key={model.value} value={model.value}>
                  {model.label} ({model.provider})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* 최대 토큰 수 */}
        <div className="space-y-3">
          <Label htmlFor="max-tokens">최대 토큰 수</Label>
          <Input
            id="max-tokens"
            type="number"
            value={maxTokens}
            onChange={(e) => setMaxTokens(e.target.value)}
            min="1"
            max="8192"
          />
          <p className="text-xs text-gray-500">
            응답의 최대 길이를 제한합니다 (1-8192)
          </p>
        </div>

        {/* Temperature */}
        <div className="space-y-3">
          <Label htmlFor="temperature">창의성 수준 (Temperature)</Label>
          <Input
            id="temperature"
            type="number"
            value={temperature}
            onChange={(e) => setTemperature(e.target.value)}
            min="0"
            max="2"
            step="0.1"
          />
          <p className="text-xs text-gray-500">
            0에 가까울수록 일관된 응답, 2에 가까울수록 창의적인 응답
          </p>
        </div>

        {/* API 키 관리 */}
        <div className="space-y-3">
          <Label htmlFor="api-key">API 키</Label>
          <div className="flex gap-2">
            <Input
              id="api-key"
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="새 API 키를 입력하세요"
            />
            <Button variant="outline" size="default">
              테스트
            </Button>
          </div>
          <p className="text-xs text-gray-500">
            안전하게 암호화되어 저장됩니다
          </p>
        </div>

        {/* 모델 사용량 현황 */}
        <div className="space-y-3">
          <Label>모델별 사용량 (이번 달)</Label>
          <div className="space-y-3">
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
              <span className="text-sm font-medium">GPT-4</span>
              <span className="text-sm text-gray-600">$45.30</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
              <span className="text-sm font-medium">Claude 3</span>
              <span className="text-sm text-gray-600">$23.15</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
              <span className="text-sm font-medium">GPT-3.5 Turbo</span>
              <span className="text-sm text-gray-600">$8.70</span>
            </div>
          </div>
        </div>

        {/* 저장 버튼 */}
        <div className="flex justify-end gap-3">
          <Button variant="outline">취소</Button>
          <Button>설정 저장</Button>
        </div>
      </div>
    </Card>
  );
}