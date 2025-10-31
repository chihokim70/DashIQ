import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Textarea } from "./ui/textarea";
import { Switch } from "./ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Shield, Plus, Trash2, Edit2, Save, AlertTriangle } from "lucide-react";
import { toast } from "sonner@2.0.3";

const allowedServices = [
  { id: 1, name: "ChatGPT Enterprise", provider: "OpenAI", status: "active", users: 342 },
  { id: 2, name: "Claude for Work", provider: "Anthropic", status: "active", users: 256 },
  { id: 3, name: "Gemini Advanced", provider: "Google", status: "active", users: 189 },
];

const filterRules = [
  { id: 1, name: "개인정보 보호", category: "개인정보", pattern: "주민등록번호|전화번호|이메일", action: "차단", priority: "높음", status: "active" },
  { id: 2, name: "기밀정보 차단", category: "기밀정보", pattern: "재무제표|급여|계약서", action: "차단", priority: "높음", status: "active" },
  { id: 3, name: "악성코드 탐지", category: "악성코드", pattern: "랜섬웨어|악성|해킹", action: "차단", priority: "치명적", status: "active" },
  { id: 4, name: "저작권 보호", category: "저작권", pattern: "불법복제|해적판", action: "경고", priority: "중간", status: "inactive" },
];

const departments = [
  { id: 1, name: "개발팀", users: 45, allowedServices: ["ChatGPT", "Claude"], restrictions: "없음" },
  { id: 2, name: "마케팅팀", users: 32, allowedServices: ["ChatGPT", "Gemini"], restrictions: "기밀정보 제한" },
  { id: 3, name: "영업팀", users: 28, allowedServices: ["ChatGPT"], restrictions: "고객정보 제한" },
  { id: 4, name: "디자인팀", users: 15, allowedServices: ["ChatGPT", "Claude"], restrictions: "없음" },
];

export function SecurityPolicy() {
  const [newRuleName, setNewRuleName] = useState("");
  const [editingRule, setEditingRule] = useState<number | null>(null);

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

        {/* Allowed Services */}
        <TabsContent value="services" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>허용된 AI 서비스</CardTitle>
                  <CardDescription>기업에서 사용 가능한 AI 서비스 목록</CardDescription>
                </div>
                <Button className="gap-2">
                  <Plus className="w-4 h-4" />
                  서비스 추가
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>서비스명</TableHead>
                    <TableHead>제공업체</TableHead>
                    <TableHead>사용자 수</TableHead>
                    <TableHead>상태</TableHead>
                    <TableHead>작업</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {allowedServices.map((service) => (
                    <TableRow key={service.id}>
                      <TableCell className="text-slate-900">{service.name}</TableCell>
                      <TableCell className="text-slate-600">{service.provider}</TableCell>
                      <TableCell>{service.users}명</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                          활성
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button variant="ghost" size="sm">
                            <Edit2 className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm" className="text-red-600 hover:text-red-700">
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Filtering Rules */}
        <TabsContent value="filtering" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>필터링 규칙</CardTitle>
                  <CardDescription>프롬프트 필터링 및 차단 규칙 관리</CardDescription>
                </div>
                <Button className="gap-2">
                  <Plus className="w-4 h-4" />
                  규칙 추가
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>규칙명</TableHead>
                    <TableHead>카테고리</TableHead>
                    <TableHead>패턴</TableHead>
                    <TableHead>조치</TableHead>
                    <TableHead>우선순위</TableHead>
                    <TableHead>상태</TableHead>
                    <TableHead>작업</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filterRules.map((rule) => (
                    <TableRow key={rule.id}>
                      <TableCell className="text-slate-900">{rule.name}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{rule.category}</Badge>
                      </TableCell>
                      <TableCell className="max-w-xs">
                        <code className="text-xs bg-slate-100 px-2 py-1 rounded">
                          {rule.pattern}
                        </code>
                      </TableCell>
                      <TableCell>
                        <Badge variant={rule.action === "차단" ? "destructive" : "outline"}>
                          {rule.action}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={rule.priority === "치명적" ? "destructive" : "outline"}
                          className={
                            rule.priority === "높음" ? "bg-red-50 text-red-700 border-red-200" :
                            rule.priority === "중간" ? "bg-amber-50 text-amber-700 border-amber-200" :
                            ""
                          }
                        >
                          {rule.priority}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Switch checked={rule.status === "active"} />
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button variant="ghost" size="sm">
                            <Edit2 className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm" className="text-red-600 hover:text-red-700">
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Department Policies */}
        <TabsContent value="departments" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>부서별 정책</CardTitle>
              <CardDescription>부서별 AI 사용 권한 및 제한사항</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>부서명</TableHead>
                    <TableHead>사용자 수</TableHead>
                    <TableHead>허용 서비스</TableHead>
                    <TableHead>제한사항</TableHead>
                    <TableHead>작업</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {departments.map((dept) => (
                    <TableRow key={dept.id}>
                      <TableCell className="text-slate-900">{dept.name}</TableCell>
                      <TableCell>{dept.users}명</TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          {dept.allowedServices.map((service) => (
                            <Badge key={service} variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                              {service}
                            </Badge>
                          ))}
                        </div>
                      </TableCell>
                      <TableCell className="text-slate-600">{dept.restrictions}</TableCell>
                      <TableCell>
                        <Button variant="ghost" size="sm">
                          <Edit2 className="w-4 h-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* General Settings */}
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

                <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                  <div className="space-y-1">
                    <Label>사용자 활동 로깅</Label>
                    <p className="text-sm text-slate-500">
                      모든 AI 사용 활동을 기록하고 저장합니다
                    </p>
                  </div>
                  <Switch defaultChecked />
                </div>

                <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                  <div className="space-y-1">
                    <Label>위협 알림</Label>
                    <p className="text-sm text-slate-500">
                      보안 위협 탐지 시 관리자에게 즉시 알림을 전송합니다
                    </p>
                  </div>
                  <Switch defaultChecked />
                </div>

                <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                  <div className="space-y-1">
                    <Label>프롬프트 검토 모드</Label>
                    <p className="text-sm text-slate-500">
                      차단된 프롬프트를 관리자가 검토 후 허용할 수 있습니다
                    </p>
                  </div>
                  <Switch />
                </div>
              </div>

              <div className="space-y-4 pt-4 border-t">
                <div className="grid gap-2">
                  <Label>로그 보관 기간</Label>
                  <Select defaultValue="90">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="30">30일</SelectItem>
                      <SelectItem value="90">90일</SelectItem>
                      <SelectItem value="180">180일</SelectItem>
                      <SelectItem value="365">1년</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid gap-2">
                  <Label>위협 탐지 민감도</Label>
                  <Select defaultValue="medium">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">낮음</SelectItem>
                      <SelectItem value="medium">중간</SelectItem>
                      <SelectItem value="high">높음</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid gap-2">
                  <Label>관리자 이메일</Label>
                  <Input type="email" placeholder="admin@company.com" defaultValue="admin@company.com" />
                </div>

                <div className="grid gap-2">
                  <Label>알림 임계값 (시간당 차단 건수)</Label>
                  <Input type="number" placeholder="10" defaultValue="10" />
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
