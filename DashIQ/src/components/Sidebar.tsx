import { 
  LayoutDashboard, 
  MessageSquare, 
  Shield, 
  Eye, 
  Server, 
  Image, 
  Folder,
  Settings
} from "lucide-react";
import { cn } from "./ui/utils";

interface SidebarProps {
  currentPage: string;
  onPageChange: (page: string) => void;
}

const menuItems = [
  { id: "dashboard", label: "Dashboard Overview", icon: LayoutDashboard },
  { id: "prompt", label: "Prompt Usage", icon: MessageSquare },
  { id: "policy", label: "Policy Monitor", icon: Shield },
  { id: "shadow", label: "Shadow AI", icon: Eye },
  { id: "onprem", label: "On-Prem LLM", icon: Server },
  { id: "image", label: "Image Generation", icon: Image },
  { id: "case", label: "Case Management", icon: Folder },
  { id: "settings", label: "Settings", icon: Settings },
];

export function Sidebar({ currentPage, onPageChange }: SidebarProps) {
  return (
    <aside className="w-64 border-r bg-card h-screen sticky top-0 flex flex-col">
      <nav className="flex-1 p-4 space-y-1">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          
          return (
            <button
              key={item.id}
              onClick={() => onPageChange(item.id)}
              className={cn(
                "w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all",
                isActive
                  ? "bg-[#1E90FF] text-white shadow-lg"
                  : "text-foreground hover:bg-sidebar-accent"
              )}
            >
              <Icon className="w-5 h-5" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>
      
      <div className="p-4 border-t">
        <div className="text-sm text-muted-foreground">
          <p>Version 2.4.1</p>
          <p className="mt-1">© 2025 AiGov</p>
        </div>
      </div>
    </aside>
  );
}
