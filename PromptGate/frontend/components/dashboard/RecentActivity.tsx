import { Shield, AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import { Card } from '../ui/card';
import { ScrollArea } from '../ui/scroll-area';

export function RecentActivity() {
  const activities = [
    {
      id: '1',
      type: 'blocked',
      message: '프롬프트 인젝션 시도가 차단되었습니다',
      user: '김개발',
      time: '2분 전',
      icon: Shield,
      iconColor: 'text-red-500',
      bgColor: 'bg-red-50',
    },
    {
      id: '2',
      type: 'warning',
      message: '민감정보 포함 프롬프트가 마스킹 처리되었습니다',
      user: '이기획',
      time: '5분 전',
      icon: AlertTriangle,
      iconColor: 'text-orange-500',
      bgColor: 'bg-orange-50',
    },
    {
      id: '3',
      type: 'success',
      message: 'AI 응답이 성공적으로 전송되었습니다',
      user: '박디자인',
      time: '8분 전',
      icon: CheckCircle,
      iconColor: 'text-green-500',
      bgColor: 'bg-green-50',
    },
    {
      id: '4',
      type: 'info',
      message: '새로운 보안 정책이 적용되었습니다',
      user: '시스템',
      time: '15분 전',
      icon: Clock,
      iconColor: 'text-blue-500',
      bgColor: 'bg-blue-50',
    },
    {
      id: '5',
      type: 'blocked',
      message: '금지 키워드 사용으로 프롬프트가 차단되었습니다',
      user: '최개발',
      time: '22분 전',
      icon: Shield,
      iconColor: 'text-red-500',
      bgColor: 'bg-red-50',
    },
  ];

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">최근 활동</h3>
      <ScrollArea className="h-80">
        <div className="space-y-4">
          {activities.map((activity) => (
            <div key={activity.id} className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors">
              <div className={`p-2 rounded-full ${activity.bgColor}`}>
                <activity.icon className={`w-4 h-4 ${activity.iconColor}`} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-900 mb-1">{activity.message}</p>
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <span>{activity.user}</span>
                  <span>•</span>
                  <span>{activity.time}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>
    </Card>
  );
}