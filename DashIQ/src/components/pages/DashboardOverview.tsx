import { Activity, AlertTriangle, Eye, Server } from "lucide-react";
import { KPICard } from "../KPICard";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

const dailyUsageData = [
  { date: "Oct 24", requests: 1200, violations: 45 },
  { date: "Oct 25", requests: 1850, violations: 32 },
  { date: "Oct 26", requests: 2100, violations: 28 },
  { date: "Oct 27", requests: 1950, violations: 51 },
  { date: "Oct 28", requests: 2400, violations: 38 },
  { date: "Oct 29", requests: 2800, violations: 42 },
  { date: "Oct 30", requests: 3200, violations: 35 },
  { date: "Oct 31", requests: 2950, violations: 29 },
];

const departmentData = [
  { department: "Engineering", requests: 8500 },
  { department: "Sales", requests: 3200 },
  { department: "Marketing", requests: 4100 },
  { department: "HR", requests: 1800 },
  { department: "Finance", requests: 2400 },
];

const modelVendorData = [
  { name: "OpenAI", value: 45, color: "#1E90FF" },
  { name: "Anthropic", value: 25, color: "#10B981" },
  { name: "Google", value: 15, color: "#F59E0B" },
  { name: "On-Prem", value: 10, color: "#8B5CF6" },
  { name: "Others", value: 5, color: "#6B7280" },
];

const recentEvents = [
  { time: "14:32", user: "john.doe@company.com", model: "GPT-4", policy: "PII Detection", risk: "High" },
  { time: "14:28", user: "jane.smith@company.com", model: "Claude-2", policy: "Data Leak Prevention", risk: "Critical" },
  { time: "14:15", user: "mike.johnson@company.com", model: "On-Prem LLaMA", policy: "Usage Limit", risk: "Medium" },
  { time: "14:05", user: "sarah.williams@company.com", model: "GPT-4", policy: "Shadow AI Detection", risk: "High" },
  { time: "13:58", user: "robert.brown@company.com", model: "Gemini Pro", policy: "Content Filter", risk: "Low" },
];

const heatmapData = [
  { hour: "00:00", Mon: 2, Tue: 1, Wed: 3, Thu: 2, Fri: 1, Sat: 0, Sun: 0 },
  { hour: "04:00", Mon: 1, Tue: 0, Wed: 1, Thu: 1, Fri: 0, Sat: 0, Sun: 0 },
  { hour: "08:00", Mon: 15, Tue: 18, Wed: 22, Thu: 19, Fri: 16, Sat: 3, Sun: 2 },
  { hour: "12:00", Mon: 28, Tue: 32, Wed: 35, Thu: 30, Fri: 25, Sat: 5, Sun: 4 },
  { hour: "16:00", Mon: 22, Tue: 25, Wed: 28, Thu: 24, Fri: 20, Sat: 2, Sun: 1 },
  { hour: "20:00", Mon: 8, Tue: 10, Wed: 12, Thu: 9, Fri: 15, Sat: 1, Sun: 1 },
];

export function DashboardOverview() {
  return (
    <div className="space-y-6 p-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          title="Total AI Requests"
          value="28.4K"
          icon={Activity}
          trend={{ value: "12.5%", isPositive: true }}
          color="primary"
        />
        <KPICard
          title="Policy Violations"
          value="342"
          icon={AlertTriangle}
          trend={{ value: "8.2%", isPositive: false }}
          color="destructive"
        />
        <KPICard
          title="Shadow AI Detected"
          value="28"
          icon={Eye}
          trend={{ value: "15.3%", isPositive: false }}
          color="accent"
        />
        <KPICard
          title="On-Prem LLM Usage"
          value="2.8K"
          icon={Server}
          trend={{ value: "22.1%", isPositive: true }}
          color="secondary"
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Daily Usage Trend */}
        <Card>
          <CardHeader>
            <CardTitle>AI Usage Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={dailyUsageData}>
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
                  dataKey="requests" 
                  stroke="#1E90FF" 
                  strokeWidth={2}
                  name="Requests"
                />
                <Line 
                  type="monotone" 
                  dataKey="violations" 
                  stroke="#EF4444" 
                  strokeWidth={2}
                  name="Violations"
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Department Requests */}
        <Card>
          <CardHeader>
            <CardTitle>Department Usage</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={departmentData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis dataKey="department" stroke="#6B7280" />
                <YAxis stroke="#6B7280" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#ffffff', 
                    border: '1px solid #E5E7EB',
                    borderRadius: '8px'
                  }}
                />
                <Bar dataKey="requests" fill="#1E90FF" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Model Vendor Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Model Vendor Distribution</CardTitle>
          </CardHeader>
          <CardContent className="flex justify-center">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={modelVendorData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="value"
                  label={(entry) => `${entry.name} ${entry.value}%`}
                >
                  {modelVendorData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Recent High-Risk Events */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Recent High-Risk Events</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recentEvents.map((event, idx) => (
                <div 
                  key={idx}
                  className="flex items-center justify-between p-3 bg-muted/50 rounded-lg hover:bg-muted transition-colors"
                >
                  <div className="flex items-center gap-4 flex-1">
                    <span className="text-muted-foreground min-w-[50px]">{event.time}</span>
                    <span className="flex-1 truncate">{event.user}</span>
                    <span className="text-muted-foreground">{event.model}</span>
                    <span className="text-muted-foreground">{event.policy}</span>
                  </div>
                  <Badge 
                    className={
                      event.risk === "Critical" ? "bg-[#EF4444]" :
                      event.risk === "High" ? "bg-[#F59E0B]" :
                      event.risk === "Medium" ? "bg-[#1E90FF]" :
                      "bg-[#6B7280]"
                    }
                  >
                    {event.risk}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Shadow AI Heatmap */}
      <Card>
        <CardHeader>
          <CardTitle>Shadow AI Activity Heatmap (by Hour)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr>
                  <th className="text-left p-2">Hour</th>
                  {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((day) => (
                    <th key={day} className="text-center p-2">{day}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {heatmapData.map((row, idx) => (
                  <tr key={idx}>
                    <td className="p-2 text-muted-foreground">{row.hour}</td>
                    {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((day) => {
                      const value = row[day as keyof typeof row] as number;
                      const intensity = Math.min(value / 35, 1);
                      return (
                        <td key={day} className="p-1">
                          <div 
                            className="w-12 h-8 rounded flex items-center justify-center transition-all hover:scale-110"
                            style={{
                              backgroundColor: `rgba(30, 144, 255, ${intensity})`,
                              color: intensity > 0.5 ? '#ffffff' : '#111827'
                            }}
                            title={`${day} ${row.hour}: ${value} detections`}
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
    </div>
  );
}
