# AI Security Dashboard - 전체 코드

AI보안솔루션의 관리자 대시보드 전체 소스 코드입니다.

## 📁 파일 구조

```
├── App.tsx
└── components/
    ├── Dashboard.tsx
    ├── OverviewStats.tsx
    ├── PromptFiltering.tsx
    ├── ShadowAIDetection.tsx
    ├── UserLogs.tsx
    └── SecurityPolicy.tsx
```

---

## 📄 App.tsx

```tsx
import { Dashboard } from "./components/Dashboard";

export default function App() {
  return <Dashboard />;
}
```

---

## 📄 components/Dashboard.tsx

메인 대시보드 컴포넌트 - 탭 네비게이션 및 전체 레이아웃

```tsx
import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Shield, AlertTriangle, Users, Settings } from "lucide-react";
import { OverviewStats } from "./OverviewStats";
import { PromptFiltering } from "./PromptFiltering";
import { ShadowAIDetection } from "./ShadowAIDetection";
import { UserLogs } from "./UserLogs";
import { SecurityPolicy } from "./SecurityPolicy";

export function Dashboard() {
  const [activeTab, setActiveTab] = useState("overview");

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-10 h-10 bg-blue-600 rounded-lg">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-slate-900">AI Security Dashboard</h1>
                <p className="text-slate-500 text-sm">기업 AI 사용 현황 및 보안 관리</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                시스템 정상
              </Badge>
              <div className="text-sm text-slate-600">
                마지막 업데이트: {new Date().toLocaleTimeString('ko-KR')}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="p-6">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="bg-white border border-slate-200">
            <TabsTrigger value="overview" className="gap-2">
              <Shield className="w-4 h-4" />
              대시보드 개요
            </TabsTrigger>
            <TabsTrigger value="filtering" className="gap-2">
              <AlertTriangle className="w-4 h-4" />
              프롬프트 필터링
            </TabsTrigger>
            <TabsTrigger value="shadow-ai" className="gap-2">
              <AlertTriangle className="w-4 h-4" />
              Shadow AI 탐지
            </TabsTrigger>
            <TabsTrigger value="logs" className="gap-2">
              <Users className="w-4 h-4" />
              사용자 로그
            </TabsTrigger>
            <TabsTrigger value="policy" className="gap-2">
              <Settings className="w-4 h-4" />
              보안 정책
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <OverviewStats />
          </TabsContent>

          <TabsContent value="filtering" className="space-y-6">
            <PromptFiltering />
          </TabsContent>

          <TabsContent value="shadow-ai" className="space-y-6">
            <ShadowAIDetection />
          </TabsContent>

          <TabsContent value="logs" className="space-y-6">
            <UserLogs />
          </TabsContent>

          <TabsContent value="policy" className="space-y-6">
            <SecurityPolicy />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
```

---

## 📄 components/OverviewStats.tsx

대시보드 개요 - 통계, 차트, 최근 알림

```tsx
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
```

---

## 📄 components/PromptFiltering.tsx

프롬프트 필터링 통계 및 차단된 프롬프트 목록

```tsx
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Button } from "./ui/button";
import { Progress } from "./ui/progress";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { Shield, AlertTriangle, Eye, Download } from "lucide-react";

const filterStats = [
  { category: "개인정보", blocked: 256, total: 1200, risk: "high" },
  { category: "기밀정보", blocked: 189, total: 890, risk: "high" },
  { category: "악성코드", blocked: 142, total: 450, risk: "critical" },
  { category: "부적절한 콘텐츠", blocked: 98, total: 650, risk: "medium" },
  { category: "저작권 위반", blocked: 76, total: 420, risk: "medium" },
];

const recentBlocked = [
  {
    id: 1,
    user: "김철수",
    dept: "개발팀",
    prompt: "고객 데이터베이스에서 주민등록번호 추출하는 SQL 쿼리 작성해줘",
    category: "개인정보",
    time: "2025-01-21 14:32:15",
    action: "차단됨",
  },
  {
    id: 2,
    user: "이영희",
    dept: "마케팅팀",
    prompt: "회사 내부 재무제표 분석 및 요약해줘",
    category: "기밀정보",
    time: "2025-01-21 14:28:42",
    action: "차단됨",
  },
  {
    id: 3,
    user: "박민수",
    dept: "영업팀",
    prompt: "경쟁사 고객 리스트 확보 방법 알려줘",
    category: "부적절한 콘텐츠",
    time: "2025-01-21 14:15:30",
    action: "차단됨",
  },
  {
    id: 4,
    user: "정수진",
    dept: "개발팀",
    prompt: "랜섬웨어 코드 작성하는 방법",
    category: "악성코드",
    time: "2025-01-21 13:58:12",
    action: "차단됨",
  },
  {
    id: 5,
    user: "최지훈",
    dept: "디자인팀",
    prompt: "고객 신용카드 정보 추출하는 스크립트",
    category: "개인정보",
    time: "2025-01-21 13:42:05",
    action: "차단됨",
  },
];

const hourlyData = [
  { hour: "00:00", blocked: 12 },
  { hour: "03:00", blocked: 8 },
  { hour: "06:00", blocked: 15 },
  { hour: "09:00", blocked: 45 },
  { hour: "12:00", blocked: 62 },
  { hour: "15:00", blocked: 58 },
  { hour: "18:00", blocked: 38 },
  { hour: "21:00", blocked: 22 },
];

export function PromptFiltering() {
  return (
    <div className="space-y-6">
      {/* Filter Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {filterStats.map((stat) => (
          <Card key={stat.category}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardDescription>{stat.category}</CardDescription>
                <Badge 
                  variant={stat.risk === "critical" ? "destructive" : "outline"}
                  className={
                    stat.risk === "high" ? "bg-red-50 text-red-700 border-red-200" :
                    stat.risk === "medium" ? "bg-amber-50 text-amber-700 border-amber-200" :
                    ""
                  }
                >
                  {stat.risk === "critical" ? "치명적" : stat.risk === "high" ? "높음" : "중간"}
                </Badge>
              </div>
              <CardTitle className="text-slate-900">{stat.blocked}</CardTitle>
            </CardHeader>
            <CardContent>
              <Progress value={(stat.blocked / stat.total) * 100} className="h-2" />
              <div className="text-sm text-slate-500 mt-2">
                전체 {stat.total}건 중 {((stat.blocked / stat.total) * 100).toFixed(1)}%
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Hourly Blocking Trend */}
      <Card>
        <CardHeader>
          <CardTitle>시간대별 차단 추이</CardTitle>
          <CardDescription>오늘 시간대별 프롬프트 차단 현황</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={hourlyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="hour" stroke="#64748b" />
              <YAxis stroke="#64748b" />
              <Tooltip />
              <Bar dataKey="blocked" fill="#ef4444" name="차단된 프롬프트" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Recent Blocked Prompts */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>최근 차단된 프롬프트</CardTitle>
              <CardDescription>실시간으로 차단된 프롬프트 목록</CardDescription>
            </div>
            <Button variant="outline" className="gap-2">
              <Download className="w-4 h-4" />
              내보내기
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>사용자</TableHead>
                <TableHead>부서</TableHead>
                <TableHead>프롬프트</TableHead>
                <TableHead>카테고리</TableHead>
                <TableHead>시간</TableHead>
                <TableHead>상태</TableHead>
                <TableHead>작업</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {recentBlocked.map((item) => (
                <TableRow key={item.id}>
                  <TableCell>{item.user}</TableCell>
                  <TableCell className="text-slate-600">{item.dept}</TableCell>
                  <TableCell className="max-w-md">
                    <div className="truncate">{item.prompt}</div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">
                      {item.category}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-slate-600">{item.time}</TableCell>
                  <TableCell>
                    <Badge variant="destructive">{item.action}</Badge>
                  </TableCell>
                  <TableCell>
                    <Button variant="ghost" size="sm" className="gap-2">
                      <Eye className="w-4 h-4" />
                      상세
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Filter Rules Status */}
      <Card>
        <CardHeader>
          <CardTitle>필터링 규칙 현황</CardTitle>
          <CardDescription>현재 적용 중인 필터링 규칙</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              { name: "개인정보 보호", rules: 45, active: true, matches: 256 },
              { name: "기밀정보 차단", rules: 32, active: true, matches: 189 },
              { name: "악성코드 탐지", rules: 28, active: true, matches: 142 },
              { name: "부적절한 콘텐츠", rules: 21, active: true, matches: 98 },
              { name: "저작권 보호", rules: 18, active: false, matches: 0 },
            ].map((rule, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                <div className="flex items-center gap-4">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                    rule.active ? "bg-green-100" : "bg-slate-200"
                  }`}>
                    <Shield className={`w-5 h-5 ${rule.active ? "text-green-600" : "text-slate-400"}`} />
                  </div>
                  <div>
                    <div className="text-slate-900">{rule.name}</div>
                    <div className="text-sm text-slate-500">{rule.rules}개 규칙 적용</div>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <div className="text-slate-900">{rule.matches}건</div>
                    <div className="text-sm text-slate-500">매칭됨</div>
                  </div>
                  <Badge variant={rule.active ? "outline" : "secondary"} className={
                    rule.active ? "bg-green-50 text-green-700 border-green-200" : ""
                  }>
                    {rule.active ? "활성" : "비활성"}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
```

---

## 📄 components/ShadowAIDetection.tsx

Shadow AI 탐지 현황 및 통계

```tsx
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Button } from "./ui/button";
import { Progress } from "./ui/progress";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import { AlertTriangle, Ban, CheckCircle2, Eye, Activity } from "lucide-react";

const detectedServices = [
  {
    id: 1,
    service: "ChatGPT (개인계정)",
    users: 23,
    requests: 1245,
    risk: "high",
    status: "detected",
    lastSeen: "2025-01-21 14:35:20",
  },
  {
    id: 2,
    service: "Claude (비인가)",
    users: 15,
    requests: 892,
    risk: "high",
    status: "detected",
    lastSeen: "2025-01-21 14:28:45",
  },
  {
    id: 3,
    service: "Gemini (개인계정)",
    users: 12,
    requests: 567,
    risk: "medium",
    status: "detected",
    lastSeen: "2025-01-21 14:15:10",
  },
  {
    id: 4,
    service: "Perplexity AI",
    users: 8,
    requests: 234,
    risk: "medium",
    status: "detected",
    lastSeen: "2025-01-21 13:52:33",
  },
  {
    id: 5,
    service: "미확인 AI 서비스",
    users: 5,
    requests: 128,
    risk: "critical",
    status: "detected",
    lastSeen: "2025-01-21 13:20:15",
  },
];

const trendData = [
  { date: "01/15", detected: 45, blocked: 12 },
  { date: "01/16", detected: 52, blocked: 18 },
  { date: "01/17", detected: 48, blocked: 15 },
  { date: "01/18", detected: 61, blocked: 22 },
  { date: "01/19", detected: 58, blocked: 19 },
  { date: "01/20", detected: 67, blocked: 28 },
  { date: "01/21", detected: 63, blocked: 25 },
];

const riskDistribution = [
  { name: "치명적", value: 15, color: "#dc2626" },
  { name: "높음", value: 38, color: "#f59e0b" },
  { name: "중간", value: 32, color: "#3b82f6" },
  { name: "낮음", value: 15, color: "#10b981" },
];

const topUsers = [
  { name: "김철수", dept: "개발팀", services: 5, requests: 342 },
  { name: "이영희", dept: "마케팅팀", services: 4, requests: 289 },
  { name: "박민수", dept: "영업팀", services: 3, requests: 256 },
  { name: "정수진", dept: "개발팀", services: 4, requests: 234 },
  { name: "최지훈", dept: "디자인팀", services: 3, requests: 198 },
];

export function ShadowAIDetection() {
  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>탐지된 Shadow AI</CardDescription>
            <CardTitle className="text-slate-900">28</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 text-red-600 text-sm">
              <AlertTriangle className="w-4 h-4" />
              <span>5개 서비스 신규 탐지</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription>사용 중인 사용자</CardDescription>
            <CardTitle className="text-slate-900">63</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 text-amber-600 text-sm">
              <Activity className="w-4 h-4" />
              <span>전체의 18.4%</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription>총 비인가 요청</CardDescription>
            <CardTitle className="text-slate-900">3,066</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 text-red-600 text-sm">
              <AlertTriangle className="w-4 h-4" />
              <span>이번 주 누적</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription>차단 성공률</CardDescription>
            <CardTitle className="text-slate-900">94.3%</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 text-green-600 text-sm">
              <CheckCircle2 className="w-4 h-4" />
              <span>효과적으로 차단 중</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detection Trend */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Shadow AI 탐지 추이</CardTitle>
            <CardDescription>최근 7일간 탐지 및 차단 현황</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="date" stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip />
                <Line type="monotone" dataKey="detected" stroke="#f59e0b" strokeWidth={2} name="탐지됨" />
                <Line type="monotone" dataKey="blocked" stroke="#ef4444" strokeWidth={2} name="차단됨" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>위험도 분포</CardTitle>
            <CardDescription>서비스별 위험도</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={riskDistribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {riskDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="space-y-2 mt-4">
              {riskDistribution.map((item) => (
                <div key={item.name} className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-slate-600">{item.name}</span>
                  </div>
                  <span className="text-slate-900">{item.value}%</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detected Services */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>탐지된 Shadow AI 서비스</CardTitle>
              <CardDescription>비인가 AI 서비스 사용 현황</CardDescription>
            </div>
            <Button variant="outline" className="gap-2">
              <Ban className="w-4 h-4" />
              일괄 차단
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>서비스명</TableHead>
                <TableHead>사용자 수</TableHead>
                <TableHead>요청 수</TableHead>
                <TableHead>위험도</TableHead>
                <TableHead>상태</TableHead>
                <TableHead>마지막 탐지</TableHead>
                <TableHead>작업</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {detectedServices.map((service) => (
                <TableRow key={service.id}>
                  <TableCell className="text-slate-900">{service.service}</TableCell>
                  <TableCell>{service.users}명</TableCell>
                  <TableCell>{service.requests.toLocaleString()}</TableCell>
                  <TableCell>
                    <Badge
                      variant={service.risk === "critical" ? "destructive" : "outline"}
                      className={
                        service.risk === "high" ? "bg-red-50 text-red-700 border-red-200" :
                        service.risk === "medium" ? "bg-amber-50 text-amber-700 border-amber-200" :
                        ""
                      }
                    >
                      {service.risk === "critical" ? "치명적" : service.risk === "high" ? "높음" : "중간"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">
                      탐지됨
                    </Badge>
                  </TableCell>
                  <TableCell className="text-slate-600">{service.lastSeen}</TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button variant="ghost" size="sm" className="gap-2">
                        <Eye className="w-4 h-4" />
                        상세
                      </Button>
                      <Button variant="ghost" size="sm" className="gap-2 text-red-600 hover:text-red-700">
                        <Ban className="w-4 h-4" />
                        차단
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Top Users */}
      <Card>
        <CardHeader>
          <CardTitle>Shadow AI 사용 상위 사용자</CardTitle>
          <CardDescription>비인가 AI 서비스를 가장 많이 사용하는 사용자</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {topUsers.map((user, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center text-slate-600">
                    {index + 1}
                  </div>
                  <div>
                    <div className="text-slate-900">{user.name}</div>
                    <div className="text-sm text-slate-500">{user.dept}</div>
                  </div>
                </div>
                <div className="flex items-center gap-8">
                  <div className="text-center">
                    <div className="text-slate-900">{user.services}</div>
                    <div className="text-sm text-slate-500">서비스</div>
                  </div>
                  <div className="text-center">
                    <div className="text-slate-900">{user.requests}</div>
                    <div className="text-sm text-slate-500">요청 수</div>
                  </div>
                  <Button variant="outline" size="sm">
                    상세 보기
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
```

---

## 📄 components/UserLogs.tsx

사용자 활동 로그 및 검색/필터 기능

```tsx
import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Search, Download, Filter, Eye, ChevronLeft, ChevronRight } from "lucide-react";

const logs = [
  {
    id: 1,
    timestamp: "2025-01-21 14:35:20",
    user: "김철수",
    dept: "개발팀",
    service: "ChatGPT",
    action: "프롬프트 전송",
    prompt: "Python으로 데이터 분석 코드 작성해줘",
    result: "성공",
    risk: "low",
  },
  {
    id: 2,
    timestamp: "2025-01-21 14:32:15",
    user: "이영희",
    dept: "마케팅팀",
    service: "Claude",
    action: "프롬프트 전송",
    prompt: "고객 데이터베이스에서 주민등록번호 추출...",
    result: "차단됨",
    risk: "high",
  },
  // ... 나머지 로그 데이터
];

export function UserLogs() {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterDept, setFilterDept] = useState("all");
  const [filterResult, setFilterResult] = useState("all");

  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>총 로그 수</CardDescription>
            <CardTitle className="text-slate-900">15,482</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-slate-600">오늘</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription>성공한 요청</CardDescription>
            <CardTitle className="text-slate-900 text-green-600">13,635</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-slate-600">88.1% 성공률</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription>차단된 요청</CardDescription>
            <CardTitle className="text-slate-900 text-red-600">1,847</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-slate-600">11.9% 차단율</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription>활성 사용자</CardDescription>
            <CardTitle className="text-slate-900">342</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-slate-600">현재 접속 중</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>사용자 활동 로그</CardTitle>
              <CardDescription>모든 AI 사용 활동이 기록됩니다</CardDescription>
            </div>
            <Button variant="outline" className="gap-2">
              <Download className="w-4 h-4" />
              로그 내보내기
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Filter Bar */}
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input
                placeholder="사용자, 프롬프트 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={filterDept} onValueChange={setFilterDept}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="부서 선택" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">모든 부서</SelectItem>
                <SelectItem value="dev">개발팀</SelectItem>
                <SelectItem value="marketing">마케팅팀</SelectItem>
                <SelectItem value="sales">영업팀</SelectItem>
                <SelectItem value="design">디자인팀</SelectItem>
                <SelectItem value="hr">HR팀</SelectItem>
                <SelectItem value="finance">재무팀</SelectItem>
              </SelectContent>
            </Select>
            <Select value={filterResult} onValueChange={setFilterResult}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="결과 필터" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">모든 결과</SelectItem>
                <SelectItem value="success">성공</SelectItem>
                <SelectItem value="blocked">차단됨</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" className="gap-2">
              <Filter className="w-4 h-4" />
              필터
            </Button>
          </div>

          {/* Logs Table */}
          <div className="border rounded-lg">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>시간</TableHead>
                  <TableHead>사용자</TableHead>
                  <TableHead>부서</TableHead>
                  <TableHead>서비스</TableHead>
                  <TableHead>프롬프트</TableHead>
                  <TableHead>결과</TableHead>
                  <TableHead>위험도</TableHead>
                  <TableHead>작업</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {logs.map((log) => (
                  <TableRow key={log.id}>
                    <TableCell className="text-slate-600 text-sm">{log.timestamp}</TableCell>
                    <TableCell className="text-slate-900">{log.user}</TableCell>
                    <TableCell className="text-slate-600">{log.dept}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{log.service}</Badge>
                    </TableCell>
                    <TableCell className="max-w-xs">
                      <div className="truncate text-sm">{log.prompt}</div>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={log.result === "성공" ? "outline" : "destructive"}
                        className={log.result === "성공" ? "bg-green-50 text-green-700 border-green-200" : ""}
                      >
                        {log.result}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={log.risk === "critical" || log.risk === "high" ? "destructive" : "outline"}
                        className={
                          log.risk === "high" ? "bg-red-50 text-red-700 border-red-200" :
                          log.risk === "medium" ? "bg-amber-50 text-amber-700 border-amber-200" :
                          log.risk === "low" ? "bg-blue-50 text-blue-700 border-blue-200" :
                          ""
                        }
                      >
                        {log.risk === "critical" ? "치명적" : 
                         log.risk === "high" ? "높음" : 
                         log.risk === "medium" ? "중간" : "낮음"}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Button variant="ghost" size="sm" className="gap-2">
                        <Eye className="w-4 h-4" />
                        상세
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between pt-4">
            <div className="text-sm text-slate-600">
              전체 15,482개 중 1-10 표시
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" disabled>
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <Button variant="outline" size="sm">1</Button>
              <Button variant="outline" size="sm">2</Button>
              <Button variant="outline" size="sm">3</Button>
              <Button variant="outline" size="sm">...</Button>
              <Button variant="outline" size="sm">1548</Button>
              <Button variant="outline" size="sm">
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
```

---

## 📄 components/SecurityPolicy.tsx

보안 정책 설정 및 관리

```tsx
import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Switch } from "./ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Shield, Plus, Trash2, Edit2, Save, AlertTriangle } from "lucide-react";
import { toast } from "sonner@2.0.3";

export function SecurityPolicy() {
  const handleSavePolicy = () => {
    toast("보안 정책이 저장되었습니다", {
      description: "변경사항이 즉시 적용됩니다.",
    });
  };

  return (
    <div className="space-y-6">
      {/* Policy Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>활성 정책</CardDescription>
            <CardTitle className="text-slate-900">27</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-slate-600">적용 중인 보안 규칙</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription>허용된 AI 서비스</CardDescription>
            <CardTitle className="text-slate-900">3</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-slate-600">기업용 라이센스 보유</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription>마지막 업데이트</CardDescription>
            <CardTitle className="text-slate-900">2시간 전</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-slate-600">관리자: 김관리</div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="services" className="space-y-6">
        <TabsList className="bg-white border border-slate-200">
          <TabsTrigger value="services">허용 서비스</TabsTrigger>
          <TabsTrigger value="filtering">필터링 규칙</TabsTrigger>
          <TabsTrigger value="departments">부서별 정책</TabsTrigger>
          <TabsTrigger value="general">일반 설정</TabsTrigger>
        </TabsList>

        {/* General Settings Tab Example */}
        <TabsContent value="general" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>일반 설정</CardTitle>
              <CardDescription>전사 적용되는 보안 정책 설정</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                  <div className="space-y-1">
                    <Label>프롬프트 자동 필터링</Label>
                    <p className="text-sm text-slate-500">
                      민감한 정보가 포함된 프롬프트를 자동으로 차단합니다
                    </p>
                  </div>
                  <Switch defaultChecked />
                </div>

                <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                  <div className="space-y-1">
                    <Label>Shadow AI 실시간 탐지</Label>
                    <p className="text-sm text-slate-500">
                      비인가 AI 서비스 사용을 실시간으로 탐지합니다
                    </p>
                  </div>
                  <Switch defaultChecked />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t">
                <Button variant="outline">취소</Button>
                <Button className="gap-2" onClick={handleSavePolicy}>
                  <Save className="w-4 h-4" />
                  정책 저장
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Security Alert */}
          <Card className="border-amber-200 bg-amber-50">
            <CardHeader>
              <div className="flex gap-3">
                <AlertTriangle className="w-5 h-5 text-amber-600" />
                <div>
                  <CardTitle className="text-amber-900">보안 정책 변경 안내</CardTitle>
                  <CardDescription className="text-amber-700">
                    보안 정책 변경사항은 즉시 적용되며, 모든 사용자에게 영향을 미칩니다.
                    변경 전 충분히 검토해주시기 바랍니다.
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

---

## 🎨 사용된 주요 기술

- **React** - UI 프레임워크
- **TypeScript** - 타입 안전성
- **Tailwind CSS** - 스타일링
- **Recharts** - 데이터 시각화
- **Lucide React** - 아이콘
- **Shadcn/ui** - UI 컴포넌트 라이브러리
- **Sonner** - 토스트 알림

## 📋 주요 기능

### 1. 대시보드 개요
- 실시간 통계 (총 요청, 차단, 활성 사용자, 위협 탐지율)
- AI 사용 추이 라인 차트
- AI 서비스 사용 분포 파이 차트
- 위협 카테고리 분석 바 차트
- 최근 보안 알림 목록

### 2. 프롬프트 필터링
- 카테고리별 필터링 통계
- 시간대별 차단 추이
- 최근 차단된 프롬프트 테이블
- 필터링 규칙 현황

### 3. Shadow AI 탐지
- 탐지된 서비스 통계
- 탐지 추이 차트
- 위험도 분포
- 상위 사용자 목록

### 4. 사용자 로그
- 검색 및 필터 기능
- 활동 로그 테이블
- 페이지네이션
- 로그 내보내기

### 5. 보안 정책
- 허용 서비스 관리
- 필터링 규칙 설정
- 부서별 정책
- 일반 설정 및 알림

---

**생성일**: 2025-01-21
**버전**: 1.0.0
