import { useState } from 'react';
import { MessageSquare, Plus, FolderOpen, ChevronDown, ChevronRight, FolderPlus, MoreHorizontal, Share2, Edit3, Star, Trash2 } from 'lucide-react';
import { Button } from '../ui/button';
import { ScrollArea } from '../ui/scroll-area';
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

export function ChatSidebar({ onNavigate, currentPage }: ChatSidebarProps) {
  const [projects, setProjects] = useState<Project[]>([
    {
      id: '1',
      name: '프로젝트 1',
      expanded: true,
      chats: [
        { id: '1-1', title: 'React 컴포넌트 설계', timestamp: '2024-01-15' },
        { id: '1-2', title: 'API 연동 방법', timestamp: '2024-01-14' },
      ]
    },
    {
      id: '2',
      name: '프로젝트 2',
      expanded: false,
      chats: [
        { id: '2-1', title: '데이터베이스 설계', timestamp: '2024-01-13' },
      ]
    }
  ]);

  const [sharedChats] = useState<Chat[]>([
    { id: 'shared-1', title: '공유된 채팅 1', timestamp: '2024-01-12' },
    { id: 'shared-2', title: '공유된 채팅 2', timestamp: '2024-01-11' },
  ]);

  const [newProjectDialogOpen, setNewProjectDialogOpen] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);

  const handleNewChat = () => {
    console.log('새 채팅 생성');
  };

  const handleCreateProject = () => {
    if (!newProjectName.trim()) {
      return;
    }

    const newProject: Project = {
      id: Date.now().toString(),
      name: newProjectName,
      expanded: true,
      chats: []
    };

    setProjects([...projects, newProject]);
    setNewProjectName('');
    setNewProjectDialogOpen(false);
  };

  const toggleProject = (projectId: string) => {
    setProjects(projects.map(project => 
      project.id === projectId 
        ? { ...project, expanded: !project.expanded }
        : project
    ));
  };

  return (
    <div className="flex flex-col h-full bg-gray-900 text-white">
      {/* Navigation Menu */}
      <div className="p-3 border-b border-gray-700">
        <div className="space-y-1">
          <div 
            className={`px-3 py-2 rounded-lg cursor-pointer transition-colors text-sm ${
              currentPage === 'chat' ? "bg-gray-700" : "hover:bg-gray-800"
            }`}
            onClick={() => onNavigate?.('chat')}
          >
            채팅
          </div>
          <div 
            className={`px-3 py-2 rounded-lg cursor-pointer transition-colors text-sm ${
              currentPage === 'project' ? "bg-gray-700" : "hover:bg-gray-800"
            }`}
            onClick={() => onNavigate?.('project')}
          >
            프로젝트
          </div>
          <div 
            className={`px-3 py-2 rounded-lg cursor-pointer transition-colors text-sm ${
              currentPage === 'apps' ? "bg-gray-700" : "hover:bg-gray-800"
            }`}
            onClick={() => onNavigate?.('apps')}
          >
            Apps
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="p-3 border-b border-gray-700">
        <Button
          className="w-full justify-start gap-2 bg-transparent hover:bg-gray-800 text-white border border-gray-600"
          onClick={handleNewChat}
        >
          <Plus className="w-4 h-4" />
          새 채팅
        </Button>
        <Dialog open={newProjectDialogOpen} onOpenChange={setNewProjectDialogOpen}>
          <DialogTrigger asChild>
            <Button className="w-full justify-start gap-2 bg-transparent hover:bg-gray-800 text-white border border-gray-600 mt-2">
              <FolderPlus className="w-4 h-4" />
              새 프로젝트
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-white text-gray-900">
            <DialogHeader>
              <DialogTitle>새 프로젝트 생성</DialogTitle>
              <DialogDescription>
                프로젝트 이름을 입력해주세요.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="project-name" className="text-right">
                  프로젝트명
                </Label>
                <Input
                  id="project-name"
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  className="col-span-3"
                  placeholder="프로젝트 이름을 입력하세요"
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setNewProjectDialogOpen(false)}>
                취소
              </Button>
              <Button onClick={handleCreateProject}>
                생성
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Chat History */}
      <ScrollArea className="flex-1">
        <div className="p-2">
          {/* 채팅 히스토리 그룹 */}
          <div className="mb-4">
            <div className="px-3 py-2 text-xs font-medium text-gray-400 uppercase tracking-wide">
              채팅 히스토리
            </div>
            <div className="space-y-1">
              {projects.map((project) => (
                <div key={project.id} className="mb-2">
                  {/* Project Header */}
                  <button
                    onClick={() => toggleProject(project.id)}
                    className="w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-colors hover:bg-gray-800 text-sm"
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
                        <div
                          key={chat.id}
                          className="relative group"
                          onMouseEnter={() => setHoveredItem(chat.id)}
                          onMouseLeave={() => setHoveredItem(null)}
                        >
                          <button
                            className="w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-colors text-left hover:bg-gray-800 text-sm"
                          >
                            <MessageSquare className="w-4 h-4 flex-shrink-0" />
                            <div className="flex-1 min-w-0">
                              <div className="truncate">{chat.title}</div>
                              <div className="text-xs text-gray-400">{chat.timestamp}</div>
                            </div>
                          </button>
                          
                          {/* Action Menu */}
                          {hoveredItem === chat.id && (
                            <div className="absolute right-2 top-1/2 transform -translate-y-1/2">
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-6 w-6 p-0 text-gray-400 hover:text-white"
                              >
                                <MoreHorizontal className="w-3 h-3" />
                              </Button>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* 프로젝트 히스토리 그룹 */}
          <div className="mb-4">
            <div className="px-3 py-2 text-xs font-medium text-gray-400 uppercase tracking-wide">
              프로젝트 히스토리
            </div>
            <div className="space-y-1">
              {projects.map((project) => (
                <div
                  key={`project-${project.id}`}
                  className="relative group"
                  onMouseEnter={() => setHoveredItem(`project-${project.id}`)}
                  onMouseLeave={() => setHoveredItem(null)}
                >
                  <button className="w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-colors text-left hover:bg-gray-800 text-sm">
                    <FolderOpen className="w-4 h-4" />
                    <div className="flex-1 min-w-0">
                      <div className="truncate">{project.name}</div>
                      <div className="text-xs text-gray-400">{project.chats.length}개 채팅</div>
                    </div>
                  </button>
                  
                  {/* Action Menu */}
                  {hoveredItem === `project-${project.id}` && (
                    <div className="absolute right-2 top-1/2 transform -translate-y-1/2">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-6 w-6 p-0 text-gray-400 hover:text-white"
                      >
                        <MoreHorizontal className="w-3 h-3" />
                      </Button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* 공유 채팅 그룹 */}
          <div className="mb-4">
            <div className="px-3 py-2 text-xs font-medium text-gray-400 uppercase tracking-wide">
              공유 채팅
            </div>
            <div className="space-y-1">
              {sharedChats.map((chat) => (
                <div
                  key={chat.id}
                  className="relative group"
                  onMouseEnter={() => setHoveredItem(chat.id)}
                  onMouseLeave={() => setHoveredItem(null)}
                >
                  <button className="w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-colors text-left hover:bg-gray-800 text-sm">
                    <Share2 className="w-4 h-4" />
                    <div className="flex-1 min-w-0">
                      <div className="truncate">{chat.title}</div>
                      <div className="text-xs text-gray-400">{chat.timestamp}</div>
                    </div>
                  </button>
                  
                  {/* Action Menu */}
                  {hoveredItem === chat.id && (
                    <div className="absolute right-2 top-1/2 transform -translate-y-1/2">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-6 w-6 p-0 text-gray-400 hover:text-white"
                      >
                        <MoreHorizontal className="w-3 h-3" />
                      </Button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </ScrollArea>
    </div>
  );
}