import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Switch } from "../ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../ui/table";
import { Shield, Plus, Trash2, Edit2, Save, AlertTriangle } from "lucide-react";

export function SecurityPolicy() {
  const handleSavePolicy = () => {
    // Handle save policy logic here
    console.log("보안 정책이 저장되었습니다");
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

        {/* Allowed Services Tab */}
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
                    <TableHead>라이센스</TableHead>
                    <TableHead>사용자 수</TableHead>
                    <TableHead>상태</TableHead>
                    <TableHead>작업</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {[
                    { name: "ChatGPT Enterprise", license: "기업용", users: 250, status: "active" },
                    { name: "Claude Pro", license: "프로페셔널", users: 150, status: "active" },
                    { name: "Gemini Advanced", license: "고급", users: 100, status: "active" },
                  ].map((service, index) => (
                    <TableRow key={index}>
                      <TableCell className="text-slate-900">{service.name}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                          {service.license}
                        </Badge>
                      </TableCell>
                      <TableCell>{service.users}명</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                          활성
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button variant="ghost" size="default">
                            <Edit2 className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="default">
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

        {/* Filtering Rules Tab */}
        <TabsContent value="filtering" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>필터링 규칙</CardTitle>
                  <CardDescription>프롬프트 필터링 규칙 관리</CardDescription>
                </div>
                <Button className="gap-2">
                  <Plus className="w-4 h-4" />
                  규칙 추가
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { name: "개인정보 보호", description: "주민등록번호, 전화번호 등 개인정보 감지", active: true, severity: "high" },
                  { name: "기밀정보 차단", description: "회사 기밀, 재무 정보 등 민감 데이터 차단", active: true, severity: "critical" },
                  { name: "악성코드 탐지", description: "멀웨어, 바이러스 등 악성 코드 생성 차단", active: true, severity: "critical" },
                  { name: "부적절한 콘텐츠", description: "폭력적, 성적 콘텐츠 등 부적절한 내용 차단", active: false, severity: "medium" },
                ].map((rule, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                    <div className="flex items-center gap-4">
                      <Switch defaultChecked={rule.active} />
                      <div>
                        <div className="text-slate-900 font-medium">{rule.name}</div>
                        <div className="text-sm text-slate-500">{rule.description}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <Badge
                        variant={rule.severity === "critical" ? "destructive" : "outline"}
                        className={
                          rule.severity === "high" ? "bg-red-50 text-red-700 border-red-200" :
                          rule.severity === "medium" ? "bg-amber-50 text-amber-700 border-amber-200" :
                          ""
                        }
                      >
                        {rule.severity === "critical" ? "치명적" : rule.severity === "high" ? "높음" : "중간"}
                      </Badge>
                      <Button variant="ghost" size="default">
                        <Edit2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Department Policies Tab */}
        <TabsContent value="departments" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>부서별 정책</CardTitle>
              <CardDescription>부서별 차별화된 보안 정책 설정</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>부서</TableHead>
                    <TableHead>허용 서비스</TableHead>
                    <TableHead>필터링 수준</TableHead>
                    <TableHead>사용자 수</TableHead>
                    <TableHead>작업</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {[
                    { dept: "개발팀", services: 3, level: "중간", users: 45 },
                    { dept: "마케팅팀", services: 2, level: "높음", users: 32 },
                    { dept: "영업팀", services: 2, level: "높음", users: 28 },
                    { dept: "디자인팀", services: 3, level: "낮음", users: 15 },
                    { dept: "HR팀", services: 1, level: "최고", users: 8 },
                  ].map((dept, index) => (
                    <TableRow key={index}>
                      <TableCell className="text-slate-900">{dept.dept}</TableCell>
                      <TableCell>{dept.services}개</TableCell>
                      <TableCell>
                        <Badge
                          variant="outline"
                          className={
                            dept.level === "최고" ? "bg-red-50 text-red-700 border-red-200" :
                            dept.level === "높음" ? "bg-amber-50 text-amber-700 border-amber-200" :
                            dept.level === "중간" ? "bg-blue-50 text-blue-700 border-blue-200" :
                            "bg-green-50 text-green-700 border-green-200"
                          }
                        >
                          {dept.level}
                        </Badge>
                      </TableCell>
                      <TableCell>{dept.users}명</TableCell>
                      <TableCell>
                        <Button variant="ghost" size="default">
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

        {/* General Settings Tab */}
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
                      모든 AI 사용 활동을 상세히 기록합니다
                    </p>
                  </div>
                  <Switch defaultChecked />
                </div>

                <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                  <div className="space-y-1">
                    <Label>관리자 알림</Label>
                    <p className="text-sm text-slate-500">
                      보안 이벤트 발생 시 관리자에게 즉시 알림을 전송합니다
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