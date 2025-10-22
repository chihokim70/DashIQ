import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../ui/table";
import { Button } from "../ui/button";
import { Progress } from "../ui/progress";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

// Type assertions for Recharts components
const RContainer = ResponsiveContainer as any;
const BChart = BarChart as any;
const XAxisComponent = XAxis as any;
const YAxisComponent = YAxis as any;
const TooltipComponent = Tooltip as any;
const BarComponent = Bar as any;
const CartesianGridComponent = CartesianGrid as any;
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
          <RContainer width="100%" height={300}>
            <BChart data={hourlyData}>
              <CartesianGridComponent strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxisComponent dataKey="hour" stroke="#64748b" />
              <YAxisComponent stroke="#64748b" />
              <TooltipComponent />
              <BarComponent dataKey="blocked" fill="#ef4444" name="차단된 프롬프트" />
            </BChart>
          </RContainer>
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
                    <Button variant="ghost" size="default" className="gap-2">
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