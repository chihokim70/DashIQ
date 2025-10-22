import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../ui/table";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../ui/select";
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
  {
    id: 3,
    timestamp: "2025-01-21 14:28:45",
    user: "박민수",
    dept: "영업팀",
    service: "Gemini",
    action: "프롬프트 전송",
    prompt: "경쟁사 분석 보고서 작성해줘",
    result: "성공",
    risk: "medium",
  },
  {
    id: 4,
    timestamp: "2025-01-21 14:25:30",
    user: "정수진",
    dept: "개발팀",
    service: "ChatGPT",
    action: "프롬프트 전송",
    prompt: "JavaScript 함수 최적화 방법",
    result: "성공",
    risk: "low",
  },
  {
    id: 5,
    timestamp: "2025-01-21 14:20:15",
    user: "최지훈",
    dept: "디자인팀",
    service: "Claude",
    action: "프롬프트 전송",
    prompt: "UI/UX 디자인 트렌드 분석",
    result: "성공",
    risk: "low",
  },
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
                      <Button variant="ghost" size="default" className="gap-2">
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
              <Button variant="outline" size="default" disabled>
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <Button variant="outline" size="default">1</Button>
              <Button variant="outline" size="default">2</Button>
              <Button variant="outline" size="default">3</Button>
              <Button variant="outline" size="default">...</Button>
              <Button variant="outline" size="default">1548</Button>
              <Button variant="outline" size="default">
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}