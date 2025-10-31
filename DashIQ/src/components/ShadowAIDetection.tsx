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
