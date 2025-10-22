import { useState } from 'react';
import { Shield, AlertTriangle } from 'lucide-react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';

export function SecuritySettings() {
  const [securityLevel, setSecurityLevel] = useState('medium');
  const [bannedKeywords, setBannedKeywords] = useState('기밀, 내부문서, 개인정보');
  const [allowedDomains, setAllowedDomains] = useState('openai.com, anthropic.com');

  return (
    <Card className="p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-red-50 rounded-lg">
          <Shield className="w-6 h-6 text-red-600" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900">보안 정책</h3>
          <p className="text-sm text-gray-600">프롬프트 필터링 및 보안 설정을 관리합니다</p>
        </div>
      </div>

      <div className="space-y-6">
        {/* 보안 수준 */}
        <div className="space-y-3">
          <Label htmlFor="security-level">보안 수준</Label>
          <Select value={securityLevel} onValueChange={setSecurityLevel}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="low">낮음 - 기본적인 필터링만 수행</SelectItem>
              <SelectItem value="medium">보통 - 일반적인 보안 정책 적용</SelectItem>
              <SelectItem value="high">높음 - 엄격한 보안 정책 적용</SelectItem>
              <SelectItem value="strict">최고 - 모든 프롬프트 승인 필요</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* 금지 키워드 */}
        <div className="space-y-3">
          <Label htmlFor="banned-keywords">금지 키워드</Label>
          <Textarea
            id="banned-keywords"
            value={bannedKeywords}
            onChange={(e) => setBannedKeywords(e.target.value)}
            placeholder="콤마로 구분하여 입력하세요"
            rows={3}
          />
          <p className="text-xs text-gray-500">
            입력된 키워드가 포함된 프롬프트는 자동으로 차단됩니다
          </p>
        </div>

        {/* 허용된 도메인 */}
        <div className="space-y-3">
          <Label htmlFor="allowed-domains">허용된 AI 서비스 도메인</Label>
          <Textarea
            id="allowed-domains"
            value={allowedDomains}
            onChange={(e) => setAllowedDomains(e.target.value)}
            placeholder="허용할 도메인을 콤마로 구분하여 입력하세요"
            rows={2}
          />
        </div>

        {/* 경고 메시지 */}
        <div className="flex items-start gap-3 p-4 bg-amber-50 rounded-lg">
          <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-amber-800">
            <p className="font-medium mb-1">보안 정책 변경 시 주의사항</p>
            <p>변경된 설정은 즉시 적용되며, 모든 사용자의 프롬프트 필터링에 영향을 줍니다.</p>
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