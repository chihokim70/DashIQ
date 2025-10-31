import { Eye, AlertTriangle, Globe } from "lucide-react";
import { KPICard } from "../KPICard";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../ui/table";

const detectionTrendData = [
  { date: "Oct 24", detections: 3 },
  { date: "Oct 25", detections: 5 },
  { date: "Oct 26", detections: 4 },
  { date: "Oct 27", detections: 7 },
  { date: "Oct 28", detections: 6 },
  { date: "Oct 29", detections: 9 },
  { date: "Oct 30", detections: 8 },
  { date: "Oct 31", detections: 11 },
];

const unauthorizedTools = [
  { tool: "Claude API (Personal)", domain: "api.anthropic.com", detections: 42, users: 8, lastSeen: "2 min ago" },
  { tool: "ChatGPT Plus", domain: "chat.openai.com", detections: 35, users: 12, lastSeen: "15 min ago" },
  { tool: "LM Studio", domain: "localhost:1234", detections: 28, users: 5, lastSeen: "1 hour ago" },
  { tool: "Ollama", domain: "localhost:11434", detections: 22, users: 4, lastSeen: "3 hours ago" },
  { tool: "Perplexity AI", domain: "perplexity.ai", detections: 18, users: 7, lastSeen: "30 min ago" },
  { tool: "Gemini (Personal)", domain: "gemini.google.com", detections: 15, users: 6, lastSeen: "45 min ago" },
  { tool: "Poe.com", domain: "poe.com", detections: 12, users: 3, lastSeen: "2 hours ago" },
  { tool: "HuggingChat", domain: "huggingface.co/chat", detections: 9, users: 2, lastSeen: "4 hours ago" },
];

const suspiciousProcesses = [
  { process: "LM Studio", department: "Engineering", users: 5, risk: "High", activity: "Local LLM inference" },
  { process: "Ollama", department: "Engineering", users: 4, risk: "High", activity: "Uncorporate LLM usage" },
  { process: "GPT4All", department: "Marketing", users: 2, risk: "Medium", activity: "Desktop AI assistant" },
  { process: "text-generation-webui", department: "Engineering", users: 3, risk: "High", activity: "Custom model hosting" },
];

const departmentActivity = [
  { department: "Engineering", total: 95, critical: 12, high: 28, medium: 35, low: 20 },
  { department: "Marketing", total: 42, critical: 5, high: 12, medium: 18, low: 7 },
  { department: "Sales", total: 38, critical: 3, high: 10, medium: 15, low: 10 },
  { department: "HR", total: 15, critical: 1, high: 4, medium: 6, low: 4 },
  { department: "Finance", total: 12, critical: 2, high: 3, medium: 5, low: 2 },
];

export function ShadowAI() {
  return (
    <div className="space-y-6 p-6">
      {/* Page Title */}
      <div>
        <h1>Shadow AI Detection</h1>
        <p className="text-muted-foreground mt-1">
          Monitor and detect unauthorized AI tool usage across your organization
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <KPICard
          title="Total Detections"
          value="202"
          icon={Eye}
          trend={{ value: "28.5%", isPositive: false }}
          color="destructive"
        />
        <KPICard
          title="Unauthorized Tools"
          value="18"
          icon={Globe}
          trend={{ value: "12.3%", isPositive: false }}
          color="accent"
        />
        <KPICard
          title="Affected Users"
          value="47"
          icon={AlertTriangle}
          trend={{ value: "15.8%", isPositive: false }}
          color="destructive"
        />
      </div>

      {/* Detection Trend */}
      <Card>
        <CardHeader>
          <CardTitle>Shadow AI Detection Trend</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={detectionTrendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="date" stroke="#6B7280" />
              <YAxis stroke="#6B7280" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#ffffff', 
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px'
                }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="detections" 
                stroke="#EF4444" 
                strokeWidth={3}
                name="Detections"
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Unauthorized Tools Table */}
      <Card>
        <CardHeader>
          <CardTitle>Unauthorized Tools & Domains</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Tool/Service</TableHead>
                <TableHead>Domain</TableHead>
                <TableHead className="text-right">Detections</TableHead>
                <TableHead className="text-right">Users</TableHead>
                <TableHead>Last Seen</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {unauthorizedTools.map((tool, idx) => (
                <TableRow key={idx} className="hover:bg-muted/50">
                  <TableCell>{tool.tool}</TableCell>
                  <TableCell className="font-mono text-sm text-muted-foreground">
                    {tool.domain}
                  </TableCell>
                  <TableCell className="text-right">
                    <Badge className="bg-[#EF4444]">{tool.detections}</Badge>
                  </TableCell>
                  <TableCell className="text-right">{tool.users}</TableCell>
                  <TableCell className="text-muted-foreground">{tool.lastSeen}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Suspicious Processes */}
      <Card>
        <CardHeader>
          <CardTitle>Suspicious Processes Detected</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {suspiciousProcesses.map((process, idx) => (
              <div 
                key={idx}
                className="p-4 border border-border rounded-lg hover:border-[#EF4444]/50 transition-colors"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="mb-1">{process.process}</h4>
                    <p className="text-muted-foreground">{process.activity}</p>
                  </div>
                  <Badge 
                    className={
                      process.risk === "High" ? "bg-[#EF4444]" :
                      process.risk === "Medium" ? "bg-[#F59E0B]" :
                      "bg-[#1E90FF]"
                    }
                  >
                    {process.risk}
                  </Badge>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">{process.department}</span>
                  <span>{process.users} users affected</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Department Activity Map */}
      <Card>
        <CardHeader>
          <CardTitle>Shadow AI Activity by Department</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {departmentActivity.map((dept, idx) => (
              <div key={idx} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span>{dept.department}</span>
                  <span className="text-muted-foreground">{dept.total} total detections</span>
                </div>
                <div className="flex gap-1 h-8">
                  <div 
                    className="bg-[#EF4444] rounded-l flex items-center justify-center text-white text-sm"
                    style={{ width: `${(dept.critical / dept.total) * 100}%` }}
                    title={`${dept.critical} critical`}
                  >
                    {dept.critical > 0 && dept.critical}
                  </div>
                  <div 
                    className="bg-[#F59E0B] flex items-center justify-center text-white text-sm"
                    style={{ width: `${(dept.high / dept.total) * 100}%` }}
                    title={`${dept.high} high`}
                  >
                    {dept.high > 0 && dept.high}
                  </div>
                  <div 
                    className="bg-[#1E90FF] flex items-center justify-center text-white text-sm"
                    style={{ width: `${(dept.medium / dept.total) * 100}%` }}
                    title={`${dept.medium} medium`}
                  >
                    {dept.medium > 0 && dept.medium}
                  </div>
                  <div 
                    className="bg-[#6B7280] rounded-r flex items-center justify-center text-white text-sm"
                    style={{ width: `${(dept.low / dept.total) * 100}%` }}
                    title={`${dept.low} low`}
                  >
                    {dept.low > 0 && dept.low}
                  </div>
                </div>
                <div className="flex gap-4 text-sm text-muted-foreground">
                  <span>🔴 Critical: {dept.critical}</span>
                  <span>🟠 High: {dept.high}</span>
                  <span>🔵 Medium: {dept.medium}</span>
                  <span>⚪ Low: {dept.low}</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
