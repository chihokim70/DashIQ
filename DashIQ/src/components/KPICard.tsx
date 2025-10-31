import { LucideIcon } from "lucide-react";
import { Card, CardContent } from "./ui/card";

interface KPICardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: {
    value: string;
    isPositive: boolean;
  };
  color?: "primary" | "secondary" | "accent" | "destructive";
  onClick?: () => void;
}

export function KPICard({ title, value, icon: Icon, trend, color = "primary", onClick }: KPICardProps) {
  const colorClasses = {
    primary: "bg-[#1E90FF]/10 text-[#1E90FF]",
    secondary: "bg-[#10B981]/10 text-[#10B981]",
    accent: "bg-[#F59E0B]/10 text-[#F59E0B]",
    destructive: "bg-[#EF4444]/10 text-[#EF4444]",
  };

  return (
    <Card 
      className={`transition-all hover:shadow-lg ${onClick ? 'cursor-pointer' : ''}`}
      onClick={onClick}
    >
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-muted-foreground mb-2">{title}</p>
            <p className="text-3xl mb-2">{value}</p>
            {trend && (
              <div className="flex items-center gap-1">
                <span className={trend.isPositive ? "text-[#10B981]" : "text-[#EF4444]"}>
                  {trend.isPositive ? "↑" : "↓"} {trend.value}
                </span>
                <span className="text-muted-foreground">vs last period</span>
              </div>
            )}
          </div>
          <div className={`p-3 rounded-xl ${colorClasses[color]}`}>
            <Icon className="w-6 h-6" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
