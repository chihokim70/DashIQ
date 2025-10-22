import { useState } from 'react';
import { User, Mail, Building } from 'lucide-react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Avatar, AvatarFallback } from '../ui/avatar';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';

export function UserSettings() {
  const [name, setName] = useState('김개발');
  const [email, setEmail] = useState('kim.dev@company.com');
  const [department, setDepartment] = useState('개발팀');
  const [role, setRole] = useState('developer');
  const [timezone, setTimezone] = useState('Asia/Seoul');

  return (
    <Card className="p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-green-50 rounded-lg">
          <User className="w-6 h-6 text-green-600" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900">사용자 계정</h3>
          <p className="text-sm text-gray-600">개인 정보 및 계정 설정을 관리합니다</p>
        </div>
      </div>

      <div className="space-y-6">
        {/* 프로필 이미지 */}
        <div className="flex items-center gap-4">
          <Avatar className="w-16 h-16">
            <AvatarFallback className="text-lg">김</AvatarFallback>
          </Avatar>
          <div>
            <Button variant="outline" size="default">
              프로필 이미지 변경
            </Button>
            <p className="text-xs text-gray-500 mt-1">
              JPG, PNG 파일만 업로드 가능 (최대 2MB)
            </p>
          </div>
        </div>

        {/* 기본 정보 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-3">
            <Label htmlFor="name">이름</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          <div className="space-y-3">
            <Label htmlFor="email">이메일</Label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          <div className="space-y-3">
            <Label htmlFor="department">부서</Label>
            <div className="relative">
              <Building className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
              <Input
                id="department"
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          <div className="space-y-3">
            <Label htmlFor="role">역할</Label>
            <Select value={role} onValueChange={setRole}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="admin">관리자</SelectItem>
                <SelectItem value="developer">개발자</SelectItem>
                <SelectItem value="analyst">분석가</SelectItem>
                <SelectItem value="user">일반 사용자</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* 환경 설정 */}
        <div className="space-y-3">
          <Label htmlFor="timezone">시간대</Label>
          <Select value={timezone} onValueChange={setTimezone}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Asia/Seoul">한국 표준시 (KST)</SelectItem>
              <SelectItem value="Asia/Tokyo">일본 표준시 (JST)</SelectItem>
              <SelectItem value="UTC">협정 세계시 (UTC)</SelectItem>
              <SelectItem value="America/New_York">동부 표준시 (EST)</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* 권한 정보 */}
        <div className="p-4 bg-blue-50 rounded-lg">
          <h4 className="font-medium text-blue-900 mb-2">현재 권한</h4>
          <div className="space-y-1 text-sm text-blue-800">
            <p>• AI 모델 사용 권한: GPT-4, Claude 3</p>
            <p>• 일일 사용 한도: 100회</p>
            <p>• 프롬프트 필터링 수준: 보통</p>
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