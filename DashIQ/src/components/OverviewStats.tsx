import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from "recharts";
import { TrendingUp, TrendingDown, AlertTriangle, CheckCircle2, Users, Shield } from "lucide-react";

const usageData = [
  { date: "01/15", requests: 2400, blocked: 180 },
  { date: "01/16", requests: 3200, blocked: 250 },
  { date: "01/17", requests: 2800, blocked: 190 },
  { date: "01/18", requests: 3800, blocked: 320 },
  { date: "01/19", requests: 4200, blocked: 280 },
  { date: "01/20", requests: 3900, blocked: 240 },
  { date: "01/21", requests: 4500, blocked: 310 },
];

const aiServiceData = [
  { name: "ChatGPT", value: 45, color: "#10b981" },
  { name: "Claude", value: 25, color: "#3b82f6" },
  { name: "Gemini", value: 15, color: "#f59e0b" },
  { name: "기타", value: 15, color: "#6366f1" },
];

const threatData = [
  { category: "민감정보 유출", count: 45 },
  { category: "악성 프롬프트", count: 32 },
  { category: "정책 위반", count: 28 },
  { category: "비인가 AI", count: 21 },
];

export function OverviewStats() {
  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>총 AI 요청</CardDescription>
            <CardTitle className="text-slate-900">24,563</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 text-green-600 text-sm">
              <TrendingUp className="w-4 h-4" />
              <span>+12.5% 전주 대비</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription>차단된 요청</CardDescription>
            <CardTitle className="text-slate-900">1,847</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 text-red-600 text-sm">
              <TrendingUp className="w-4 h-4" />
              <span>+8.3% 전주 대비</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription>활성 사용자</CardDescription>
            <CardTitle className="text-slate-900">342</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 text-green-600 text-sm">
              <TrendingUp className="w-4 h-4" />
              <span>+5.2% 전주 대비</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription>위협 탐지율</CardDescription>
            <CardTitle className="text-slate-900">7.5%</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 text-amber-600 text-sm">
              <TrendingDown className="w-4 h-4" />
              <span>-2.1% 전주 대비</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* AI Usage Trend */}
        <Card>
          <CardHeader>
            <CardTitle>AI 사용 추이</CardTitle>
            <CardDescription>최근 7일간 요청 및 차단 현황</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={usageData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="date" stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip />
                <Line type="monotone" dataKey="requests" stroke="#3b82f6" strokeWidth={2} name="전체 요청" />
                <Line type="monotone" dataKey="blocked" stroke="#ef4444" strokeWidth={2} name="차단됨" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* AI Service Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>AI 서비스 사용 분포</CardTitle>
            <CardDescription>서비스별 사용 비율</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <ResponsiveContainer width="50%" height={250}>
                <PieChart>
                  <Pie
                    data={aiServiceData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {aiServiceData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-3">
                {aiServiceData.map((item) => (
                  <div key={item.name} className="flex items-center gap-3">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                    <div>
                      <div className="text-sm text-slate-900">{item.name}</div>
                      <div className="text-sm text-slate-500">{item.value}%</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Threat Categories */}
      <Card>
        <CardHeader>
          <CardTitle>위협 카테고리 분석</CardTitle>
          <CardDescription>탐지된 위협 유형별 통계</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={threatData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="category" stroke="#64748b" />
              <YAxis stroke="#64748b" />
              <Tooltip />
              <Bar dataKey="count" fill="#ef4444" name="탐지 건수" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Recent Alerts */}
      <Card>
        <CardHeader>
          <CardTitle>최근 보안 알림</CardTitle>
          <CardDescription>실시간 위협 탐지 현황</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              { type: "critical", message: "민감정보 포함 프롬프트 차단", user: "김철수", time: "2분 전" },
              { type: "warning", message: "비인가 AI 서비스 접근 시도", user: "이영희", time: "15분 전" },
              { type: "info", message: "정책 위반 프롬프트 감지", user: "박민수", time: "1시간 전" },
              { type: "critical", message: "악성 코드 생성 시도 차단", user: "정수진", time: "2시간 전" },
            ].map((alert, index) => (
              <div key={index} className="flex items-start gap-4 p-4 bg-slate-50 rounded-lg">
                <div className={`mt-0.5 ${
                  alert.type === "critical" ? "text-red-500" : 
                  alert.type === "warning" ? "text-amber-500" : 
                  "text-blue-500"
                }`}>
                  <AlertTriangle className="w-5 h-5" />
                </div>
                <div className="flex-1">
                  <div className="text-slate-900">{alert.message}</div>
                  <div className="text-sm text-slate-500 mt-1">
                    사용자: {alert.user} · {alert.time}
                  </div>
                </div>
                <Badge variant={alert.type === "critical" ? "destructive" : "outline"}>
                  {alert.type === "critical" ? "긴급" : alert.type === "warning" ? "경고" : "정보"}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
