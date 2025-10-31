import { Shield, AlertTriangle, CheckCircle } from "lucide-react";
import { KPICard } from "../KPICard";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { Progress } from "../ui/progress";

const policyViolations = [
  { policy: "PII Detection", severity: "Critical", violations: 85, trend: "+12%" },
  { policy: "Data Leak Prevention", severity: "Critical", violations: 67, trend: "+8%" },
  { policy: "Confidential Info Filter", severity: "High", violations: 52, trend: "-5%" },
  { policy: "Usage Quota Limit", severity: "High", violations: 48, trend: "+15%" },
  { policy: "Shadow AI Detection", severity: "Critical", violations: 42, trend: "+22%" },
  { policy: "NSFW Content Filter", severity: "Medium", violations: 38, trend: "-3%" },
  { policy: "Code Exposure Prevention", severity: "High", violations: 29, trend: "+7%" },
  { policy: "Prompt Injection Detection", severity: "Critical", violations: 24, trend: "-12%" },
  { policy: "Token Rate Limit", severity: "Low", violations: 18, trend: "+2%" },
  { policy: "External API Usage", severity: "Medium", violations: 15, trend: "-8%" },
];

const heatmapData = [
  { department: "Engineering", "00-04": 2, "04-08": 5, "08-12": 45, "12-16": 38, "16-20": 28, "20-24": 8 },
  { department: "Sales", "00-04": 0, "04-08": 1, "08-12": 22, "12-16": 35, "16-20": 18, "20-24": 3 },
  { department: "Marketing", "00-04": 1, "04-08": 2, "08-12": 28, "12-16": 42, "16-20": 25, "20-24": 5 },
  { department: "HR", "00-04": 0, "04-08": 1, "08-12": 12, "12-16": 18, "16-20": 8, "20-24": 2 },
  { department: "Finance", "00-04": 1, "04-08": 3, "08-12": 15, "12-16": 22, "16-20": 12, "20-24": 4 },
];

export function PolicyMonitor() {
  return (
    <div className="space-y-6 p-6">
      {/* Page Title */}
      <div>
        <h1>Policy Monitor</h1>
        <p className="text-muted-foreground mt-1">
          Monitor policy violations and compliance across all AI interactions
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <KPICard
          title="Total Policies"
          value="24"
          icon={Shield}
          color="primary"
        />
        <KPICard
          title="Active Policies"
          value="18"
          icon={CheckCircle}
          color="secondary"
        />
        <KPICard
          title="Today's Violations"
          value="127"
          icon={AlertTriangle}
          trend={{ value: "8.3%", isPositive: false }}
          color="destructive"
        />
      </div>

      {/* Department/Time Heatmap */}
      <Card>
        <CardHeader>
          <CardTitle>Policy Violations by Department & Time</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr>
                  <th className="text-left p-2">Department</th>
                  <th className="text-center p-2">00:00 - 04:00</th>
                  <th className="text-center p-2">04:00 - 08:00</th>
                  <th className="text-center p-2">08:00 - 12:00</th>
                  <th className="text-center p-2">12:00 - 16:00</th>
                  <th className="text-center p-2">16:00 - 20:00</th>
                  <th className="text-center p-2">20:00 - 24:00</th>
                </tr>
              </thead>
              <tbody>
                {heatmapData.map((row, idx) => (
                  <tr key={idx}>
                    <td className="p-2">{row.department}</td>
                    {["00-04", "04-08", "08-12", "12-16", "16-20", "20-24"].map((timeSlot) => {
                      const value = row[timeSlot as keyof typeof row] as number;
                      const intensity = Math.min(value / 45, 1);
                      return (
                        <td key={timeSlot} className="p-1">
                          <div 
                            className="w-20 h-10 rounded-lg flex items-center justify-center transition-all hover:scale-105"
                            style={{
                              backgroundColor: intensity > 0.7 
                                ? `rgba(239, 68, 68, ${intensity})` 
                                : intensity > 0.4
                                ? `rgba(245, 158, 11, ${intensity})`
                                : `rgba(30, 144, 255, ${intensity})`,
                              color: intensity > 0.5 ? '#ffffff' : '#111827'
                            }}
                            title={`${row.department} ${timeSlot}: ${value} violations`}
                          >
                            {value}
                          </div>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Top 10 Policy Violations */}
      <Card>
        <CardHeader>
          <CardTitle>Top 10 Policy Violations</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {policyViolations.map((policy, idx) => (
              <div key={idx} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3 flex-1">
                    <span className="min-w-[30px] text-muted-foreground">#{idx + 1}</span>
                    <span className="flex-1">{policy.policy}</span>
                    <Badge 
                      className={
                        policy.severity === "Critical" ? "bg-[#EF4444]" :
                        policy.severity === "High" ? "bg-[#F59E0B]" :
                        policy.severity === "Medium" ? "bg-[#1E90FF]" :
                        "bg-[#6B7280]"
                      }
                    >
                      {policy.severity}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-4 ml-4">
                    <span className="min-w-[80px] text-right">{policy.violations} violations</span>
                    <span 
                      className={`min-w-[60px] text-right ${
                        policy.trend.startsWith('+') ? 'text-[#EF4444]' : 'text-[#10B981]'
                      }`}
                    >
                      {policy.trend}
                    </span>
                  </div>
                </div>
                <Progress 
                  value={(policy.violations / 85) * 100} 
                  className="h-2"
                />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recent Critical Violations */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Critical Violations</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[
              { time: "14:32", user: "john.doe@company.com", policy: "PII Detection", detail: "Social security number detected in prompt" },
              { time: "14:15", user: "jane.smith@company.com", policy: "Data Leak Prevention", detail: "Customer database query attempt" },
              { time: "13:58", user: "mike.johnson@company.com", policy: "Shadow AI Detection", detail: "Unauthorized Claude API usage" },
              { time: "13:42", user: "sarah.williams@company.com", policy: "Confidential Info Filter", detail: "Internal project code referenced" },
              { time: "13:25", user: "robert.brown@company.com", policy: "Prompt Injection Detection", detail: "Potential jailbreak attempt" },
            ].map((violation, idx) => (
              <div 
                key={idx}
                className="flex items-start gap-4 p-4 bg-[#EF4444]/10 border border-[#EF4444]/20 rounded-lg"
              >
                <AlertTriangle className="w-5 h-5 text-[#EF4444] mt-0.5" />
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-muted-foreground">{violation.time}</span>
                    <span>•</span>
                    <span>{violation.user}</span>
                  </div>
                  <p className="mb-1">{violation.policy}</p>
                  <p className="text-muted-foreground">{violation.detail}</p>
                </div>
                <Badge className="bg-[#EF4444]">Critical</Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
