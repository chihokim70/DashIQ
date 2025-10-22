import { Card } from '../ui/card';

export function DashboardCharts() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      {/* 사용량 추이 차트 */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">일별 사용량 추이</h3>
        <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
          <div className="text-center">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4 mx-auto">
              <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
            </div>
            <p className="text-gray-500">차트 데이터 로딩 중...</p>
          </div>
        </div>
      </Card>

      {/* 위험 탐지 현황 */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">위험 탐지 유형별 현황</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">프롬프트 인젝션</span>
            <span className="text-sm font-medium">12건</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="bg-red-500 h-2 rounded-full" style={{width: '60%'}}></div>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">민감정보 유출</span>
            <span className="text-sm font-medium">8건</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="bg-orange-500 h-2 rounded-full" style={{width: '40%'}}></div>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">금지 키워드</span>
            <span className="text-sm font-medium">3건</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="bg-yellow-500 h-2 rounded-full" style={{width: '15%'}}></div>
          </div>
        </div>
      </Card>
    </div>
  );
}