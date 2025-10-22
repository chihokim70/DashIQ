import { BarChart, Shield, Zap, TrendingUp } from 'lucide-react';
import { Card } from '../ui/card';

export function DashboardStats() {
  const stats = [
    {
      title: '오늘의 프롬프트 처리',
      value: '1,247',
      change: '+12%',
      changeType: 'positive' as const,
      icon: BarChart,
    },
    {
      title: '차단된 위험 프롬프트',
      value: '23',
      change: '-8%',
      changeType: 'positive' as const,
      icon: Shield,
    },
    {
      title: '평균 응답 시간',
      value: '1.2초',
      change: '-0.3초',
      changeType: 'positive' as const,
      icon: Zap,
    },
    {
      title: '이번 주 사용량',
      value: '8,432',
      change: '+24%',
      changeType: 'positive' as const,
      icon: TrendingUp,
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {stats.map((stat, index) => (
        <Card key={index} className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-blue-50 rounded-lg">
              <stat.icon className="w-6 h-6 text-blue-600" />
            </div>
            <span className={`text-sm font-medium ${
              stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
            }`}>
              {stat.change}
            </span>
          </div>
          <div>
            <p className="text-2xl font-bold text-gray-900 mb-1">{stat.value}</p>
            <p className="text-sm text-gray-600">{stat.title}</p>
          </div>
        </Card>
      ))}
    </div>
  );
}