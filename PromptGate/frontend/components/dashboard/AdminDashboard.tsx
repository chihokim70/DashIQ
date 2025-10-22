import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { Shield, AlertTriangle, Users, Settings } from "lucide-react";
import { OverviewStats } from "./OverviewStats";
import { PromptFiltering } from "./PromptFiltering";
import { ShadowAIDetection } from "./ShadowAIDetection";
import { UserLogs } from "./UserLogs";
import { SecurityPolicy } from "./SecurityPolicy";

export function AdminDashboard() {
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
                <h1 className="text-slate-900 text-xl font-semibold">AI Security Dashboard</h1>
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