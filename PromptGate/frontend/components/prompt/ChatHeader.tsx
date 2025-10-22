import { User, Settings, LogIn, PanelLeftClose, PanelLeft } from 'lucide-react';
import { Button } from '../ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import { Avatar, AvatarFallback } from '../ui/avatar';

interface ChatHeaderProps {
  sidebarOpen: boolean;
  onToggleSidebar: () => void;
}

export function ChatHeader({ sidebarOpen, onToggleSidebar }: ChatHeaderProps) {
  return (
    <header className="h-16 border-b border-gray-200 bg-gray-50 flex items-center justify-between px-6">
      {/* Logo/Title */}
      <div className="flex items-center gap-3">
        {/* Sidebar Toggle */}
        <Button 
          variant="ghost" 
          size="icon"
          onClick={onToggleSidebar}
        >
          {sidebarOpen ? (
            <PanelLeftClose className="w-5 h-5" />
          ) : (
            <PanelLeft className="w-5 h-5" />
          )}
        </Button>
        <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg flex items-center justify-center">
          <span className="text-white">AI</span>
        </div>
        <div>
          <h1 className="text-lg">Enterprise LLM Proxy</h1>
          <p className="text-xs text-gray-500">보안 필터링 지원</p>
        </div>
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-3">
        {/* Settings Button */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon">
              <Settings className="w-5 h-5" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>설정</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>
              <span>보안 정책 설정</span>
            </DropdownMenuItem>
            <DropdownMenuItem>
              <span>LLM 모델 선택</span>
            </DropdownMenuItem>
            <DropdownMenuItem>
              <span>프롬프트 템플릿</span>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem>
              <span>환경 설정</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* User Menu */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="gap-2">
              <Avatar className="w-7 h-7">
                <AvatarFallback>김</AvatarFallback>
              </Avatar>
              <span>김개발</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>내 계정</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>
              <span>프로필</span>
            </DropdownMenuItem>
            <DropdownMenuItem>
              <span>사용 내역</span>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem>
              <span>로그아웃</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
