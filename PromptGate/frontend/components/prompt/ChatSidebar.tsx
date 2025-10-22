import { useState } from 'react';
import { MessageSquare, Plus, FolderOpen, Settings, User, ChevronDown, ChevronRight, FolderPlus, BarChart3, Home } from 'lucide-react';
import { Button } from '../ui/button';
import { ScrollArea } from '../ui/scroll-area';
import { cn } from '../ui/utils';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../ui/dialog';
import { Input } from '../ui/input';
import { Label } from '../ui/label';

interface Chat {
  id: string;
  title: string;
  timestamp: string;
}

interface Project {
  id: string;
  name: string;
  chats: Chat[];
  expanded?: boolean;
}

interface ChatSidebarProps {
  onNavigate?: (page: string) => void;
  currentPage?: string;
}

export function ChatSidebar({ onNavigate, currentPage = 'chat' }: ChatSidebarProps) {
  const [projects, setProjects] = useState<Project[]>([
    {
      id: '1',
      name: 'AI 개발 프로젝트',
      expanded: true,
      chats: [
        { id: '1', title: '데이터 전처리 방법', timestamp: '2025-10-20 10:30' },
        { id: '2', title: '모델 학습 최적화', timestamp: '2025-10-19 15:20' },
        { id: '3', title: 'API 연동 가이드', timestamp: '2025-10-18 09:15' },
      ],
    },
    {
      id: '2',
      name: '보안 컴플라이언스',
      expanded: false,
      chats: [
        { id: '4', title: '보안 정책 검토', timestamp: '2025-10-17 14:00' },
        { id: '5', title: '데이터 암호화', timestamp: '2025-10-16 11:45' },
      ],
    },
  ]);

  const [activeChat, setActiveChat] = useState<string | null>(null);
  const [newProjectDialogOpen, setNewProjectDialogOpen] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');

  const toggleProject = (projectId: string) => {
    setProjects(projects.map(p => 
      p.id === projectId ? { ...p, expanded: !p.expanded } : p
    ));
  };

  const handleNewChat = () => {
    if (projects.length === 0) {
      alert('먼저 프로젝트를 생성해주세요.');
      return;
    }
    
    const timestamp = new Date().toLocaleString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });

    const newChat: Chat = {
      id: Date.now().toString(),
      title: '새 채팅',
      timestamp,
    };

    // Add to first project or first expanded project
    const targetProject = projects.find(p => p.expanded) || projects[0];
    
    setProjects(projects.map(p => 
      p.id === targetProject.id 
        ? { ...p, chats: [newChat, ...p.chats], expanded: true }
        : p
    ));
    setActiveChat(newChat.id);
  };

  const handleCreateProject = () => {
    if (!newProjectName.trim()) {
      return;
    }

    const newProject: Project = {
      id: Date.now().toString(),
      name: newProjectName,
      chats: [],
      expanded: true,
    };

    setProjects([newProject, ...projects]);
    setNewProjectName('');
    setNewProjectDialogOpen(false);
  };

  const navItems = [
    { id: 'chat', label: '채팅', icon: MessageSquare },
    { id: 'dashboard', label: '대시보드', icon: BarChart3 },
    { id: 'settings', label: '설정', icon: Settings },
  ];

  return (
    <div className="flex flex-col h-full" style={{backgroundColor: '#111827', color: 'white'}}>
      {/* Navigation Menu */}
      <div className="p-4 border-b border-gray-700">
        <div className="space-y-1">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => onNavigate?.(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors text-left ${
                currentPage === item.id 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'
              }`}
            >
              <item.icon className="w-4 h-4" />
              <span>{item.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="p-4 border-b border-gray-700 space-y-2">
        <Button 
          className="w-full justify-start gap-2" 
          variant="default"
          onClick={handleNewChat}
          style={{backgroundColor: 'white', color: '#111827'}}
        >
          <Plus className="w-4 h-4" />
          새 채팅
        </Button>

        <Dialog open={newProjectDialogOpen} onOpenChange={setNewProjectDialogOpen}>
          <DialogTrigger asChild>
            <Button className="w-full justify-start gap-2" variant="outline" style={{backgroundColor: 'white', color: '#111827', borderColor: '#6b7280'}}>
              <FolderPlus className="w-4 h-4" />
              새 프로젝트
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>새 프로젝트 만들기</DialogTitle>
              <DialogDescription>
                새로운 프로젝트를 생성하여 채팅을 구조화하세요.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="project-name">프로젝트 이름</Label>
                <Input
                  id="project-name"
                  placeholder="예: AI 모델 개발"
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      handleCreateProject();
                    }
                  }}
                />
              </div>
            </div>
            <DialogFooter>
              <Button 
                variant="outline" 
                onClick={() => {
                  setNewProjectDialogOpen(false);
                  setNewProjectName('');
                }}
              >
                취소
              </Button>
              <Button onClick={handleCreateProject}>생성</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Chat History */}
      <ScrollArea className="flex-1">
        <div className="p-2">
          {projects.map((project) => (
            <div key={project.id} className="mb-2">
              {/* Project Header */}
                     <button
                       onClick={() => toggleProject(project.id)}
                       className="w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-colors"
                       style={{color: 'white'}}
                       onMouseEnter={(e) => (e.target as HTMLElement).style.backgroundColor = '#374151'}
                       onMouseLeave={(e) => (e.target as HTMLElement).style.backgroundColor = 'transparent'}
                     >
                {project.expanded ? (
                  <ChevronDown className="w-4 h-4" />
                ) : (
                  <ChevronRight className="w-4 h-4" />
                )}
                <FolderOpen className="w-4 h-4" />
                <span className="flex-1 text-left">{project.name}</span>
              </button>

              {/* Project Chats */}
              {project.expanded && (
                <div className="ml-6 mt-1 space-y-1">
                  {project.chats.map((chat) => (
                           <button
                             key={chat.id}
                             onClick={() => setActiveChat(chat.id)}
                             className="w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-colors text-left"
                             style={{
                               color: 'white',
                               backgroundColor: activeChat === chat.id ? '#374151' : 'transparent'
                             }}
                             onMouseEnter={(e) => {
                               if (activeChat !== chat.id) {
                                 (e.target as HTMLElement).style.backgroundColor = '#374151';
                               }
                             }}
                             onMouseLeave={(e) => {
                               if (activeChat !== chat.id) {
                                 (e.target as HTMLElement).style.backgroundColor = 'transparent';
                               }
                             }}
                           >
                      <MessageSquare className="w-4 h-4 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <div className="truncate">{chat.title}</div>
                        <div className="text-xs" style={{color: '#9ca3af'}}>{chat.timestamp}</div>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}
